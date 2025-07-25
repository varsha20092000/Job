from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from .views import registration_view,subscription_plans
from .views import job_list,apply_for_job


urlpatterns = [
    path('', views.loading_page, name='loading_page'),
    path('welcome', views.loading_page1, name='welcomepage'), 
    path('register/', registration_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('subscription-plans/',views. subscription_plans, name='subscription_plans'),
    path('payment-options/', views.payment_options, name='payment_options'),
    path('home/', views.home, name='home'),
    path('job/<int:job_id>/', views.job_detail_view, name='job_detail'),
    
    path('income/', views.income, name='income'),
    path('profile/', views.profile, name='profile'),
    path('jobs/', views.jobs_view, name='jobs'),
    path('certificate/',views.certificate,name='certificate'),
    path('notifications/', views.notifications, name='notifications'),
    path('api/jobs/', views.job_list, name='job_list'),
    path('companyreg/', views.companyreg, name='companyreg'),
    path("companyhome/",views.companyhome,name="companyhome"),
     path("company/job-details/", views.job_list_with_first_job, name="job_details_blank"),
    path("company/job-details/<int:job_id>/", views.compjob_details, name="job_details"),
   

    path("post-job/", views.post_job, name="post_job"),
    path("employee-details/", views.employee_details, name="employee_details"), 
    path("employee/<int:employee_id>/", views.employee_detail, name="employee_detail"), 
    path("employee-payment/", views.employee_payment, name="employee_payment"),
    path("employee-payment/<int:employee_id>/", views.employee_payment_detail, name="employee_payment_detail"),
    path('tax-payment/', views.TaxPaymentView.as_view(), name='tax_payment'),
    path('total-payment/', views.total_payment_view, name='total_payment'),
    path('employee-wise/', views.employee_wise_view, name='employee_wise'),
    path('certificates/', views.requested_certificates_view, name='requested_certificates'),
    path('certificate-detail/<int:employee_id>/', views.certificate_detail_view, name='certificate_detail'),
    path('certificate-of-achievement/<int:employee_id>/', views.certificate_of_achievement_view, name='certificate_of_achievement'),
    path('compnotifications/', views.notifications_view, name='compnotifications'),
    path('applicants/<str:job_code>/', views.applicants_view, name='applicants_list'),
    path('candidate/<int:candidate_id>/', views.candidate_detail_view, name='candidate_detail'),
    path('profile-form/', views.profile_form_view, name='profile_form'),
    path('companyprofile/', views.create_company, name='companyprofile'),
    path('subscription/', views.subscription_plans, name='subscription'),
    path('subscription/payment/', views.subscription_payment, name='subscription_payment'),
    path('subscription/success/', views.subscription_success, name='subscription_success'),
    path('job/<int:job_id>/apply/', views.apply_for_job, name='apply_for_job'),

]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
