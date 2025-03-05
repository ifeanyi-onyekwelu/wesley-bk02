from django.urls import path
from . import views

app_name = "auth"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
    path(
        "reset-password/<uuid:token>/", views.reset_password_view, name="reset_password"
    ),
    path(
        "reset-password/sent/",
        views.reset_password_sent_view,
        name="reset_password_sent",
    ),
    path(
        "reset-password/done/",
        views.reset_password_done_view,
        name="reset_password_done",
    ),
    path("logout/", views.logout_view, name="logout"),
    path("verify-account/", views.verify_account, name="verify_account"),
    path("verify-login/", views.verify_login, name="verify_login"),
    path("resend-verification/", views.resend_verification_email, name="resend_verification"),
    path("resend-password-reset/", views.resend_password_reset_email, name="resend_password_reset"),
    path("resend-login-verification/", views.resend_verify_login_email, name="resend_verify_login"),
]
