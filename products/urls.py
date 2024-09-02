from django.urls import path

from products.views import ProductView

products_view = ProductView()
urlpatterns = [
    path("products/", products_view.get_products, name="product-list"),
]
