"""Urls for the api views of system_management app"""
from django.urls import path
import case_management.api.views as views



urlpatterns = [
            path('create_client_api/', views.create_client_api, name="create_client_api"),


]
