from django.urls import path, re_path
from forms_engine_management import views
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static
  

urlpatterns = [

    path('create_question/', views.create_question, name="create_question"),
    path('assign_question_to_section/<int:template_id>/<int:section_id>/', views.assign_question_to_section, name="assign_question_to_section"),
    path('update_question/<int:question_id>/', views.update_question, name="update_question"),
    path('get_question/<int:question_id>/', views.get_question, name="get_question"),
    path('create_form_template/', views.create_form_template, name="create_form_template"),
    path('list_form_templates/', views.list_form_templates, name="list_form_templates"),
    path('list_questions/', views.list_questions, name="list_questions"),
    path('list_form_sections/<int:template_id>/', views.list_form_sections, name="list_form_sections"),
    path('list_section_questions/<int:template_id>/<int:section_id>/', views.list_section_questions, name="list_section_questions"),
    path('get_form_template/<int:template_id>/', views.get_form_template, name="get_form_template"),
    path('create_form_section/<int:template_id>/', views.create_form_section, name="create_form_section"),
    path('update_form_template/<int:template_id>/', views.update_form_template, name="update_form_template"),
    path('update_form_section/<int:section_id>/<int:template_id>/', views.update_form_section, name="update_form_section"),
    path('update_section_question/<int:template_id>/<int:section_id>/<int:section_question_id>/', views.update_section_question, name="update_section_question"),
    path('remove_question_from_section/<int:template_id>/<int:section_id>/<int:section_question_id>/', views.remove_question_from_section, name="remove_question_from_section"),
    path('list_case_form_assignments/<int:case_id>/', views.list_case_form_assignments, name="list_case_form_assignments"),
    path('assign_form_to_case/<int:case_id>/', views.assign_form_to_case, name="assign_form_to_case"),
    path('review_case_form_assignment/<int:assignment_id>/', views.review_case_form_assignment  , name="review_case_form_assignment"),
    path('get_case_form_assignment/<int:assignment_id>/', views.get_case_form_assignment, name="get_case_form_assignment"),
    path('get_form_submission/<int:assignment_id>/', views.get_form_submission, name="get_form_submission"),
    path('list_form_responses/<int:submission_id>/', views.list_form_responses, name="list_form_responses"),
    path('start_form_submission/<int:assignment_id>/', views.start_form_submission, name="start_form_submission"),
    path('save_form_response/<int:submission_id>/', views.save_form_response, name="save_form_response"),
    path('add_question_option/<int:question_id>/', views.add_question_option, name="add_question_option"),
    path('list_question_options/<int:question_id>/', views.list_question_options, name="list_question_options"),
    path('update_question_option/<int:option_id>/', views.update_question_option, name="update_question_option"),
    path('delete_question_option/<int:option_id>/', views.delete_question_option, name="delete_question_option"),
    path('submit_form/<int:submission_id>/', views.submit_form, name="submit_form"),
    # path('submit_form_submission/<int:assignment_id>/', views.submit_form_submission, name="submit_form_submission"),





]   