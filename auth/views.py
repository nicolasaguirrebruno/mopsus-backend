import os

import boto3
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from auth.service import AuthService

cognito_client = boto3.client("cognito-idp", os.getenv("AWS_REGION"))  # region_name='us-east-2'

service = AuthService()


@csrf_exempt
@swagger_auto_schema(
    method="post",
    tags=["Auth"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email del usuario"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, description="Contraseña del usuario"),
        },
        required=["email", "password"],
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="Token de acceso del usuario"),
                "id_token": openapi.Schema(type=openapi.TYPE_STRING, description="Token de identificación del usuario"),
                "refresh_token": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token del usuario"),
            },
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de error"),
            },
        ),
        401: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "bloqued": openapi.Schema(type=openapi.TYPE_STRING, description="Usuario bloqueado"),
            },
        ),
    },
)
@api_view(["POST"])
def login(request):
    data = request.data
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return Response({"error": "Faltan las credenciales"}, status=status.HTTP_400_BAD_REQUEST)

    response = service.login_user(email, password)
    if "error" in response:
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    if "bloqued" in response:
        return Response(response, status=status.HTTP_401_UNAUTHORIZED)
    return Response(response, status=status.HTTP_200_OK)


@csrf_exempt
@swagger_auto_schema(
    method="post",
    tags=["Auth"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email del usuario"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, description="Contraseña del usuario"),
            "name": openapi.Schema(type=openapi.TYPE_STRING, description="Nombre completo del usuario"),
        },
        required=["email", "password"],
    ),
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de éxito"),
            },
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de error"),
            },
        ),
    },
)
@api_view(["POST"])
def register_user(request):
    data = request.data

    if "email" not in data or "password" not in data:
        return Response({"error": "Los campos email y password son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

    email = data["email"]
    password = data["password"]
    name = data.get("name")

    response = service.register_user(email, password, name)
    if "error" in response:
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Usuario creado con exito"}, status=status.HTTP_201_CREATED)


@csrf_exempt
@swagger_auto_schema(
    method="post",
    tags=["Auth"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email del usuario"),
            "confirmation_code": openapi.Schema(type=openapi.TYPE_STRING, description="Código de confirmación enviado al correo"),
        },
        required=["email", "confirmation_code"],
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de éxito"),
            },
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de error"),
            },
        ),
    },
)
@api_view(["POST"])
def confirm_signup(request):
    data = request.data

    if "email" not in data or "confirmation_code" not in data:
        return Response({"error": "Los campos email y confirmation_code son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

    email = data["email"]
    confirmation_code = data["confirmation_code"]
    response = service.confirm_user_signup(email, confirmation_code)
    if "error" in response:
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Usuario confirmado"}, status=status.HTTP_200_OK)


@csrf_exempt
@swagger_auto_schema(
    method="post",
    tags=["Auth"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "refresh_token": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token del usuario"),
        },
        required=["refresh_token"],
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="Token de acceso del usuario"),
                "id_token": openapi.Schema(type=openapi.TYPE_STRING, description="Token de identificación del usuario"),
            },
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de error"),
            },
        ),
    },
)
@api_view(["POST"])
def refresh_token(request):
    data = request.data
    refresh_token_from_request = data.get("refresh_token")
    if not refresh_token_from_request:
        return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        auth_result = service.refresh_cognito_token(refresh_token_from_request)
        return Response(
            {
                "access_token": auth_result["AccessToken"],
                "id_token": auth_result["IdToken"],
            },
            status=status.HTTP_200_OK,
        )

    except boto3.client("cognito-idp").exceptions.NotAuthorizedException:
        return Response({"error": "Refresh token no válido"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@swagger_auto_schema(
    method="post",
    tags=["Auth"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email del usuario"),
        },
        required=["email"],
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de éxito"),
            },
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de error"),
            },
        ),
    },
)
@api_view(["POST"])
def resend_confirmation_code(request):
    data = request.data
    email = data.get("email")

    if not email:
        return Response({"error": "El campo email es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    result = service.resend_confirmation_code_to_user(email)

    if "error" in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response(result, status=status.HTTP_200_OK)


@csrf_exempt
@swagger_auto_schema(
    method="post",
    tags=["Auth"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="Token de acceso del usuario"),
        },
        required=["access_token"],
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de éxito"),
            },
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de error"),
            },
        ),
    },
)
@api_view(["POST"])
def logout(request):
    data = request.data
    access_token = data.get("access_token")

    if not access_token:
        return Response({"error": "Access token is required"}, status=status.HTTP_400_BAD_REQUEST)

    service.logout(access_token)
    return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


@csrf_exempt
@swagger_auto_schema(
    method="put",
    tags=["Auth"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="Email del usuario"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, description="Contraseña del usuario"),
            "old_password": openapi.Schema(type=openapi.TYPE_STRING, description="Contraseña anterior del usuario"),
        },
        required=["email", "password", "old_password"],
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de éxito"),
            },
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de error"),
            },
        ),
    },
)
@api_view(["PUT"])
def change_password(request):
    data = request.data
    if "access_token" not in data or "password" not in data or "old_password" not in data:
        return Response({"error": "Los campos access_token, old_password y password son requeridos"}, status=status.HTTP_400_BAD_REQUEST)
    access_token = data["access_token"]
    password = data["password"]
    old_password = data["old_password"]
    if password == old_password:
        return Response({"error": "La nueva contraseña no puede ser igual a la anterior"}, status=status.HTTP_400_BAD_REQUEST)
    response = service.change_password(access_token, password, old_password)
    if "error" in response:
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Cambio de contraseña fue exitoso"}, status=status.HTTP_200_OK)


@csrf_exempt
@swagger_auto_schema(
    method="post",
    tags=["Auth"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email del usuario"),
        },
        required=["email"],
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de éxito"),
            },
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de error"),
            },
        ),
    },
)
@api_view(["POST"])
def forgot_password(request):
    data = request.data
    email = data.get("email")
    if not email:
        return Response({"error": "El campo email es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)
    result = service.forgot_password(email)
    if "error" in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Email de cambio de contraseña enviado exitosamente"}, status=status.HTTP_200_OK)


@csrf_exempt
@swagger_auto_schema(
    method="post",
    tags=["Auth"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email del usuario"),
            "new_password": openapi.Schema(type=openapi.TYPE_STRING, description="Nueva contraseña"),
            "confirmation_code": openapi.Schema(type=openapi.TYPE_STRING, description="Código de confirmación enviado al correo"),
        },
        required=["email", "new_password", "confirmation_code"],
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de éxito"),
            },
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de error"),
            },
        ),
    },
)
@api_view(["POST"])
def forgot_password_confirmation(request):
    data = request.data
    email = data.get("email")
    new_password = data.get("new_password")
    confirmation_code = data.get("confirmation_code")
    if not email or not new_password or not confirmation_code:
        return Response({"error": "El campo email, confirmation_code, new_password son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
    result = service.confirm_forgot_password(email, confirmation_code, new_password)
    if "error" in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "cambio de contraseña exitoso"}, status=status.HTTP_200_OK)
