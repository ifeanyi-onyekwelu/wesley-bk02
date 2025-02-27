from django.shortcuts import render
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from app.models import BankAccount
from users.models import User
import random
from django.utils.timezone import now
import random
from django.utils.timezone import now
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from utils.helpers import json_response, send_email

template_root = "public/auth"


@csrf_exempt
def signup_view(request):
    if request.method == "GET":
        return render(request, f"{template_root}/signup.html")

    if request.method == "POST":
        # Personal details
        first_name = request.POST.get("firstName")
        middle_name = request.POST.get("middleName", "")  # Optional
        last_name = request.POST.get("lastName")
        date_of_birth = request.POST.get("dateOfBirth")  # YYYY-MM-DD format
        address1 = request.POST.get("address1")
        country = request.POST.get("country")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zipcode = request.POST.get("zipcode")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone")

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Banking details
        ssn_tin = request.POST.get("ssn")  # Social Security Number / Tax ID
        occupation = request.POST.get("occupation")
        annual_income = request.POST.get("income")
        account_type = request.POST.get("accountType", "SAVINGS")  # Default to savings
        account_currency = request.POST.get("currency", "USD")  # Default currency
        transaction_pin = request.POST.get("pin")  # 6-digit PIN
        passport = request.FILES.get("passport")  # Uploaded passport image

        # Validate required fields
        required_fields = [
            first_name,
            last_name,
            date_of_birth,
            state,
            address1,
            city,
            zipcode,
            email,
            phone_number,
            password1,
            password2,
            ssn_tin,
            occupation,
            annual_income,
            transaction_pin,
            passport,
        ]

        if any(field is None or field == "" for field in required_fields):
            return json_response(False, "All fields are required.", status=400)

        if User.objects.filter(email=email).exists():
            return json_response(False, "Email already exists.", status=400)

        if User.objects.filter(phone_number=phone_number).exists():
            return json_response(False, "Phone number already exists.", status=400)

        if len(transaction_pin) != 4 or not transaction_pin.isdigit():
            return json_response(
                False, "Transaction PIN must be a 4-digit number.", status=400
            )

        # Create User
        user = User.objects.create_user(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            state=state,
            address1=address1,
            city=city,
            zipcode=zipcode,
            country=country,
            email=email,
            phone_number=phone_number,
            password=make_password(password1),
            ssn_tin=ssn_tin,
            occupation=occupation,
            annual_income=annual_income,
            passport=passport,
        )

        # Create a Bank Account
        bank_account = BankAccount.objects.create(
            user=user,
            account_type=account_type,
            account_currency=account_currency,
            transaction_pin=transaction_pin,
        )

        # Send Verification Email
        verification_code = random.randint(100000, 999999)
        send_email(
            "Verify Your Account",
            f"Your verification code is {verification_code}",
            [email],
        )

        return json_response(
            True,
            "Signup successful, verify your email.",
            {"account_number": bank_account.account_number},
        )


@csrf_exempt
def login_view(request):
    if request.method == "GET":
        return render(request, f"{template_root}/login.html")

    if request.method == "POST":
        account_number = request.POST.get("account_number")
        password = request.POST.get("password")

        try:
            bank_account = BankAccount.objects.get(account_number=account_number)
            user = bank_account.user
        except BankAccount.DoesNotExist:
            return json_response(False, "Invalid account number.", status=200)

        if not user.check_password(password):
            return json_response(False, "Incorrect password.", status=200)

        if not user.is_active:
            return json_response(False, "Could not log in.", status=200)

        login(request, user)
        return json_response(
            True, "Login successful.", {"account_number": account_number}
        )


@csrf_exempt
def forgot_password_view(request):
    if request.method == "GET":
        return render(request, f"{template_root}/forgot_password.html")

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return json_response(
                False, "User with this email does not exist.", status=400
            )

        if not user.is_active:
            return json_response(False, "Account is not active.", status=400)

        # Generate Reset Token
        reset_token = user.generate_reset_token()

        # Send Reset Link via Email
        reset_link = f"http://yourfrontend.com/reset-password/{reset_token}/"  # Update with frontend URL
        send_email(
            "Password Reset Link",
            f"Click the link to reset your password: {reset_link}",
            [email],
        )

        return json_response(True, "Password reset link sent to your email.")


@csrf_exempt
def reset_password_view(request, token):
    if request.method == "GET":
        return render(request, f"{template_root}/reset_password.html")

    if request.method == "POST":
        new_password = request.POST.get("new_password")

        try:
            user = User.objects.get(reset_token=token, reset_token_expiry__gt=now())
        except User.DoesNotExist:
            return json_response(False, "Invalid or expired token.", status=400)

        user.set_password(new_password)
        user.reset_token = None  # Clear the token after successful reset
        user.reset_token_expiry = None
        user.save()

        return json_response(True, "Password reset successfully.")


def reset_password_sent_view(request):
    return render(request, f"{template_root}/reset_password_sent.html")


def reset_password_done_view(request):
    return render(request, f"{template_root}/reset_password_done.html")


@csrf_exempt
def logout_view(request):
    if not request.user.is_authenticated:
        return json_response(False, "No user logged in", 400)
    logout(request)
    return json_response(True, "User logged out", 200)
