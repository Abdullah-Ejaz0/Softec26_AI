import base64
import re


OPPORTUNITY_KEYWORDS = [
    "apply",
    "application",
    "deadline",
    "grant",
    "fellowship",
    "internship",
    "scholarship",
    "funding",
    "pitch",
    "rfp",
    "proposal",
    "accelerator",
    "call for",
    "submission",
]

DEADLINE_PATTERNS = [
    re.compile(r"deadline\s*[:\-]?\s*([^\n\r\.;]+)", re.IGNORECASE),
    re.compile(r"apply by\s*[:\-]?\s*([^\n\r\.;]+)", re.IGNORECASE),
    re.compile(r"last date\s*[:\-]?\s*([^\n\r\.;]+)", re.IGNORECASE),
    re.compile(r"due date\s*[:\-]?\s*([^\n\r\.;]+)", re.IGNORECASE),
]

ELIGIBILITY_PATTERNS = [
    re.compile(r"eligibility\s*[:\-]\s*([^\n\r]+)", re.IGNORECASE),
    re.compile(r"who can apply\s*[:\-]?\s*([^\n\r]+)", re.IGNORECASE),
    re.compile(r"eligible\s+(?:applicants|candidates)\s*[:\-]?\s*([^\n\r]+)", re.IGNORECASE),
]

DOC_PATTERN = re.compile(
    r"(required documents?|documents required|submit the following)\s*[:\-]?\s*([^\n\r]+)",
    re.IGNORECASE,
)

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?:\+?\d[\d\-\s]{7,}\d)")

TYPE_HINTS = {
    "grant": "grant",
    "scholarship": "scholarship",
    "fellowship": "fellowship",
    "internship": "internship",
    "accelerator": "accelerator",
    "rfp": "request_for_proposal",
    "call for": "call_for_applications",
}


def clean_text(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def get_header(headers, name):
    name = name.lower()
    for item in headers:
        if item.get("name", "").lower() == name:
            return item.get("value", "")
    return ""


def decode_plain_text(part):
    mime_type = part.get("mimeType", "")
    body_data = part.get("body", {}).get("data")

    if mime_type == "text/plain" and body_data:
        try:
            return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
        except Exception:
            return ""

    if mime_type.startswith("multipart/"):
        for child in part.get("parts", []):
            decoded = decode_plain_text(child)
            if decoded.strip():
                return decoded
    return ""


def extract_deadline(text):
    for pattern in DEADLINE_PATTERNS:
        match = pattern.search(text)
        if match:
            return clean_text(match.group(1))
    return ""


def extract_eligibility(text):
    matches = []
    for pattern in ELIGIBILITY_PATTERNS:
        for match in pattern.finditer(text):
            matches.append(clean_text(match.group(1)))

    unique = []
    for item in matches:
        if item and item not in unique:
            unique.append(item)
    return unique[:5]


def extract_required_documents(text):
    match = DOC_PATTERN.search(text)
    if not match:
        return []

    raw = clean_text(match.group(2))
    chunks = [chunk.strip(" .") for chunk in re.split(r",|;| and ", raw) if chunk.strip()]
    return chunks[:10]


def extract_contact_info(text):
    emails = list(dict.fromkeys(EMAIL_PATTERN.findall(text)))[:5]
    phones = list(dict.fromkeys(clean_text(p) for p in PHONE_PATTERN.findall(text)))[:5]
    return {"emails": emails, "phones": phones}


def detect_type(text):
    lowered = text.lower()
    for hint, normalized in TYPE_HINTS.items():
        if hint in lowered:
            return normalized
    return "general_opportunity"


def is_real_opportunity(subject, snippet, body):
    text = f"{subject} {snippet} {body}".lower()
    keyword_hits = sum(1 for keyword in OPPORTUNITY_KEYWORDS if keyword in text)
    deadline_hit = bool(extract_deadline(text))
    apply_signal = "apply" in text or "application" in text
    return keyword_hits >= 2 or (keyword_hits >= 1 and (deadline_hit or apply_signal))


def parse_message(message):
    payload = message.get("payload", {})
    headers = payload.get("headers", [])

    subject = get_header(headers, "Subject")
    date = get_header(headers, "Date")
    from_email = get_header(headers, "From")
    to_email = get_header(headers, "To")
    cc_email = get_header(headers, "Cc")

    snippet = message.get("snippet", "")
    body = clean_text(decode_plain_text(payload))

    return {
        "message_id": message.get("id", ""),
        "thread_id": message.get("threadId", ""),
        "subject": subject,
        "date": date,
        "from": from_email,
        "to": to_email,
        "cc": cc_email,
        "snippet": snippet,
        "body": body,
        "labels": message.get("labelIds", []),
    }


def build_opportunity_record(parsed_message, position_in_thread, thread_size):
    full_text = clean_text(
        f"{parsed_message['subject']}\n{parsed_message['snippet']}\n{parsed_message['body']}"
    )

    return {
        "message_id": parsed_message["message_id"],
        "thread_id": parsed_message["thread_id"],
        "position_in_thread": position_in_thread,
        "thread_size": thread_size,
        "subject": parsed_message["subject"],
        "date": parsed_message["date"],
        "from": parsed_message["from"],
        "to": parsed_message["to"],
        "cc": parsed_message["cc"],
        "opportunity_type": detect_type(full_text),
        "deadline": extract_deadline(full_text),
        "eligibility_conditions": extract_eligibility(full_text),
        "required_documents": extract_required_documents(full_text),
        "application_contact_information": extract_contact_info(full_text),
        "labels": parsed_message["labels"],
        "summary_text": clean_text(f"{parsed_message['snippet']} {parsed_message['body'][:700]}"),
    }
