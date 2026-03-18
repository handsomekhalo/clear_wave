"""Urls for the api views of system_management app"""
from django.urls import path
import system_management.api.views as views
from . import views


urlpatterns = [
    path('get_all_clients/',views.get_all_clients, name='get_all_clients'),
    path('create_client/', views.create_client, name='create_client' ),
    path('create_case/', views.create_case, name='create_case'),
    path('get_all_matter_types/',views.get_all_matter_types, name='get_all_matter_types'),
    path('create_matter_type/', views.create_matter_type,name='create_matter_type'),

    # path('create')


]
