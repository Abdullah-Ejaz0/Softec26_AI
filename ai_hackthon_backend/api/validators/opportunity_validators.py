from api.validators.common import RequestValidationError


def validate_extract_payload(data):
    user_key = "default"
    query = str(data.get("query", "")).strip()
    mailbox = str(data.get("mailbox", "inbox")).strip().lower()

    raw_count = data.get("email_count", 20)
    try:
        email_count = int(raw_count)
    except (TypeError, ValueError) as exc:
        raise RequestValidationError("'email_count' must be an integer.") from exc

    if email_count < 1 or email_count > 500:
        raise RequestValidationError("'email_count' must be between 1 and 500.")

    if mailbox not in {"inbox", "spam", "both"}:
        raise RequestValidationError("'mailbox' must be one of: 'inbox', 'spam', 'both'.")

    return {
        "user_key": user_key,
        "email_count": email_count,
        "query": query,
        "mailbox": mailbox,
    }
