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
            'name',
            'website',
            'description',
            'location',
            'logo'
        ]

from .models import JobApplication
class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        exclude = ['user', 'job', 'job_name', 'company_name','applied_date']