from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from app.models import JobSeeker, Company  # Example models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from admin_panel.models import Job,AdminJobApplication
from admin_panel.forms import JobForm
from django.contrib import messages
def dashboard(request):
    # Count total jobseekers and employers
    total_jobseekers = JobSeeker.objects.count()
    total_employers = Company.objects.count()
    print("=== DEBUG: APPLICATIONS ===")
    
    # Fetch all jobs ordered by latest created date
    applications = Job.objects.all().order_by('-created_at')  

    return render(request, 'admindashboard.html', {
        'total_jobseekers': total_jobseekers,
        'total_employers': total_employers,
        'applications': applications,
    })
def job_list(request):
    jobs = Job.objects.all()
    return render(request, 'company_job_posts.html', {'jobs': jobs})
def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            print("✅ Job Saved")
            return redirect('job_list')  # After save, redirect
        else:
            print("❌ Form Errors:", form.errors)  # Debug print
    else:
        form = JobForm()

    return render(request, 'addjob.html', {'form': form})
def job_update(request, pk):
    job = get_object_or_404(Job, pk=pk)
    form = JobForm(request.POST or None, instance=job)
    if form.is_valid():
        form.save()
        return redirect('job_list')
    return render(request, 'job_form.html', {'form': form})

def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        job.delete()
        return redirect('job_list')
    return render(request, 'job_confirm_delete.html', {'job': job})
def user_management(request):
    # List jobseekers or employers
    jobseekers = JobSeeker.objects.all()
    employers = Company.objects.all()
    return render(request, 'user_management.html', {
        'jobseekers': jobseekers,
        'employers': employers,
    })
from django.shortcuts import render

def company_details(request):
    # 1. Read status from query parameters; default to "active"
    status = request.GET.get('status', 'active').lower()
    # 2. Read search query
    search_query = request.GET.get('search', '').strip()

    # 3. Example data for "active" status (Sachin, as you requested)
    active_data = {
        
        'first_name': 'Sachin',
        'last_name': 'Kumar',
        'mobile': '1234567890',
        'email': 'Kerala.woods@gmail.com',
        'address': 'Kerala woods',
        'state': 'Kerala',
        'city': 'Kochi',
        'pincode': '673000',
        'po_address': 'PO Mumbai - 007',
        'ifsc_code': '000000',
        'bank_name': 'KeralaWoods',
        'registration_number': '123456',
        'description': 'bjhbjbh',
        'idcard_proof': 'bjbhjbh',
        'pancard_photo': 'bjbhjbh',
        'bank_passbook': 'bjbhjbh',
        'company_name': 'KeralaWoods'
    }

    # 4. Example data for "inactive" status (just an example)
    #    You can use the same data as active if you want them identical.
    inactive_data = {
        'first_name': 'Ravi',
        'last_name': 'K',
        'mobile': '9876543210',
        'email': 'woods.inactive@gmail.com',
        'address': 'Inactive Lane',
        'state': 'Kerala',
        'city': 'Kochi',
        'pincode': '673001',
        'po_address': 'PO Mumbai - 008',
        'ifsc_code': '111111',
        'bank_name': 'InactiveBank',
        'registration_number': '999999',
        'description': 'inactive data',
        'idcard_proof': 'id_inactive',
        'pancard_photo': 'pan_inactive',
        'bank_passbook': 'passbook_inactive',
        'company_name': 'InactiveWoods'
    }

    # Decide which data set to show based on status
    if status == 'inactive':
        company_data = inactive_data
    else:
        company_data = active_data

    # 5. Basic search logic
    #    If search query is not found in first_name or company_name, hide data.
    show_data = True
    if search_query:
        if (search_query.lower() not in company_data['first_name'].lower() and
            search_query.lower() not in company_data['company_name'].lower()):
            show_data = False

    # 6. Build context for template
    context = {
        'status': status,                    # 'active' or 'inactive'
        'search_query': search_query,
        'company_data': company_data if show_data else None,
    }
    return render(request, 'company_details.html', context)
def company_job_posts(request):
    # Hardcoded data replicating your screenshot exactly
    jobs = [
        {
            'job_name': 'Carpenter Job helper',
            'company_name': 'Shobha interiors',
            'location': 'Bangalore',
            'hourly_rates': '60/hr',
            'job_details': 'Smart and hardworking carpenter helper needed.',
            'vacancies': '10',
            'duration': '1 year project',
            'contact_number': '123456789',
            'email': 'shobhainto@gmail.com',
            'status': 'Active'
        },
        {
            'job_name': 'Interior Designer Trainee',
            'company_name': 'Shobha interiors',
            'location': 'Calicut',
            'hourly_rates': '80/hr',
            'job_details': 'Dedicated interior designers who possess great knowledge in interior works',
            'vacancies': '10',
            'duration': '1 year project',
            'contact_number': '123456789',
            'email': 'shobhainto@gmail.com',
            'status': 'Inactive'
        },
        {
            'job_name': 'Carpenter Job helper',
            'company_name': 'Shobha interiors',
            'location': 'Bangalore',
            'hourly_rates': '60/h',  # Notice "60/h" matches your snippet
            'job_details': 'Smart and hardworking carpenter helper needed.',
            'vacancies': '10',
            'duration': '1 year project',
            'contact_number': '123456789',
            'email': 'shobhainto@gmail.com',
            'status': 'Active'
        },
    ]
    return render(request, 'company_job_posts.html', {'jobs': jobs})

def jobseeker_details(request):
    """
    Renders a page that looks exactly like your screenshot,
    showing job seeker details on the right, a sidebar on the left,
    and a search/filter row on top.
    """

    # 1. Example data for the job seeker (extra dark details).
    #    Adjust or expand fields as needed.
    data = {
        'first_name': 'Sachin',
        'last_name': 'Kumar',
        'mobile_no': '12345678910',
        'email': 'kerala.woods@gmail.com',
        'address': 'Kerala woods, PO A, Mumbai - 007',
        'state': 'Kerala',
        'city': 'Kochi',
        'pincode': '673000',
        'bank_account_number': '123456789',
        'ifsc_code': '58234567',
        'bank_name': 'Ker',
        'id_card_proof': 'Pancard',
        'pancard': 'SomePANNumber',
        'educational_details': 'B.Com',
        'dob': '20/04/2024',
    }

    # 2. Check status (active/inactive) from query parameters
    status = request.GET.get('status', 'active').lower()

    # 3. Build context
    context = {
        'data': data,
        'status': status,  # "active" or "inactive"
    }
    return render(request, 'job_seeker_details.html', context)
from django.shortcuts import render

def jobseeker_applied_jobs(request):
    """
    Renders a page with three cards showing job seekers' applied job details,
    exactly matching the screenshot.
    """
    applied_jobs = [
        {
            'id': 1,
            'applicant_name': 'Ravi Kumar',
            'job_name': 'Carpenter Job helper',
            'job_code': '6002',
            'shop_name': 'Shobha wood works',
            'hourly_rates': '50/hr',
            'location': 'Calicut',
            'status': 'Applied'
        },
        {
            'id': 2,
            'applicant_name': 'Ravi Kumar',
            'job_name': 'Carpenter Job helper',
            'job_code': '6003',
            'shop_name': 'Shobha wood works',
            'hourly_rates': '50/hr',
            'location': 'Calicut',
            'status': 'Saved'
        },
        {
            'id': 3,
            'applicant_name': 'Ravi Kumar',
            'job_name': 'Carpenter Job helper',
            'job_code': '6004',
            'shop_name': 'Shobha wood works',
            'hourly_rates': '50/hr',
            'location': 'Calicut',
            'status': 'Applied'
        },
    ]
    return render(request, 'jobseeker_applied_jobs.html', {'applied_jobs': applied_jobs})

from django.core.paginator import Paginator
def admin_job_listing(request):
    job_list = Job.objects.all().order_by('-created_at')
    paginator = Paginator(job_list, 4)  # Show 4 jobs per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_job_listing.html', {'page_obj': page_obj})
def subscription_view(request):
    return render(request, 'subscriptions.html')
def create_subscription_view(request):
    return render(request, 'create_subscription.html')
def company_subscriptions_view(request):
    return render(request, 'company_subscriptions.html')
def jobseeker_sub_view(request):
    return render(request, 'jobseeker_sub.html')

import json
from django.shortcuts import render
from django.http import JsonResponse

def content_management_page(request):
    
    return render(request, 'content_management.html')


def save_content(request):
    """
    Handles the form submission (via fetch/AJAX) from content_management.html.
    In a real app, you would parse the data, save to DB, etc.
    """
    if request.method == 'POST':
        try:
            # If you're using fetch with JSON:
            data = json.loads(request.body)

            content_type = data.get('contentType')
            title = data.get('title')
            description = data.get('description')
           
            return JsonResponse({
                'success': True,
                'message': 'Content saved successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def settings_customization_page(request):
    return render(request, 'settings_customization.html')

@csrf_exempt
def save_settings(request):
   
    if request.method == 'POST':
        try:
            data = json.loads(request.body)


            # TODO: Store data in your database or settings model
            # e.g.:
            # Settings.objects.update_or_create(defaults={
            #     "enable_feature_x": data["platformBehavior"]["enableFeatureX"],
            #     "role_management": data["platformBehavior"]["roleManagement"],
            #     ...
            # })

            return JsonResponse({"success": True, "message": "Settings saved successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    else:
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

def report_analytics_page(request):
    context = {
        'total_users': 1250,
        'total_jobs': 340,
        'monthly_signups': [50, 75, 120, 90, 140, 200],  # example
        'monthly_applications': [300, 400, 600, 450, 700, 900],  # example
    }
    return render(request, 'report_analytics.html', context)

# from admin_panel.models import AdminJobApplication # import your model correctly
from app.models import JobApplication  # ✅ Correct source

def applications_dashboard(request):
    applications = JobApplication.objects.all().order_by('-applied_date')

    print("=== DEBUG: APPLICATIONS ===")
    print("=== DEBUG: APPLICATIONS COUNT ===", applications.count())
    for a in applications:
        print("🔹", a.full_name)
        print("User:", a.user)
        print("Username:", getattr(a.user, "username", "❌ user is None"))
   

    return render(request, 'applications.html', {'applications': applications})

from django.contrib import messages
from.models import Job, AdminJobApplication

@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    already_applied = AdminJobApplication.objects.filter(user=request.user, job=job).exists()

    if request.method == 'POST':
        if already_applied:
            messages.info(request, "You have already applied for this job.")
        else:
            AdminJobApplication.objects.create(user=request.user, job=job)
            messages.success(request, "Your application has been submitted successfully.")
            return redirect('applications')

    return render(request, 'job_detail.html', {
        'job': job,
        'already_applied': already_applied
    })
def list_companies(request):
    companies = Company.objects.select_related('user').all().order_by('-user__date_joined')  # latest by default

    query = request.GET.get('q')
    sort = request.GET.get('sort')

    if query:
        companies = companies.filter(user__username__icontains=query)

    if sort == 'oldest':
        companies = companies.order_by('user__date_joined')
    elif sort == 'latest':
        companies = companies.order_by('-user__date_joined')

    return render(request, 'companylist.html', {'companies': companies})

# views.py
from app.models import JobSeeker

def list_jobseekers(request):
    sort = request.GET.get("sort", "latest")
    if sort == "oldest":
        jobseekers = JobSeeker.objects.select_related('user').order_by('user__date_joined')
    else:
        jobseekers = JobSeeker.objects.select_related('user').order_by('-user__date_joined')

    return render(request, "jobseekelist.html", {
        "jobseekers": jobseekers,
        "sort": sort
    })
