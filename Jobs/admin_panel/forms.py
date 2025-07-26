from django import forms
from admin_panel.models import Job

class JobForm(forms.ModelForm):
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter skills '}),
        required=False
    )

    class Meta:
        model = Job
        fields = ['job_name', 'company_name', 'location', 'hourly_rates', 'job_details',
                  'vacancies', 'duration', 'contact_number', 'email', 'status', 'skills','salary']
