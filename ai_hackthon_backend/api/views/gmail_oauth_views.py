from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.services.gmail import auth as gmail_auth_service
from api.validators import RequestValidationError, validate_oauth_start_payload


oauth_start_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["redirect_uri"],
    properties={
        "redirect_uri": openapi.Schema(type=openapi.TYPE_STRING, format="uri"),
    },
)


@swagger_auto_schema(method="post", request_body=oauth_start_schema, operation_summary="Start Gmail OAuth")
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def gmail_oauth_start(request):
    try:
        validated = validate_oauth_start_payload(request.data)
        state_token = dumps(
            {
                "user_key": validated["user_key"],
                "redirect_uri": validated["redirect_uri"],
            },
            salt="gmail-oauth-state",
        )
        data = gmail_auth_service.start_oauth(
            redirect_uri=validated["redirect_uri"],
            state_token=state_token,
        )
        return Response(
            {
                "ok": True,
                "user_key": validated["user_key"],
                "redirect_uri": validated["redirect_uri"],
                "auth_url": data["auth_url"],
            }
        )
    except (RequestValidationError, FileNotFoundError, ValueError, ImportError) as exc:
        return Response({"ok": False, "error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="Gmail OAuth callback",
    manual_parameters=[
        openapi.Parameter("code", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),
        openapi.Parameter("state", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),
    ],
)
@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def gmail_oauth_callback(request):
    code = request.query_params.get("code", "")
    state = request.query_params.get("state", "")

    if not code or not state:
        return Response(
            {"ok": False, "error": "Missing one of required query params: code, state."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        state_payload = loads(state, max_age=900, salt="gmail-oauth-state")
        user_key = str(state_payload.get("user_key", "default")).strip() or "default"
        redirect_uri = str(state_payload.get("redirect_uri", "")).strip()
        if not redirect_uri:
            raise ValueError("redirect_uri missing in OAuth state.")

        result = gmail_auth_service.finish_oauth(
            code=code,
            state=state,
            redirect_uri=redirect_uri,
        )
        token = gmail_auth_service.save_token(
            user_key=user_key,
            token_json=result["token_json"],
            gmail_address=result["gmail_address"],
        )

        return Response(
            {
                "ok": True,
                "message": "Gmail connected successfully.",
                "user_key": token.user_key,
                "gmail_address": token.gmail_address,
            }
        )
    except (BadSignature, SignatureExpired):
        return Response(
            {"ok": False, "error": "Invalid or expired OAuth state."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        return Response({"ok": False, "error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
