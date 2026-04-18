from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class StudentForm(models.Model):
    degree_program = models.CharField(max_length=255)
    semester = models.PositiveSmallIntegerField()
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(4)],
    )
    # Stored as JSON string for SQLite compatibility.
    skills_interests = models.TextField(blank=True, default="[]")
    preferred_opportunity_types = models.TextField(blank=True, default="[]")
    financial_need = models.CharField(max_length=100)
    location_preference = models.CharField(max_length=255)
    past_experience = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.degree_program} - Sem {self.semester}"
