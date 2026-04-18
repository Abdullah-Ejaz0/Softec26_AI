from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.models import GmailExtractionJob
from api.services.gmail.opportunities import extract_opportunities
from api.validators import RequestValidationError, validate_extract_payload


extract_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "email_count": openapi.Schema(type=openapi.TYPE_INTEGER, default=20, minimum=1, maximum=500),
        "query": openapi.Schema(type=openapi.TYPE_STRING, default=""),
        "mailbox": openapi.Schema(type=openapi.TYPE_STRING, default="inbox", enum=["inbox", "spam", "both"]),
    },
)


@swagger_auto_schema(method="post", request_body=extract_schema, operation_summary="Extract opportunities")
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def extract_gmail_opportunities(request):
    try:
        validated = validate_extract_payload(request.data)

        job = GmailExtractionJob.objects.create(
            user_key=validated["user_key"],
            requested_email_count=validated["email_count"],
            gmail_query=(
                f"in:spam {validated['query']}".strip()
                if validated["mailbox"] == "spam"
                else (
                    f"(in:inbox OR in:spam) {validated['query']}".strip()
                    if validated["mailbox"] == "both"
                    else f"in:inbox {validated['query']}".strip()
                )
            ),
            status=GmailExtractionJob.STATUS_PENDING,
        )

        try:
            result = extract_opportunities(
                user_key=validated["user_key"],
                email_count=validated["email_count"],
                query=validated["query"],
                mailbox=validated["mailbox"],
            )
            job.status = GmailExtractionJob.STATUS_SUCCESS
            job.total_messages_scanned = result["meta"]["messages_scanned"]
            job.opportunities_found = result["meta"]["opportunities_found"]
            job.result_json = result
            job.error_message = ""
            job.save(
                update_fields=[
                    "status",
                    "total_messages_scanned",
                    "opportunities_found",
                    "result_json",
                    "error_message",
                    "updated_at",
                ]
            )
        except Exception as exc:
            job.status = GmailExtractionJob.STATUS_FAILED
            job.error_message = str(exc)
            job.save(update_fields=["status", "error_message", "updated_at"])
            raise

        return Response({"ok": True, "job_id": job.id, "result": job.result_json})
    except (RequestValidationError, ValueError) as exc:
        return Response({"ok": False, "error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        return Response({"ok": False, "error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method="get", operation_summary="Get extraction job status")
@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def extraction_job_status(request, job_id):
    job = GmailExtractionJob.objects.filter(id=job_id).first()
    if not job:
        return Response({"ok": False, "error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(
        {
            "ok": True,
            "job": {
                "id": job.id,
                "user_key": job.user_key,
                "status": job.status,
                "requested_email_count": job.requested_email_count,
                "gmail_query": job.gmail_query,
                "total_messages_scanned": job.total_messages_scanned,
                "opportunities_found": job.opportunities_found,
                "error_message": job.error_message,
                "result": job.result_json,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat(),
            },
        }
    )
