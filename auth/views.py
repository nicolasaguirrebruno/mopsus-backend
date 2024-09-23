import boto3
from botocore.exceptions import ClientError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django import views

from auth.service import AuthService

cognito_client = boto3.client('cognito-idp', region_name='us-east-2')


class AuthView(views.View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = AuthService()

    # Inicializamos el cliente de Cognito


    @csrf_exempt
    def login(self, request):

        if request.method == 'POST':
            # Obtenemos el JSON que contiene email y password
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            # Verificamos que los datos estén presentes
            if not email or not password:
                return JsonResponse({"error": "Faltan las credenciales"}, status=400)

            try:
                # Autenticar con Cognito
                response = cognito_client.initiate_auth(
                    ClientId='1ouph4qf218gqa41btah2jfd9t',
                    AuthFlow='USER_PASSWORD_AUTH',
                    AuthParameters={
                        'USERNAME': email,
                        'PASSWORD': password,
                    },
                )

                # Si la autenticación es exitosa, devolvemos los tokens
                return JsonResponse({
                    'access_token': response['AuthenticationResult']['AccessToken'],
                    'id_token': response['AuthenticationResult']['IdToken'],
                    'refresh_token': response['AuthenticationResult']['RefreshToken']
                }, status=200)

            except ClientError as e:
                # Si hay algún error (usuario incorrecto, contraseña incorrecta, etc.)
                error_message = e.response['Error']['Message']
                return JsonResponse({"error": error_message}, status=400)

        return JsonResponse({"error": "Método no permitido"}, status=405)
