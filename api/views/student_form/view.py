import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import StudentForm


@csrf_exempt
def create_student_form(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    required_fields = [
        "degree_program",
        "semester",
        "cgpa",
        "skills_interests",
        "preferred_opportunity_types",
        "financial_need",
        "location_preference",
        "past_experience",
    ]

    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        return JsonResponse(
            {
                "error": "Missing required fields",
                "missing_fields": missing_fields,
            },
            status=400,
        )

    try:
        skills_interests = payload["skills_interests"]
        preferred_opportunity_types = payload["preferred_opportunity_types"]

        if not isinstance(skills_interests, list) or not isinstance(
            preferred_opportunity_types, list
        ):
            return JsonResponse(
                {
                    "error": "skills_interests and preferred_opportunity_types must be arrays"
                },
                status=400,
            )

        student_form = StudentForm.objects.create(
            degree_program=str(payload["degree_program"]).strip(),
            semester=int(payload["semester"]),
            cgpa=payload["cgpa"],
            skills_interests=json.dumps(skills_interests),
            preferred_opportunity_types=json.dumps(preferred_opportunity_types),
            financial_need=str(payload["financial_need"]).strip(),
            location_preference=str(payload["location_preference"]).strip(),
            past_experience=str(payload["past_experience"]).strip(),
        )
    except (TypeError, ValueError):
        return JsonResponse(
            {"error": "Invalid data type for one or more fields"},
            status=400,
        )

    return JsonResponse(
        {
            "message": "Student form submitted successfully",
            "id": student_form.id,
        },
        status=201,
    )
