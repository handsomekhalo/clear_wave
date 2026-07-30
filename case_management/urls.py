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
    path('get_all_cases/',views.get_all_cases, name='get_all_cases'),
    path("get_case_details/<int:case_id>/",views.get_case_details,name="get_case_detais"),
    path('get_firm_members/',views.get_firm_members, name='get_firm_members'),
    path('assign_to_case/<int:case_id>/',views.assign_to_case, name='assign_to_case'),
    path('update_case/<int:case_id>/', views.update_case, name='update_case'),
    path("add_note/<int:case_id>/", views.add_note, name="add_note"),
    path("get_case_notes/<int:case_id>/", views.get_case_notes, name="get_case_notes"),
    path('add_time_log/<int:case_id>/', views.add_time_log, name='add_time_log'),
    path('list_time_logs/<int:case_id>/', views.list_time_logs, name='list_time_logs'),
    path('update_time_log/<int:case_id>/<int:log_id>/', views.update_time_log, name='update_time_log'),
    path('delete_time_log/<int:case_id>/<int:log_id>/', views.delete_time_log, name='delete_time_log'),
    path('dashboard_stats/', views.dashboard_stats, name='dashboard_stats'),
    path("list_case_tasks/<int:case_id>/", views.list_case_tasks, name="list_case_tasks"),
    path("create_task/<int:case_id>/", views.create_task, name="create_task"),
    path("update_task/<int:case_id>/<int:task_id>/", views.update_task, name="update_task"),
    path("delete_task/<int:case_id>/<int:task_id>/", views.delete_task, name="delete_task"),
]
