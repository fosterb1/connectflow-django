from django.urls import path
from . import views

app_name = 'announcements'

urlpatterns = [
    path('', views.announcement_list, name='index'),
    path('create/', views.announcement_create, name='create'),
    path('<uuid:pk>/edit/', views.announcement_edit, name='edit'),
    path('<uuid:pk>/delete/', views.announcement_delete, name='delete'),
    path('<uuid:pk>/acknowledge/', views.acknowledge_announcement, name='acknowledge'),
]