from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('user-management/', views.user_management, name='user_management'),
    path('company-job-posts/', views.company_job_posts, name='company_job_posts'),
    path('company-details/', views.company_details, name='company_details'),
    path('job-seeker-details/', views.jobseeker_details, name='jobseeker_details'),
    path('jobseeker-applied-jobs/', views.jobseeker_applied_jobs, name='jobseeker_applied_jobs'),
     path('admin-job-listing/', views.admin_job_listing, name='admin_job_listing'),
     path('subscriptions/', views.subscription_view, name='subscriptions'),
      path('create-subscription/', views.create_subscription_view, name='create_subscription'),
      path('company-subscriptions/', views.company_subscriptions_view, name='company_subscriptions'),
      path('jobseeker_sub/', views.jobseeker_sub_view, name='jobseeker_sub'),
      path('content-management/', views.content_management_page, name='content_management'),
    path('api/save-content/', views.save_content, name='save_content'),
     path('settings-customization/', views.settings_customization_page, name='settings_customization'),
    path('save-settings/', views.save_settings, name='save_settings'),
    path('report-analytics/', views.report_analytics_page, name='report_analytics'),
     path('create-job/', views.job_create, name='job_create'),
     path('applications/', views.applications_dashboard, name='applications'),
      path('list-companies/', views.list_companies, name='list_companies'),
      path('list_jobseekers/', views.list_jobseekers, name='list_jobseekers'),

]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
