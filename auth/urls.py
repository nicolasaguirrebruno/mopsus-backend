from django.urls import path

from auth.views import (
    change_password, confirm_signup, forgot_password, forgot_password_confirmation, login, logout, refresh_token,
    register_user, resend_confirmation_code,
)

urlpatterns = [
    path("auth/", login, name="login"),
    path("auth/register", register_user, name="register"),
    path("auth/confirm_signup", confirm_signup, name="confirm_signup"),
    path("auth/resend_confirmation_code", resend_confirmation_code, name="resend_confirmation_code"),
    path("auth/logout", logout, name="logout"),
    path("auth/refresh_token", refresh_token, name="refresh_token"),
    path("auth/change_password", change_password, name="change_password"),
    path("auth/forgot_password", forgot_password, name="forgot_password"),
    path("auth/forgot_password_confirmation", forgot_password_confirmation, name="forgot_password_confirmation"),
]
