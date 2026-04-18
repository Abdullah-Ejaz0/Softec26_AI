from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('classify_email/', views.classify_email, name='classify_email'),
]
