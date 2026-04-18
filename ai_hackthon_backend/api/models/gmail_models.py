from django.db import models


class GmailOAuthToken(models.Model):
    """Stores Gmail OAuth credentials for a logical client/user key."""

    user_key = models.CharField(max_length=128, unique=True, default="default")
    gmail_address = models.EmailField(blank=True)
    token_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_key} ({self.gmail_address or 'unknown'})"


class GmailExtractionJob(models.Model):
    """Tracks extraction requests and stores normalized JSON output."""

    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    user_key = models.CharField(max_length=128, default="default")
    requested_email_count = models.PositiveIntegerField()
    gmail_query = models.CharField(max_length=512, blank=True, default="")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)

    total_messages_scanned = models.PositiveIntegerField(default=0)
    opportunities_found = models.PositiveIntegerField(default=0)
    result_json = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Job #{self.id} [{self.status}]"
