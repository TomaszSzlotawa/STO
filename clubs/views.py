from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from .models import UsersClub, Club, Team, Profile
from .forms import SignUpForm, ProfileForm, UserForm, ClubCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm


def data_for_menu(request):
    user = request.user
    usersClubs = UsersClub.objects.filter(user = user)
    teams = []
    for club in usersClubs:
        club_team = Team.objects.filter(club=club.club)
        teams.extend(club_team)
    return usersClubs, teams

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
            return redirect(user_panel)
    else:
        form = SignUpForm()
    return render(request, 'clubs\signup.html', {'form': form})

def user_panel(request):
    usersClubs, teams = data_for_menu(request)

    return render(request,'clubs\\user_panel.html',{'usersClubs':usersClubs,'teams':teams})

def user_profile(request):
    user = request.user
    user_form = UserForm(request.POST or None, instance = user)
    profile = get_object_or_404(Profile, user = user)
    profile_form = ProfileForm(request.POST or None, instance = profile)
    if all((user_form.is_valid(),profile_form.is_valid())):
        user = user_form.save()
        profile = profile_form.save()
        return redirect(user_profile)
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect(user_profile)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        password_form = PasswordChangeForm(request.user)

    #return render(request, 'clubs\signup.html', {'form': form,'profile':profile})
    return render(request, 'clubs\\user_profile.html',{'profile_form': profile_form,'user_form':user_form,'password_form':password_form})

def delete_profile(request):
    user = request.user
    if request.method == 'POST':
        user.delete()
        return redirect(user_panel)
    return render(request,'clubs\\confirm.html',{'user':user})

def create_club(request,user_id):
    form = ClubCreationForm(request.POST or None)
    if form.is_valid():
        user = get_object_or_404(User, pk = user_id)
        club = form.save()
        users_club = UsersClub(club = club,user = user, admin = True)
        users_club.save()
        return redirect(user_panel)
    return render(request,'clubs\\create_club.html',{'form':form})

def club_settings(request, club_id):
    club = get_object_or_404(Club,pk=club_id)
    form = ClubCreationForm(request.POST or None, instance = club)
    usersClubs, teams = data_for_menu(request)

    return render(request,'clubs\\club_settings.html',{'form':form,'usersClubs':usersClubs,'teams':teams})
    