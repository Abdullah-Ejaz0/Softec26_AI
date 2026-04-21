# MAILSENSE

MAILSENSE is a web app that helps users find useful opportunities (jobs, internships, programs, etc.) from their Gmail inbox quickly.

## What Problem It Solves

Many users receive a lot of emails and miss important opportunity emails.
This project solves that by:

- Connecting to Gmail securely using OAuth.
- Scanning selected emails from inbox/spam.
- Classifying whether an email is an opportunity.
- Showing structured results in a simple UI.

## How It Works

The project has 2 parts:

- Backend: Django + Django REST Framework
- Frontend: React + Vite

Main flow:

1. User opens the frontend and fills profile details.
2. User connects Gmail using OAuth.
3. Backend fetches emails from Gmail (inbox, spam, or both).
4. Backend classifies emails using:
	- Heuristic rules
	- AI-based endpoint (Gemini key via environment variable)
5. Results are shown in the frontend as opportunity cards/details.

Useful backend endpoints:

- `/api/gmail/oauth/start/`
- `/api/gmail/oauth/callback/`
- `/api/gmail/opportunities/extract/`
- `/api/classify_email/`
- `/api/classify_email/heuristic/`

API docs:

- Swagger UI: `http://127.0.0.1:8000/swagger/`
- ReDoc: `http://127.0.0.1:8000/redoc/`

## How To Run It

### 1) Backend Setup (Django)

Open terminal in `ai_hackthon_backend` and run:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend runs at: `http://127.0.0.1:8000`

### 2) Frontend Setup (React)

Open a second terminal in `my-react-app` and run:

```bash
npm install
npm run dev
```

Frontend runs at: `http://127.0.0.1:5173`

### 3) Environment Variables

In `ai_hackthon_backend/.env`, add:

```env
GEMINI_API_KEY=your_key_here
```

Optional in `my-react-app/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 4) Gmail OAuth Credentials

Place Google OAuth client credentials in:

- `ai_hackthon_backend/credentials.json`

Important:

- Never commit tokens/secrets to git.
- Keep `db.sqlite3`, `.env`, and credential files out of version control.

## Tech Stack

- Frontend: React, Vite, Framer Motion
- Backend: Django, Django REST Framework, drf-yasg
- Integrations: Gmail API, Google OAuth, Gemini API