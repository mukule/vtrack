from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import UserChangeForm
from .models import *


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={'placeholder': 'Username', 'class': 'form-control'}),
        label='',
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={'placeholder': 'Email', 'class': 'form-control'}),
        label='',
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter First Name', 'class': 'form-control'}),
        label='',

    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter Last Name', 'class': 'form-control'}),
        label='',

    )
    user_type = forms.ChoiceField(
        choices=get_user_model().USER_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='User Type',
    )

    password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password', 'class': 'form-control', 'autocomplete': 'new-password'}),

    )
    password2 = forms.CharField(
        label='',
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Confirm Password', 'class': 'form-control', 'autocomplete': 'new-password'}),

    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name',
                  'email', 'user_type', 'password1', 'password2']

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(
        label='username',
        widget=forms.TextInput(attrs={
                               'placeholder': 'Staff Number or Email', 'class': 'form-control', 'id': 'inputEmailAddress'})
    )

    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password', 'id': 'inputChoosePassword'})
    )


class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['full_name', 'phone', 'purpose_of_visit', 'host',
                  'department', 'email', 'company', 'possessions']

    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'placeholder': 'Full Name', 'class': 'form-control'}),
        label='',
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={'placeholder': 'Phone', 'class': 'form-control'}),
        label='',
    )
    purpose_of_visit = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Purpose of Visit', 'class': 'form-control'}),
        label='',
    )
    host = forms.ModelChoiceField(
        queryset=Staff.objects.all(),
        empty_label='Choose Host',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'host'}),
        label='',
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label='Choose Department',
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'department'}),
        label='',
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={'placeholder': 'Email (Optional)', 'class': 'form-control'}),
        label='',
        required=False,
    )
    company = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'placeholder': 'Company (Optional)', 'class': 'form-control'}),
        label='',
        required=False,
    )
    possessions = forms.CharField(
        widget=forms.Textarea(attrs={
                              'placeholder': 'Items in Possession (Optional)', 'class': 'form-control', 'rows': '3'}),
        label='',
        required=False,
    )


class DriveInVisitorForm(VisitorForm):
    class Meta:
        model = Visitor
        fields = VisitorForm.Meta.fields + ['number_plate']

    number_plate = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={'placeholder': 'Number Plate', 'class': 'form-control'}),
        label='',
        required=False,
    )


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['department', 'first_name', 'last_name', 'email']

        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].empty_label = 'Choose Department'
        self.fields['department'].queryset = Department.objects.all()


class VisitorTagForm(forms.ModelForm):
    class Meta:
        model = VisitorTag
        fields = ['tag_number']

    tag_number = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'placeholder': 'Last Number', 'class': 'form-control'}),
        label='',
        required=True,
    )

    def clean_tag_number(self):
        tag_number = self.cleaned_data.get('tag_number')
        if tag_number <= 0:
            raise forms.ValidationError(
                "Tag number must be a positive integer greater than 0.")
        return tag_number


class VisitorVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=4,
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter OTP', 'class': 'form-control'}),
        label='',
        required=True,
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit() or len(otp) != 4:
            raise forms.ValidationError("OTP must be a 6-digit number.")
        return otp
