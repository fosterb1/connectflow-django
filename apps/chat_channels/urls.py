from django.urls import path
from . import views

app_name = 'chat_channels'

urlpatterns = [
    path('', views.channel_list, name='channel_list'),
    path('create/', views.channel_create, name='channel_create'),
    path('<uuid:pk>/', views.channel_detail, name='channel_detail'),
    path('<uuid:pk>/edit/', views.channel_edit, name='channel_edit'),
    path('<uuid:pk>/delete/', views.channel_delete, name='channel_delete'),
    
    # Message actions
    path('message/<uuid:pk>/delete/', views.message_delete, name='message_delete'),
    path('message/<uuid:pk>/react/', views.message_react, name='message_react'),
]
