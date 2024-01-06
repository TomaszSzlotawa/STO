from collections import defaultdict
from itertools import product
from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Attendance, Equipment, ImplementedMezocycle, Mezocycle, Place, Rented_equipment, TeamsCoaching_Staff, Training, Training_in_mezocycle, UsersClub, Club, Team, Profile, Season, Player, Player_data
from .forms import AddCoachToTeam, AttendanceForm, AttendanceReportFilter, CreateEquipment, CreatePlayerDataForm, CreatePlayerForm, EditCoachInTeam, ImplementMezocycleForm, ImplementTrainingForm, MezocycleForm, PlaceForm, RentEquipmentForm, SignUpForm, ProfileForm, Training_in_mezocycleForm, TrainingForm, UserForm, ClubCreationForm, UsersClubForm, UserRoleAnswerForm, TeamCreateForm, SeasonCreateForm, SeasonChooseForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from datetime import date, datetime, timedelta
from django.template.defaulttags import register
from django.db.models import Q
from sto.utils import render_to_pdf
from django.contrib.auth import views as auth_views

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def get_data_for_menu(request):
    if request.user.is_authenticated:
        user = request.user
        usersClubs = UsersClub.objects.filter(user=user, accepted=True).order_by('club__name')
        teams = []
        for club in usersClubs:
            club_team = Team.objects.filter(club=club.club).order_by('name')
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
    return render(request, 'clubs/signup.html', {'form': form})




def user_panel(request):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    user_coaching_teams = TeamsCoaching_Staff.objects.filter(coach=request.user, leaving_date=None)
    coach_in_teams = [coaching_team.team for coaching_team in user_coaching_teams]
    seasons = Season.objects.filter(team__in=coach_in_teams)
    upcoming_trainings = Training.objects.filter(season__in=seasons, start_datatime__gt=datetime.now(), end_datatime__lt=datetime.now() + timedelta(days=7)).order_by('start_datatime')
    profile = get_object_or_404(Profile,pk=request.user.id)
    is_admin = False
    is_training_coordinator = False
    is_coach = False
    is_employee = False
    for u in usersClubs:
        if u.admin:
            is_admin = True
        if u.training_coordinator:
            is_training_coordinator = True
        if u.coach:
            is_coach = True
        if u.employee:
            is_employee = True
    return render(request,'clubs/user_panel.html',{'profile':profile,'usersClubs':usersClubs,'teams':teams,'upcoming_trainings':upcoming_trainings, 'user_coaching_teams':user_coaching_teams, 
                                                   'is_admin':is_admin,'is_training_coordinator':is_training_coordinator, 'is_coach':is_coach, 'is_employee':is_employee})

def club_panel(request, club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    clubs_teams = Team.objects.filter(club=club)
    seasons = Season.objects.filter(team__in=clubs_teams,active=True)
    coaching_staff = TeamsCoaching_Staff.objects.filter(team__in=clubs_teams,leaving_date=None).order_by('coach')
    upcoming_trainings = Training.objects.filter(season__in=seasons, start_datatime__gt=datetime.now(), end_datatime__lt=datetime.now() + timedelta(days=7)).order_by('start_datatime')
    #attendance
    seasons_att = []
    for s in seasons:
        trainings = Training.objects.filter(season=s,start_datatime__range=[s.date_of_start, date.today()])
        attendances = Attendance.objects.filter(training__in = trainings)
        players = s.player.all()
        present = 0
        len_attendance=0
        for att in attendances:
            if att.training.end_datatime < datetime.now():
                len_attendance += 1
                if att.present:
                    present += 1
        if len_attendance==0:
            avg_attendance = 0.00
        else:
            avg_attendance = round(present / len_attendance * 100,2)
        absent = 100-avg_attendance
        seasons_att.append((s,avg_attendance,absent))
    places = Place.objects.filter(club=club)    
    users = UsersClub.objects.filter(club=club, accepted=True)
    return render(request,'clubs/club_panel.html',{'users':users,'club':club,'places':places,'usersClubs':usersClubs,'teams':teams,'coaching_staff':coaching_staff,'upcoming_trainings':upcoming_trainings, 'seasons':seasons,'clubs_teams':clubs_teams,'seasons_att':seasons_att})



def user_profile(request):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    is_admin = False
    is_training_coordinator = False
    is_coach = False
    is_employee = False
    for u in usersClubs:
        if u.admin:
            is_admin = True
        if u.training_coordinator:
            is_training_coordinator = True
        if u.coach:
            is_coach = True
        if u.employee:
            is_employee = True

    user = request.user
    profile = get_object_or_404(Profile, user = user)

    if request.method == 'POST':
        if "data-submit" in request.POST:
            user_form = UserForm(request.POST or None, instance=user)
            profile_form = ProfileForm(request.POST or None, instance=profile)
            password_form = PasswordChangeForm(request.user)
            if all((user_form.is_valid(),profile_form.is_valid())):
                user = user_form.save()
                profile = profile_form.save()
        if "password-submit" in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            user_form = UserForm(instance=user)
            profile_form = ProfileForm(instance = profile)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password was successfully updated!')
            else:
                print("err")
                messages.error(request, 'Please correct the error below.')
    else:
        password_form = PasswordChangeForm(request.user)
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance = profile)


    #return render(request, 'clubs\signup.html', {'form': form,'profile':profile})
    return render(request, 'clubs/user_profile.html',{'profile_form': profile_form,'user_form':user_form,'password_form':password_form,'usersClubs':usersClubs,'teams':teams, 
                                                      'is_admin':is_admin,'is_training_coordinator':is_training_coordinator, 'is_coach':is_coach, 'is_employee':is_employee})




def delete_profile(request):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request or None)
    user = request.user
    if request.method == 'POST':
        user.delete()
        return redirect(user_panel)
    return render(request,'clubs/confirm.html',{'user':user,'usersClubs':usersClubs,'teams':teams})

def create_club(request):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    form = ClubCreationForm(request.POST or None)
    if form.is_valid():
        user = request.user
        club = form.save()
        users_club = UsersClub(club = club,user = user, admin = True, accepted = True)
        users_club.save()
        return redirect(club_panel,club.id)
    return render(request,'clubs/create_club.html',{'form':form,'usersClubs':usersClubs,'teams':teams})

def club_settings(request, club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    

    clubs_teams = Team.objects.filter(club=club)
    seasons = Season.objects.filter(team__in=clubs_teams,active=True)
    coaching_staff = TeamsCoaching_Staff.objects.filter(team__in=clubs_teams, leaving_date=None).order_by('coach')

    #attendance
    seasons_att = []
    for s in seasons:
        trainings = Training.objects.filter(season=s,start_datatime__range=[s.date_of_start, date.today()])
        attendances = Attendance.objects.filter(training__in = trainings)
        present = 0
        len_attendance=0
        for att in attendances:
            if att.training.end_datatime < datetime.now():
                len_attendance += 1
                if att.present:
                    present += 1
        if len_attendance==0:
            avg_attendance = 0.00
        else:
            avg_attendance = round(present / len_attendance * 100,2)
        absent = 100-avg_attendance
        seasons_att.append((s,avg_attendance,absent))

    allowed = False
    for usersClub in usersClubs:
        if usersClub.club == club:
            if usersClub.admin == True or usersClub.coach or usersClub.training_coordinator:
                allowed=True

    if allowed:
        users = UsersClub.objects.filter(club = club, accepted=True)
        form = ClubCreationForm(request.POST or None, instance = club)
        if request.method == 'POST':
            if form.is_valid():
                club = form.save()
                return redirect(club_settings, club.id)
            else:
                messages.error(request, 'Błąd')
        return render(request,'clubs/club_settings.html',{'clubs_teams':clubs_teams, 'seasons_att':seasons_att,'coaching_staff':coaching_staff,'form':form,'usersClubs':usersClubs,'teams':teams,'club':club,'users':users,'seasons':seasons})
    else:
        return render(request, 'clubs/lack_of_access.html',{'usersClubs':usersClubs,'teams':teams})

def delete_club(request,club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    role = UsersClub.objects.filter(club=club, user=request.user).first()
    if role.admin == False:
        return render(request, 'clubs/lack_of_access.html',{'usersClubs':usersClubs,'teams':teams})
    if request.method == 'POST':
        club.delete()
        return redirect(user_panel)
    return render(request,'clubs/confirm_club.html',{'club':club,'usersClubs':usersClubs,'teams':teams})

def roles_in_club(request,club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    role = UsersClub.objects.filter(club=club, user=request.user).first()
    club_teams = Team.objects.filter(club=club)
    print(club_teams)
    if role.admin == False:
        return render(request, 'clubs/lack_of_access.html',{'usersClubs':usersClubs,'teams':teams})
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
                    if not user.coach:
                        user_in_teams = TeamsCoaching_Staff.objects.filter(team__in = club_teams, leaving_date=None, coach_id=user.user.id)
                        for u in user_in_teams:
                            u.leaving_date = date.today()
                            u.save()
                else:
                    user_in_teams = TeamsCoaching_Staff.objects.filter(team__in = club_teams, leaving_date=None, coach_id=user.user.id)
                    for u in user_in_teams:
                        u.leaving_date = date.today()
                        u.save()
                    user.delete()
        else:
            return redirect(roles_in_club,club.id)

        return redirect(club_settings, club.id)
    return render(request,'clubs/roles_in_club.html',{'club':club,'usersClubs':usersClubs,'teams':teams,'users':users})

def add_user_to_club(request,club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    role = UsersClub.objects.filter(club=club, user=request.user).first()
    if role.admin == False:
        return render(request, 'clubs/lack_of_access.html',{'usersClubs':usersClubs,'teams':teams})
    if request.method == 'POST':
        form = UsersClubForm(club, request.POST)
        if form.is_valid():
            user = form.cleaned_data['email'] 
            admin = form.cleaned_data['admin']
            coach = form.cleaned_data['coach']
            employee = form.cleaned_data['employee']
            training_coordinator = form.cleaned_data['training_coordinator']

            users_club,created = UsersClub.objects.get_or_create(user=user, club=club)

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

    return render(request,'clubs/add_user_to_club.html',{'club':club,'usersClubs':usersClubs,'teams':teams,'form':form})

def user_roles(request):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    usersClubs_roles = UsersClub.objects.filter(user = request.user)
    return render(request,'clubs/user_roles.html',{'usersClubs':usersClubs,'teams':teams,'usersClubs_roles':usersClubs_roles})

def user_role_delete(request, club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    club = get_object_or_404(Club, pk = club_id)
    users = UsersClub.objects.filter(club = club)
    for user in users: 
        if user.admin == True and user.user != request.user:
            if user.accepted==True:
                usersclub = UsersClub.objects.filter(user = request.user, club=club)
                usersclub.delete()

    return redirect(user_roles)
def user_role_answer(request, club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
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
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club, pk = club_id)
    if request.method == 'POST':
        team_form = TeamCreateForm(request.POST or None,club=club)
        season_form = SeasonCreateForm(request.POST or None)
        if team_form.is_valid() and season_form.is_valid():
            team = team_form.save(commit=False)
            team.club = club
            team.save()
            season = season_form.save(team=team)
            season.save()
            return redirect(club_settings, club.id)
    else:
        team_form = TeamCreateForm()
        season_form = SeasonCreateForm()
    return render(request,'clubs/create_team.html',{'club':club,'usersClubs':usersClubs,
        'teams':teams,'team_form':team_form, 'season_form':season_form})

def delete_team(request, team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team,pk=team_id)
    club = team.club
    if request.method == 'POST':
        team.delete()
        return redirect(club_settings,club.id)
    return render(request,'clubs/confirm_team.html',{'team':team,'club':club,'usersClubs':usersClubs,'teams':teams})

def edit_team(request, team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)

    team = get_object_or_404(Team,pk=team_id)
    seasons = Season.objects.filter(team=team).order_by('-date_of_start')
    club = team.club
    active_season = Season.objects.filter(team=team, active=True).first()
    team_form = TeamCreateForm(request.POST or None, instance=team,club = club)
    season_form = SeasonChooseForm(request.POST or None, team=team, active_season=active_season)
    if request.method == 'POST':
        if "data-submit" in request.POST:
            if team_form.is_valid():
                team = team_form.save()
                if season_form.is_valid():
                    selected_season_id = request.POST.get('active_season')
                    if selected_season_id:
                        Season.objects.filter(team=team).exclude(id=selected_season_id).update(active=False)
                        season = get_object_or_404(Season,pk=selected_season_id)
                        season.active = True
                        season.save()
                return redirect(edit_team,team.id)

    return render(request,'clubs/edit_team.html',{'club':club,'usersClubs':usersClubs,
        'teams':teams,'team_form':team_form, 'season_form':season_form, 'team':team, 'seasons':seasons})

def club_staff(request, club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    players = Player.objects.filter(club=club)
    teams = Team.objects.filter(club = club)
    seasons = Season.objects.filter(team__in = teams, active = True)
    show_hidden = request.GET.get('show_hidden', False) == 'on'

    return render(request,'clubs/club_staff.html',{'club':club,'teams':teams,'usersClubs':usersClubs, 'players':players, 'seasons':seasons,'show_hidden':show_hidden})

def create_player(request, club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    player_form = CreatePlayerForm(request.POST or None)
    player_data_form = CreatePlayerDataForm(request.POST or None)
    if request.method == 'POST':
        if player_form.is_valid():
            print('dane')
            player = player_form.save(commit=False)
            player.club = club
            player.save()
        if player_data_form.is_valid():
            print('profil')
            player_data = player_data_form.save(commit=False)
            player_data.player = player
            player_data.save()
        return redirect(club_staff, club.id)
    return render(request,'clubs/create_player.html',{'club':club,'teams':teams,'usersClubs':usersClubs, 'player_form':player_form,'player_data_form':player_data_form, 'edit':False})

def team_staff(request, team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team,pk=team_id)
    season = Season.objects.filter(team = team, active = True).first()
    if season:
        players = season.player.all()
    else:
        players = []
    return render(request,'clubs/team_staff.html',{'teams':teams,'usersClubs':usersClubs, 'players':players,'team':team, 'season':season})

def add_player(request, team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team,pk=team_id)
    players = Player.objects.filter(club=team.club)
    season = Season.objects.filter(team = team, active = True).first()    
    if season:
        players_in_team = season.player.all()
    else:
        players_in_team = []
    player_form = CreatePlayerForm(request.POST or None)
    player_data_form = CreatePlayerDataForm(request.POST or None)
    if request.method == 'POST':
        if 'add-players' in request.POST:
            selected_players_ids = request.POST.getlist('selected_players')
            for player_id in selected_players_ids:
                player = get_object_or_404(Player, pk=player_id)
                season.player.add(player)
        if 'create-player' in request.POST:
            if player_form.is_valid():
                player = player_form.save(commit=False)
                player.club = team.club
                player.save()
                player_form = CreatePlayerForm(None)
            if player_data_form.is_valid():
                player_data = player_data_form.save(commit=False)
                player_data.player = player
                player_data.save()
                player_data_form = CreatePlayerDataForm(None)
            season.player.add(player)
            return redirect(team_staff, team.id)
            
    return render(request,'clubs/add_player.html',{'club':team.club, 'players_in_team':players_in_team,'teams':teams,'usersClubs':usersClubs,'players':players, 'player_form':player_form,'player_data_form':player_data_form,'team':team})
def delete_player_from_club(request, player_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    player = get_object_or_404(Player,pk = player_id)
    club = player.club
    usersClubs, teams = get_data_for_menu(request)
    if request.method == 'POST':
        player.delete()
        return redirect(club_staff, club.id)
    return render(request, 'clubs/confirm_player_from_club.html', {'teams':teams, 'usersClubs':usersClubs,'player':player}) 

def hide_player_in_club(request, player_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    player = get_object_or_404(Player,pk = player_id)
    club = player.club
    player.hidden = not player.hidden
    player.save()
    return redirect(club_staff, club.id)


def delete_player_from_team(request, season_id, player_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    player = get_object_or_404(Player, pk = player_id)
    season = get_object_or_404(Season, pk=season_id)
    season.player.remove(player)
    
    return redirect(team_staff, season.team.id)


def club_coaching_staff(request, club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club, pk=club_id)
    coaches = UsersClub.objects.filter(club=club, coach=True)
    club_teams = Team.objects.filter(club=club)
    roles_in_teams = TeamsCoaching_Staff.objects.filter(team__in=club_teams,leaving_date=None)
    print(roles_in_teams)
    return render(request,'clubs/club_coaching_staff.html',{'teams':teams,'usersClubs':usersClubs, 'club':club, 'coaches':coaches,'roles_in_teams':roles_in_teams})


def team_coaching_staff(request, team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team, pk=team_id)
    team_coaches = TeamsCoaching_Staff.objects.filter(team=team,leaving_date=None).order_by('takeover_date')
    team_historical_coaches = TeamsCoaching_Staff.objects.filter(team=team, leaving_date__isnull=False).order_by('-leaving_date')
    coaches = UsersClub.objects.filter(club=team.club, coach=True, accepted=True)
    coaches_in_team = TeamsCoaching_Staff.objects.filter(team=team,leaving_date=None)
    coaches_not_in_team = coaches.exclude(user__in=coaches_in_team.values('coach'))
    form = AddCoachToTeam(coaches_not_in_team, request.POST or None)
    if request.method == 'POST':
        form.save(team=team)
        return redirect(team_coaching_staff,team.id)   
         

    return render(request,'clubs/team_coaching_staff.html',{'team_historical_coaches':team_historical_coaches,'teams':teams,'usersClubs':usersClubs,'form':form, 'team_coaches':team_coaches,'team':team})

def edit_team_coaching_staff(request, team_id, coach_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team, pk=team_id)
    coach = get_object_or_404(TeamsCoaching_Staff, team=team, leaving_date=None, coach_id=coach_id)
    r = coach.role_in_team
    take_ovr = coach.takeover_date
    form = EditCoachInTeam(instance=coach)
    if request.method == 'POST':
        if "edit-role" in request.POST:
            form = EditCoachInTeam(request.POST, instance=coach)
            if form.is_valid():
                role = form.cleaned_data['role_in_team']
                takeover_date = form.cleaned_data['takeover_date']
                if role != r:
                    if take_ovr != takeover_date:
                        if takeover_date > take_ovr:
                            coach.leaving_date = takeover_date
                            coach.role_in_team = r
                            coach.takeover_date = take_ovr
                            coach.save()
                            new_role = TeamsCoaching_Staff(coach=coach.coach, team=coach.team, takeover_date=takeover_date,  role_in_team=role)
                            new_role.save()
                        else:
                            coach.role_in_team = role
                            coach.takeover_date = takeover_date
                            coach.save()
                    else:
                        coach.role_in_team = role
                        coach.takeover_date = takeover_date
                        coach.save()
                else:
                    coach.takeover_date = takeover_date
                    coach.save()
                return redirect(team_coaching_staff,team.id)
    return render(request,'clubs/edit_team_coaching_staff.html',{'teams':teams,'usersClubs':usersClubs, 'team':team, 'form':form, 'coach':coach})


def delete_coach_from_team(request, team_id, coach_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team, pk=team_id)
    coach = get_object_or_404(TeamsCoaching_Staff, team=team, leaving_date=None, coach_id=coach_id)

    if request.method == 'POST':
        coach.leaving_date = date.today()
        coach.save()
        return redirect(team_coaching_staff,team.id)  
    else:
        return render(request, 'clubs/confirm_coach_from_team.html', {'teams':teams, 'usersClubs':usersClubs,'coach':coach, 'team':team}) 


# def add_coach_to_team(request, team_id):
#     usersClubs, teams = get_data_for_menu(request)
#     team = get_object_or_404(Team, pk=team_id)
#     coaches = UsersClub.objects.filter(club=team.club, coach=True, accepted = True)
#     coaches_in_team = TeamsCoaching_Staff.objects.filter(team=team,leaving_date=None)
#     coaches_not_in_team = coaches.exclude(user__in=coaches_in_team.values('coach'))
#     form = AddCoachToTeam(coaches_not_in_team, request.POST or None)
#     if request.method == 'POST':
#         form.save(team=team)
#         return redirect(team_coaching_staff,team.id)
#     return render(request,'clubs/add_coach_to_team.html',{'teams':teams,'usersClubs':usersClubs, 'team':team, 'form':form})

def add_season(request, team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team, pk=team_id)
    form = SeasonCreateForm(request.POST or None,team=team)
    if request.method == 'POST':
        if form.is_valid():
            form.save(team)
            return redirect(edit_team, team.id)
    return render(request,'clubs/create_season.html',{'teams':teams,'usersClubs':usersClubs, 'team':team, 'season_form':form,'edit':False})

def edit_active_season(request, team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team, pk=team_id)
    season = Season.objects.filter(team=team, active = True).first()
    print(season,"ads")
    form = SeasonCreateForm(request.POST or None, instance=season, team=team)
    if request.method == 'POST':
        if form.is_valid():
            season = form.save(team)
            return redirect(edit_team,team.id)
    return render(request,'clubs/create_season.html',{'teams':teams,'usersClubs':usersClubs, 'team':team, 'season_form':form, 'edit':True})

def edit_player(request, player_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    player = get_object_or_404(Player,pk=player_id)
    player_form = CreatePlayerForm(request.POST or None, instance=player)
    player_data = get_object_or_404(Player_data, player=player)
    player_data_form = CreatePlayerDataForm(request.POST or None, instance=player_data)
    print(player_data.date_of_birth)
    if request.method == 'POST':
        if player_form.is_valid():
            player.save()
            if player_data_form.is_valid():
                player_data.save()
                return redirect(club_staff, player.club.id)
    return render(request,'clubs/create_player.html',{'club':player.club,'teams':teams,'usersClubs':usersClubs, 'player_form':player_form,'player_data_form':player_data_form, 'edit':True})


def clubs_equipment(request, club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club, pk=club_id)
    equipment = Equipment.objects.filter(club=club)
    return render(request,'clubs/equipment.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'equipment':equipment})

def create_equipment(request, club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club, pk=club_id)
    form = CreateEquipment(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save(club=club)
            return redirect(clubs_equipment, club.id)
    return render(request,'clubs/create_equipment.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'form':form})



def edit_equipment(request, item_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    item = get_object_or_404(Equipment, pk=item_id)
    club = get_object_or_404(Club, pk=item.club.id)
    form = CreateEquipment(request.POST or None, instance= item)
    if request.method == 'POST':
        if form.is_valid():
            form.save(club=club)
            return redirect(clubs_equipment, club.id)
    return render(request,'clubs/create_equipment.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'form':form, 'edit':True})

def delete_equipment(request, item_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    item = get_object_or_404(Equipment, pk=item_id)
    club = get_object_or_404(Club, pk=item.club.id)
    if request.method == 'POST':
        item.delete()
        return redirect(clubs_equipment, club.id)
    return render(request,'clubs/confirm_equipment.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'item':item})

def rent_equipment(request, item_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    item = get_object_or_404(Equipment, pk=item_id)
    club = item.club
    form = RentEquipmentForm(club, item, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save(item)
            form = RentEquipmentForm(club, None)
    return render(request,'clubs/rent_equipment.html',{'teams':teams,'usersClubs':usersClubs, 'club':club, 'form':form})

def rented_equipment(request, item_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    item = get_object_or_404(Equipment, pk=item_id)
    equipment_holders = Rented_equipment.objects.filter(equipment = item, date_of_return = None)
    historical_holders = Rented_equipment.objects.filter(equipment = item, date_of_return__isnull=False)
    sum = 0
    for holder in equipment_holders:
        sum += holder.quantity
    rest = item.all_quantity - sum
    return render(request,'clubs/rented_equipment.html',{'teams':teams,'usersClubs':usersClubs, 'item':item, 'equipment_holders':equipment_holders, 'historical_holders':historical_holders,'sum':sum, 'rest':rest})

def return_equipment(request, rent_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    rent = get_object_or_404(Rented_equipment,pk=rent_id)
    rent.date_of_return = date.today()
    rent.save()
    return redirect(rented_equipment, rent.equipment.id)

def players_equipment(request, player_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    player = get_object_or_404(Player, pk = player_id)
    items = Rented_equipment.objects.filter(player=player, date_of_return__isnull=True)

    return render(request, 'clubs/players_equipment.html',{'usersClubs':usersClubs, 'teams':teams, 'items':items})

def teams_equipment(request, team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team, pk=team_id)
    season = Season.objects.filter(team = team, active = True).first()
    if season:
        players = season.player.all()
    else:
        players = []
    rented_equipments = Rented_equipment.objects.filter(player__in=players, date_of_return__isnull=True)
    player_counts = defaultdict(int)

    for rent in rented_equipments:
        player_counts[rent.player.id] += 1
    for player in players:
        if player_counts[player.id] == 0:
            player_counts[player.id] += 1

    player_counts_dict = dict(player_counts)



    return render(request,'clubs/teams_equipment.html',{'team':team,'teams':teams,'usersClubs':usersClubs,'rented_equipments':rented_equipments,'players':players,'player_counts_dict':player_counts_dict})

def places(request, club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    places = Place.objects.filter(club=club)

    return render(request,'clubs/places.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'places':places})

def create_place(request, club_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    form = PlaceForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save(club=club)
        return redirect(places, club.id)
    return render(request,'clubs/create_place.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'form':form})

def delete_place(request, place_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    place = get_object_or_404(Place, pk=place_id)
    club = get_object_or_404(Club, pk=place.club.id)
    if request.method == 'POST':
        place.delete()
        return redirect(places, club.id)
    return render(request,'clubs/confirm_place.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'place':place})

def edit_place(request,place_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    place = get_object_or_404(Place, pk=place_id)
    club = get_object_or_404(Club,pk=place.club.id)
    form = PlaceForm(request.POST or None, instance=place)
    if request.method == 'POST':
        if form.is_valid():
            form.save(club=club)
        return redirect(places, club.id)
    return render(request,'clubs/create_place.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'form':form,'edit':True})

def place_details(request, place_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    place = get_object_or_404(Place, pk=place_id)
    club = get_object_or_404(Club,pk=place.club.id)
    form = PlaceForm(request.POST or None, instance=place)
    for field_name in form.fields:
        form.fields[field_name].widget.attrs['disabled'] = True
    
    return render(request,'clubs/create_place.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'form':form,'details':True})

def trainings(request, team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team,pk=team_id)
    season = Season.objects.filter(team=team, active=True).first()
    schedueled_trainings = Training.objects.filter(season=season).order_by('-start_datatime')
    finished_trainings = [training for training in schedueled_trainings if training.end_datatime < datetime.now()]
    finished_training_ids = [training.id for training in finished_trainings]
    schedueled_trainings = schedueled_trainings.exclude(id__in=finished_training_ids).order_by('start_datatime')

    return render(request,'clubs/trainings.html',{'teams':teams,'usersClubs':usersClubs,'team':team, 'schedueled_trainings':schedueled_trainings, 'finished_trainings':finished_trainings})

def add_training(request,team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team,pk=team_id)
    season = Season.objects.filter(team=team, active=True).first()
    players = season.player.all().order_by('surname')
    form = TrainingForm(request.POST or None, players = players, season=season)
    if request.method =='POST':
        if form.is_valid():
            form.save()
            return redirect(trainings,season.team.id)
    return render(request,'clubs/create_training.html',{'teams':teams,'usersClubs':usersClubs,'team':team, 'form':form})

def edit_training(request,training_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    training = get_object_or_404(Training,pk=training_id)
    team = get_object_or_404(Team,pk=training.season.team.id)
    season = get_object_or_404(Season,pk=training.season.id)
    players = season.player.all()
    form = TrainingForm(request.POST or None, players = players, season=season, instance=training)
    if request.method =='POST':
        if form.is_valid():
            form.save()
            return redirect(trainings,season.team.id)
    return render(request,'clubs/create_training.html',{'teams':teams,'usersClubs':usersClubs,'team':team, 'form':form,'edit':True})

def training_details(request,training_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    training = get_object_or_404(Training,pk=training_id)
    team = get_object_or_404(Team,pk=training.season.team.id)
    season = get_object_or_404(Season,pk=training.season.id)
    players = season.player.all()
    form = TrainingForm(request.POST or None, players = players, season=season, instance=training)
    for field_name in form.fields:
        form.fields[field_name].widget.attrs['disabled'] = True
    return render(request,'clubs/create_training.html',{'teams':teams,'usersClubs':usersClubs,'team':team, 'form':form,'details':True})

def delete_training(request,training_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    training = get_object_or_404(Training,pk=training_id)
    team = get_object_or_404(Team,pk=training.season.team.id)
    if request.method == 'POST':
        training.delete()
        return redirect(trainings, team.id)
    return render(request,'clubs/confirm_training.html',{'teams':teams,'usersClubs':usersClubs,'team':team,'training':training})

def training_attendance(request, training_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    training = get_object_or_404(Training, pk=training_id)
    attendance = Attendance.objects.filter(training=training).order_by('player__surname')
    forms_list = []
    for att in attendance:
        form = AttendanceForm(request.POST or None, instance=att, prefix=str(att.player.id))
        forms_list.append((att, form))
    if request.method == 'POST':
        # Przetwarzanie formularzy po kliknięciu przycisku "Zapisz"
        for att, form in forms_list:
            form = AttendanceForm(request.POST, instance=att, prefix=str(att.player.id))
            if form.is_valid():
                form.save()

        # Przekierowanie gdziekolwiek chcesz po zapisaniu danych
        return redirect(trainings,training.season.team.id)
    return render(request, 'clubs/training_attendance.html', {'teams': teams, 'usersClubs': usersClubs, 'attendance': attendance, 'training': training, 'forms_list': forms_list})

def training_attendance_report(request, training_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    training = get_object_or_404(Training, pk=training_id)
    attendance = Attendance.objects.filter(training=training).order_by('player')
    present = 0
    for att in attendance:
        if att.present:
            present += 1
    if len(attendance) != 0:
        avg_attendance = round(present / len(attendance) *100,2)
    else: 
        avg_attendance = 0
    return render(request, 'clubs/training_attendance_report.html', {'teams': teams, 'usersClubs': usersClubs,'attendance':attendance, 'training': training,'avg_attendance':avg_attendance})

def team_attendance_report(request,team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team,pk=team_id)
    season = Season.objects.filter(team = team, active = True).first()
    attendance_filter = AttendanceReportFilter(request.GET or None, season = season)
    if attendance_filter.is_valid():
        start_date = attendance_filter.cleaned_data.get('start_date')
        end_date = attendance_filter.cleaned_data.get('end_date')
        end_date += timedelta(days=1)
    else:
        start_date = season.date_of_start
        end_date = season.date_of_end
        end_date += timedelta(days=1)

    trainings = Training.objects.filter(season=season,start_datatime__range=[start_date, end_date]).order_by('start_datatime')
    attendances = Attendance.objects.filter(training__in = trainings,)
    if season:
        players = season.player.all().order_by('surname')
    else:
        players = []
    players_att = {p.id: 0 for p in players}
    players_presents = {p.id: 0 for p in players}
    present = 0
    len_attendance = 0

    for att in attendances:
        if att.training.end_datatime < datetime.now():
            len_attendance += 1
            if att.present:
                present += 1
            for p in players:
                if p.id == att.player.id:
                        players_att[p.id]+=1
                        if att.present:
                            players_presents[p.id]+=1
    players_avg = {p_id: round(players_presents[p_id] / players_att[p_id] * 100,2) if players_att[p_id] > 0 else 0 for p_id in players_att}
    
    if len_attendance==0:
        avg_attendance = 0.00
    else:
        avg_attendance = round(present / len_attendance * 100,2)


    return render(request,'clubs/team_attendance_report.html',{'attendance_filter':attendance_filter, 'players_avg':players_avg,'avg_attendance':avg_attendance,'teams':teams,'usersClubs':usersClubs,'players':players,'trainings':trainings, 'team':team,'attendances':attendances, 'season':season})


def player_attendance_report(request, season_id, player_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    player = get_object_or_404(Player,pk=player_id)
    season = get_object_or_404(Season,pk=season_id)
    team = season.team
    attendance_filter = AttendanceReportFilter(request.GET or None, season = season)
    if attendance_filter.is_valid():
        start_date = attendance_filter.cleaned_data.get('start_date')
        end_date = attendance_filter.cleaned_data.get('end_date')
        end_date += timedelta(days=1)
    else:
        start_date = season.date_of_start
        end_date = season.date_of_end
        end_date += timedelta(days=1)
    trainings = Training.objects.filter(season=season,start_datatime__range=[start_date, end_date]).order_by('start_datatime')
    attendances = Attendance.objects.filter(training__in = trainings, player = player)
    present = 0
    len_attendance = 0
    for att in attendances:
        if att.training.end_datatime < datetime.now():
            len_attendance +=1
            if att.present:
                present += 1
    if len_attendance ==0:
        avg_attendance = 0.00
    else:
        avg_attendance = round(present / len_attendance *100,2)

    return render(request,'clubs/player_attendance_report.html',{'attendance_filter':attendance_filter, 'avg_attendance':avg_attendance,'teams':teams,'usersClubs':usersClubs,'player':player,'trainings':trainings, 'team':team,'attendances':attendances, 'season':season})


def mezocycles(request,team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team,pk = team_id)
    mezocycles = Mezocycle.objects.filter(Q(team=team)).order_by('id')
    implemented_mezocycles = ImplementedMezocycle.objects.filter(team=team ).order_by('id')
    return render(request,'clubs/mezocycles.html',{'teams':teams,'usersClubs':usersClubs, 'team':team, 'mezocycles':mezocycles,'implemented_mezocycles':implemented_mezocycles})

def create_mezocycle(request, team_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    print(request.POST)

    class Training_in_week:
        def __init__(self, week, training):
            self.week = week
            self.training = training

    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team,pk = team_id)
    user = request.user
    mezocycle_form = MezocycleForm(request.POST or None,team=team)
    weeks = 0
    trainings_per_week = 0
    mezocycle_set = False
    forms_list = []
    for_w = []
    for_t = []
    

    if request.method == 'POST':
        if 'mezocycle' in request.POST:
            if mezocycle_form.is_valid():
                weeks = mezocycle_form.cleaned_data.get('weeks')
                trainings_per_week = mezocycle_form.cleaned_data.get('trainings_per_week')
                mezocycle_set = True
                for_w = range(1, weeks + 1)
                for_t = range(1, trainings_per_week + 1)
                for_wt = list(product(for_w, for_t))
                for w,t in for_wt:
                    form = Training_in_mezocycleForm(request.POST or None,initial={'topic':'ee','duration':3}, prefix=(str(w)+'_'+str(t)))
                    wt = Training_in_week(w,t)
                    forms_list.append((wt,form))
                    
        if 'mezocycle_details' in request.POST:
            if mezocycle_form.is_valid():
                weeks = mezocycle_form.cleaned_data.get('weeks')
                trainings_per_week = mezocycle_form.cleaned_data.get('trainings_per_week')
                mezocycle_set = True
                for_w = range(1, weeks + 1)
                for_t = range(1, trainings_per_week + 1)
                for_wt = list(product(for_w, for_t))
                for w,t in for_wt:
                    form = Training_in_mezocycleForm(request.POST or None,initial={'topic':'ee','duration':3}, prefix=(str(w)+'_'+str(t)))
                    wt = Training_in_week(w,t)
                    forms_list.append((wt,form))

            all_forms_valid = True
            for wt, form in forms_list:
                if not form.is_valid():
                    print("brak walidacji")
                    all_forms_valid=False

            if all_forms_valid:
                if mezocycle_form.is_valid():
                    mezocycle = mezocycle_form.save(commit=False)
                    mezocycle.user = user
                    mezocycle.team = team
                    mezocycle.save()
                    
                    for_w = range(1, mezocycle.weeks + 1)
                    for_t = range(1, mezocycle.trainings_per_week + 1)
                    for_wt = list(product(for_w, for_t))

                    for w,t in for_wt:
                        training_in_mezocycle = Training_in_mezocycle()
                        training_in_mezocycle.topic = request.POST.get(str(w)+'_'+str(t)+"-topic", "")
                        training_in_mezocycle.week_number = request.POST.get(str(w)+'_'+str(t)+"-week_number", "")
                        training_in_mezocycle.training_number = request.POST.get(str(w)+'_'+str(t)+"-training_number", "")
                        training_in_mezocycle.goals = request.POST.get(str(w)+'_'+str(t)+"-goals", "")
                        training_in_mezocycle.motoric_goals = request.POST.get(str(w)+'_'+str(t)+"-motoric_goals", "")
                        training_in_mezocycle.rules = request.POST.get(str(w)+'_'+str(t)+"-rules", "")
                        training_in_mezocycle.actions = request.POST.get(str(w)+'_'+str(t)+"-actions", "")
                        training_in_mezocycle.duration = request.POST.get(str(w)+'_'+str(t)+"-duration", "")
                        training_in_mezocycle.mezocycle = mezocycle
                        training_in_mezocycle.save()
                    return redirect(mezocycles,team.id)
    else:
        for_w = range(1, weeks + 1)
        for_t = range(1, trainings_per_week + 1)
        for_wt = list(product(for_w, for_t))
        print(request.POST)
        for w,t in for_wt:
            form = Training_in_mezocycleForm(request.POST or None,initial={'topic':'ee','duration':3}, prefix=(str(w)+'_'+str(t)))
            wt = Training_in_week(w,t)
            forms_list.append((wt,form))


    return render(request,'clubs/create_mezocycle.html',{'for_t':for_t,'for_w':for_w,'mezocycle_set':mezocycle_set,
                                                         'teams':teams,'usersClubs':usersClubs, 'team':team,'mezocycle_form':mezocycle_form,
                                                         'forms_list':forms_list,})


def edit_mezocycle(request, mezocycle_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    mezocycle = get_object_or_404(Mezocycle,pk = mezocycle_id)
    trainings = Training_in_mezocycle.objects.filter(mezocycle = mezocycle)
    mezocycle_form = MezocycleForm(request.POST or None, instance=mezocycle,team=mezocycle.team)
    for_w = []
    for_t = []
    forms_list=[]
    if request.method == 'POST':
        if 'mezocycle' in request.POST:
            if mezocycle_form.is_valid():
                mezocycle = mezocycle_form.save(commit=False)
            forms_list = []
            for_w = range(1, mezocycle.weeks + 1)
            for_t = range(1, mezocycle.trainings_per_week + 1)
            weeks = trainings.order_by('-week_number').first()
            tranings_per_week = trainings.order_by('-training_number').first()
            for w in for_w:
                for t in for_t:
                    for training in trainings:
                        if training.week_number == w and training.training_number == t:
                            form = Training_in_mezocycleForm(request.POST or None, instance=training, prefix=(str(training.week_number)+'_'+str(training.training_number)))
                            form.week_number = training.week_number
                            form.training_number =  training.training_number
                            forms_list.append(form)
                    if t > tranings_per_week.training_number or w > weeks.week_number:
                        form = Training_in_mezocycleForm(request.POST or None, initial={'topic':None,'duration':None}, prefix=(str(w)+'_'+str(t)))
                        form.week_number = w
                        form.training_number = t
                        forms_list.append(form)
        if 'mezocycle_details' in request.POST:
            if mezocycle_form.is_valid():
                mezocycle = mezocycle_form.save(commit=False)

                forms_list = []
                for_w = range(1, mezocycle.weeks + 1)
                for_t = range(1, mezocycle.trainings_per_week + 1)
                weeks = trainings.order_by('-week_number').first()
                tranings_per_week = trainings.order_by('-training_number').first()
                for w in for_w:
                    for t in for_t:
                        for training in trainings:
                            if training.week_number == w and training.training_number == t:
                                form = Training_in_mezocycleForm(request.POST or None, instance=training, prefix=(str(training.week_number)+'_'+str(training.training_number)))
                                form.week_number = training.week_number
                                form.training_number =  training.training_number
                                forms_list.append(form)
                        if t > tranings_per_week.training_number or w > weeks.week_number:
                            training_in_mezocycle = Training_in_mezocycle()
                            training_in_mezocycle.topic = request.POST.get(str(w)+'_'+str(t)+"-topic", "")
                            training_in_mezocycle.week_number = w
                            training_in_mezocycle.training_number = t
                            training_in_mezocycle.goals = request.POST.get(str(w)+'_'+str(t)+"-goals", "")
                            training_in_mezocycle.motoric_goals = request.POST.get(str(w)+'_'+str(t)+"-motoric_goals", "")
                            training_in_mezocycle.rules = request.POST.get(str(w)+'_'+str(t)+"-rules", "")
                            training_in_mezocycle.actions = request.POST.get(str(w)+'_'+str(t)+"-actions", "")
                            training_in_mezocycle.duration = request.POST.get(str(w)+'_'+str(t)+"-duration", "")
                            training_in_mezocycle.mezocycle = mezocycle
                            form = Training_in_mezocycleForm(request.POST or None, instance=training_in_mezocycle, prefix=(str(w)+'_'+str(t)))
                            form.week_number = w
                            form.training_number = t
                            forms_list.append(form)

                all_forms_valid = True
                for form in forms_list:
                    if not form.is_valid():
                        print("brak walidacji")
                        all_forms_valid=False

                if all_forms_valid:
                    for form in forms_list:
                        if form.is_valid():
                            form.save()
                    mezocycle.save()
                    for training in trainings:
                        if training.week_number not in for_w or training.training_number not in for_t:
                            training.delete()
                    return redirect(mezocycles,mezocycle.team.id)
    
        if 'mezocycle_copy' in request.POST:
            if mezocycle_form.is_valid():
                print('mezocykl form valid')
                mezocycle = mezocycle_form.save(commit=False)
            forms_list = []
            for_w = range(1, mezocycle.weeks + 1)
            for_t = range(1, mezocycle.trainings_per_week + 1)
            weeks = trainings.order_by('-week_number').first()
            tranings_per_week = trainings.order_by('-training_number').first()
            for w in for_w:
                for t in for_t:
                    for training in trainings:
                        if training.week_number == w and training.training_number == t:
                            form = Training_in_mezocycleForm(request.POST or None, instance=training, prefix=(str(training.week_number)+'_'+str(training.training_number)))
                            form.week_number = training.week_number
                            form.training_number =  training.training_number
                            forms_list.append(form)
                    if t > tranings_per_week.training_number or w > weeks.week_number:
                        training_in_mezocycle = Training_in_mezocycle()
                        training_in_mezocycle.topic = request.POST.get(str(w)+'_'+str(t)+"-topic", "")
                        training_in_mezocycle.week_number = w
                        training_in_mezocycle.training_number = t
                        training_in_mezocycle.goals = request.POST.get(str(w)+'_'+str(t)+"-goals", "")
                        training_in_mezocycle.motoric_goals = request.POST.get(str(w)+'_'+str(t)+"-motoric_goals", "")
                        training_in_mezocycle.rules = request.POST.get(str(w)+'_'+str(t)+"-rules", "")
                        training_in_mezocycle.actions = request.POST.get(str(w)+'_'+str(t)+"-actions", "")
                        training_in_mezocycle.duration = request.POST.get(str(w)+'_'+str(t)+"-duration", "")
                        training_in_mezocycle.mezocycle = mezocycle
                        form = Training_in_mezocycleForm(request.POST or None, instance=training_in_mezocycle, prefix=(str(w)+'_'+str(t)))
                        form.week_number = w
                        form.training_number =  t
                        forms_list.append(form)
            

            all_forms_valid = True
            for form in forms_list:
                if not form.is_valid():
                    print("brak walidacji")
                    all_forms_valid=False
            if all_forms_valid:
                def check_name(name,team):
                    name_not_awailable = Mezocycle.objects.filter(name=name, team=team)
                    if name_not_awailable:
                        name+="-kopia"
                        return check_name(name,team)
                    else:
                        return name
                n = check_name(mezocycle.name,mezocycle.team)
                new_mezocycle = Mezocycle(name=n, user=mezocycle.user, team=mezocycle.team, weeks=mezocycle.weeks, trainings_per_week=mezocycle.trainings_per_week)
                new_mezocycle.save()
                for form in forms_list:
                    if form.is_valid():
                        training = form.save(commit=False)
                        new_training = Training_in_mezocycle()
                        new_training.mezocycle = new_mezocycle
                        new_training.topic = training.topic
                        new_training.week_number = training.week_number
                        new_training.training_number = training.training_number
                        new_training.goals = training.goals
                        new_training.motoric_goals = training.motoric_goals
                        new_training.rules = training.rules
                        new_training.actions = training.actions
                        new_training.duration = training.duration
                        new_training.save()
                    else:
                        print('błąd walidacji')

                return redirect(mezocycles,mezocycle.team.id)

    else:  
        forms_list = []
        for_w = range(1, mezocycle.weeks + 1)
        for_t = range(1, mezocycle.trainings_per_week + 1)
        for training in trainings:
            #print(training)
            form = Training_in_mezocycleForm(request.POST or None, instance=training, prefix=(str(training.week_number)+'_'+str(training.training_number)))
            form.week_number = training.week_number
            form.training_number =  training.training_number
            forms_list.append(form)


    return render(request,'clubs/edit_mezocycle.html',{'mezocycle_form':mezocycle_form,'for_t':for_t,'for_w':for_w,'teams':teams, 'usersClubs':usersClubs, 'mezocycle':mezocycle,'forms_list':forms_list})

def delete_mezocycle(request, mezocycle_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    mezocycle = get_object_or_404(Mezocycle,pk = mezocycle_id)
    team = get_object_or_404(Team, pk=mezocycle.team.id)
    if request.method == 'POST':
        mezocycle.delete()
        return redirect(mezocycles, team.id)
    return render(request, 'clubs/confirm_mezocycle.html', {'teams':teams, 'usersClubs':usersClubs, 'mezocycle':mezocycle,}) 

def implement_mezocycle(request, mezocycle_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    mezocycle = get_object_or_404(Mezocycle,pk = mezocycle_id)
    team = mezocycle.team
    season = Season.objects.filter(team=team, active=True).first()
    trainings_in_mezocycle = Training_in_mezocycle.objects.filter(mezocycle=mezocycle)
    players = season.player.all()
    forms_list = []
    for_w = range(1, mezocycle.weeks + 1)
    for_t = range(1, mezocycle.trainings_per_week + 1)
    mezocycle_form = ImplementMezocycleForm(request.POST or None,team=team,initial={'weeks':mezocycle.weeks,'trainings_per_week':mezocycle.trainings_per_week,'name':mezocycle.name})
    mezocycle_form.fields['weeks'].required = False
    mezocycle_form.fields['trainings_per_week'].required = False
    mezocycle_form.fields['weeks'].widget = forms.HiddenInput()
    mezocycle_form.fields['trainings_per_week'].widget = forms.HiddenInput()
    for tr in trainings_in_mezocycle:
        training = Training(topic=tr.topic,actions=tr.actions,goals=tr.goals,rules=tr.rules, motoric_goals=tr.motoric_goals)
        form = ImplementTrainingForm(request.POST or None,initial={'topic':tr.topic,'actions':tr.actions,'motoric_goals':tr.motoric_goals,'goals':tr.goals,'rules':tr.rules,'duration':tr.duration}, players = players,season=season, prefix=(str(tr.week_number)+'_'+str(tr.training_number)))
        form.week_number = tr.week_number
        form.training_number =  tr.training_number
        forms_list.append(form) 
    
    if request.method =='POST':

        if 'trainings' in request.POST:
            all_forms_valid = True
            for form in forms_list:
                if form.is_valid():
                   pass
                else:
                    all_forms_valid=False
                    break
            if all_forms_valid:
                print(mezocycle_form)

                if mezocycle_form.is_valid():
                    implemented_mezocycle = mezocycle_form.save(commit=False)
                    implemented_mezocycle.team = team
                    implemented_mezocycle.save()
                    for form in forms_list:
                        if form.is_valid():
                            training = form.save()
                            training.implemented_mezocycle = implemented_mezocycle
                            training.save()
                        else:
                            print("błąd")
                    return redirect(trainings,season.team.id)
        
    return render(request,'clubs/implement_mezocycle.html',{'mezocycle_form':mezocycle_form,'for_t':for_t,'for_w':for_w,'teams':teams, 'usersClubs':usersClubs, 'mezocycle':mezocycle,'forms_list':forms_list})

def delete_implemented_mezocycle(request, mezocycle_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    mezocycle = get_object_or_404(ImplementedMezocycle,pk = mezocycle_id)
    trainings = Training.objects.filter(implemented_mezocycle=mezocycle)
    team = get_object_or_404(Team, pk=mezocycle.team.id)
    if request.method == 'POST':
        if 'mezocycle' in request.POST:
            mezocycle.delete()
        if 'trainings' in request.POST:
            for training in trainings:
                training.delete()
            mezocycle.delete()
        return redirect(mezocycles, team.id)
    return render(request, 'clubs/confirm_implemented_mezocycle.html', {'teams':teams, 'usersClubs':usersClubs, 'mezocycle':mezocycle,}) 

def review_implemented_mezocycle(request, mezocycle_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    usersClubs, teams = get_data_for_menu(request)
    mezocycle = get_object_or_404(ImplementedMezocycle,pk = mezocycle_id)
    trainings = Training.objects.filter(implemented_mezocycle=mezocycle).order_by('start_datatime')
    for_w = range(1, mezocycle.weeks + 1)
    for_t = range(1, mezocycle.trainings_per_week + 1)
    trainings_list=[]
    for w in for_w:
        for t in for_t:
            trainings_list.append(((w,t),trainings[0]))
            trainings = trainings[1:]

    return render(request,'clubs/review_implemented_mezocycle.html',{'for_t':for_t,'for_w':for_w,'teams':teams,'usersClubs':usersClubs,'mezocycle':mezocycle, 'team':mezocycle.team, 'trainings_list':trainings_list})

def pdf_view(request,mezocycle_id):
    if not request.user.is_authenticated:
        login = reverse('login')
        return redirect(login)
    mezocycle = get_object_or_404(ImplementedMezocycle,pk = mezocycle_id)
    trainings = Training.objects.filter(implemented_mezocycle=mezocycle).order_by('start_datatime')
    date_of_start_mezocycle = trainings.first().start_datatime.date()
    date_of_end_mezocycle = trainings.last().start_datatime.date()

    for_w = range(1, mezocycle.weeks + 1)
    for_t = range(1, mezocycle.trainings_per_week + 1)
    trainings_list=[]
    print(trainings)
    for w in for_w:
        for t in for_t:
            trainings_list.append(((w,t),trainings[0]))
            trainings = trainings[1:]

    response = render_to_pdf('pdf/mezocycle_report.html',{'date_of_end_mezocycle':date_of_end_mezocycle,'date_of_start_mezocycle':date_of_start_mezocycle,'for_t':for_t,'for_w':for_w,'mezocycle':mezocycle, 'team':mezocycle.team, 'trainings_list':trainings_list})
    response['Content-Type'] = 'application/pdf; charset=utf-8'
    return response
