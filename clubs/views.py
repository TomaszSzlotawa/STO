from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import UsersClub, Club, Team
from .forms import SignUpForm
from django.contrib.auth import login, authenticate

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.license = form.cleaned_data.get('license')
            user.profile.license_expiry_date = form.cleaned_data.get('license_expiry_date')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect(index)
    else:
        form = SignUpForm()
    return render(request, 'clubs\signup.html', {'form': form})

def index(request):
    clubs = Club.objects.all()
    usersClubs = UsersClub.objects.all()
    teams = Team.objects.all()
    return render(request,'clubs\main.html',{'clubs':clubs,'usersClubs':usersClubs,'teams':teams})

