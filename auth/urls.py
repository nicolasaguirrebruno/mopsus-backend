from django.urls import path

from auth.views import AuthView
from products.views import ProductView

auth_view = AuthView()
urlpatterns = [
    path("auth/", auth_view.login, name="login"),
]
