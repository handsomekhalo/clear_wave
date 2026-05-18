"""Urls for the api views of forms_engine_management app"""
from django.urls import path
import forms_engine_management.api.views as views
from system_management.helper_function import send_email_api




urlpatterns = [
    path('create_form_template_api/', views.create_form_template_api, name="create_form_template_api"),
    path('list_form_templates_api/', views.list_form_templates_api, name="list_form_templates_api"),
    path('get_form_template_api/<int:template_id>/', views.get_form_template_api, name="get_form_template_api"),
    path('update_form_template_api/<int:template_id>/', views.update_form_template_api, name="update_form_template_api"),
    path('create_form_section_api/', views.create_form_section_api, name="create_form_section_api"),
    path('list_form_sections_api/', views.list_form_sections_api, name="list_form_sections_api"),
    path('update_form_section_api/<int:section_id>/', views.update_form_section_api, name="update_form_section_api"),
    path('create_question_api/', views.create_question_api, name="create_question_api"),
    path('list_questions_api/', views.list_questions_api, name="list_questions_api"),
    path('get_question_api/<int:question_id>/', views.get_question_api, name="get_question_api"),
    path('update_question_api/<int:question_id>/', views.update_question_api, name="update_question_api"),
    path('add_question_option_api/', views.add_question_option_api, name="add_question_option_api"),    
    path('list_question_options_api/', views.list_question_options_api, name="list_question_options_api"),
    path('update_question_option_api/<int:option_id>/', views.update_question_option_api, name="update_question_option_api"),
    path('delete_question_option_api/<int:option_id>/', views.delete_question_option_api, name="delete_question_option_api"),
    path('assign_question_to_section_api/', views.assign_question_to_section_api, name="assign_question_to_section_api"),
    path('list_section_questions_api/', views.list_section_questions_api, name="list_section_questions_api"),
    path('update_section_question_api/<int:section_question_id>/', views.update_section_question_api, name="update_section_question_api"),
    path('list_case_form_assignments_api/', views.list_case_form_assignments_api, name="list_case_form_assignments_api"),
    path('remove_question_from_section_api/', views.remove_question_from_section_api, name="remove_question_from_section_api"),
    path('assign_form_to_case_api/', views.assign_form_to_case_api, name="assign_form_to_case_api"),
    path('list_case_form_assignments_api/', views.list_case_form_assignments_api, name="list_case_form_assignments_api"),
    path('get_case_form_assignment_api/<int:assignment_id>/', views.get_case_form_assignment_api, name="get_case_form_assignment_api"),
    path('review_case_form_assignment_api/<int:assignment_id>/', views.review_case_form_assignment_api, name="review_case_form_assignment_api"),
    path('start_form_submission_api/', views.start_form_submission_api, name="start_form_submission_api"),    
    path('get_form_submission_api/<int:submission_id>/', views.get_form_submission_api, name="get_form_submission_api"),
    path('save_form_response_api/<int:submission_id>/', views.save_form_response_api, name="save_form_response_api"),
    path('list_form_responses_api/<int:submission_id>/', views.list_form_responses_api, name="list_form_responses_api"),
    path('submit_form_api/<int:submission_id>/', views.submit_form_api, name="submit_form_api"),








]   