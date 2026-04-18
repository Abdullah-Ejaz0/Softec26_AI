import json

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import StudentEmail, StudentEmailBatch


@csrf_exempt
def create_student_email_batch(request):
    if request.method == "GET":
        return _list_student_emails(request)

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    required_fields = ["emails"]
    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        return JsonResponse(
            {"error": "Missing required fields", "missing_fields": missing_fields},
            status=400,
        )

    emails = payload["emails"]

    if not isinstance(emails, list):
        return JsonResponse({"error": "emails must be an array"}, status=400)

    email_records = []
    recipient_list = []
    for index, email_item in enumerate(emails, start=1):
        if not isinstance(email_item, dict):
            return JsonResponse(
                {
                    "error": "Each email item must be an object with email, subject, and body",
                    "invalid_index": index,
                },
                status=400,
            )

        missing_item_fields = [
            field for field in ["email", "subject", "body"] if field not in email_item
        ]
        if missing_item_fields:
            return JsonResponse(
                {
                    "error": "Email item missing required fields",
                    "invalid_index": index,
                    "missing_fields": missing_item_fields,
                },
                status=400,
            )

        normalized_email = str(email_item["email"]).strip().lower()
        subject = str(email_item["subject"]).strip()
        body = str(email_item["body"]).strip()

        try:
            validate_email(normalized_email)
        except ValidationError:
            return JsonResponse(
                {"error": f"Invalid email address at index {index}: {normalized_email}"},
                status=400,
            )

        if not subject:
            return JsonResponse(
                {
                    "error": "subject is required for each email item",
                    "invalid_index": index,
                },
                status=400,
            )

        if not body:
            return JsonResponse(
                {
                    "error": "body is required for each email item",
                    "invalid_index": index,
                },
                status=400,
            )

        recipient_list.append(normalized_email)
        email_records.append(
            {
                "recipient_email": normalized_email,
                "subject": subject,
                "body": body,
            }
        )

    if len(email_records) == 0:
        return JsonResponse(
            {"error": "emails must contain at least one address"},
            status=400,
        )

    with transaction.atomic():
        batch = StudentEmailBatch.objects.create(
            recipient_emails=json.dumps(recipient_list),
            total_recipients=len(email_records),
        )

        StudentEmail.objects.bulk_create(
            [
                StudentEmail(
                    batch=batch,
                    recipient_email=item["recipient_email"],
                    subject=item["subject"],
                    body=item["body"],
                )
                for item in email_records
            ]
        )

    return JsonResponse(
        {
            "message": "Student email batch saved successfully",
            "batch_id": batch.id,
            "total_recipients": batch.total_recipients,
        },
        status=201,
    )


def _list_student_emails(request):
    batch_id = request.GET.get("batch_id")
    emails_qs = StudentEmail.objects.select_related("batch").order_by("id")

    if batch_id:
        if not str(batch_id).isdigit():
            return JsonResponse({"error": "batch_id must be a positive integer"}, status=400)
        emails_qs = emails_qs.filter(batch_id=int(batch_id))

    data = [
        {
            "id": email.id,
            "batch_id": email.batch_id,
            "email": email.recipient_email,
            "subject": email.subject,
            "body": email.body,
            "status": email.status,
            "created_at": email.created_at.isoformat(),
        }
        for email in emails_qs
    ]

    return JsonResponse({"count": len(data), "results": data}, status=200)
