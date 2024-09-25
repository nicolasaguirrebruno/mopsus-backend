from auth.repository import AuthRepository
import boto3
from botocore.exceptions import ClientError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import os

cognito_client = boto3.client('cognito-idp', os.getenv('AWS_REGION'))


class AuthService:
    def __init__(self):
        self.repository = AuthRepository()

    # Función para registrar un nuevo usuario en Cognito
    def register_user(self, email, password, name):
        try:
            response = cognito_client.sign_up(
                ClientId=os.getenv('COGNITO_CLIENT_ID'),
                Username=email,
                Password=password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    },
                    {
                        'Name': 'name',  # El nombre completo requerido
                        'Value': name
                    }
                ]
            )

            return JsonResponse(response)
        except ClientError as e:
            error_message = e.response['Error']['Message']
            return JsonResponse({"error": error_message}, status=400)

        # Función para confirmar el código de verificación

    def confirm_user_signup(self, email, confirmation_code):
        try:
            response = cognito_client.confirm_sign_up(
                ClientId=os.getenv('COGNITO_CLIENT_ID'),
                Username=email,
                ConfirmationCode=confirmation_code
            )
            return JsonResponse(response)
        except ClientError as e:
            error_message = e.response['Error']['Message']
            return JsonResponse({"error": error_message}, status=400)

    # Función que maneja la llamada a Cognito para reenviar el código de confirmación
    def resend_confirmation_code_to_user(self, email):
        try:
            response = cognito_client.resend_confirmation_code(
                ClientId=os.getenv('COGNITO_CLIENT_ID'),
                Username=email
            )
            return {'message': 'El código de confirmación ha sido reenviado al correo.'}
        except ClientError as e:
            error_message = e.response['Error']['Message']
            return JsonResponse({"error": error_message}, status=400)