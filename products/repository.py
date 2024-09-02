import os

from google.cloud import bigquery

from products.querys import SELECT_ACTIVE_PRODUCTS


class ProductRepository:
    def __init__(self):
        self.client = bigquery.Client(project=os.getenv("PROJECT_ID"))

    def get_products(self):
        query_results = self.client.query(SELECT_ACTIVE_PRODUCTS)
        products = []
        for row in query_results:
            products.append(
                {
                    "id": row.id,
                    "title": row.title,
                    "price": row.price,
                    "reposition_point": row.reposition_point,
                    "is_active": row.is_active,
                    "stock": row.stock,
                }
            )
        return products
