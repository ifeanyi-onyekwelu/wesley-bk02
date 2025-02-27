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
]
