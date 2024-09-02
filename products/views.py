from django import views
from django.http import JsonResponse

from products.service import ProductService


# Create your views here.
class ProductView(views.View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductService()

    def get_products(self, request, *args, **kwargs):
        products = self.service.get_products()
        return JsonResponse(products, safe=False)
