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
from datetime import date, timedelta
from django.core.paginator import Paginator
from django.db.models import Q

def home(request):
    jobs = Job.objects.filter(status='Active')

    # --- Filters ---
    selected_type = request.GET.get('type')  
    selected_locations = request.GET.getlist('location')  
    selected_dates = request.GET.getlist('date')  
    sort = request.GET.get('sort', '')  
    search_query = request.GET.get('q', '').strip()  

    # Job Type filter
    if selected_type and selected_type != 'Other':
        jobs = jobs.filter(job_type=selected_type)

    # Location filter
    if selected_locations:
        jobs = jobs.filter(location__in=selected_locations)

    # Date filter
    if selected_dates and "All" not in selected_dates:
        today = date.today()
        q_date = Q()
        for label in selected_dates:
            if label == "Today":
                q_date |= Q(created_at__date=today)
            elif label == "Less than 10 days":
                q_date |= Q(created_at__gte=today - timedelta(days=10))
            elif label == "More than 10 days":
                q_date |= Q(created_at__lt=today - timedelta(days=10))
        jobs = jobs.filter(q_date)

    # Search filter
    if search_query:
        jobs = jobs.filter(
            Q(job_name__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(skills__icontains=search_query)
        )

    # Sort
    if sort == 'recent':
        jobs = jobs.order_by('-created_at')
    elif sort == 'oldest':
        jobs = jobs.order_by('created_at')
    elif sort == 'vacancy':
        jobs = jobs.order_by('-vacancies')
    else:
        jobs = jobs.order_by('-created_at')

    # Pagination
    paginator = Paginator(jobs, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Sidebar options
    date_labels = ["Today", "Less than 10 days", "More than 10 days"]
    job_types = ["Physical work", "Office work", "IT work", "Kitchen work",
                 "Field work", "Health work", "Other"]
    locations = ["Ernakulam", "Thiruvananthapuram", "Thrissur", "Malappuram",
                 "Kozhikode", "Idukki", "Pathanamthitta", "Kollam",
                 "Palakkad", "Wayanad", "Kannur", "Kasaragod"]

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'homepage.html', {
        'page_obj': page_obj,
        'all_jobs': jobs,
        'date_labels': date_labels,
        'job_types': job_types,
        'locations': locations,
        'unread_count': unread_count,
        'selected_type': selected_type,
        'selected_locations': selected_locations,
        'selected_dates': selected_dates,
        'search_query': search_query,
        'sort': sort,
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

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save form including uploaded files
            profile = form.save(commit=False)

            # Ensure only updated files are replaced
            for field_name in ['upload_id_card', 'upload_proof_detail', 'upload_pan_card', 'upload_passbook']:
                if field_name in request.FILES:
                    setattr(profile, field_name, request.FILES[field_name])

            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "There was an error updating your profile.")
    else:
        form = ProfileForm(instance=profile)

    document_fields = {
        'upload_id_card': profile.upload_id_card.url if profile.upload_id_card else None,
        'upload_proof_detail': profile.upload_proof_detail.url if profile.upload_proof_detail else None,
        'upload_pan_card': profile.upload_pan_card.url if profile.upload_pan_card else None,
        'upload_passbook': profile.upload_passbook.url if profile.upload_passbook else None,
    }

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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import JobApplication,Notification

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_archived=False).order_by("-created_at")
    favorites = notifications.filter(is_favorite=True)
    archive = Notification.objects.filter(user=request.user, is_archived=True)
    # Mark all unread notifications as read
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, "notification.html", {
        "notifications": notifications,
        "favorites": favorites,
        "archive": archive,
        "notifications_count": notifications.count(),
    })

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
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import JobApplication, Job, Company

# ✅ List of applicants for jobs posted by this company
@login_required
def employee_details(request):
    # Ensure this user has a company profile
    company = get_object_or_404(Company, user=request.user)

    # Get only applications for jobs posted by this company
    applications = JobApplication.objects.select_related("user", "job") \
                                         .filter(job__user=request.user)

    return render(request, "employee_details.html", {"employees": applications})


# ✅ Detail view for a single applicant (restricted by company)
@login_required
def employee_detail(request, employee_id):
    # Ensure this user has a company profile
    company = get_object_or_404(Company, user=request.user)

    # Restrict applications to jobs posted by this company
    application = get_object_or_404(
        JobApplication.objects.select_related("user", "job"),
        id=employee_id,
        job__user=request.user  # restrict to jobs this company posted
    )

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
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "notifications.html", {
        
        "notifications": notifications,
       
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
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, JobApplication, Profile, Education
from .forms import JobApplicationForm
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Job, JobApplication, Profile, Education, SavedJob
from .models import Education, Experience
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

            # Save applicant info into JobApplication
            application.full_name = request.POST.get('full_name')
            application.email = request.POST.get('email')
            application.phone_number = request.POST.get('phone_number')

            application.age = request.POST.get('age')
            application.gender = request.POST.get('gender')
            dob_str = request.POST.get('dob')
            if dob_str:
                try:
                    application.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                except ValueError:
                    application.dob = None
            application.place = request.POST.get('place')

            application.skills = request.POST.get('skills')
            
            application.cover_letter = request.POST.get('cover_letter')
            if request.FILES.get('resume'):
                application.resume = request.FILES.get('resume')
            application.save()
            print("DEBUG POST phone_number:", request.POST.get("phone_number"))
            print("DEBUG about to save:", application.phone_number)

            # Notifications
                # Jobseeker notification
            Notification.objects.create(
                user=request.user,
                message=f"You successfully applied for {job.job_name} at {job.company_name}",
                type="jobseeker_applied"
            )

            # Company notification
            Notification.objects.create(
                user=job.user,
                job=job,
                message=f"{request.user.username} applied for your job '{job.job_name}'",
                type="company_received"
            )


            # Save education (first one for now)
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

            # Save multiple experiences
           # save multiple experiences
        # Save multiple experiences
        i = 0
        while request.POST.get(f'experience[{i}][company]'):
            company = request.POST.get(f'experience[{i}][company]')
            role = request.POST.get(f'experience[{i}][role]')
            location = request.POST.get(f'experience[{i}][location]')
            start_date = request.POST.get(f'experience[{i}][start_date]')
            end_date = request.POST.get(f'experience[{i}][end_date]')
            description = request.POST.get(f'experience[{i}][description]')
            certificate = request.FILES.get(f'experience[{i}][certificate]')

            def parse_month(value):
                if value:
                    try:
                        return datetime.strptime(value, "%Y-%m").date().replace(day=1)
                    except ValueError:
                        return None
                return None

            start_date = parse_month(start_date)
            end_date = parse_month(end_date)

            if company and role:
                # Avoid duplicates
                exp_exists = Experience.objects.filter(
                    user=request.user,
                    company=company,
                    role=role,
                    start_date=start_date,
                    end_date=end_date
                ).exists()

                if not exp_exists:
                    Experience.objects.create(
                        user=request.user,
                        company=company,
                        role=role,
                        location=location,
                        start_date=start_date,
                        end_date=end_date,
                        description=description,
                        certificate=certificate
                    )
            i += 1

        # ✅ Done saving everything, now render once
        return render(request, 'jobseeker_job_detail.html', {
            'form': JobApplicationForm(),
            'job': job,
            'applied_successfully': True,
            'saved_job_ids': saved_job_ids,
            'all_jobs': all_jobs,
        })

    else:
        form = JobApplicationForm()

    return render(request, 'jobseeker_job_detail.html', {
        'form': form,
        'job': job,
        'form_errors': form.errors,
        'saved_job_ids': saved_job_ids,
        'all_jobs': all_jobs,
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
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from .models import Job, Notification
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from .models import Job, Notification

def post_job(request):
    if request.method == 'POST':
        job_code = get_random_string(8).upper()

        # Get multiple skills from form and join as comma-separated string
        skills_list = request.POST.getlist('skills')  # from checkboxes or multiple input
        skills = ", ".join(skill.strip() for skill in skills_list)

        # Create Job object
        job = Job.objects.create(
            user=request.user,
            job_name=request.POST.get('job_name'),
            company_name=request.POST.get('company_name'),
            location=request.POST.get('posted_location'),
            job_time=request.POST.get('job_time'),
            experience=request.POST.get('experience'),
            job_code=job_code,
            work_hour=request.POST.get('work_hour'),
            short_description=request.POST.get('short_description'),
            job_details=request.POST.get('short_description'),  # or use separate field if needed
            vacancies=request.POST.get('vacancy'),
            duration=request.POST.get('duration'),
            contact_number=request.POST.get('contact'),
            email=request.POST.get('email'),
            hourly_rates=request.POST.get('wage'),
            salary=request.POST.get('salary'),
            skills=skills,
            end_date=request.POST.get("end_date"),
        )

        Notification.objects.create(
    user=request.user,
    message=f"New job '{job.job_name}' posted by {job.company_name}",
    type="job_posted"
)
     # after job.save()
        Notification.objects.create(
            user=job.user,  # company who posted
            job=job,
            message=f"Your job '{job.job_name}' has been posted successfully!",
            type="job_posted"
        )


        messages.success(request, "Job successfully posted. We will contact you soon.")
        return redirect('post_job')  # redirect to clear form and show message

    # For GET request: generate a random job code
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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Job, JobApplication

@login_required
def view_applicants(request, job_id):
    # Ensure only job owner (company) can view applicants
    job = get_object_or_404(Job, id=job_id)

    if job.user != request.user:
        return HttpResponseForbidden("❌ You are not allowed to view these applicants.")

    # Fetch applications for this job
    applicants = JobApplication.objects.filter(job=job).select_related("user")

    return render(request, "applicant_list.html", {
        "job": job,
        "applicants": applicants
    })

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from .models import Job, JobApplication, Profile, Education
@login_required
def view_applicant_detail(request, job_id, application_id):
    job = get_object_or_404(Job, id=job_id)
    application = get_object_or_404(JobApplication, id=application_id, job=job)
    
    # Unique education
    education_qs = Education.objects.filter(user=application.user)
    seen_schools = set()
    unique_education = []
    for edu in education_qs:
        if edu.school not in seen_schools:
            unique_education.append(edu)
            seen_schools.add(edu.school)

    # Unique experiences (by company + role + start + end)
    experiences_qs = Experience.objects.filter(user=application.user)
    seen_exp = set()
    unique_experiences = []
    for exp in experiences_qs:
        key = (exp.company, exp.role, exp.start_date, exp.end_date)
        if key not in seen_exp:
            unique_experiences.append(exp)
            seen_exp.add(key)

    context = {
        'job': job,
        'application': application,
        'education_list': unique_education,
        'experiences': unique_experiences,
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
    Notification.objects.create(
    user=job.company.user,
    message=f"Your job '{job.title}' has been deleted.",
    type="job_deleted",
    job=job
)

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
# jobs/views.py
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Job
import logging

logger = logging.getLogger(__name__)

def filtered_jobs(request):
    logger.info("✅ filtered_jobs view called")

    # Start with all jobs
    jobs = Job.objects.all()

    # Get query parameters
    job_date = request.GET.get('job_date')
    job_type = request.GET.get('job_type')
    location = request.GET.get('location')
    work_days = request.GET.get('work_days')
    work_hours = request.GET.get('work_hours')

    # Debug: print the received filters
    logger.debug(f"Received filters: job_date={job_date}, job_type={job_type}, location={location}, work_days={work_days}, work_hours={work_hours}")

    # ----- Filter by Job Date -----
    if job_date:
        now = timezone.now()
        if job_date == 'today':
            jobs = jobs.filter(posted_date__date=now.date())
        elif job_date == 'less10':
            jobs = jobs.filter(posted_date__gte=now - timedelta(days=10))
        elif job_date == 'more10':
            jobs = jobs.filter(posted_date__lt=now - timedelta(days=10))
        logger.debug(f"After job_date filter ({job_date}): {jobs.count()} jobs")

    # ----- Filter by Job Type -----
    if job_type:
        jobs = jobs.filter(job_time__icontains=job_type)
        logger.debug(f"After job_type filter ({job_type}): {jobs.count()} jobs")

    # ----- Filter by Location (Kerala States if empty) -----
    kerala_states = ['Thiruvananthapuram', 'Kollam', 'Pathanamthitta', 'Alappuzha', 'Kottayam', 'Idukki', 'Ernakulam', 'Thrissur', 'Palakkad', 'Malappuram', 'Kozhikode', 'Wayanad', 'Kannur', 'Kasaragod']
    if location:
        jobs = jobs.filter(location__iexact=location)
    else:
        # If no location selected, default to all Kerala states
        jobs = jobs.filter(location__in=kerala_states)
    logger.debug(f"After location filter ({location}): {jobs.count()} jobs")

    # ----- Filter by Work Days -----
    if work_days:
        jobs = jobs.filter(duration__icontains=work_days)  # Assuming 'duration' field stores work days
        logger.debug(f"After work_days filter ({work_days}): {jobs.count()} jobs")

    # ----- Filter by Work Hours -----
    if work_hours:
        jobs = jobs.filter(work_hour=work_hours)  # Assuming 'work_hour' is exact match
        logger.debug(f"After work_hours filter ({work_hours}): {jobs.count()} jobs")

    logger.info(f"Final queryset count: {jobs.count()} jobs")

    return render(request, 'filtered_jobs.html', {'jobs': jobs})


from datetime import date, timedelta
from django.shortcuts import render
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from .models import Job

@login_required
def filtered_jobs(request):
    user = request.user

    # ✅ Start with only jobs posted by the logged-in company
    jobs = Job.objects.filter(user=user)

    # ----- Get query parameters -----
    job_date = request.GET.get('job_date')
    job_type = request.GET.get('job_type')
    location = request.GET.get('location')
    work_days = request.GET.get('work_days')
    work_hours = request.GET.get('work_hours')
    search_query = request.GET.get('search')
    sort_by = request.GET.get('sort')

    # ----- Search -----
    if search_query:
        jobs = jobs.filter(job_name__icontains=search_query)

    # ----- Filter by Job Date -----
    if job_date:
        now = timezone.now()
        if job_date == 'today':
            jobs = jobs.filter(posted_date__date=now.date())
        elif job_date == 'less10':
            jobs = jobs.filter(posted_date__gte=now - timedelta(days=10))
        elif job_date == 'more10':
            jobs = jobs.filter(posted_date__lt=now - timedelta(days=10))

    # ----- Filter by Job Type -----
    if job_type:
        jobs = jobs.filter(job_time__icontains=job_type)

    # ----- Filter by Location -----
    if location:
        jobs = jobs.filter(location__iexact=location)

    # ----- Filter by Work Days -----
    if work_days:
        jobs = jobs.filter(duration__icontains=work_days)  # adjust field if different

    # ----- Filter by Work Hours -----
    if work_hours:
        jobs = jobs.filter(work_hour=work_hours)

    # ----- Sorting -----
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
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)

            # If "Remember Me" is not checked, expire the session when browser closes
            if not remember_me:
                request.session.set_expiry(0)  # Session expires on browser close
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days

            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')
from django.shortcuts import render

def about_us(request):
    return render(request, 'about_us.html')

from django.shortcuts import render

def terms_of_use(request):
    return render(request, 'terms_of_use.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

from django.shortcuts import redirect, get_object_or_404

def toggle_favorite(request, note_id):
    note = get_object_or_404(Notification, id=note_id, user=request.user)
    note.is_favorite = not note.is_favorite
    note.save()
    return redirect("notifications")

def archive_notification(request, note_id):
    note = get_object_or_404(Notification, id=note_id, user=request.user)
    note.is_archived = True
    note.save()
    return redirect("notifications")

from django.http import JsonResponse
from App.models import Notification

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@login_required
@require_POST
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"status": "success"})
