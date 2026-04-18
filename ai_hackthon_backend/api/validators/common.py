import json

from django.core.exceptions import ValidationError


class RequestValidationError(ValidationError):
    """Raised when incoming request payload is invalid."""


def parse_json_body(request):
    try:
        body = request.body.decode("utf-8") if request.body else "{}"
        data = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RequestValidationError("Invalid JSON payload.") from exc

    if not isinstance(data, dict):
        raise RequestValidationError("Request JSON must be an object.")
    return data
