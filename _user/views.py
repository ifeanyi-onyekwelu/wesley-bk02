from django.shortcuts import render


template_root = "dashboard/user"


# Create your views here.
def dashboard_view(request):
    return render(request, f"{template_root}/dashboard.html")


# ****************************************************************
# * Transfer views
# ****************************************************************
def interbank_transfer_view(request):
    return render(request, f"{template_root}/transfer/interbank.html")


def wire_transfer_view(request):
    return render(request, f"{template_root}/transfer/wire/wire.html")


def add_a_wire_transfer_recipient_view(request):
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
