from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.document_list, name='index'),
    path('folder/<uuid:folder_id>/', views.document_list, name='index_with_folder'),
    path('folder/create/', views.folder_create, name='folder_create'),
    path('folder/<uuid:parent_id>/create/', views.folder_create, name='folder_create_sub'),
    path('upload/', views.document_upload, name='upload'),
    path('folder/<uuid:folder_id>/upload/', views.document_upload, name='upload_in_folder'),
    path('<uuid:pk>/download/', views.document_download, name='download'),
    path('<uuid:pk>/delete/', views.document_delete, name='delete'),
]