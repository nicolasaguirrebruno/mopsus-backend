from products.repository import ProductRepository


class ProductService:
    def __init__(self):
        self.repository = ProductRepository()

    def get_products(self):
        return self.repository.get_products()
