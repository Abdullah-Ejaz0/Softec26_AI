from django.core.exceptions import ValidationError
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from api.models import GmailExtractionJob
from api.services.gmail_opportunity_service import GmailOpportunityService
from api.validators import (
    RequestValidationError,
    parse_json_body,
    validate_extract_payload,
    validate_oauth_start_payload,
)


@require_GET
def home(request):
    return JsonResponse(
        {
            "message": "API connected successfully.",
            "endpoints": {
                "oauth_start": "/api/gmail/oauth/start/",
                "oauth_callback": "/api/gmail/oauth/callback/",
                "extract": "/api/gmail/opportunities/extract/",
                "job_status": "/api/gmail/opportunities/jobs/<job_id>/",
            },
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def gmail_oauth_start(request):
    try:
        payload = parse_json_body(request)
        validated = validate_oauth_start_payload(payload)

        state_token = dumps(
            {
                "user_key": validated["user_key"],
                "redirect_uri": validated["redirect_uri"],
            },
            salt="gmail-oauth-state",
        )
        data = GmailOpportunityService.start_oauth(
            redirect_uri=validated["redirect_uri"],
            state_token=state_token,
        )
        return JsonResponse(
            {
                "ok": True,
                "user_key": validated["user_key"],
                "redirect_uri": validated["redirect_uri"],
                "auth_url": data["auth_url"],
            }
        )
    except (RequestValidationError, ValidationError, FileNotFoundError, ValueError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@require_GET
def gmail_oauth_callback(request):
    code = request.GET.get("code", "")
    state = request.GET.get("state", "")

    if not code or not state:
        return JsonResponse(
            {
                "ok": False,
                "error": "Missing one of required query params: code, state.",
            },
            status=400,
        )

    try:
        state_payload = loads(state, max_age=900, salt="gmail-oauth-state")
        user_key = str(state_payload.get("user_key", "default")).strip() or "default"
        redirect_uri = str(state_payload.get("redirect_uri", "")).strip()
        if not redirect_uri:
            raise ValueError("redirect_uri missing in OAuth state.")

        result = GmailOpportunityService.finish_oauth(
            code=code,
            state=state,
            redirect_uri=redirect_uri,
        )
        token = GmailOpportunityService.save_token(
            user_key=user_key,
            token_json=result["token_json"],
            gmail_address=result["gmail_address"],
        )

        return JsonResponse(
            {
                "ok": True,
                "message": "Gmail connected successfully.",
                "user_key": token.user_key,
                "gmail_address": token.gmail_address,
            }
        )
    except (BadSignature, SignatureExpired):
        return JsonResponse({"ok": False, "error": "Invalid or expired OAuth state."}, status=400)
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def extract_gmail_opportunities(request):
    try:
        payload = parse_json_body(request)
        validated = validate_extract_payload(payload)

        job = GmailExtractionJob.objects.create(
            user_key=validated["user_key"],
            requested_email_count=validated["email_count"],
            gmail_query=validated["query"],
            status=GmailExtractionJob.STATUS_PENDING,
        )

        try:
            result = GmailOpportunityService.extract_opportunities(
                user_key=validated["user_key"],
                email_count=validated["email_count"],
                query=validated["query"],
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

        return JsonResponse(
            {
                "ok": True,
                "job_id": job.id,
                "result": job.result_json,
            }
        )
    except (RequestValidationError, ValidationError, ValueError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)


@require_GET
def extraction_job_status(request, job_id):
    job = GmailExtractionJob.objects.filter(id=job_id).first()
    if not job:
        return JsonResponse({"ok": False, "error": "Job not found."}, status=404)

    return JsonResponse(
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
