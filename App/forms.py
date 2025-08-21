# myapp/forms.py
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'input-field'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'input-field'})
    )
class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))  # ADD THIS
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))  
    mobile_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': 'Mobile Number'}))
    email_id = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email ID'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Address', 'rows': 3}))
    state = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    pincode = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'placeholder': 'Pincode'}))
    

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'company_name', 'location', 'google_map', 'company_type',
            'employee_size', 'company_industry', 'company_number',
            'company_hr_number', 'profile_image', 'pancard',
            'adhaar', 'personal_id'
        ]


from App.models import JobApplication
class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        exclude = ['user', 'job', 'job_name', 'company_name','applied_date','salary','end_date']
        unique_together = ('user', 'job') 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills'].required = False

# forms.py

from django import forms
from .models import Profile, Education

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['resume']

class CertificateUploadForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school', 'place', 'certificate']
from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'user', 'phone', 'gender', 'dob', 'address', 'education', 'age', 'resume', 'location',
            'profile_image', 'upload_id_card', 'upload_proof_detail', 'upload_pan_card',
            'upload_passbook', 'skills', 'bank_account', 'ifsc_code', 'pan_card',
            'Highest_Qualification', 'work_experience', 'account_type',
            'country', 'city', 'short_bio',  # ✅ Added new fields
        ]

        widgets = {
            'phone': forms.TextInput(attrs={'class': 'w-full mt-1 px-3 py-2 border border-gray-300 rounded'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full mt-1 px-3 py-2 border border-gray-300 rounded'}),
            'gender': forms.Select(attrs={'class': 'w-full mt-1 px-3 py-2 border border-gray-300 rounded'}),
            'country': forms.TextInput(attrs={'class': 'w-full mt-1 px-3 py-2 border border-gray-300 rounded'}),
            'city': forms.TextInput(attrs={'class': 'w-full mt-1 px-3 py-2 border border-gray-300 rounded'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'w-full mt-1 px-3 py-2 border border-gray-300 rounded'}),
            'education': forms.Textarea(attrs={'rows': 2, 'class': 'w-full mt-1 px-3 py-2 border border-gray-300 rounded'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'w-full mt-1 px-3 py-2'}),
            'work_experience': forms.Textarea(attrs={'rows': 2, 'class': 'w-full mt-1 px-3 py-2 border border-gray-300 rounded'}),
        }
