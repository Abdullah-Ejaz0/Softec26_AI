from django.urls import path

from .views import create_student_form, home

urlpatterns = [
    path('', home),
    path('student-form/', create_student_form, name='create-student-form'),
]
