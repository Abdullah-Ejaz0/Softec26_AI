from django.contrib import admin

from api.models import StudentForm

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
