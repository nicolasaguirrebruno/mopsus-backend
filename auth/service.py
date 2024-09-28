import os

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from auth.repository import AuthRepository

cognito_client: BaseClient = boto3.client("cognito-idp", os.getenv("AWS_REGION"))


class AuthService:
    def __init__(self):
        self.repository = AuthRepository()

    def register_user(self, email: str, password: str, name: str) -> dict:
        """
        Función para registrar un usuario en Cognito
        :param email: Email del usuario
        :param password: Contraseña del usuario
        :param name: Nombre completo del usuario
        """
        try:
            response = cognito_client.sign_up(
                ClientId=os.getenv("COGNITO_CLIENT_ID"),
                Username=email,
                Password=password,
                UserAttributes=[{"Name": "email", "Value": email}, {"Name": "name", "Value": name}],  # El nombre completo requerido
            )
            self.repository.create_user(email, name)
            return response
        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            return {"error": error_message}

        # Función para confirmar el código de verificación

    def confirm_user_signup(self, email: str, confirmation_code: str) -> dict:
        """
        Función para confirmar el registro del usuario
        :param email: Email del usuario
        :param confirmation_code: Código de confirmación enviado al correo
        """
        try:
            response = cognito_client.confirm_sign_up(
                ClientId=os.getenv("COGNITO_CLIENT_ID"), Username=email, ConfirmationCode=confirmation_code
            )
            return response
        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            return {"error": error_message}

    def resend_confirmation_code_to_user(self, email: str) -> dict:
        """
        Función para reenviar el código de confirmación al usuario
        :param email: Email del usuario
        """
        try:
            cognito_client.resend_confirmation_code(ClientId=os.getenv("COGNITO_CLIENT_ID"), Username=email)
            return {"message": "El código de confirmación ha sido reenviado al correo."}
        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            return {"error": error_message}

    def login_user(self, email: str, password: str) -> dict:
        """
        Función para autenticar al usuario
        :param email: Email del usuario
        :param password: Contraseña del usuario
        :return: Tokens de autenticación si el usuario es válido
        """
        try:
            if self.repository.get_counter(email) >= 5:
                return {"bloqued": "Demasiados intentos de inicio de sesión. Por su seguridad ambie la contraseña."}
            # Autenticar con Cognito
            response = cognito_client.initiate_auth(
                ClientId=os.getenv("COGNITO_CLIENT_ID"),
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "PASSWORD": password,
                },
            )
            user_info = cognito_client.get_user(AccessToken=response["AuthenticationResult"]["AccessToken"])
            name = [attribute for attribute in user_info["UserAttributes"] if attribute["Name"] == "name"][0]["Value"]
            self.repository.reset_counter(email)
            return {
                "access_token": response["AuthenticationResult"]["AccessToken"],
                "id_token": response["AuthenticationResult"]["IdToken"],
                "refresh_token": response["AuthenticationResult"]["RefreshToken"],
                "name": name,
            }

        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            self.repository.increment_counter(email)
            return {"error": error_message}

    def refresh_cognito_token(self, refresh_token: str) -> dict:
        """
        Función para refrescar el token de autenticación
        :param refresh_token: Token de refresco
        :return: Tokens de autenticación si el token de refresco es válido
        """
        response = cognito_client.initiate_auth(
            ClientId=os.getenv("COGNITO_CLIENT_ID"),
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": refresh_token,
            },
        )

        return response["AuthenticationResult"]

    def logout(self, access_token: str) -> None:
        """
        Función para cerrar sesión
        :param access_token: Token de acceso
        """
        try:
            # Llamar a globalSignOut para invalidar todos los tokens asociados al usuario
            cognito_client.global_sign_out(AccessToken=access_token)
        except ClientError as e:
            print(e)

    def change_password(self, access_token: str, password: str, old_password: str) -> dict:
        """
        Función para cambiar la contraseña del usuario
        :param access_token: Email del usuario
        :param password: Nueva contraseña
        :param old_password: Contraseña actual
        """
        try:
            response = cognito_client.change_password(
                PreviousPassword=old_password,
                ProposedPassword=password,
                AccessToken=access_token,
            )
            return response
        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            return {"error": error_message}

    def forgot_password(self, email: str) -> dict:
        """
        Función cuando el usuario se olvido la contraseña
        :param email: Email del usuario
        """
        try:
            response = cognito_client.forgot_password(
                ClientId=os.getenv("COGNITO_CLIENT_ID"),
                Username=email,
            )
            return response
        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            return {"error": error_message}

    def confirm_forgot_password(self, email: str, confirmation_code: str, new_password: str) -> dict:
        """
        Función para modificar contraseña con codigo de verificacion
        :param1 email: Email del usuario
        :param2 confirmation_code: Codigo de verificacion del correo
        :param1 new_password: Nueva contraseña
        """
        try:
            response = cognito_client.confirm_forgot_password(
                ClientId=os.getenv("COGNITO_CLIENT_ID"), Username=email, ConfirmationCode=confirmation_code, Password=new_password
            )
            self.repository.reset_counter(email)
            return response
        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            return {"error": error_message}
