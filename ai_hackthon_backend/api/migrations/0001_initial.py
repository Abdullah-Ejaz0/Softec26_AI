# Generated manually because Django is not installed in the current execution environment.

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GmailExtractionJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_key", models.CharField(default="default", max_length=128)),
                ("requested_email_count", models.PositiveIntegerField()),
                ("gmail_query", models.CharField(blank=True, default="", max_length=512)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("total_messages_scanned", models.PositiveIntegerField(default=0)),
                ("opportunities_found", models.PositiveIntegerField(default=0)),
                ("result_json", models.JSONField(blank=True, default=dict)),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="GmailOAuthToken",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_key", models.CharField(default="default", max_length=128, unique=True)),
                ("gmail_address", models.EmailField(blank=True, max_length=254)),
                ("token_json", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
