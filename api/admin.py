from django.contrib import admin

from api.models import StudentEmail, StudentEmailBatch, StudentForm

# Register your models here.


@admin.register(StudentForm)
class StudentFormAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"degree_program",
		"semester",
		"cgpa",
		"financial_need",
		"location_preference",
		"created_at",
	)
	search_fields = ("degree_program", "location_preference", "financial_need")


@admin.register(StudentEmailBatch)
class StudentEmailBatchAdmin(admin.ModelAdmin):
	list_display = ("id", "total_recipients", "created_at")


@admin.register(StudentEmail)
class StudentEmailAdmin(admin.ModelAdmin):
	list_display = ("id", "batch", "recipient_email", "subject", "status", "created_at")
	search_fields = ("recipient_email", "subject", "status")
	list_filter = ("status", "created_at")
