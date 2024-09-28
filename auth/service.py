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

    # metodo para poder loguearse
    def login_user(self, email, password):
        try:
            # Autenticar con Cognito
            response = cognito_client.initiate_auth(
                ClientId=os.getenv('COGNITO_CLIENT_ID'),
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password,
                },
            )
            # Obtener el usuario de Cognito
            user_info = cognito_client.get_user(
                AccessToken=response['AuthenticationResult']['AccessToken']
            )
            # Buscar el atributo name
            name = None
            for atribute in user_info['UserAttributes']:
                if atribute['Name'] == 'name':
                    name = atribute['Value']

            # Si la autenticación es exitosa, devolvemos los tokens
            return JsonResponse({
                'access_token': response['AuthenticationResult']['AccessToken'],
                'id_token': response['AuthenticationResult']['IdToken'],
                'refresh_token': response['AuthenticationResult']['RefreshToken'],
                'name': name
            }, status=200)

        except ClientError as e:
            # Si hay algún error (usuario incorrecto, contraseña incorrecta, etc.)
            error_message = e.response['Error']['Message']
            return JsonResponse({"error": error_message}, status=400)

    def refresh_cognito_token(self, refresh_token):
        # Llamar a la API para refrescar el token
        response = cognito_client.initiate_auth(
            ClientId=os.getenv('COGNITO_CLIENT_ID'),
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
            }
        )

        return response['AuthenticationResult']

    def logout(self, access_token):
        try:
            # Llamar a globalSignOut para invalidar todos los tokens asociados al usuario
            cognito_client.global_sign_out(
                AccessToken=access_token
            )
            print(222222)
        except ClientError as e:
            print(e)

