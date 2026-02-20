"""Urls for the api views of system_management app"""
from django.urls import path
import system_management.api.views as views



urlpatterns = [
    path('login_api/', views.login_api, name="login_api"),
    path('create_firm_with_owner_api/', views.create_firm_with_owner_api, name="create_firm_with_owner_api"),
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
    #  path('register_artist_api/', views.register_artist_api, name='register_artist_api'),
    # path('register_listener_api/', views.register_listener_api, name='register_listener_api'),
    # path('get_artist_api/', views.get_artist_api, name="get_artist_api"),
    # path('get_user_types_api/', views.get_user_types_api, name="get_user_types_api"),
    # path('get_all_users_api/', views.get_all_users_api, name="get_all_users_api"),
    # path('get_artist_profile_api/', views.get_artist_profile_api, name="get_artist_profile_api"),
    # # path('update_artist_profile_api/', views.update_artist_profile_api, name="update_artist_profile_api"),
    # path('update_profile_api/', views.update_profile_api, name="update_profile_api"),
    # path('update_admin_profile_api/', views.update_admin_profile_api, name="update_admin_profile_api"),
    # # path('artist_onboarding_api/', views.artist_onboarding_api, name="artist_onboarding_api"),
    # path('artist_onboarding_step_1_api/', views.artist_onboarding_step_1_api, name="artist_onboarding_step_1_api"),
    # path('artist_onboarding_step_2_api/', views.artist_onboarding_step_2_api, 
    #      name="artist_onboarding_step_2_api"),
    # path('get_all_admins_api/', views.get_all_admins_api, name="get_all_admins_api"),
    # path('get_all_artists_api/', views.get_all_artists_api, name="get_all_artists_api"),
    # path('toggle_user_active_api/<int:user_id>/', views.toggle_user_active_api, name="toggle_user_active_api"),
    # path('get_users_api/', views.get_users_api, name="get_users_api"),
    # path('get_user_types_api/', views.get_user_types_api, name="get_user_types_api"),
    # path('update_user_api/', views.update_user_api, name="update_user_api"),
    # path('create_users_api/', views.create_users_api, name="create_users_api"),

    # path('logout_api/', views.logout_api, name="logout_api"),
    # path('send_email_api/', send_email_api, name='send_email_api'),
    # path('delete_user_api/', views.delete_user_api, name='delete_user_api'),


]
