from django.urls import path

from .views import create_student_email_batch, create_student_form, home

urlpatterns = [
    path('', home),
    path('student-form/', create_student_form, name='create-student-form'),
    path(
        'student-emails/',
        create_student_email_batch,
        name='create-student-email-batch',
    ),
]
