from django.shortcuts import render, get_object_or_404, redirect
from app.models import BankAccount, Transfer, Recipient
from django.db import transaction
from django.contrib import messages
from decimal import Decimal
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.decorators import login_required


template_root = "dashboard/user"


def has_sufficient_funds(sender_account, amount):
    try:
        amount_decimal = Decimal(
            str(amount)
        )  # Convert via string to avoid float issues
        return sender_account.balance >= amount_decimal
    except (TypeError, ValueError):
        return False


# Create your views here.
def dashboard_view(request):
    account = get_object_or_404(BankAccount, user=request.user)
    IP = None

    context = {
        "account": account,
        "IP": IP,
    }

    return render(request, f"{template_root}/dashboard.html", context)


# ****************************************************************
# * Transfer views
# ****************************************************************
def interbank_transfer_view(request):
    if request.method == "POST":
        try:
            with transaction.atomic():  # All or nothing
                amount = request.POST.get("amount")
                account_number = request.POST.get("accountNumber")

                if not amount and not account_number:
                    messages.error(request, "Please fill in all fields.")

                sender_account = get_object_or_404(BankAccount, user=request.user)
                recipient_account = get_object_or_404(
                    BankAccount, account_number=account_number
                )

                if not recipient_account:
                    messages.error(request, "Account validation failed.")
                    return render(request, f"{template_root}/transfer/interbank.html")

                if sender_account.is_blocked or recipient_account.is_blocked:
                    messages.error(
                        request,
                        "One of the accounts is blocked from transferring/recieving funds.",
                    )
                    return render(request, f"{template_root}/transfer/interbank.html")

                amount_decimal = Decimal(str(amount))

                # Deduct and add in single atomic operation
                sender_account = BankAccount.objects.select_for_update().get(
                    user=request.user
                )
                recipient_account = BankAccount.objects.select_for_update().get(
                    account_number=account_number
                )

                if not has_sufficient_funds(sender_account, amount_decimal):
                    raise ValueError("Insufficient funds")

                Transfer.objects.create(
                    user=request.user,
                    recipient_account=recipient_account,
                    sender=sender_account,
                    amount=amount,
                    transfer_type="interbank",
                )

                sender_account.balance -= amount_decimal
                sender_account.save()

                recipient_account.balance += amount_decimal
                recipient_account.save()

                messages.success(request, "Transfer successful!")
                return redirect("dashboard")

        except Exception as e:
            messages.error(request, f"Transfer failed: {str(e)}")

    return render(request, f"{template_root}/transfer/interbank.html")


@login_required
def wire_transfer_view(request):
    if request.method == "POST":
        try:
            with transaction.atomic():  # All or nothing
                recipient = request.POST.get("recipient")
                date = request.POST.get("delivery_date")
                amount = request.POST.get("amount")
                reason = request.POST.dict("description")

                if not recipient or not date or not amount or not reason:
                    messages.error(request, "Please fill in all fields.")
                    return render(request, f"{template_root}/transfer/wire/wire.html")

                amount_decimal = Decimal(str(amount))
                sender_account = get_object_or_404(BankAccount, user=request.user)

                if not has_sufficient_funds(sender_account, amount_decimal):
                    messages.error(request, "Insufficient funds")
                    return render(request, f"{template_root}/transfer/wire/wire.html")

                sender_account.balance -= amount_decimal

        except Exception as e:
            messages.error(request, f"Failed to validate recipient data: {str(e)}")
            return render(request, f"{template_root}/transfer/wire/wire.html")
    return render(request, f"{template_root}/transfer/wire/wire.html")


def validate_recipient_data(data):
    """Helper function to validate recipient data (raises ValidationError)"""
    if not data.get("country"):
        raise ValidationError("Country is required")
    if not data.get("address"):
        raise ValidationError("Address is required")
    if not data.get("email") or not re.match(r"^[^@]+@[^@]+\.[^@]+$", data["email"]):
        raise ValidationError("A valid email is required")
    if not data.get("phone") or not re.match(
        r"^\+?[0-9\s\-\(\)]{7,20}$", data["phone"]
    ):
        raise ValidationError("A valid phone number is required")
    if not data.get("fullName"):
        raise ValidationError("Full name is required")
    if not data.get("accountNumber"):
        raise ValidationError("Account number is required")
    if data.get("swift") and not re.match(
        r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$", data["swift"]
    ):
        raise ValidationError("Invalid SWIFT code")
    if data.get("iban") and not re.match(
        r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$", data["iban"]
    ):
        raise ValidationError("Invalid IBAN format")


@login_required
def add_a_wire_transfer_recipient_view(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                # Extract and clean data
                data = {
                    "country": request.POST.get("country", "").strip(),
                    "state": request.POST.get("state", "").strip(),
                    "city": request.POST.get("city", "").strip(),
                    "address": request.POST.get("address", "").strip(),
                    "postal": request.POST.get("postal", "").strip(),
                    "email": request.POST.get("email", "").strip(),
                    "phone": request.POST.get("phone", "").strip(),
                    "fullName": request.POST.get("fullName", "").strip(),
                    "iban": request.POST.get("iban", "").strip(),
                    "swift": request.POST.get("swift", "").strip(),
                    "accountNumber": request.POST.get("accountNumber", "").strip(),
                }

                # Validate data (raises ValidationError if invalid)
                validate_recipient_data(data)

                # Create recipient
                recipient = Recipient(
                    user=request.user,
                    full_name=data["fullName"],
                    email=data["email"],
                    phone_number=data["phone"],
                    country=data["country"],
                    state=data["state"] or None,
                    city=data["city"] or None,
                    address=data["address"],
                    postal_code=data["postal"] or None,
                    transfer_type="wire_transfer",
                    iban=data["iban"] or None,
                    swift_code=data["swift"] or None,
                    account_number=data["accountNumber"],
                )
                recipient.full_clean()  # Final model validation
                recipient.save()

                messages.success(request, "Recipient added successfully!")
                return redirect("user:wire_transfer")  # Redirect to success page

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, f"{template_root}/transfer/wire/add-a-recipient.html")


def wire_transfer_history_view(request):
    return render(request, f"{template_root}/transfer/wire/history.html")


def deposit_check_view(request):
    return render(request, f"{template_root}/transfer/deposit-check.html")


def other_bank_transfer_view(request):
    return render(request, f"{template_root}/transfer/other-bank.html")


# ****************************************************************
# * Pay bills views
# ****************************************************************
def pay_a_biller_view(request):
    return render(request, f"{template_root}/bills/pay_a_biller.html")


def add_a_payee_view(request):
    return render(request, f"{template_root}/bills/add_a_payee.html")


def pay_a_biller_history_view(request):
    return render(request, f"{template_root}/bills/pay_a_biller_history.html")


# ****************************************************************
# * Virtual Cards views
# ****************************************************************
def virtual_card_view(request):
    return render(request, f"{template_root}/virtual-cards/virtual_card.html")


# ****************************************************************
def virtual_card_application_view(request):
    return render(request, f"{template_root}/virtual-cards/card_application.html")


# ****************************************************************
# * Loans views
# ****************************************************************
def new_loan_request_view(request):
    return render(request, f"{template_root}/loans/request.html")


def loan_history_view(request):
    return render(request, f"{template_root}/loans/loan_history.html")


def transaction_history_view(request):
    return render(request, f"{template_root}/transaction_history.html")


def account_settings_view(request):
    return render(request, f"{template_root}/account_settings.html")


def kyc_verification_view(request):
    return render(request, f"{template_root}/kyc/kyc_verification.html")


def complete_verification_view(request):
    return render(request, f"{template_root}/kyc/complete_verification.html")


def support_ticket_view(request):
    return render(request, f"{template_root}/support_ticket.html")
