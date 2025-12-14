from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    # Overview
    path('', views.organization_overview, name='overview'),
    
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<uuid:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<uuid:pk>/delete/', views.department_delete, name='department_delete'),
    
    # Teams
    path('teams/', views.team_list, name='team_list'),
    path('departments/<uuid:department_pk>/teams/', views.team_list, name='team_list_by_dept'),
    path('departments/<uuid:department_pk>/teams/create/', views.team_create, name='team_create'),
    path('teams/<uuid:pk>/edit/', views.team_edit, name='team_edit'),
    path('teams/<uuid:pk>/delete/', views.team_delete, name='team_delete'),
]
