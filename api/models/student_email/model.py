from django.db import models


class StudentEmailBatch(models.Model):
    recipient_emails = models.TextField()
    subject = models.CharField(max_length=255, blank=True, default="")
    body = models.TextField(blank=True, default="")
    total_recipients = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email batch {self.id} ({self.total_recipients} recipients)"


class StudentEmail(models.Model):
    batch = models.ForeignKey(
        StudentEmailBatch,
        on_delete=models.CASCADE,
        related_name="emails",
    )
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    rank = models.PositiveIntegerField(null=True, blank=True)
    recommendation = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient_email} ({self.status})"
