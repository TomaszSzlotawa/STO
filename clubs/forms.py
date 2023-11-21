from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30,required=True, help_text="wpisz swoje imię")
    last_name = forms.CharField(max_length=30,required=True, help_text="wpisz swoje nazwisko")
    email = forms.EmailField(max_length=254,help_text="Wprowadź swój adres email")
    licenses = [
    (None,"Brak"),
    ("UEFA D","UEFA D"),
    ("UEFA FUTSAL C","UEFA FUTSAL C"),
    ("UEFA C","UEFA C"),
    ("UEFA FUTSAL B","UEFA FUTSAL B"),
    ("UEFA GOALKEEPER B","UEFA GOALKEEPER B"),
    ("UEFA B","UEFA B"),
    ("UEFA B ELITE YOUTH","UEFA B ELITE YOUTH"),
    ("UEFA GOALKEEPER A","UEFA GOALKEEPER A"),
    ("UEFA A","UEFA A"),
    ("UEFA A ELITE YOUTH","UEFA A ELITE YOUTH"),
    ("UEFA PRO","UEFA PRO"),
    ]
    
    license = forms.ChoiceField(choices =licenses, required=False, help_text="Uprawnienia")
    license_expiry_date = forms.DateField(required=False, help_text='Data wygaśnięcia uprawnień')

    class Meta:
        model = User
        fields = ('username','email','first_name','last_name','license','license_expiry_date','password1','password2')

