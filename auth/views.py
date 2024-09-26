import os

import boto3
from botocore.exceptions import ClientError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django import views

from auth.service import AuthService

cognito_client = boto3.client('cognito-idp', os.getenv('AWS_REGION')) #region_name='us-east-2'


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

            response = self.service.login_user(email, password)

            return response

        return JsonResponse({"error": "Método no permitido"}, status=405)

    # Endpoint para registrar un nuevo usuario
    @csrf_exempt
    def register_user(self, request):
        data = json.loads(request.body)

        # Verificar si los datos requeridos están presentes
        if 'email' not in data or 'password' not in data:

            return JsonResponse({'error': 'Los campos email y password son requeridos'}), 400

        email = data['email']
        password = data['password']
        name = data['name']

        # Registrar al usuario
        response = self.service.register_user(email, password, name)

        # Devolver el resultado en formato JSON
        return response


    # Endpoint para confirmar el correo con el código enviado
    @csrf_exempt
    def confirm_signup(self, request):

        data = json.loads(request.body)

        # Verificar si los datos requeridos están presentes
        if 'email' not in data or 'confirmation_code' not in data:
            return JsonResponse({'error': 'Los campos email y confirmation_code son requeridos'}), 400

        email = data['email']
        confirmation_code = data['confirmation_code']
        # Confirmar el código de verificación
        response = self.service.confirm_user_signup(email, confirmation_code)

        # Devolver el resultado en formato JSON
        return response

    @csrf_exempt
    def resend_confirmation_code(self, request):
        if request.method == 'POST':
            try:
                # Parsear el cuerpo de la solicitud
                data = json.loads(request.body)
                email = data.get('email')

                if not email:
                    return JsonResponse({'error': 'El campo email es obligatorio'}, status=400)

                # Llamar a la función para reenviar el código de confirmación
                result = self.service.resend_confirmation_code_to_user(email)

                # Retornar la respuesta al cliente
                if 'error' in result:
                    return JsonResponse(result, status=400)
                else:
                    return JsonResponse(result)

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Error en el formato del cuerpo de la solicitud'}, status=400)

        else:
            return JsonResponse({'error': 'Método no permitido'}, status=405)