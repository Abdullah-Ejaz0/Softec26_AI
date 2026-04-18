from api.validators.common import RequestValidationError


def validate_oauth_start_payload(data):
    user_key = "default"
    redirect_uri = str(data.get("redirect_uri", "")).strip()

    if not redirect_uri:
        raise RequestValidationError("'redirect_uri' is required.")

    return {
        "user_key": user_key,
        "redirect_uri": redirect_uri,
    }
