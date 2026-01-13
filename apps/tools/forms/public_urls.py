"""Public URLs for form submission (no authentication required)"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.form_submit_page, name='form_submit'),
    path('success/', views.form_submit_success, name='form_submit_success'),
]
