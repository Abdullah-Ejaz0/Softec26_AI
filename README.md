# Softec26_AI

## Backend Setup

1. Open terminal in `ai_hackthon_backend`.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Start server:

```bash
python manage.py runserver
```

## Swagger Testing

After starting the backend, open:

- Swagger UI: `http://127.0.0.1:8000/swagger/`
- ReDoc: `http://127.0.0.1:8000/redoc/`
- OpenAPI JSON: `http://127.0.0.1:8000/swagger.json`