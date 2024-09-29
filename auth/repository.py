import os

from google.cloud import bigquery

from auth.querys import (
    INSERT_USER_COUNTER_QUERY, INSERT_USER_QUERY, RESET_COUNTER_QUERY, SELECT_COUNTER_QUERY, UPDATE_COUNTER_QUERY,
)


class AuthRepository:
    def __init__(self):
        self.client = bigquery.Client(project=os.getenv("PROJECT_ID"))

    def create_user(self, email: str, name: str) -> None:

        query_user = f"{INSERT_USER_QUERY} ('{email}', '{name}')"
        query_job = self.client.query(query_user)
        query_job.result()
        query_counter = f"{INSERT_USER_COUNTER_QUERY} ('{email}', 0)"
        query_job = self.client.query(query_counter)
        query_job.result()

    def reset_counter(self, email: str) -> None:
        query = f"{RESET_COUNTER_QUERY} '{email}'"
        query_job = self.client.query(query)
        query_job.result()

    def increment_counter(self, email: str) -> None:
        query = f"{UPDATE_COUNTER_QUERY} '{email}'"
        query_job = self.client.query(query)
        query_job.result()

    def get_counter(self, email: str) -> int:
        """
        Función para obtener el contador de intentos de inicio de sesión
        :param email: Email del usuario
        :return: Contador de intentos de inicio de sesión
        """
        query = f"{SELECT_COUNTER_QUERY} '{email}'"
        query_job = self.client.query(query)
        result = query_job.result()
        for row in result:
            return row.try_counter
        return 0
