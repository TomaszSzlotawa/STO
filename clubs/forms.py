from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile



class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30,required=True, help_text="wpisz swoje imię")
    last_name = forms.CharField(max_length=30,required=True, help_text="wpisz swoje nazwisko")
    email = forms.EmailField(max_length=254,help_text="Wprowadź swój adres email")

    class Meta:
        model = User
        fields = ('username','email','first_name','last_name','password1','password2')

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An user with this email already exists!")
        return email

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email','first_name','last_name')
    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An user with this email already exists!")
        return email

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('license','license_expiry_date')

