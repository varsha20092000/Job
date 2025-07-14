from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from admin_panel.models import Job as AdminJob


# 1️⃣ Job Seeker Profile
class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    resume = models.FileField(upload_to='resumes/')
    skills = models.TextField()
    experience = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True) 
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    class Meta:
        app_label = 'App'

# 2️⃣ Company Profile
class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    website = models.URLField()
    description = models.TextField()
    location = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    is_complete = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)  


    def __str__(self):
        return self.company_name or f"Company ({self.user.username})"
    class Meta:
        app_label = 'App'

# 3️⃣ Job Posting
class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_time = models.CharField(max_length=50, choices=[('Full Time', 'Full Time'), ('Part Time', 'Part Time')], default='Full Time')  # ✅ NEW
    experience = models.CharField(max_length=50, choices=[('1-2 Year', '1-2 Year'), ('2-5 Year', '2-5 Year'), ('5+ Year', '5+ Year')], default='1-2 Year')  # ✅ NEW
    job_code = models.CharField(max_length=20, unique=True)  # ✅ NEW
    work_hour = models.PositiveIntegerField(default=2)  # ✅ NEW
    short_description = models.TextField(blank=True)  # ✅ NEW
    job_details = models.TextField()
    vacancies = models.IntegerField(default=1)
    duration = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, default='0000000000')
    email = models.EmailField(default='admin@example.com')
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')
    hourly_rates = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=8, decimal_places=2)
    posted_date = models.DateTimeField(auto_now_add=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    skills = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.job_name} at {self.company_name}"
    
    def total_payment(self):
        try:
            return float(self.hourly_rates) * self.work_hour
        except:
            return 0
    class Meta:
        app_label = 'App'


# 4️⃣ Full Job Application Form (details of candidate)
class FullJobApplication(models.Model):
    full_name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=20)
    dob = models.DateField()
    place = models.CharField(max_length=200)

    school1_name = models.CharField(max_length=200, blank=True)
    school1_place = models.CharField(max_length=200, blank=True)
    school1_marks = models.CharField(max_length=50, blank=True)
    school1_certificate = models.FileField(upload_to='certificates/', blank=True)

    school2_name = models.CharField(max_length=200, blank=True)
    school2_place = models.CharField(max_length=200, blank=True)
    school2_marks = models.CharField(max_length=50, blank=True)
    school2_certificate = models.FileField(upload_to='certificates/', blank=True)

    college_name = models.CharField(max_length=200, blank=True)
    college_place = models.CharField(max_length=200, blank=True)
    college_marks = models.CharField(max_length=50, blank=True)
    college_certificate = models.FileField(upload_to='certificates/', blank=True)

    skills = models.CharField(max_length=300)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')

    applied_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Application - {self.full_name}"
    class Meta:
        app_label = 'App'

# 5️⃣ Application Display for Admin (username, jobname, date only)
class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(AdminJob, on_delete=models.CASCADE)
    
    job_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    applied_date = models.DateTimeField(default=timezone.now)
    
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField(null=True, blank=True)

    gender = models.CharField(max_length=10, blank=True, null=True)  # Optional if not always available
    dob = models.DateField(null=True, blank=True)  # <-- FIX THIS

    place = models.CharField(max_length=100)
    education = models.CharField(max_length=255, blank=True, null=True)
    experience = models.CharField(max_length=100, blank=True, null=True)
    hourly_rate = models.CharField(max_length=50, blank=True, null=True)
    skills = models.TextField()
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    job_code = models.CharField(max_length=50, blank=True, null=True)
    
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.user.username} applied for {self.job_name}"

    class Meta:
        app_label = 'App'

# ➡️ Continue with your other models (SubscriptionPlan, Payment, Notification, Contact, Review, SavedJob, JobAlert, Interview, SiteAnalytics)
# (No problem there. You can keep them same.)

# 5️⃣ Subscription Plans
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_in_days = models.IntegerField()  # Duration for the plan
    features = models.TextField()  # Description of features

    def __str__(self):
        return self.name
    class Meta:
        app_label = 'App'

# 6️⃣ Payment Model
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')], default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} - {self.status}"
    class Meta:
        app_label = 'App'

# 7️⃣ Notifications
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"
    class Meta:
        app_label = 'App'

class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Query from {self.user.username} - {self.subject}"
    class Meta:
        app_label = 'App'

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.user.username} - {self.user.username} ({self.rating}⭐)"
    class Meta:
        app_label = 'App'

class SavedJob(models.Model):
    jobseeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.jobseeker.user.username} saved {self.job.title}"
    class Meta:
        app_label = 'App'

class JobAlert(models.Model):
    jobseeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    keywords = models.CharField(max_length=255)  # Example: "Python Developer"
    location = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=20, choices=[('Daily', 'Daily'), ('Weekly', 'Weekly')], default='Daily')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert for {self.jobseeker.user.username} - {self.keywords}"
    class Meta:
        app_label = 'App'



class SiteAnalytics(models.Model):
    date = models.DateField(auto_now_add=True)
    total_users = models.IntegerField()
    total_jobs_posted = models.IntegerField()
    total_applications = models.IntegerField()
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Analytics for {self.date}"
    class Meta:
        app_label = 'App'

from django.utils import timezone

class Profile(models.Model):
    ACCOUNT_CHOICES = (
        ('jobseeker', 'Job Seeker'),
        ('company', 'Company'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.account_type}"
    class Meta:
        app_label = 'App'
