"""Main tools URL router."""

from django.urls import path, include
from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('forms/', include('apps.tools.forms.urls')),
    path('documents/', include('apps.tools.documents.urls')),
    path('announcements/', include('apps.tools.announcements.urls')),
    path('bookings/', include('apps.tools.bookings.urls')),
    path('timeoff/', include('apps.tools.timeoff.urls')),
]
