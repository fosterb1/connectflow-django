from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='index'),
    path('resource/add/', views.resource_create, name='resource_create'),
    path('resource/<uuid:resource_id>/book/', views.booking_create, name='booking_create'),
    path('<uuid:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('<uuid:pk>/approve/<str:action>/', views.booking_approve, name='booking_approve'),
]