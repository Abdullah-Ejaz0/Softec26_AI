from django.http import JsonResponse
from django.views.decorators.http import require_GET

from api.models import StudentEmail


@require_GET
def get_opportunity_recommendations(request):
    batch_id = request.GET.get("batch_id")
    limit = request.GET.get("limit")
    email_id = request.GET.get("email_id")
    email_address = request.GET.get("email")

    emails_qs = StudentEmail.objects.order_by("id")

    if batch_id is not None:
        if not str(batch_id).isdigit() or int(batch_id) <= 0:
            return JsonResponse({"error": "batch_id must be a positive integer"}, status=400)
        emails_qs = emails_qs.filter(batch_id=int(batch_id))

    if limit is not None:
        if not str(limit).isdigit() or int(limit) <= 0:
            return JsonResponse({"error": "limit must be a positive integer"}, status=400)
        emails_qs = emails_qs[: int(limit)]

    if email_id is not None:
        if not str(email_id).isdigit() or int(email_id) <= 0:
            return JsonResponse({"error": "email_id must be a positive integer"}, status=400)
        emails_qs = emails_qs.filter(id=int(email_id))

    if email_address is not None:
        normalized_email = str(email_address).strip().lower()
        if not normalized_email:
            return JsonResponse({"error": "email must be a non-empty value"}, status=400)
        emails_qs = emails_qs.filter(recipient_email=normalized_email)

    emails = list(emails_qs)

    # Rank is pass-through: use stored rank when present, otherwise keep stable order.
    sorted_emails = sorted(
        emails,
        key=lambda email: (
            email.rank is None,
            email.rank if email.rank is not None else 10**9,
            email.id,
        ),
    )

    results = []
    for index, email in enumerate(sorted_emails, start=1):
        results.append(
            {
                "id": email.id,
                "batch_id": email.batch_id,
                "email": email.recipient_email,
                "subject": email.subject,
                "body": email.body,
                "rank": email.rank if email.rank is not None else index,
                "recommendation": email.recommendation or "Recommendation pending",
                "status": email.status,
                "created_at": email.created_at.isoformat(),
            }
        )

    return JsonResponse(
        {
            "count": len(results),
            "results": results,
        },
        status=200,
    )
