from api.validators.common import RequestValidationError


def validate_extract_payload(data):
    user_key = "default"
    query = str(data.get("query", "")).strip()

    raw_count = data.get("email_count", 20)
    try:
        email_count = int(raw_count)
    except (TypeError, ValueError) as exc:
        raise RequestValidationError("'email_count' must be an integer.") from exc

    if email_count < 1 or email_count > 500:
        raise RequestValidationError("'email_count' must be between 1 and 500.")

    return {
        "user_key": user_key,
        "email_count": email_count,
        "query": query,
    }
