from django.urls import path

from auth.views import AuthView
from products.views import ProductView

auth_view = AuthView()
urlpatterns = [
    path("auth/", auth_view.login, name="login"),
    path("auth/register", auth_view.register_user, name="register"),
    path("auth/confirm_signup", auth_view.confirm_signup, name="confirm_signup"),
    path("auth/resend_confirmation_code", auth_view.resend_confirmation_code, name="resend_confirmation_code"),
    path("auth/logout", auth_view.logout, name="logout"),
    path("auth/refresh_token", auth_view.refresh_token, name="refresh_token"),
]
