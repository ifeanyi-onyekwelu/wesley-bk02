from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # ****************************************************************
    # * Transfer views
    # ****************************************************************
    path("transfer/local/", views.interbank_transfer_view, name="interbank_transfer"),
    path("transfer/wire/", views.wire_transfer_view, name="wire_transfer"),
    path(
        "transfer/wire/recipient/add/",
        views.add_a_wire_transfer_recipient_view,
        name="add_a_wire_transfer_recipient",
    ),
    path(
        "transfer/wire/history/",
        views.wire_transfer_history_view,
        name="wire_transfer_history",
    ),
    path(
        "transfer/deposit-check/",
        views.deposit_check_view,
        name="deposit_check",
    ),
    path(
        "transfer/",
        views.other_bank_transfer_view,
        name="other_bank_transfer",
    ),
    # ****************************************************************
    # * Pay a biller views
    # ****************************************************************
    path("pay-bills/", views.pay_a_biller_view, name="pay_a_biller"),
    path("pay-bills/add-payee/", views.add_a_payee_view, name="add_a_payee"),
    path(
        "pay-bills/history/",
        views.pay_a_biller_history_view,
        name="pay_a_biller_history",
    ),
    # ****************************************************************
    # * virtual card views
    # ****************************************************************
    path("virtual-card/", views.virtual_card_view, name="virtual_card"),
    path(
        "virtual-card/application/",
        views.virtual_card_application_view,
        name="virtual_card_application",
    ),
    # ****************************************************************
    # * Loan views
    # ****************************************************************
    path("loans/request/", views.new_loan_request_view, name="new_loan_request"),
    path(
        "loans/history/",
        views.loan_history_view,
        name="loan_history",
    ),
    path("summary/", views.transaction_history_view, name="transaction_history"),
    path("account-settings/", views.account_settings_view, name="account_settings"),
    path("kyc/", views.kyc_verification_view, name="kyc_verification"),
    path("kyc-form/", views.complete_verification_view, name="complete_verification"),
    path("contact/", views.support_ticket_view, name="support_ticket"),
]
