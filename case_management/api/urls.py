"""Urls for the api views of system_management app"""
from django.urls import path
import case_management.api.views as views



urlpatterns = [
            path('create_client_api/', views.create_client_api, name="create_client_api"),
            path('create_case_api/', views.create_case_api, name="create_case_api"),  
            path('create_matter_type_api/', views.create_matter_type_api, name="create_matter_type_api"),
            path('view_cases_by_firm_api/', views.view_cases_by_firm_api, name="view_cases_by_firm_api"),
            path('get_all_matter_types_api/', views.get_all_matter_types_api, name="get_all_matter_types_api"),
            # path('case_detail_api/<int:pk>', views.case_detail_api, name="case_detail_api")
            path('get_case_detail_api/<int:case_id>/', views.get_case_detail_api, name="get_case_detail_api"),
            path('assign_to_case_api/<int:case_id>/', views.assign_to_case_api, name="assign_to_case_api"),
            path('get_all_cases_api/', views.get_all_cases_api, name="get_all_cases_api"),
            path('update_case_api/<int:case_id>/', views.update_case_api, name="update_case_api"),
            path('change_status_api/<int:case_id>/', views.change_status_api, name="change_status_api"),
            path('add_note_api/<int:case_id>/', views.add_note_api, name="add_note_api"),
            path('get_case_notes_api/<int:case_id>/', views.get_case_notes_api, name="get_case_notes_api"),
            path('get_all_clients_api/', views.get_all_clients_api,name='get_all_clients_api'),
            path('get_firm_members_api',views.get_firm_members_api, name='get_firm_members_api'),
            path("add_note_api/<int:case_id>/", views.add_note_api, name="add_note_api"),
            path("get_case_notes_api/<int:case_id>/", views.get_case_notes_api, name="get_case_notes_api"),
            path('add_time_log_api/<int:case_id>/', views.add_time_log_api, name='add_time_log_api'),
            path('list_time_logs_api/<int:case_id>/', views.list_time_logs_api, name='list_time_logs_api'),
            path('update_time_log_api/<int:case_id>/<int:log_id>/', views.update_time_log_api, name='update_time_log_api'),
            path('delete_time_log_api/<int:case_id>/<int:log_id>/', views.delete_time_log_api, name='delete_time_log_api'),
            path('dashboard_stats_api/', views.dashboard_stats_api, name='dashboard_stats_api'),
            
            # path('cases_by_matter_type_api/', views.cases_by_matter_type_api, name='cases_by_matter_type_api'),
            # path('cases_by_status_api/', views.cases_by_status_api, name='cases_by_status_api'),
                        # path('get_case_by_id_api/<int:case_id>/', views.get_case_by_id_api, name="get_case_by_id_api"),
            


]
