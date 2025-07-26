from django.contrib import admin
from .models import (
    JobApplication, JobSeeker, Job, Company,
    FullJobApplication, SubscriptionPlan, Payment,
    Notification, Contact, Review, SavedJob,
    JobAlert, SiteAnalytics, Profile
)

def list_all_fields(model):
    return [field.name for field in model._meta.fields]

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = list_all_fields(JobApplication)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = list_all_fields(Job)

@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = list_all_fields(JobSeeker)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = list_all_fields(Company)

@admin.register(FullJobApplication)
class FullJobApplicationAdmin(admin.ModelAdmin):
    list_display = list_all_fields(FullJobApplication)

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = list_all_fields(SubscriptionPlan)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = list_all_fields(Payment)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = list_all_fields(Notification)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = list_all_fields(Contact)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = list_all_fields(Review)

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = list_all_fields(SavedJob)

@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = list_all_fields(JobAlert)

@admin.register(SiteAnalytics)
class SiteAnalyticsAdmin(admin.ModelAdmin):
    list_display = list_all_fields(SiteAnalytics)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = list_all_fields(Profile)
