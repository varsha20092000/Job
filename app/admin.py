from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import JobApplication

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_name', 'company_name', 'applied_date', 'email', 'phone_number', 'age', 'gender', 'place')
    search_fields = ('user__username', 'job_name', 'company_name', 'email', 'phone_number')
    list_filter = ('gender', 'applied_date', 'company_name')
