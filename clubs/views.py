from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from .models import Equipment, Rented_equipment, TeamsCoaching_Staff, UsersClub, Club, Team, Profile, Season, Player, Player_data
from .forms import AddCoachToTeam, CreateEquipment, CreatePlayerDataForm, CreatePlayerForm, EditCoachInTeam, RentEquipmentForm, SignUpForm, ProfileForm, UserForm, ClubCreationForm, UsersClubForm, UserRoleAnswerForm, TeamCreateForm, SeasonCreateForm, SeasonChooseForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from datetime import date

def get_data_for_menu(request):
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
    usersClubs, teams = get_data_for_menu(request)

    return render(request,'clubs\\user_panel.html',{'usersClubs':usersClubs,'teams':teams})

def user_profile(request):
    usersClubs, teams = get_data_for_menu(request)

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
    usersClubs, teams = get_data_for_menu(request or None)
    user = request.user
    if request.method == 'POST':
        user.delete()
        return redirect(user_panel)
    return render(request,'clubs\\confirm.html',{'user':user,'usersClubs':usersClubs,'teams':teams})

def create_club(request):
    usersClubs, teams = get_data_for_menu(request)
    form = ClubCreationForm(request.POST or None)
    if form.is_valid():
        user = request.user
        club = form.save()
        users_club = UsersClub(club = club,user = user, admin = True, accepted = True)
        users_club.save()
        return redirect(user_panel)
    return render(request,'clubs\\create_club.html',{'form':form,'usersClubs':usersClubs,'teams':teams})

def club_settings(request, club_id):
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    seasons = Season.objects.filter(team__in=teams)
    allowed = False
    for usersClub in usersClubs:
        if usersClub.club == club:
            if usersClub.admin == True or usersClub.coach or usersClub.training_coordinator:
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
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    role = UsersClub.objects.filter(club=club, user=request.user).first()
    if role.admin == False:
        return render(request, 'clubs\\lack_of_access.html',{'usersClubs':usersClubs,'teams':teams})
    if request.method == 'POST':
        club.delete()
        return redirect(user_panel)
    return render(request,'clubs\\confirm_club.html',{'club':club,'usersClubs':usersClubs,'teams':teams})

def roles_in_club(request,club_id):
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    role = UsersClub.objects.filter(club=club, user=request.user).first()
    if role.admin == False:
        return render(request, 'clubs\\lack_of_access.html',{'usersClubs':usersClubs,'teams':teams})
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
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    role = UsersClub.objects.filter(club=club, user=request.user).first()
    if role.admin == False:
        return render(request, 'clubs\\lack_of_access.html',{'usersClubs':usersClubs,'teams':teams})
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
    usersClubs, teams = get_data_for_menu(request)
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
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club, pk = club_id)
    if request.method == 'POST':
        team_form = TeamCreateForm(request.POST or None)
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
    return render(request,'clubs\\create_team.html',{'club':club,'usersClubs':usersClubs,
        'teams':teams,'team_form':team_form, 'season_form':season_form})

def delete_team(request, team_id):
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team,pk=team_id)
    club = team.club
    if request.method == 'POST':
        team.delete()
        return redirect(club_settings,club.id)
    return render(request,'clubs\\confirm_team.html',{'team':team,'club':club,'usersClubs':usersClubs,'teams':teams})

def edit_team(request, team_id):
    usersClubs, teams = get_data_for_menu(request)

    team = get_object_or_404(Team,pk=team_id)
    seasons = Season.objects.filter(team=team).order_by('-date_of_start')
    club = team.club
    active_season = Season.objects.filter(team=team, active=True).first()
    season_form = SeasonChooseForm(request.POST or None, team=team, active_season=active_season)
    team_form = TeamCreateForm(request.POST or None, instance=team)
    if request.method == 'POST':
        if "data-submit" in request.POST:
            if team_form.is_valid:
                team = team_form.save()
            if season_form.is_valid:
                selected_season_id = request.POST.get('active_season')
                if selected_season_id:
                    Season.objects.filter(team=team).exclude(id=selected_season_id).update(active=False)
                    season = get_object_or_404(Season,pk=selected_season_id)
                    print(season)
                    season.active = True
                    season.save()
            return redirect(edit_team,team.id)

    return render(request,'clubs\\edit_team.html',{'club':club,'usersClubs':usersClubs,
        'teams':teams,'team_form':team_form, 'season_form':season_form, 'team':team, 'seasons':seasons})

def club_staff(request, club_id):
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    players = Player.objects.filter(club=club)
    teams = Team.objects.filter(club = club)
    seasons = Season.objects.filter(team__in = teams, active = True)
    show_hidden = request.GET.get('show_hidden', False) == 'on'

    return render(request,'clubs\\club_staff.html',{'club':club,'teams':teams,'usersClubs':usersClubs, 'players':players, 'seasons':seasons,'show_hidden':show_hidden})

def create_player(request, club_id):
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club,pk=club_id)
    player_form = CreatePlayerForm(request.POST or None)
    player_data_form = CreatePlayerDataForm(request.POST or None)
    if request.method == 'POST':
        if player_form.is_valid():
            player = player_form.save(commit=False)
            player.club = club
            player.save()
        if player_data_form.is_valid():
            player_data = player_data_form.save(commit=False)
            player_data.player = player
            player_data.save()
        return redirect(club_staff, club.id)
    return render(request,'clubs\\create_player.html',{'club':club,'teams':teams,'usersClubs':usersClubs, 'player_form':player_form,'player_data_form':player_data_form, 'edit':False})

def team_staff(request, team_id):
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team,pk=team_id)
    season = Season.objects.filter(team = team, active = True).first()
    if season:
        players = season.player.all()
    else:
        players = []
    return render(request,'clubs\\team_staff.html',{'teams':teams,'usersClubs':usersClubs, 'players':players,'team':team, 'season':season})

def add_player(request, team_id):
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
            
    return render(request,'clubs\\add_player.html',{'club':team.club, 'players_in_team':players_in_team,'teams':teams,'usersClubs':usersClubs,'players':players, 'player_form':player_form,'player_data_form':player_data_form,'team':team})
def delete_player_from_club(request, player_id):
    player = get_object_or_404(Player,pk = player_id)
    club = player.club
    player.delete()
    return redirect(club_staff, club.id)

def hide_player_in_club(request, player_id):
    player = get_object_or_404(Player,pk = player_id)
    club = player.club
    player.hidden = not player.hidden
    player.save()
    return redirect(club_staff, club.id)


def delete_player_from_team(request, season_id, player_id):
    player = get_object_or_404(Player, pk = player_id)
    season = get_object_or_404(Season, pk=season_id)
    season.player.remove(player)
    
    return redirect(team_staff, season.team.id)


def club_coaching_staff(request, club_id):
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club, pk=club_id)
    coaches = UsersClub.objects.filter(club=club, coach=True)
    club_teams = Team.objects.filter(club=club)
    roles_in_teams = TeamsCoaching_Staff.objects.filter(team__in=club_teams,leaving_date=None)
    print(roles_in_teams)
    return render(request,'clubs\\club_coaching_staff.html',{'teams':teams,'usersClubs':usersClubs, 'club':club, 'coaches':coaches,'roles_in_teams':roles_in_teams})


def team_coaching_staff(request, team_id):
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team, pk=team_id)
    coaches = TeamsCoaching_Staff.objects.filter(team=team,leaving_date=None)

    return render(request,'clubs\\team_coaching_staff.html',{'teams':teams,'usersClubs':usersClubs, 'coaches':coaches,'team':team})

def edit_team_coaching_staff(request, team_id, coach_id):
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
                    coach.leaving_date = date.today()
                    coach.role_in_team = r
                    coach.takeover_date = take_ovr
                    coach.save()
                    new_role = TeamsCoaching_Staff(coach=coach.coach, team=coach.team, takeover_date=takeover_date,  role_in_team=role)
                    new_role.save()
                else:
                    coach.takeover_date = takeover_date
                    coach.save()
                return redirect(team_coaching_staff,team.id)
        if "delete-role" in request.POST:
            coach.leaving_date = date.today()
            coach.save()
            return redirect(team_coaching_staff,team.id)
    return render(request,'clubs\\edit_team_coaching_staff.html',{'teams':teams,'usersClubs':usersClubs, 'team':team, 'form':form, 'coach':coach})

def add_coach_to_team(request, team_id):
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team, pk=team_id)
    coaches = UsersClub.objects.filter(club=team.club, coach=True)
    coaches_in_team = TeamsCoaching_Staff.objects.filter(team=team,leaving_date=None)
    coaches_not_in_team = coaches.exclude(user__in=coaches_in_team.values('coach'))
    form = AddCoachToTeam(coaches_not_in_team, request.POST or None)
    if request.method == 'POST':
        form.save(team=team)
        return redirect(team_coaching_staff,team.id)
    return render(request,'clubs\\add_coach_to_team.html',{'teams':teams,'usersClubs':usersClubs, 'team':team, 'form':form})

def add_season(request, team_id):
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team, pk=team_id)
    form = SeasonCreateForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save(team)
            return redirect(edit_team, team.id)
    return render(request,'clubs\\create_season.html',{'teams':teams,'usersClubs':usersClubs, 'team':team, 'form':form,'edit':False})

def edit_active_season(request, team_id):
    usersClubs, teams = get_data_for_menu(request)
    team = get_object_or_404(Team, pk=team_id)
    season = Season.objects.filter(team=team, active = True).first()
    form = SeasonCreateForm(request.POST or None, instance=season)
    if request.method == 'POST':
        if form.is_valid():
            season = form.save(team)
            return redirect(edit_team,team.id)
    return render(request,'clubs\\create_season.html',{'teams':teams,'usersClubs':usersClubs, 'team':team, 'form':form, 'edit':True})

def edit_player(request, player_id):
    usersClubs, teams = get_data_for_menu(request)
    player = get_object_or_404(Player,pk=player_id)
    player_form = CreatePlayerForm(request.POST or None, instance=player)
    player_data = get_object_or_404(Player_data, player=player)
    player_data_form = CreatePlayerDataForm(request.POST or None, instance=player_data)
    if request.method == 'POST':
        if player_form.is_valid():
            player.save()
        if player_data_form.is_valid():
            player_data.save()
        return redirect(club_staff, player.club.id)
    return render(request,'clubs\\create_player.html',{'club':player.club,'teams':teams,'usersClubs':usersClubs, 'player_form':player_form,'player_data_form':player_data_form, 'edit':True})


def clubs_equipment(request, club_id):
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club, pk=club_id)
    equipment = Equipment.objects.filter(club=club)
    return render(request,'clubs\\equipment.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'equipment':equipment})

def create_equipment(request, club_id):
    usersClubs, teams = get_data_for_menu(request)
    club = get_object_or_404(Club, pk=club_id)
    form = CreateEquipment(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save(club=club)
        return redirect(clubs_equipment, club.id)
    return render(request,'clubs\\create_equipment.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'form':form})



def edit_equipment(request, item_id):
    usersClubs, teams = get_data_for_menu(request)
    item = get_object_or_404(Equipment, pk=item_id)
    club = get_object_or_404(Club, pk=item.club.id)
    form = CreateEquipment(request.POST or None, instance= item)
    if request.method == 'POST':
        if form.is_valid():
            form.save(club=club)
        return redirect(clubs_equipment, club.id)
    return render(request,'clubs\\create_equipment.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'form':form, 'edit':True})

def delete_equipment(request, item_id):
    usersClubs, teams = get_data_for_menu(request)
    item = get_object_or_404(Equipment, pk=item_id)
    club = get_object_or_404(Club, pk=item.club.id)
    if request.method == 'POST':
        item.delete()
        return redirect(clubs_equipment, club.id)
    return render(request,'clubs\\confirm_equipment.html',{'teams':teams,'usersClubs':usersClubs, 'club':club,'item':item})

def rent_equipment(request, item_id):
    usersClubs, teams = get_data_for_menu(request)
    item = get_object_or_404(Equipment, pk=item_id)
    club = item.club
    form = RentEquipmentForm(club, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save(item)
            form = RentEquipmentForm(club, None)
    return render(request,'clubs\\rent_equipment.html',{'teams':teams,'usersClubs':usersClubs, 'club':club, 'form':form})

def rented_equipment(request, item_id):
    usersClubs, teams = get_data_for_menu(request)
    item = get_object_or_404(Equipment, pk=item_id)
    equipment_holders = Rented_equipment.objects.filter(equipment = item, date_of_return = None)
    historical_holders = Rented_equipment.objects.filter(equipment = item, date_of_return__isnull=False)
    sum = 0
    for holder in equipment_holders:
        sum += holder.quantity
    rest = item.all_quantity - sum
    return render(request,'clubs\\rented_equipment.html',{'teams':teams,'usersClubs':usersClubs, 'item':item, 'equipment_holders':equipment_holders, 'historical_holders':historical_holders,'sum':sum, 'rest':rest})

def return_equipment(request, rent_id):
    rent = get_object_or_404(Rented_equipment,pk=rent_id)
    rent.date_of_return = date.today()
    rent.save()
    return redirect(rented_equipment, rent.equipment.id)
