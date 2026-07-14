"""Urls for the api views of system_management app"""
from django.urls import path
import system_management.api.views as views
from system_management.helper_function import send_email_api




urlpatterns = [
    path('login_api/', views.login_api, name="login_api"),
    path('create_firm_with_owner_api/', views.create_firm_with_owner_api, name="create_firm_with_owner_api"),
    path('register_firm_owner_api/', views.register_firm_owner_api, name="register_firm_owner_api"),
    path('admin_firm_list_api/',views.admin_firm_list_api, name="admin_firm_list_api"),
    path('admin_firm_retrieve_api/<int:pk>/', views.admin_firm_retrieve_api, name="admin_firm_retrieve_api"),
    path('admin_firm_update_api/<int:pk>/', views.admin_firm_update_api, name="admin_firm_update_api"),
    path('admin_firm_delete_api/<int:pk>/', views.admin_firm_delete_api, name="admin_firm_delete_api"),
    path('firm_user_create_api/',views.firm_user_create_api, name="firm_user_create_api"),
    path('firm_user_list_api/', views.firm_user_list_api, name="firm_user_list_api"),
    path('firm_user_retrieve_api/<int:pk>/', views.firm_user_retrieve_api, name="firm_user_retrieve_api"),
    path('firm_user_update_api/<int:pk>/', views.firm_user_update_api, name="firm_user_update_api"),
    path('firm_user_delete_api/<int:pk>/', views.firm_user_delete_api, name="firm_user_delete_api"),
    path('change_user_role_api/<int:pk>/', views.change_user_role_api, name="change_user_role_api"),
    path('my_firm_retrieve_api/', views.my_firm_retrieve_api, name="my_firm_retrieve_api"),
    path('my_firm_update_api/', views.my_firm_update_api, name="my_firm_update_api"),
    path('my_profile_retrieve_api/', views.my_profile_retrieve_api, name="my_profile_retrieve_api"),
    path('my_profile_update_api/', views.my_profile_update_api, name="my_profile_update_api"),
    path('change_password_api/', views.change_password_api, name="change_password_api"),
    path('audit_log_list_api/', views.audit_log_list_api, name="audit_log_list_api"),
    path('audit_log_detail_api/<int:pk>/', views.audit_log_detail_api, name="audit_log_detail_api"),
    path('onboarding_step_1_api/', views.onboarding_step_1_api, name="onboarding_step_1_api"),
    path('onboarding_step_2_api/', views.onboarding_step_2_api, name="onboarding_step_2_api"),
    path('get_all_roles_api/',views.get_all_roles_api, name='get_all_roles_api'),
    path('send_email_api/', send_email_api,name='send_email_api'),
    path(
    "firm_user_toggle_status_api/<int:pk>/",views.firm_user_toggle_status_api,name="firm_user_toggle_status_api"
),
    path('request_password_reset_api/', views.request_password_reset_api, name='request_password_reset_api'),
    path('confirm_password_reset_api/', views.confirm_password_reset_api, name='confirm_password_reset_api'),
     # API layer (proxy calls these)
    path("subscription_initialize_api/", views.subscription_initialize_api, name="subscription_initialize_api"),
    path("subscription_verify_api/",     views.subscription_verify_api,     name="subscription_verify_api"),

    
]   
