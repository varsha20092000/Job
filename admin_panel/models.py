from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Job(models.Model):
    job_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    hourly_rates = models.CharField(max_length=100)
    job_details = models.TextField()
    vacancies = models.IntegerField(default=1)
    duration = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, default='0000000000')
    email = models.EmailField(default='admin@example.com')
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')
    created_at = models.DateTimeField(default=timezone.now)
    salary = models.DecimalField(max_digits=8, decimal_places=2)
    posted_date = models.DateTimeField(auto_now_add=True)
    skills = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.job_name

class AdminJobApplication(models.Model):
    full_name = models.CharField(max_length=100)
    age = models.IntegerField()
    place = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    applied_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.job.job_name}"



