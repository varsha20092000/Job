from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.decorators import login_required

def loading_page(request):
    return render(request, 'job.html')

def loading_page1(request):
    return render(request, 'welcome.html')

# myapp/views.py
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib.auth.models import User
def login_view(request):
    show_otp_modal = request.session.pop('show_otp_modal', False)
    open_forgot_modal = request.session.pop('open_forgot_modal', False)

    if request.method == 'POST':
        identifier = request.POST.get('username')
        password = request.POST.get('password')
        account_type = request.POST.get('account_type')

        print("🔍 POST Data:", request.POST)

        # Try login by username first, then by email
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                messages.error(request, "❌ User not found.")
                return redirect('login')

        user = authenticate(request, username=user.username, password=password)
        if user is None:
            messages.error(request, "❌ Incorrect password.")
            return redirect('login')

        login(request, user)

        if account_type == 'company':
            try:
                company = Company.objects.get(user=user)
                print("🟩 Company is_complete:", company.is_complete)
                if company.is_complete:
                    return redirect('companyhome')
                else:
                    return redirect('companyreg')
            except Company.DoesNotExist:
                return redirect('companyreg')

        elif account_type == 'jobseeker':
            try:
                JobSeeker.objects.get(user=user)
                return redirect('home')
            except JobSeeker.DoesNotExist:
                messages.error(request, "❌ Jobseeker profile not found.")
                return redirect('register')

        messages.error(request, "❌ Invalid account type.")
        return redirect('login')

    return render(request, 'login.html', {
        'show_otp_modal': show_otp_modal,
        'open_forgot_modal': open_forgot_modal,
    })

from .forms import RegistrationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from .models import JobSeeker
from .models import JobSeeker, Profile 
def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        account_type = request.POST.get('account_type')
        print(f"📥 Account type received: {account_type}")

        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            email = form.cleaned_data['email_id']
            password = form.cleaned_data['password']

            print("📥 Username:", username)
            print("📥 Email:", email)

            # ✅ Duplicate username check
            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'register.html', {'form': form})

            # ✅ Duplicate email check
            if User.objects.filter(email__iexact=email).exists():
                messages.error(request, 'Email already exists.')
                return render(request, 'register.html', {'form': form})

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            print("✅ Registered username:", user.username)

            if account_type == 'jobseeker':
                JobSeeker.objects.create(
                    user=user,
                    phone=form.cleaned_data['mobile_number'],
                    date_of_birth=form.cleaned_data['date_of_birth'],
                    location=form.cleaned_data['city'],
                    resume='resumes/default.pdf',
                    skills='',
                    experience=0,
                    bio='',
                )
                messages.success(request, '✅ Registration successful. Please login.')
                return redirect('login')

            elif account_type == 'company':
                Company.objects.create(user=user, is_complete=False)
                messages.success(request, '✅ Account created. Please complete your company profile.')
                # Auto-login
                login(request, user)
                return redirect('companyreg') 
            else:
                messages.error(request, "❌ Please select a valid account type.")
        else:
            print("Form not valid ❌")
            print(form.errors)
            messages.error(request, 'Form submission failed. Please fix errors.')
    else:
        form = RegistrationForm()

    states_cities = {
        'Kerala': ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Malapuram', 'Idukki'],
        'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai'],
        'Karnataka': ['Bengaluru', 'Mysuru', 'Mangaluru'],
    }

    return render(request, 'register.html', {'form': form, 'states_cities': states_cities})

from .models import Company
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser


from django.contrib.auth import logout
@login_required
def companyreg(request):
    user = request.user

    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        registration_number = request.POST.get('registration_number')
        description = request.POST.get('description')
        account_number = request.POST.get('accountNumber')
        ifsc_code = request.POST.get('ifscCode')
        pancard_number = request.POST.get('pancardNumber')
        id_card = request.FILES.get('idCardUpload')
        pan_card = request.FILES.get('panCardUpload')

        # ✅ Don't check or set password here
        # Just save the company details
        Company.objects.update_or_create(
            user=user,
            defaults={
                'company_name': company_name,
                'registration_number': registration_number,
                'description': description,
                'account_number': account_number,
                'ifsc_code': ifsc_code,
                'pancard_number': pancard_number,
                'id_card': id_card,
                'pan_card': pan_card,
                'is_complete': True,
            }
        )

        print(f"✅ Company profile created for: {user.username}")
        return redirect('login')  # Or redirect to 'comphome' if needed

    return render(request, 'companyreg.html')


from django.http import HttpResponseForbidden
from django.db.models import Count
@login_required
def companyhome(request):
    current_user = request.user
    other_jobs = Job.objects.exclude(user=current_user).order_by('-posted_date')[:10]
    user = request.user
    user_jobs = Job.objects.filter(user=user)

    if not Company.objects.filter(user=request.user).exists():
        return HttpResponseForbidden("❌ Not authorized as Company.")

    jobs = Job.objects.filter(user=request.user).order_by('-posted_date')

    for job in jobs:
        job.applicant_count = JobApplication.objects.filter(job=job).values('user').distinct().count()

    paginator = Paginator(jobs, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'comphome.html', {
        'jobs': jobs,
        'page_obj': page_obj,
         'other_jobs': user_jobs
    })
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Job  # Ensure you import your Job model


@login_required
def jobseeker_home(request):
    # Initial queryset
    jobs = Job.objects.filter(status='Active').order_by('-created_at')

    # Pagination
    paginator = Paginator(jobs, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Context
    context = {
        'page_obj': page_obj,
        
        
    }

    return render(request, 'home.html', context)

def subscription_plans(request):
    return render(request, 'subscription.html')

def payment_options(request):
    return render(request, 'payment_options.html')
def home(request):
    job_list = Job.objects.filter(status='Active').order_by('-created_at')
    paginator = Paginator(job_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    date_labels = ["Today", "Less than 10 days", "More than 10 days"]
    job_types = ["Physical work", "Office work", "IT work", "Kitchen work", "Field work", "Health work", "Other"]
    locations = ["Kochi", "Idukki", "Kozhikode", "Bangalore", "Malappuram", "Thiruvanathapuram", "Pathnamthitta"]
    # Show ALL active jobs (including ones in page_obj)
    suggested_jobs = Job.objects.filter(status='Active').order_by('-created_at')

    return render(request, 'homepage.html', {
        'page_obj': page_obj,
        'all_jobs': suggested_jobs,
        'date_labels': date_labels,
        'job_types': job_types,
        'locations': locations,
        
    })

from django.shortcuts import get_object_or_404


def job_detail_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'job_detail.html', {'job': job})


def income(request):
    
    return render(request, 'income.html')
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileForm
from .models import Profile

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    skill_list = profile.skills.split(',') if profile.skills else []

    document_fields = {
        'upload_id_card': profile.upload_id_card.url if profile.upload_id_card else None,
        'upload_proof_detail': profile.upload_proof_detail.url if profile.upload_proof_detail else None,
        'upload_pan_card': profile.upload_pan_card.url if profile.upload_pan_card else None,
        'upload_passbook': profile.upload_passbook.url if profile.upload_passbook else None,
    }

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            profile = form.save(commit=False)  # Don’t save to DB yet
            profile.phone = request.POST.get('phone')
            profile.date_of_birth = request.POST.get('date_of_birth')
            profile.gender = request.POST.get('gender')
            profile.country = request.POST.get('country')
            profile.city = request.POST.get('city')
            profile.bio = request.POST.get('bio')

            # Check and save file fields individually
            if 'upload_id_card' in request.FILES:
                profile.upload_id_card = request.FILES['upload_id_card']
            if 'upload_proof_detail' in request.FILES:
                profile.upload_proof_detail = request.FILES['upload_proof_detail']
            if 'upload_pan_card' in request.FILES:
                profile.upload_pan_card = request.FILES['upload_pan_card']
            if 'upload_passbook' in request.FILES:
                profile.upload_passbook = request.FILES['upload_passbook']

            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "There was an error updating your profile.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {
        'form': form,
        'user': request.user,
        'profile': profile,
        'skill_list': skill_list,
        'document_fields': document_fields,
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Profile

@login_required
def update_profile(request):
    if request.method == 'POST':
        profile = request.user.profile

        profile.first_name = request.POST.get('first_name')
        profile.last_name = request.POST.get('last_name')
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.gender = request.POST.get('gender')
        profile.city = request.POST.get('city')
        profile.country = request.POST.get('country')
        profile.bio = request.POST.get('bio')
        profile.dob = request.POST.get('dob')

        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']

        profile.save()
        
        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
        else:
            form = ProfileForm(instance=profile)
    return redirect('profile')  # Fallback for GET

def certificate(request):
    return render(request, 'certificate.html')  
def notifications(request):
    return render(request, 'notification.html')
from django.core.paginator import Paginator
from .models import Job, JobApplication
from django.contrib.auth.decorators import login_required
from django.db.models import Subquery, OuterRef
@login_required
def jobs_view(request):
    page = request.GET.get('page', 1)

    # Ensure only one application per job (latest one)
    latest_app_ids = JobApplication.objects.filter(user=request.user)\
        .order_by('job', '-applied_date')\
        .distinct('job')\
        .values('id')  # PostgreSQL only

    # For other DBs (like MySQL/SQLite), use Subquery method:
    applications = JobApplication.objects.filter(
        id__in=Subquery(
            JobApplication.objects.filter(user=request.user)
            .order_by('job', '-applied_date')
            .values('job')
            .distinct()
            .values('id')
        )
    ).select_related('job')

    paginator = Paginator(applications, 6)
    applications_page = paginator.get_page(page)

    # Fetch saved jobs
    saved_jobs = []
    if hasattr(request.user, 'jobseeker'):
        saved_jobs = SavedJob.objects.filter(jobseeker=request.user.jobseeker).select_related('job')

    # AJAX request (pagination)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'job_cards.html', {'applied_jobs': applications_page})

    # Full page load
    return render(request, 'findjob.html', {
        'applied_jobs': applications_page,
        'saved_jobs': saved_jobs
    })
from django.http import JsonResponse
from admin_panel.models import Job

def job_list(request):
    jobs = Job.objects.all().order_by('-id')  # Ensuring consistent ordering
    paginator = Paginator(jobs, 6)  # 6 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Handle AJAX request for 'Show More' button
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'job_cards.html', {'jobs': page_obj})

    # Default full page load
    return render(request, 'homepage.html', {'jobs': page_obj})



def compjob_details(request, job_id):
    user = request.user
    jobs = Job.objects.filter(user=user) 
    selected_job = get_object_or_404(Job, id=job_id, user=user)
    return render(request, "job_detail.html", {
        "jobs": jobs,
        "selected_job": selected_job,
    })
    
    
def job_list_with_first_job(request):
    user = request.user
    jobs = Job.objects.filter(user=user)
    return render(request, "job_detail.html", {'jobs': jobs,'selected_job': None})
# views.py

from .models import JobApplication

def employee_details(request):
    applications = JobApplication.objects.select_related("user", "job").all()
    return render(request, "employee_details.html", {"employees": applications})

from django.shortcuts import get_object_or_404

def employee_detail(request, employee_id):
    application = get_object_or_404(JobApplication, id=employee_id)
    return render(request, "employee_detail.html", {"employee": application})


from django.shortcuts import render

def employee_payment(request):
    employees = [
        {
            "id": 1,
            "name": "Sravan",
            "title": "Junior Developer",
            "rate_per_hour": "200/hr",
            "work_hours": "7hr",
            "total_payment": "",
            "payment_date": "9 Aug 2024",
            "job_code": "1234",
        },
        {
            "id": 2,
            "name": "manoj",
            "title": "Junior Developer",
            "rate_per_hour": "200/hr",
            "work_hours": "7hr",
            "total_payment": "",
            "payment_date": "9 Aug 2024",
            "job_code": "1234",
        },
        {
            "id": 3,
            "name": "Kevin",
            "title": "Junior Developer",
            "rate_per_hour": "200/hr",
            "work_hours": "7hr",
            "total_payment": "",
            "payment_date": "9 Aug 2024",
            "job_code": "1234",
        },
        {
            "id": 4,
            "name": "Samuel",
            "title": "Junior Developer",
            "rate_per_hour": "200/hr",
            "work_hours": "7hr",
            "total_payment": "",
            "payment_date": "9 Aug 2024",
            "job_code": "1234",
        }
    ]
    return render(request, "employee_payment.html", {"employees": employees})
from django.shortcuts import render, get_object_or_404

# Unified Employee Payment Data
EMPLOYEES_PAYMENT = [
    {"id": 1, "name": "Sravan", "title": "Junior Developer", "rate_per_hour": "200/hr", 
     "work_hours": "7hr", "total_payment": "30K", "payment_date": "9 Aug 2024", "job_code": "1234","total_hours":"7hr"},
    
    {"id": 2, "name": "John", "title": "Senior Developer", "rate_per_hour": "250/hr", 
     "work_hours": "8hr", "total_payment": "45K", "payment_date": "9 Aug 2024", "job_code": "5678","total_hours":"8hr"},
    
    {"id": 3, "name": "Amit", "title": "UI/UX Designer", "rate_per_hour": "180/hr", 
     "work_hours": "6hr", "total_payment": "35K", "payment_date": "10 Aug 2024", "job_code": "9101","total_hours":"9hr"},
    
    {"id": 4, "name": "Rahul", "title": "Software Engineer", "rate_per_hour": "300/hr", 
     "work_hours": "9hr", "total_payment": "50K", "payment_date": "11 Aug 2024", "job_code": "1121","total_hours":"6hr"},
]

def employee_payment(request):
    """Render the Employee Payment List Page"""
    return render(request, "employee_payment.html", {"employees": EMPLOYEES_PAYMENT})

def employee_payment_detail(request, employee_id):
    """Render the Individual Employee Payment Detail Page"""
    employee_id = int(employee_id)  # Convert to integer to match list IDs
    employee = next((emp for emp in EMPLOYEES_PAYMENT if emp["id"] == employee_id), None)

    if employee is None:
        return render(request, "404.html", status=404)  # Redirect to 404 page if employee not found

    return render(request, "employee_payment_detail.html", {"employee": employee})
# views.py
from django.views.generic import TemplateView

class TaxPaymentView(TemplateView):
    template_name = 'tax_payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Example static data to display on the right side
        # In a real app, replace this with a database query.
        context['tax_details'] = [
            {
                'job_title': 'Jr Software Engineer',
                 'location': 'Kochi,Kerala',
                'company': 'Tech Wave',
                'total_paid': '50 lakh',
                'tax_percentage': '30%',
            },
            {
                'job_title': 'Sr Software Engineer',
                 'location': 'Kochi,Kerala',
                'company': 'Tech Wave',
                'total_paid': '70 lakh',
                'tax_percentage': '35%',
            },
            {
                'job_title': 'Jr Software Engineer',
                 'location': 'Kochi,Kerala',
                'company': 'Tech World',
                'total_paid': '45 lakh',
                'tax_percentage': '28%',
            },
             {
                'job_title': 'Jr Software Engineer',
                'location': 'Kochi,Kerala',
                'company': 'Tech World',
                'total_paid': '45 lakh',
                'tax_percentage': '28%',
            },
        ]
        return context

from django.shortcuts import render

def total_payment_view(request):
    # Sample data for demonstration. Replace with your actual database query or logic.
    total_payments = [
        {
            "job_title": "Carpenter",
            "location": "Calicut, Kerala",
            "job_code": "1234",
            "total_employees": 200,
            "total_payment": "50lakhs"
        },
        {
            "job_title": "Plumber",
            "location": "Kochi, Kerala",
            "job_code": "5678",
            "total_employees": 150,
            "total_payment": "30lakhs"
        },
        {
            "job_title": "Electrician",
            "location": "Bangalore, Karnataka",
            "job_code": "9101",
            "total_employees": 250,
            "total_payment": "75lakhs"
        },
        {
            "job_title": "Welder",
            "location": "Chennai, Tamil Nadu",
            "job_code": "1121",
            "total_employees": 180,
            "total_payment": "60lakhs"
        },
        {
            "job_title": "Cleaner",
            "location": "Kochi, Kerala",
            "job_code": "5678",
            "total_employees": 150,
            "total_payment": "10lakhs"
        },
        {
            "job_title": "Electrician",
            "location": "Bangalore, Karnataka",
            "job_code": "9101",
            "total_employees": 250,
            "total_payment": "75lakhs"
        },
        {
            "job_title": "House Keeping",
            "location": "Chennai, Tamil Nadu",
            "job_code": "1121",
            "total_employees": 180,
            "total_payment": "60lakhs"
        },
        {
            "job_title": "Cleaner",
            "location": "Chennai, Tamil Nadu",
            "job_code": "1121",
            "total_employees": 180,
            "total_payment": "60lakhs"
        },
    ]

    # Render the template, passing in the data
    return render(request, "total_payment.html", {"total_payments": total_payments})

def employee_wise_view(request):
    employees_wise = [
        {
            "id": 1,
            "name": "Sravan",
            "job_code": "1234",
            "job_title": "Junior developer",
            "total_payment": "30K",
            "hours": "168hr",
        },
        {
            "id": 2,
            "name": "MANI",
            "job_code": "1234",
            "job_title": "Junior developer",
            "total_payment": "30K",
            "hours": "168hr",
        },
        {
            "id": 3,
            "name": "POOJA",
            "job_code": "1234",
            "job_title": "Junior developer",
            "total_payment": "30K",
            "hours": "168hr",
        },
        {
            "id": 4,
            "name": "MANU",
            "job_code": "1234",
            "job_title": "Junior developer",
            "total_payment": "30K",
            "hours": "168hr",
        },
         {
            "id": 4,
            "name": "MAHESH",
            "job_code": "1234",
            "job_title": "Junior developer",
            "total_payment": "30K",
            "hours": "168hr",
        },
        {
            "id": 5,
            "name": "GOKUL",
            "job_code": "1234",
            "job_title": "Junior developer",
            "total_payment": "30K",
            "hours": "168hr",
        },
    ]
    return render(request, "employee_wise.html", {"employees": employees_wise})

# views.py
from django.shortcuts import render
global EMPLOYEES  # Defined globally in this module

# views.py

# Global employee data for certificate details
EMPLOYEES = [
    {
        "id": 1,
        "name": "SAMUEL GEO",
        "title": "Junior Designer",
        "hourly_rate": "500/hr",
        "employee_code": "1234",
        "location": "Kochi, Kerala"
    },
    {
        "id": 2,
        "name": "MATHEW",
        "title": "Junior Designer",
        "hourly_rate": "500/hr",
        "employee_code": "1234",
        "location": "Kochi, Kerala"
    },
    {
        "id": 3,
        "name": "VISHNAVI",
        "title": "Junior Designer",
        "hourly_rate": "500/hr",
        "employee_code": "1234",
        "location": "Kochi, Kerala"
    },
    {
        "id": 4,
        "name": "Sravan.P",
        "title": "Junior Designer",
        "hourly_rate": "500/hr",
        "employee_code": "1234",
        "location": "Kochi, Kerala"
    },
    {
        "id": 5,
        "name": "AVANI",
        "title": "Junior Designer",
        "hourly_rate": "500/hr",
        "employee_code": "1234",
        "location": "Kochi, Kerala"
    },
    {
        "id": 6,
        "name": "MANI",
        "title": "Junior Designer",
        "hourly_rate": "500/hr",
        "employee_code": "1234",
        "location": "Kochi, Kerala"
    },
]
def requested_certificates_view(request):
    profile = {
        "name": "Priya Suresh",
        "avatar_url": "https://www.w3schools.com/howto/img_avatar2.png",
        "location": "Kochi, Kerala"
    }
    return render(request, "requested_certificates.html", {
        "employees": EMPLOYEES,  # Using the global EMPLOYEES variable
        "profile": profile
    })

def certificate_detail_view(request, employee_id):
    employee = next((emp for emp in EMPLOYEES if emp["id"] == int(employee_id)), None)
    if employee is None:
        return render(request, "404.html", status=404)
    
    profile = {
        "name": "Soorya Gokul",
        "avatar_url": "https://www.w3schools.com/howto/img_avatar2.png",
        "location": "Calicut, Kerala"
    }
    return render(request, "certificate_detail.html", {
        "employee": employee,
        "profile": profile
    })
def certificate_of_achievement_view(request, employee_id):
    # Find the employee in EMPLOYEES list (or query your DB in a real app)
    employee = next((emp for emp in EMPLOYEES if emp["id"] == employee_id), None)
    if employee is None:
        return render(request, "404.html", status=404)

    return render(request, "certificate_of_achievement.html", {
        "employee": employee
    })

# views.py
from django.shortcuts import render

def notifications_view(request):
    profile = {
        "name": "Priya Suresh",
        "avatar_url": "https://www.w3schools.com/howto/img_avatar2.png",
        "location": "Kochi, Kerala",
    }

    # Example data for 6 notifications (customize as you like)
    notifications = [
        {
            "title": "Job application received",
            "company": "Abcd Technologies Pvt Ltd.",
            "location": "Calicut, Kerala",
            "job_code": "1234",
            "applied_count": "9 Applied",
            "time": "Today"
        },
        {
            "title": "Interview scheduled",
            "company": "Mck Technologies Pvt ltd.",
            "location": "Calicut, Kerala",
            "job_code": "0002",
            "applied_count": "8 Applied",
            "time": "Today"
        },
        {
            "title": "Junior Developer",
            "company": "Mck Technologies Pvt ltd.",
            "location": "Calicut, Kerala",
            "job_code": "0002",
            "applied_count": "8 Applied",
            "time": "Yesterday"
        },
        {
            "title": "Job Applied",
            "company": "Abcd Technologies Pvt Ltd.",
            "location": "Kochi, Kerala",
            "job_code": "4567",
            "applied_count": "3 Applied",
            "time": "2 Days Ago"
        },
        {
            "title": " Payment completed",
            "company": "Mck Technologies Pvt ltd.",
            "location": "Calicut, Kerala",
            "job_code": "9876",
            "applied_count": "10 Applied",
            "time": "Last Week"
        },
        {
            "title": " New applicant",
            "company": "Abcd Technologies Pvt Ltd.",
            "location": "Calicut, Kerala",
            "job_code": "1122",
            "applied_count": "5 Applied",
            "time": "Last Month"
        },
    ]

    return render(request, "notifications.html", {
        "profile": profile,
        "notifications": notifications
    })

def applicants_view(request, job_code):
    # Example data: map each job_code to a list of applicant dicts
    APPLICANTS_DATA = {
        "1234": [
            {
                "id":1,
                "avatar": "https://www.w3schools.com/howto/img_avatar.png",
                "name": "John Doe",
                "age": 25,
                "place": "Calicut, Kerala",
                "phone": "+91 9876543210"
            },
            {
                "id":2,
                "avatar": "https://cdn3.vectorstock.com/i/1000x1000/71/77/male-avatar-profile-icon-round-man-face-vector-18307177.jpg",
                "name": "Naseem shah",
                "age": 22,
                "place": "Munnar, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":3,
                "avatar": "https://th.bing.com/th/id/OIP.DatwtMCvyCOUKt9XGBdZ2gHaHa?pid=ImgDet&w=206&h=206&c=7&dpr=1.6",
                "name": "Kokila sharan",
                "age": 21,
                "place": "Pallakad, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":4,
                "avatar": "https://th.bing.com/th/id/OIP.3hilmZOt3Xgq-u1BgG9OqAHaHa?pid=ImgDet&w=206&h=206&c=7&dpr=1.6",
                "name": "Manasa Kumar",
                "age": 30,
                "place": "Kochi, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":5,
                "avatar": "https://th.bing.com/th/id/OIP.kmJ9RGeNl8ajqAwyGE41yAHaHa?pid=ImgDet&w=206&h=206&c=7&dpr=1.6",
                "name": "Lal Sathyan",
                "age": 28,
                "place": "Kollam, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":6,
                "avatar": "https://th.bing.com/th/id/OIP.OnjWcII4wBSpBva2CvsRaAHaHa?pid=ImgDet&w=206&h=206&c=7&dpr=1.6",
                "name": "Ashwin K.U",
                "age": 29,
                "place": "Idukki, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":7,
                "avatar": "https://th.bing.com/th/id/OIP.A-leBRuq4MikHNAmXB6hVwHaH_?pid=ImgDet&w=206&h=222&c=7&dpr=1.6",
                "name": "Sanju T.M",
                "age": 27,
                "place": "Malapuram, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":8,
                "avatar": "https://th.bing.com/th/id/OIP.-iknRGbI1QBfVr7dJo-TUQHaH_?pid=ImgDet&w=206&h=222&c=7&dpr=1.6",
                "name": "Sathyan",
                "age": 23,
                "place": "Kochi, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":9,
                "avatar": "https://www.w3schools.com/howto/img_avatar2.png",
                "name": "Sharanya Sam",
                "age": 24,
                "place": "Kozikode, Kerala",
                "phone": "+91 9876543211"
            },
        ],
        "0002": [
            {
                "id":10,
                "avatar": "https://www.w3schools.com/howto/img_avatar2.png",
                "name": "Rahul K",
                "age": 30,
                "place": "Kochi, Kerala",
                "phone": "+91 9876543212"
            },
            {
                "id":11,
                "avatar": "https://cdn3.vectorstock.com/i/1000x1000/71/77/male-avatar-profile-icon-round-man-face-vector-18307177.jpg",
                "name": "Naseem shah",
                "age": 22,
                "place": "Munnar, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":12,
                "avatar": "https://th.bing.com/th/id/OIP.DatwtMCvyCOUKt9XGBdZ2gHaHa?pid=ImgDet&w=206&h=206&c=7&dpr=1.6",
                "name": "Kokila sharan",
                "age": 21,
                "place": "Pallakad, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":13,
                "avatar": "https://th.bing.com/th/id/OIP.3hilmZOt3Xgq-u1BgG9OqAHaHa?pid=ImgDet&w=206&h=206&c=7&dpr=1.6",
                "name": "Manasa Kumar",
                "age": 30,
                "place": "Kochi, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":14,
                "avatar": "https://th.bing.com/th/id/OIP.kmJ9RGeNl8ajqAwyGE41yAHaHa?pid=ImgDet&w=206&h=206&c=7&dpr=1.6",
                "name": "Lal Sathyan",
                "age": 28,
                "place": "Kollam, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":15,
                "avatar": "https://th.bing.com/th/id/OIP.OnjWcII4wBSpBva2CvsRaAHaHa?pid=ImgDet&w=206&h=206&c=7&dpr=1.6",
                "name": "Ashwin K.U",
                "age": 29,
                "place": "Idukki, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":16,
                "avatar": "https://th.bing.com/th/id/OIP.A-leBRuq4MikHNAmXB6hVwHaH_?pid=ImgDet&w=206&h=222&c=7&dpr=1.6",
                "name": "Sanju T.M",
                "age": 27,
                "place": "Malapuram, Kerala",
                "phone": "+91 9876543211"
            },
            {
                "id":17,
                "avatar": "https://th.bing.com/th/id/OIP.-iknRGbI1QBfVr7dJo-TUQHaH_?pid=ImgDet&w=206&h=222&c=7&dpr=1.6",
                "name": "Sathyan",
                "age": 23,
                "place": "Kochi, Kerala",
                "phone": "+91 9876543211"
            },
        ],
        
        "4567": [
            {
                "id":18,
                "avatar": "https://www.w3schools.com/howto/img_avatar2.png",
                "name": "Rani K",
                "age": 30,
                "place": "Kochi, Kerala",
                "phone": "+91 9876543212"
            },
            {
                "id":19,
                "avatar": "https://th.bing.com/th/id/OIP.3hilmZOt3Xgq-u1BgG9OqAHaHa?pid=ImgDet&w=206&h=206&c=7&dpr=1.6",
                "name": "Soumya A.K",
                "age": 20,
                "place": "Kochi, Kerala",
                "phone": "+91 9876543212"
            },
            {
                "id":20,
                "avatar": "https://cdn4.iconfinder.com/data/icons/avatars-21/512/avatar-circle-human-female-5-512.png",
                "name": "Maya S",
                "age": 26,
                "place": "Kochi, Kerala",
                "phone": "+91 9876543212"
            }
        ],
       
        "1122": [
            {
                "id":21,
                "avatar": "https://www.w3schools.com/howto/img_avatar2.png",
                "name": "Rahul K",
                "age": 30,
                "place": "Kochi, Kerala",
                "phone": "+91 9876543212"
            }
        ],
        "9876": [
            {
                "id":22,
                "avatar": "https://www.w3schools.com/howto/img_avatar2.png",
                "name": "Rahul K",
                "age": 30,
                "place": "Kochi, Kerala",
                "phone": "+91 9876543212"
            }
        ],
        "1122": [
            {
                "id":23,
                "avatar": "https://www.w3schools.com/howto/img_avatar2.png",
                "name": "Rahul K",
                "age": 30,
                "place": "Kochi, Kerala",
                "phone": "+91 9876543212"
            }
        ],
    }

    # Get the list of applicants for this job_code, or an empty list if not found
    applicants_list = APPLICANTS_DATA.get(job_code, [])

    return render(request, "applicants.html", {
        "job_code": job_code,
        "applicants": applicants_list
    })

# views.py
from django.shortcuts import render

# Example data with multiple candidates
CANDIDATES = {
    1: {
        "id": 1,
        "name": "John Doe",
        "phone": "+91 9876543210",
        "email": "candidate1@example.com",
        "education": "B.Tech, Electronics",
        "location": "Calicut, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    2: {
        "id": 2,
        "name": "Naseem shah",
        "phone": "+91 9876543211",
        "email": "candidate2@example.com",
        "education": "B.Tech, Electronics",
        "location": "Munnar, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    3: {
        "id": 3,
        "name": "Kokila sharan",
        "phone": "+91 9876543211",
        "email": "candidate3@example.com",
        "education": "B.Tech, Electronics",
        "location": "Pallakad, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    4: {
        "id": 4,
        "name": "Manasa Kumar",
        "phone": "+91 9876543211",
        "email": "candidate4@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kochi, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    5: {
        "id": 5,
        "name": "Lal Sathyan",
        "phone": "+91 9876543211",
        "email": "candidate5@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kollam, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    6: {
        "id": 6,
        "name": "Ashwin K.U",
        "phone": "+91 9876543211",
        "email": "candidate6@example.com",
        "education": "B.Tech, Electronics",
        "location": "Idukki, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    7: {
        "id": 7,
        "name": "Sanju T.M",
        "phone": "+91 9876543211",
        "email": "candidate7@example.com",
        "education": "B.Tech, Electronics",
        "location": "Malapuram, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    8: {
        "id": 8,
        "name": "Sathyan",
        "phone": "+91 9876543211",
        "email": "candidate8@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kochi, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    9: {
        "id": 9,
        "name": "Sharanya Sam",
        "phone": "+91 9876543211",
        "email": "candidate9@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kozikode, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },

    10: {
        "id": 10,
        "name": "Rahul K",
        "phone": "+91 9876543212",
        "email": "candidate10@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kochi, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    11: {
        "id": 11,
        "name": "Naseem shah",
        "phone": "+91 9876543211",
        "email": "candidate11@example.com",
        "education": "B.Tech, Electronics",
        "location": "Munnar, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    12: {
        "id": 12,
        "name": "Kokila sharan",
        "phone": "+91 9876543211",
        "email": "candidate12@example.com",
        "education": "B.Tech, Electronics",
        "location": "Pallakad, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    13: {
        "id": 13,
        "name": "Manasa Kumar",
        "phone": "+91 9876543211",
        "email": "candidate13@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kochi, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    14: {
        "id": 14,
        "name": "Lal Sathyan",
        "phone": "+91 9876543211",
        "email": "candidate14@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kollam, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    15: {
        "id": 15,
        "name": "Ashwin K.U",
        "phone": "+91 9876543211",
        "email": "candidate15@example.com",
        "education": "B.Tech, Electronics",
        "location": "Idukki, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    16: {
        "id": 16,
        "name": "Sanju T.M",
        "phone": "+91 9876543211",
        "email": "candidate16@example.com",
        "education": "B.Tech, Electronics",
        "location": "Malapuram, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    17: {
        "id": 17,
        "name": "Sathyan",
        "phone": "+91 9876543211",
        "email": "candidate17@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kochi, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },

    18: {
        "id": 18,
        "name": "Rani K",
        "phone": "+91 9876543212",
        "email": "candidate18@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kochi, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    19: {
        "id": 19,
        "name": "Soumya A.K",
        "phone": "+91 9876543212",
        "email": "candidate19@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kochi, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    20: {
        "id": 20,
        "name": "Maya S",
        "phone": "+91 9876543212",
        "email": "candidate20@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kochi, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },

    21: {
        "id": 21,
        "name": "Rahul K",
        "phone": "+91 9876543212",
        "email": "candidate21@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kochi, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    22: {
        "id": 22,
        "name": "Rahul K",
        "phone": "+91 9876543212",
        "email": "candidate22@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kochi, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
    23: {
        "id": 23,
        "name": "Rahul K",
        "phone": "+91 9876543212",
        "email": "candidate23@example.com",
        "education": "B.Tech, Electronics",
        "location": "Kochi, Kerala",
        "cover_letter": "Lorem ipsum is simply dummy text of the printing and typesetting industry..."
    },
}

def candidate_detail_view(request, candidate_id):
    candidate = CANDIDATES.get(candidate_id)
    if not candidate:
        return render(request, "404.html", status=404)  # Or a custom error page
    
    return render(request, "candidate_detail.html", {"candidate": candidate})
@login_required
def profile_form_view(request): 
    user = request.user

    # Get or create related models
    company, _ = Company.objects.get_or_create(user=user)
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)

        if form.is_valid():
            company = form.save(commit=False)
            company.user = user

            # Keep previous image if new one is not uploaded
            if 'profile_image' in request.FILES:
                company.profile_image = request.FILES['profile_image']

            company.save()
            return redirect('profile_form')  # Refresh and show saved state

    else:
        # Pre-fill only missing values (others come from form.instance)
        initial_data = {
            'name': user.first_name,
            'phone': company.phone or profile.phone or '',
            'email': user.email,
        }
        form = CompanyForm(instance=company, initial=initial_data)

    context = {
        'form': form,
        'company': company,
        'user': user,
        'profile': profile,
    }

    return render(request, 'profile_form.html', context)
from .forms import CompanyForm
from .models import Company

def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            # Set the user field automatically (assuming user is logged in)
            company.user = request.user
            company.save()
            return redirect('some_success_page')  # or wherever you want
    else:
        form = CompanyForm()

    return render(request, 'companyprofile.html', {'form': form})


def edit_company(request, company_id):
    company = Company.objects.get(id=company_id, user=request.user)
    # Only let the owner edit, or handle permissions as needed
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect('comphome')
    else:
        form = CompanyForm(instance=company)

    return render(request, 'companyprofile.html', {'form': form})

from django.contrib import messages

def subscription_plans(request):
    # Simply render the subscription plans page.
    return render(request, 'subscription.html')

def subscription_payment(request):
    # Retrieve selected plan details from GET parameters.
    plan_title = request.GET.get('plan_title', '')
    plan_price = request.GET.get('plan_price', '')

    if request.method == 'POST':
        # Process the payment form data here.
        # For example, extract form fields:
        name = request.POST.get('name')
        email = request.POST.get('email')
        card_number = request.POST.get('card_number')
        # ... plus Aadhaar, PAN, bank details, etc.

        # Implement payment processing and subscription activation logic.
        messages.success(request, "Subscription successful! Your 7-day free trial has started.")
        return redirect('subscription_success')
    
    context = {
        'plan_title': plan_title,
        'plan_price': plan_price,
    }
    return render(request, 'subscription_payment.html', context)

def subscription_success(request):
    return render(request, 'subscription_success.html')
import traceback
from django.shortcuts import render, redirect, get_object_or_404
from .forms import JobApplicationForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from admin_panel.models import AdminJobApplication
import traceback

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, JobApplication, Profile, Education
from .forms import JobApplicationForm
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Job, JobApplication, Profile, Education, SavedJob
from .forms import JobApplicationForm
@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    all_jobs = Job.objects.exclude(id=job_id)

    saved_job_ids = []
    if hasattr(request.user, 'jobseeker'):
        saved_job_ids = SavedJob.objects.filter(jobseeker=request.user.jobseeker)\
                                        .values_list('job__id', flat=True)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.job = job
            application.job_name = job.job_name
            application.company_name = job.company_name
            application.status = 'Applied'
            application.save()

            # update profile
            profile = Profile.objects.get(user=request.user)
            profile.phone = request.POST.get('phone')
            profile.gender = request.POST.get('gender')
            profile.dob = request.POST.get('dob')
            profile.address = request.POST.get('place')
            profile.age = request.POST.get('age')
            profile.profile_picture = request.FILES.get('avatar')

            if request.FILES.get('resume'):
                profile.resume = request.FILES.get('resume')
            profile.save()

            # education
            school = request.POST.get('education[0][school]')
            place = request.POST.get('education[0][place]')
            marks = request.POST.get('education[0][marks]')
            certificate = request.FILES.get('education[0][certificate]')
            if school and place and marks:
                Education.objects.create(
                    user=request.user,
                    school=school,
                    place=place,
                    marks=marks,
                    certificate=certificate
                )

            return render(request, 'jobseeker_job_detail.html', {
                'form': JobApplicationForm(),
                'job': job,
                'applied_successfully': True,
                'saved_job_ids': saved_job_ids,
                'all_jobs': all_jobs,  # ✅ must be here too
            })

    else:
        form = JobApplicationForm()

    return render(request, 'jobseeker_job_detail.html', {
        'form': form,
        'job': job,
        'form_errors': form.errors,
        'saved_job_ids': saved_job_ids,
        'all_jobs': all_jobs,  # ✅ key context
    })

import uuid

def save(self, *args, **kwargs):
    if not self.job_code:
        self.job_code = str(uuid.uuid4())[:8].upper()
    super().save(*args, **kwargs)
from .models import JobApplication

@login_required
def applied_jobs_with_recruiter_action(request, job_id):
    application = JobApplication.objects.filter(user=request.user, job_id=job_id).first()
    
    job = get_object_or_404(Job, id=job_id)

    return render(request, 'recruiter_action_detail.html', {
        'job': job,
        'application': application
    })

from .models import SavedJob
from django.contrib import messages
from django.shortcuts import redirect
@login_required
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    try:
        jobseeker = JobSeeker.objects.get(user=request.user)
        saved, created = SavedJob.objects.get_or_create(jobseeker=jobseeker, job=job)

        # Redirect to jobseeker job detail page using the job_id
        return redirect('jobseeker_job_detail', job_id=job.id)

    except JobSeeker.DoesNotExist:
        return redirect('jobseeker_job_detail', job_id=job.id)
from .models import Job
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.shortcuts import render, redirect
from .models import Job

def post_job(request):
    if request.method == 'POST':
        job_code = get_random_string(8).upper()

        # Get multiple skills from form and join as comma-separated string
        skills_list = request.POST.getlist('skills')  # from checkboxes or multiple input
        skills = ", ".join(skill.strip() for skill in skills_list)

        job = Job.objects.create(
            user=request.user,
            job_name=request.POST['job_name'],
            company_name=request.POST['company_name'],
            location=request.POST['posted_location'],
            job_time=request.POST['job_time'],
            experience=request.POST['experience'],
            job_code=job_code,
            work_hour=request.POST['work_hour'],
            short_description=request.POST['short_description'],
            job_details=request.POST['short_description'],  # Or use 'job_details' if separate field
            vacancies=request.POST['vacancy'],
            duration=request.POST['duration'],
            contact_number=request.POST['contact'],
            email=request.POST['email'],
            hourly_rates=request.POST['wage'],
            salary=request.POST.get('salary'),
            skills=skills,
            end_date=request.POST.get("end_date"),   # ✅ Save skills here
        )

        messages.success(request, "Job successfully posted. We will contact you soon.")
        return redirect('post_job')  # redirect to clear form and show message

    generated_code = get_random_string(8).upper()
    return render(request, 'post_job.html', {'generated_code': generated_code})

from .models import JobApplication, Profile

def jobseeker_job_detail_view(request, job_id, application_id):
    job = get_object_or_404(Job, id=job_id)
    application_exists = JobApplication.objects.filter(job=job, user=request.user).exists()
    saved_jobs = SavedJob.objects.filter(jobseeker__user=request.user).values_list('job_id', flat=True)
    user_applications = JobApplication.objects.filter(user=request.user).select_related('job')

    application = get_object_or_404(JobApplication, id=application_id)
    user = application.user
    profile = Profile.objects.filter(user=user).first()
    unique_jobs = {}
    for app in user_applications:
        unique_jobs[app.job.id] = app  # Keeps only the latest application per job

    is_saved = False
    if request.user.is_authenticated and hasattr(request.user, 'jobseeker'):
        is_saved = SavedJob.objects.filter(job=job, jobseeker=request.user.jobseeker).exists()

    context = {
        'job': job,
        'application': application,  # 🔴 ADD THIS LINE
        'applied_successfully': application_exists,
        'saved_job_ids': saved_jobs,
        'is_saved': is_saved,
        'profile': profile,
        'applications': unique_jobs.values(), 
    }
    return render(request, 'findjob.html', context)


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Job, SavedJob, JobSeeker
from django.contrib.auth.decorators import login_required

@login_required
def toggle_save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Get or create the jobseeker profile
    if not hasattr(request.user, 'jobseeker'):
        return redirect('home')  # Or show an error

    jobseeker = request.user.jobseeker

    saved, created = SavedJob.objects.get_or_create(jobseeker=jobseeker, job=job)

    if not created:
        saved.delete()  # Already saved, so remove (unsave)

    return redirect(request.META.get('HTTP_REFERER', 'findjob'))  # Redirect back
@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if job.user != request.user:
        return HttpResponseForbidden("❌ You are not allowed to view these applicants.")

    
    applicants = JobApplication.objects.filter(job=job).select_related('user', 'user__profile')


    return render(request, 'applicant_list.html', {
        'job': job,
        'applicants': applicants,
    })
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from .models import Job, JobApplication, Profile, Education

@login_required
def view_applicant_detail(request, job_id, user_id):
    job = get_object_or_404(Job, id=job_id)
    applicant = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=applicant)
    education = Education.objects.filter(user=applicant)

    # ✅ Safely get the latest application (if multiple exist)
    application = JobApplication.objects.filter(job=job, user=applicant).order_by('-applied_date').first()

    context = {
        'job': job,
        'application': application,
        'applicant': applicant,
        'profile': profile,
        'education': education,
    }
    return render(request, 'applicant_detail.html', context)

from django.shortcuts import render, redirect
from .forms import ResumeUploadForm, CertificateUploadForm
from .models import Profile, Education

def upload_documents(request):
    if request.method == 'POST':
        resume_form = ResumeUploadForm(request.POST, request.FILES, instance=request.user.profile)
        certificate_form = CertificateUploadForm(request.POST, request.FILES)
        if resume_form.is_valid() and certificate_form.is_valid():
            resume_form.save()
            certificate = certificate_form.save(commit=False)
            certificate.user = request.user
            certificate.save()
            return redirect('profile')  # or any other success page
    else:
        resume_form = ResumeUploadForm(instance=request.user.profile)
        certificate_form = CertificateUploadForm()

    return render(request, 'upload_documents.html', {
        'resume_form': resume_form,
        'certificate_form': certificate_form,
    })


@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        job.job_name = request.POST.get('job_name')
        job.company_name = request.POST.get('company_name')
        job.location = request.POST.get('location')
        job.short_description = request.POST.get('short_description')
        job.job_time = request.POST.get('job_time')
        job.experience = request.POST.get('experience')
        job.posted_location = request.POST.get('posted_location')
        job.posted_date = request.POST.get('posted_date')
        job.vacancy = request.POST.get('vacancy')
        job.job_code = request.POST.get('job_code')
        job.contact_number = request.POST.get('contact')
        job.duration = request.POST.get('duration')
        job.work_hour = request.POST.get('work_hour')
        job.email = request.POST.get('email')
        job.hourly_rates = request.POST.get('wage')
        job.salary = request.POST.get('salary')
        job.save()
        return redirect('companyhome')

    return render(request, 'edit_job.html', {'job': job})
@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST' and job.user == request.user:
        job.delete()
    return redirect('companyhome')  # or wherever you list jobs


from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import EmailMessage
def email_support(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        user_email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"From: {name}\nEmail: {user_email}\n\n{message}"

        try:
            email = EmailMessage(
                subject,
                full_message,
                'your_verified_email@gmail.com',  # fixed sender
                ['support@example.com'],          # receiver
                reply_to=[user_email],            # for replies
            )
            email.send()
            return render(request, 'email_success.html')
        except Exception as e:
            return HttpResponse(f"Email sending failed: {e}", status=500)

    return render(request, 'email_support_form.html')
def call_support(request):
    return render(request, 'call_support.html')

from .models import Job
from datetime import date, timedelta

def filtered_jobs(request):
    jobs = Job.objects.all()

    job_date = request.GET.get('job_date')
    job_type = request.GET.get('job_type')
    location = request.GET.get('location')
    work_days = request.GET.get('work_days')
    work_hours = request.GET.get('work_hours')
    sort_option = request.GET.get('sort')  # <-- New

    if job_date == 'today':
        jobs = jobs.filter(posted_date=date.today())
    elif job_date == 'less10':
        jobs = jobs.filter(posted_date__gte=date.today()-timedelta(days=10))
    elif job_date == 'more10':
        jobs = jobs.filter(posted_date__lte=date.today()-timedelta(days=10))

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    if location:
        jobs = jobs.filter(location__iexact=location)

    if work_days:
        jobs = jobs.filter(work_days__iexact=work_days)

    if work_hours:
        jobs = jobs.filter(work_hour=work_hours)

    if sort_option == 'newest':
        jobs = jobs.order_by('-posted_date')
    elif sort_option == 'oldest':
        jobs = jobs.order_by('posted_date')

    return render(request, 'filtered_jobs.html', {'jobs': jobs})

from datetime import date, timedelta
from django.shortcuts import render
from .models import Job
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Job  # make sure this is your Job model
@login_required
def filtered_jobs(request):
    user = request.user
    jobs = Job.objects.filter(user=user)  # ✅ only jobs posted by current user

    search_query = request.GET.get('search')
    sort_by = request.GET.get('sort')

    if search_query:
        jobs = jobs.filter(job_name__icontains=search_query)

    if sort_by == 'newest':
        jobs = jobs.order_by('-posted_date')
    elif sort_by == 'oldest':
        jobs = jobs.order_by('posted_date')

    return render(request, 'filtered_jobs.html', {'jobs': jobs})

def jobcall_support_view(request):
    return render(request, 'jobseekercall_support.html')


from django.core.mail import send_mail
from django.contrib import messages

def jobemail_support(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Construct full message
        full_message = f"From: {name} <{email}>\n\n{message}"

        try:
            send_mail(
                subject=subject,
                message=full_message,
                from_email=email,  # or set a default in settings
                recipient_list=['varshakvinod680@gmail.com'],  # replace with your support email
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully.')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
        
        return redirect('jobemail_support')

    return render(request, 'jobemail_support.html')
import random
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.conf import settings

User = get_user_model()


# -------------------- Step 1: Forgot Password --------------------
def forgot_password(request):
    if request.method == "POST":
        identifier = (request.POST.get("email") or "").strip()
        username_input = (request.POST.get("username") or "").strip()

        # Debug: log what is received
        print("Identifier:", repr(identifier))
        print("Username input:", repr(username_input))

        # Match by username if provided
        users = User.objects.filter(username=username_input) if username_input else User.objects.none()

        # If no match, try email
        if not users.exists() and identifier:
            users = User.objects.filter(email=identifier)

        # Debug: matched users
        print("Matched users:", users)

        if not users.exists():
            messages.error(request, "❌ No account found with this email/username.")
            request.session['open_forgot_modal'] = True
            return redirect("login")

        # Multiple users? Ask to select
        if users.count() > 1:
            request.session['matched_user_ids'] = list(users.values_list('id', flat=True))
            request.session['open_select_user_modal'] = True
            return redirect("login")  # your modal will show selection
        else:
            user = users.first()
            return send_otp_for_user(request, user)

    request.session['open_forgot_modal'] = True
    return redirect("login")


# -------------------- Helper: Send OTP --------------------
def send_otp_for_user(request, user):
    otp = str(random.randint(100000, 999999))
    request.session['reset_user_id'] = user.id
    request.session['reset_otp'] = otp
    request.session['show_otp_modal'] = True

    send_mail(
        subject="Your Password Reset OTP - JOB365",
        message=f"Hello {user.username},\n\nYour OTP is: {otp}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    messages.success(request, f"✅ OTP sent to {user.username}. Please check your email.")
    return redirect("login")


# -------------------- Step 1b: Select User if multiple --------------------
def select_user_for_otp(request):
    if request.method == "POST":
        user_id = request.POST.get("selected_user_id")
        if not user_id:
            messages.error(request, "❌ Please select a user.")
            return redirect("login")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "❌ User not found.")
            return redirect("login")

        return send_otp_for_user(request, user)

    return redirect("login")


# -------------------- Step 2: Verify OTP and Reset Password --------------------
from django.core.mail import send_mail
from django.conf import settings

def verify_otp(request):
    if request.method == "POST":
        otp_input = (request.POST.get("otp") or "").strip()
        new_password = (request.POST.get("new_password") or "").strip()
        confirm_password = (request.POST.get("confirm_password") or "").strip()

        user_id = request.session.get("reset_user_id")
        otp_session = request.session.get("reset_otp")

        if not user_id or otp_input != otp_session:
            messages.error(request, "❌ Invalid OTP or session expired.")
            return redirect("login")

        if new_password != confirm_password:
            messages.error(request, "❌ Passwords do not match.")
            return redirect("login")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "❌ User not found.")
            return redirect("login")

        # Reset password
        user.set_password(new_password)
        user.save()

        # ✅ Send confirmation email
        send_mail(
            subject="Your JOB365 Password Was Changed",
            message=f"Hello {user.username},\n\nYour password on JOB365 was successfully changed.\n"
                    f"If you did not perform this action, please contact support immediately.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        # Clear session
        request.session.pop("reset_user_id", None)
        request.session.pop("reset_otp", None)
        request.session['show_otp_modal'] = False

        messages.success(request, "✅ Password reset successful! Please login. A confirmation email has been sent.")
        return redirect("login")

    return redirect("login")
