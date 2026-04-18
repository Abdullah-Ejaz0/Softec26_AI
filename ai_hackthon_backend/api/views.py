from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import requests

def home(request):
    return HttpResponse("App Connected Successfully 🚀")

@csrf_exempt
def classify_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email_subject = data.get('subject', '')
            email_from = data.get('from', '')
            email_body = data.get('body', '')

            prompt = f"""
You are an AI assistant helping a university student filter their inbox.
Analyze the following email and determine if it represents a REAL opportunity (Scholarship, Internship, Competition, Research Fellowship, Startup Program, etc.) that the student can apply for. Ignore spam, marketing, account updates, and automated application status emails.

Email Subject: {email_subject}
Email From: {email_from}
Email Body:
{email_body}

Extract the details and return ONLY a valid JSON object matching this schema:
{{
  "isOpportunity": true/false, // True if it is an actionable opportunity. False if it's spam, marketing, or general info.
  "type": "string", // If true, classify as: "Scholarship", "Internship", "Competition", "Research Fellowship", "Startup Program", or "Other". If false, set to null.
  "confidence": 0-100, // How confident are you in this classification?
  "extracted": {{
    "deadline": "string or 'Not specified'", // Extract deadline date if present.
    "eligibility": ["string"], // List of eligibility criteria. Empty array if none.
    "requiredDocs": ["string"], // List of required documents (e.g. CV, Transcript). Empty array if none.
    "contact": "string", // Contact email or link to apply.
    "applyLink": "string or null" // URL to apply, if present.
  }},
  "reasoning": "string" // A 1-sentence explanation of why it is or isn't an opportunity.
}}
"""
            api_key = settings.GEMINI_API_KEY
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "temperature": 0.1,
                }
            }

            response = requests.post(gemini_url, json=payload)
            if response.status_code == 200:
                gemini_data = response.json()
                result_text = gemini_data['candidates'][0]['content']['parts'][0]['text']
                return JsonResponse(json.loads(result_text), safe=False)
            else:
                return JsonResponse({"error": "Failed to connect to Gemini API", "details": response.text}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
