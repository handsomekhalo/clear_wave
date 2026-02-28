"""Urls for the api views of system_management app"""
from django.urls import path
import document_management.api.views as views



urlpatterns = [

    path('upload_document_api/<int:case_id>/', views.upload_document_api, name='upload_document_api'),
    path('get_documents_api/<int:case_id>/', views.get_documents_api, name='get_documents_api'),
    path('view_document_api/<int:document_id>/', views.view_document_api, name='view_document_api'),
    path('share_document_api/<int:document_id>/', views.share_document_api, name='share_document_api'),
    path('revoke_document_api/<int:document_id>/', views.revoke_document_api, name='revoke_document_api'),
    path('access_document_api/<str:shared_link>/', views.access_document_api, name='access_document_api'),
    path('document_access_logs_api/<int:document_id>/', views.document_access_logs_api, name='document_access_logs_api'),
]
