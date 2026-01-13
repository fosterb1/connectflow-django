"""Main tools URL router."""

from django.urls import path, include

app_name = 'tools'

urlpatterns = [
    path('forms/', include('apps.tools.forms.urls')),
]
