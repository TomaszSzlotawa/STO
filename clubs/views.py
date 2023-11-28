from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from .models import UsersClub, Club, Team, Profile, Season
from .forms import SignUpForm, ProfileForm, UserForm, ClubCreationForm, UsersClubForm, UserRoleAnswerForm, TeamCreateForm, SeasonCreateForm, SeasonChooseForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail


def data_for_menu(request):
    if request.user.is_authenticated:
        user = request.user
        usersClubs = UsersClub.objects.filter(user = user, accepted = True)
        teams = []
        for club in usersClubs:
            club_team = Team.objects.filter(club=club.club)
            teams.extend(club_team)
    else:
        usersClubs=[]
        teams = []
    
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
            send_mail(
            "Witamy w STO",
            f"witaj {user.first_name}, właśnie założyłeś konto w systemie STO.",
            "welcome@sto.com",
            [f"{user.email}"],
            fail_silently=False,
)
            return redirect(user_panel)
    else:
        form = SignUpForm()
    return render(request, 'clubs\signup.html', {'form': form})




def user_panel(request):
    usersClubs, teams = data_for_menu(request)

    return render(request,'clubs\\user_panel.html',{'usersClubs':usersClubs,'teams':teams})

def user_profile(request):
    usersClubs, teams = data_for_menu(request)

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
    return render(request, 'clubs\\user_profile.html',{'profile_form': profile_form,'user_form':user_form,'password_form':password_form,'usersClubs':usersClubs,'teams':teams})

def delete_profile(request):
    usersClubs, teams = data_for_menu(request or None)
    user = request.user
    if request.method == 'POST':
        user.delete()
        return redirect(user_panel)
    return render(request,'clubs\\confirm.html',{'user':user,'usersClubs':usersClubs,'teams':teams})

def create_club(request):
    usersClubs, teams = data_for_menu(request)
    form = ClubCreationForm(request.POST or None)
    if form.is_valid():
        user = request.user
        club = form.save()
        users_club = UsersClub(club = club,user = user, admin = True, accepted = True)
        users_club.save()
        return redirect(user_panel)
    return render(request,'clubs\\create_club.html',{'form':form,'usersClubs':usersClubs,'teams':teams})

def club_settings(request, club_id):
    usersClubs, teams = data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    seasons = Season.objects.filter(team__in=teams)
    allowed = False
    for usersClub in usersClubs:
        if usersClub.club == club:
            if usersClub.admin == True:
                allowed=True

    if allowed:
        users = UsersClub.objects.filter(club = club)
        form = ClubCreationForm(request.POST or None, instance = club)
        if request.method == 'POST':
            if form.is_valid():
                club = form.save()
                return redirect(club_settings, club.id)
            else:
                messages.error(request, 'Błąd')
        return render(request,'clubs\\club_settings.html',{'form':form,'usersClubs':usersClubs,'teams':teams,'club':club,'users':users,'seasons':seasons})
    else:
        return redirect(user_panel)
def delete_club(request,club_id):
    usersClubs, teams = data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    if request.method == 'POST':
        club.delete()
        return redirect(user_panel)
    return render(request,'clubs\\confirm_club.html',{'club':club,'usersClubs':usersClubs,'teams':teams})

def roles_in_club(request,club_id):
    usersClubs, teams = data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    users = UsersClub.objects.filter(club = club)
    contains_admin = False
    if request.method == 'POST':
        for user in users: 
            if request.POST.get(f'admin_{user.id}') == 'on':
                if user.accepted==True:
                    contains_admin = True
        if contains_admin:
            for user in users: 
                admin = request.POST.get(f'admin_{user.id}') == 'on'
                coach = request.POST.get(f'coach_{user.id}') == 'on'
                employee = request.POST.get(f'employee_{user.id}') == 'on'
                training_coordinator = request.POST.get(f'training_coordinator_{user.id}') == 'on'
                
                if admin or coach or employee or training_coordinator:
                    user.admin = admin
                    user.coach = coach
                    user.employee = employee
                    user.training_coordinator = training_coordinator
                    user.save()
                else:
                    user.delete()
        else:
            return redirect(roles_in_club,club.id)

        return redirect(club_settings, club.id)
    return render(request,'clubs\\roles_in_club.html',{'club':club,'usersClubs':usersClubs,'teams':teams,'users':users})

def add_user_to_club(request,club_id):
    usersClubs, teams = data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    if request.method == 'POST':
        form = UsersClubForm(club, request.POST)
        if form.is_valid():
            user = form.cleaned_data['email'] 
            admin = form.cleaned_data['admin']
            coach = form.cleaned_data['coach']
            employee = form.cleaned_data['employee']
            training_coordinator = form.cleaned_data['training_coordinator']

            users_club, created = UsersClub.objects.get_or_create(user=user, club=club)

            # Zaktualizuj dane
            users_club.admin = admin
            users_club.coach = coach
            users_club.employee = employee
            users_club.training_coordinator = training_coordinator
            users_club.save()

            return redirect('club_settings', club.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = UsersClubForm(club)

    return render(request,'clubs\\add_user_to_club.html',{'club':club,'usersClubs':usersClubs,'teams':teams,'form':form})

def user_roles(request):
    usersClubs, teams = data_for_menu(request)
    usersClubs_roles = UsersClub.objects.filter(user = request.user)
    return render(request,'clubs\\user_roles.html',{'usersClubs':usersClubs,'teams':teams,'usersClubs_roles':usersClubs_roles})

def user_role_delete(request, club_id):
    club = get_object_or_404(Club, pk = club_id)
    users = UsersClub.objects.filter(club = club)
    if request.method == 'POST':
        for user in users: 
            if user.admin == True and user.user != request.user:
                if user.accepted==True:
                    usersclub = UsersClub.objects.filter(user = request.user, club=club)
                    usersclub.delete()


    return redirect(user_roles)
def user_role_answer(request, club_id):
    if request.method == 'POST':
        club = get_object_or_404(Club, pk = club_id)
        form = UserRoleAnswerForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            usersclub = UsersClub.objects.filter(user = request.user, club=club)
            usersclub.update(accepted = status)
            return redirect(user_roles) 
    return redirect(user_roles)

def create_team(request,club_id):
    usersClubs, teams = data_for_menu(request)
    club = get_object_or_404(Club, pk = club_id)
    if request.method == 'POST':
        team_form = TeamCreateForm(request.POST)
        season_form = SeasonCreateForm(request.POST)

        if team_form.is_valid() and season_form.is_valid():
            team = team_form.save(commit=False)
            team.club = club
            team.save()

            season = season_form.save(commit=False)
            season.name = season_form.cleaned_data['season_name']
            season.team = team
            season.save()

            return redirect(club_settings, club.id)
    else:
        team_form = TeamCreateForm()
        season_form = SeasonCreateForm()

    return render(request,'clubs\\create_team.html',{'club':club,'usersClubs':usersClubs,
        'teams':teams,'team_form':team_form, 'season_form':season_form})

def delete_team(request, team_id):
    usersClubs, teams = data_for_menu(request)
    team = get_object_or_404(Team,pk=team_id)
    club = team.club
    if request.method == 'POST':
        team.delete()
        return redirect(club_settings,club.id)
    return render(request,'clubs\\confirm_team.html',{'team':team,'club':club,'usersClubs':usersClubs,'teams':teams})

def edit_team(request, team_id):
    usersClubs, teams = data_for_menu(request)
    team = get_object_or_404(Team,pk=team_id)
    club = team.club
    team_form = TeamCreateForm(request.POST or None, instance=team)
    season_form = SeasonChooseForm(request.POST, team=team)
    if request.method == 'POST':
        if team_form.is_valid:
            team = team_form.save()
            return redirect(edit_team,team.id)
        if season_form.is_valid:
            season = season_form.save()
            season.save()
            return redirect(edit_team,team.id)

    return render(request,'clubs\\edit_team.html',{'club':club,'usersClubs':usersClubs,
        'teams':teams,'team_form':team_form, 'season_form':season_form})