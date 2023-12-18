from datetime import date, datetime, timedelta
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Attendance, Equipment, Place, Player_data, Profile, Club, Rented_equipment, Training, UsersClub, Season, Team, Player, TeamsCoaching_Staff
from django.core.exceptions import ValidationError
from django.utils import timezone

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
        fields = ('username','first_name','last_name')


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('birth_date', 'license','license_expiry_date')

class ClubCreationForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ('name', 'addres', 'regon', 'nip', 'legal_form', 'year_of_foundation')

from django import forms
from django.contrib.auth.models import User
from .models import UsersClub

class UsersClubForm(forms.ModelForm):
    email = forms.EmailField(label='Adres email', required=True)
    
    class Meta:
        model = UsersClub
        fields = ['admin', 'coach', 'employee', 'training_coordinator']

    def __init__(self, club, *args, **kwargs):
        self.club = club
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            raise forms.ValidationError('Użytkownik o podanym adresie email nie istnieje.')
        
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('email')
        admin = cleaned_data.get('admin')
        coach = cleaned_data.get('coach')
        employee = cleaned_data.get('employee')
        training_coordinator = cleaned_data.get('training_coordinator')

        if UsersClub.objects.filter(user=user, club=self.club).exists():
            raise forms.ValidationError('Użytkownik jest już przypisany do tego klubu.')

        if not any([admin, coach, employee, training_coordinator]):
            raise forms.ValidationError('Musisz zaznaczyć co najmniej jedną opcję.')
        
class UserRoleAnswerForm(forms.Form):
    status = forms.BooleanField(required=False, widget=forms.HiddenInput)

class TeamCreateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name','category']


class SeasonCreateForm(forms.ModelForm):
    season_name = forms.CharField(max_length=9, required=True)

    class Meta:
        model = Season
        fields = ['season_name', 'date_of_start', 'date_of_end']

    def __init__(self, *args, **kwargs):
        super(SeasonCreateForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields['season_name'].initial = self.instance.name

    def clean(self):
        cleaned_data = super().clean()
        date_of_start = cleaned_data.get('date_of_start')
        date_of_end = cleaned_data.get('date_of_end')

        if date_of_start and date_of_end and date_of_start > date_of_end:
            raise forms.ValidationError("Data rozpoczęcia nie może być późniejsza niż data zakończenia.")        
        if date_of_start and  date_of_start > date.today():
            raise forms.ValidationError("Sezon nie może się rozpoczynać w przyszłości.")
        latest_season = Season.objects.filter(team = self.instance.team,).exclude(id = self.instance.id).order_by('-date_of_end').first()
        if latest_season and latest_season.date_of_end and date_of_start and date_of_start < latest_season.date_of_end:
            raise forms.ValidationError("Data rozpoczęcia sezonu nie może być wcześniejsza niż najnowsza data zakończenia poprzedniego sezonu dla drużyny.")


        return cleaned_data

    def save(self, team, commit=True):
        Season.objects.filter(team=team).update(active=False)
        season = super(SeasonCreateForm, self).save(commit=False)
        season.name = self.cleaned_data['season_name']
        season.team = team
        season.active=True
        if commit:
            season.save()
        return season
    
class SeasonChooseForm(forms.Form):
    class Meta:
        model = Season
        fields = ['active_season']
    active_season = forms.ModelChoiceField(queryset=Season.objects.none(), required=False, empty_label="Wybierz sezon")

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        active_season = kwargs.pop('active_season', None)
        super(SeasonChooseForm, self).__init__(*args, **kwargs)

        # Aktualizuj queryset dla existing_season na podstawie dostarczonej drużyny
        if team:
            seasons = Season.objects.filter(team=team)
            self.fields['active_season'].queryset = seasons

            # Znajdź sezon z ustawionym statusem active
            if active_season:
                self.fields['active_season'].initial = active_season.id

    def clean(self):
        cleaned_data = super().clean()
        existing_season = cleaned_data.get('active_season')

        # Sprawdź, czy użytkownik wybrał istniejący sezon
        if not existing_season:
            raise forms.ValidationError('Musisz wybrać istniejący sezon.')

        return existing_season

class CreatePlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name','surname']

class CreatePlayerDataForm(forms.ModelForm):
    class Meta:
        model = Player_data
        fields = ['pesel', 'extranet', 'date_of_birth', 'place_of_birth', 'addres']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class AddCoachToTeam(forms.ModelForm):
    class Meta:
        model = TeamsCoaching_Staff
        fields = ['role_in_team', 'takeover_date']
    
    coach = forms.ModelChoiceField(queryset=None)  

    def __init__(self, coaches, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['coach'].queryset = coaches

    def save(self,team, commit=True):
        coach_in_team = super().save(commit=False)
        coach_in_team.coach = self.cleaned_data['coach'].user  
        coach_in_team.team = team

        if commit:
            coach_in_team.save()

        return coach_in_team
    
class EditCoachInTeam(forms.ModelForm):
    class Meta:
        model = TeamsCoaching_Staff
        fields = ['role_in_team','takeover_date']


class CreateEquipment(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name','producer','all_quantity','description']

    def save(self,club, commit=True):
        item = super().save(commit=False)
        item.club = club

        if commit:
            item.save()
        return item
    
class RentEquipmentForm(forms.ModelForm):
    class Meta:
        model = Rented_equipment
        fields = ['player', 'quantity', 'date_of_rental', 'description']

    def __init__(self, club, *args, **kwargs):
        super(RentEquipmentForm, self).__init__(*args, **kwargs)
        self.fields['player'].queryset = Player.objects.filter(club=club)

    def save(self, item, commit=True):
        rent = super().save(commit=False)
        rent.equipment = item

        if commit:
            rent.save()
        return rent
    
class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields=['name','addres', 'lights', 'surface','description']

    def save(self,club, commit=True):
        place = super().save(commit=False)
        place.club = club

        if commit:
            place.save()
        return place
    
class test(forms.ModelMultipleChoiceField):
    def label_from_instance(self, player):
        return f"{player.surname} {player.name}" 

class TrainingForm(forms.ModelForm):
    duration = forms.IntegerField(min_value=1, required=True)
    player = test(
        queryset=Player.objects.all().order_by('surname', 'name'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    start_datatime = forms.DateTimeField(
        widget=forms.widgets.DateTimeInput(
            attrs={'type': 'datetime-local'},
        )
    )
    
    class Meta:
        model = Training
        exclude = ['season', 'end_datatime']
        
    def __init__(self, *args, players=None, season, **kwargs):
        super(TrainingForm, self).__init__(*args, **kwargs)
        if players is not None:
            self.fields['player'].queryset = players
            self.fields['player'].initial = players.values_list('pk', flat=True)
        self.season = season
        if self.instance.pk:
            self.fields['duration'].initial = (self.instance.end_datatime - self.instance.start_datatime).seconds // 60


    def clean(self):
        cleaned_data = super().clean()
        start_datatime = cleaned_data.get('start_datatime')
        duration = cleaned_data.get('duration')

        if start_datatime and duration:
            end_datatime = start_datatime + timedelta(minutes=duration)
            season_start = datetime.combine(self.season.date_of_start, datetime.min.time())
            season_end = datetime.combine(self.season.date_of_end, datetime.max.time())

            if start_datatime < season_start or end_datatime > season_end:
                raise ValidationError("Trening musi odbywać się w ramach trwającego sezonu.")

    def save(self, commit=True):
        training = super().save(commit=False)
        training.season = self.season
        duration_minutes = self.cleaned_data['duration']
        start_datatime = self.cleaned_data.get('start_datatime')
        
        if start_datatime:
            training.end_datatime = start_datatime + timedelta(minutes=duration_minutes)

        if commit:
            training.save()
            selected_players = self.cleaned_data['player']
            selected_players_ids = selected_players.values_list('id', flat=True)
            current_players = set(Attendance.objects.filter(training=training).values_list('player', flat=True))

            removed_players = current_players - set(selected_players_ids)

            Attendance.objects.filter(training=training, player__in=removed_players).delete()

            for player in selected_players:
                if player not in current_players:
                    Attendance.objects.get_or_create(training=training, player=player,)

        return training
    
class AttendanceForm(forms.ModelForm):
    present = forms.BooleanField(label="Obecny", required=False)
    not_specified = forms.BooleanField(label="Nieokreślono", required=False)
    absent = forms.BooleanField(label="Nieobecny", required=False)

    class Meta:
        model = Attendance
        fields = []

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.present is not None:
            self.initial['present'] = 'on' if self.instance.present else False
            self.initial['absent'] = 'on' if not self.instance.present else False
            self.initial['not_specified'] = False
        else:
            self.initial['present'] = False
            self.initial['absent'] = False
            self.initial['not_specified'] = True

    def save(self, commit=True):
        att = super().save(commit=False)
        present = self.cleaned_data.get('present') 
        absent = self.cleaned_data.get('absent')
        not_specified = self.cleaned_data.get('not_specified')

        if present:
            att.present = True
        elif absent:
            att.present = False
        elif not_specified:
            att.present = None

        if commit:
            att.save()

        return att
    
class AttendanceReportFilter(forms.Form):
    start_date = forms.DateField(label='Data początkowa', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='Data końcowa', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, season=None, **kwargs):
        super(AttendanceReportFilter, self).__init__(*args, **kwargs)
    
        if season:
            self.fields['start_date'].initial = season.date_of_start
            self.fields['start_date'].widget.attrs['min'] = season.date_of_start
            self.fields['start_date'].widget.attrs['max'] = season.date_of_end
            self.fields['end_date'].initial = season.date_of_end
            self.fields['end_date'].widget.attrs['min'] = season.date_of_start
            self.fields['end_date'].widget.attrs['max'] = season.date_of_end
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise ValidationError("Data początkowa nie może być późniejsza niż data końcowa.")
