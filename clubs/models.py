from django.db import models
from django.contrib.auth.models import User 
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

def current_year():
    return datetime.date.today().year
def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)

class Profile(models.Model):
    licenses = [
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data urodzin')
    license = models.CharField(choices=licenses,null=True,blank=True, default="null", help_text="Uprawnienia")
    license_expiry_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data wygaśnięcia uprawnień')

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

# Create your models here.
class Club(models.Model):


    name = models.CharField(max_length = 50, null = True, blank = False, help_text='Nazwa klubu',unique=True)
    addres = models.CharField(max_length=100,null = True, blank=True,help_text="Adres klubu")
    regon = models.CharField(max_length=14,null = True, blank=True,help_text="REGON klubu")
    nip = models.CharField(max_length=10,null = True, blank=True,help_text="REGON klubu")
    legal_form = models.CharField(max_length=40,null=True,blank=True,help_text="Forma prawna")
    year_of_foundation = models.PositiveSmallIntegerField(null = True, blank=True, help_text="Rok założenia klubu" , validators=[MinValueValidator(1800), max_value_current_year])
    
    def __str__(self):
        return f"{self.name}"
    def name_without_spaces(self):
        return f"{self.name.replace(' ','_').replace('-','_')}"


class Sponsor(models.Model):
    name = models.CharField(max_length = 50, null = True, blank = False, help_text='Nazwa Sponsora')
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    #phone_number = models.CharField(max_length = 18, null = True, blank = True, help_text='Numer telefonu')
    #email = models.EmailField(null=True,blank=True,help_text="email")
    
    def __str__(self):
        return f"{self.name} [{self.club.name}]"

class Sponsorship_package(models.Model):
    min_amount = models.DecimalField(null=True,blank=False, max_digits=15,decimal_places=2, help_text='Dolna granica pakietu')
    max_amount = models.DecimalField(null=True,blank=False, max_digits=15,decimal_places=2, help_text='Górna granica pakietu')
    description = models.TextField(null=True, blank=True, help_text='Opis pakietu')

    def __str__(self):
        return f"[{self.min_amount} - {self.max_amount}]"
    

class Sponsorship(models.Model):
    amount = models.DecimalField(null=True,blank=False, max_digits=15,decimal_places=2, help_text='Kwota umowy sponsoringowej')
    start_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Początek umowy')
    end_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Koniec umowy')
    description = models.TextField(null=True, blank=True, help_text='Opis umowy')
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE)
    sponsorship_package = models.ForeignKey(Sponsorship_package, on_delete=models.RESTRICT,blank=True, null=True)

    def __str__(self):
        return f"[{self.start_date}] {self.sponsor}"

class Equipment(models.Model):
    name = models.CharField(max_length = 50, null = True, blank = False, help_text='Nazwa Sprzętu',unique=True)
    producer = models.CharField(max_length = 50, null = True, blank = False, help_text='Nazwa producenta',unique=False)
    all_quantity = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Ilość sprzętu")
    #quantity_available = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Dostępna ilość sprzętu")
    description = models.TextField(null=True, blank=True, help_text='Specyfikacja sprzętu')
    #drużyna, która jest "właścicielem" sprzętu, może być sprzęt nie przypisany do drużyny
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} [{self.club.name}]"

class Player(models.Model):
    name = models.CharField(max_length = 60, null = True, blank = False, help_text='Imię',unique=False)
    surname = models.CharField(max_length = 60, null = True, blank = False, help_text='Nazwisko',unique=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE,blank=False,null=True)
    equipment = models.ManyToManyField(Equipment,through="Rented_equipment")
    joining_date = models.DateField(auto_now=True, auto_now_add=False, null=True, blank=False, help_text='Data dołącznia do klubu')
    hidden = models.BooleanField(null=False,blank=False, default=False)
    def __str__(self):
        return f"{self.surname} {self.name} [{self.club.name}]"


class Rented_equipment(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Ilość pożyczonego sprzętu")
    date_of_rental = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Data wypożyczenia')
    date_of_return = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data zwrócenia')
    description = models.TextField(null=True, blank=True, help_text='Opis do wypożyczonego sprzętu - np. nr, rozmiar')
    #numer opcjonalny, rozmiar opcjonalny
    def __str__(self):
        return f"{self.player.surname} {self.player.name} - {self.equipment.name}({self.quantity}) [{self.player.club.name}]"


class Player_data(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, primary_key=True)
    pesel = models.CharField(max_length = 11, null = True, blank = True, help_text='Pesel',unique=True)
    extranet = models.CharField(max_length = 7, null = True, blank = True, help_text='nr extranet',unique=True)
    date_of_birth = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data urodzenia')
    place_of_birth = models.CharField(max_length = 60, null = True, blank = True, help_text='Miejsce urodzenia',unique=False)
    addres = models.CharField(max_length = 60, null = True, blank = True, help_text='Adres zamieszkania',unique=False)
    
    def __str__(self):
        return f"{self.player.surname} {self.player.name} [{self.player.club.name}]"
    
class Place(models.Model):
    surfaces = [
    ("nt","murawa naturalna"),
    ("at","murawa sztuczna"),
    ("fs","płaska powierzchnia")
    ]
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    name = models.CharField(max_length = 60, null = True, blank = False, help_text='Nazwa Obiektu',unique=False)
    addres = models.CharField(max_length = 100, null = True, blank = True, help_text='Adres obiektu',unique=False)
    lights = models.BooleanField(null=True,blank=True, help_text='Oświetlenie')
    toilets = models.BooleanField(null=True,blank=True, help_text='Toalety')
    changing_rooms = models.BooleanField(null=True,blank=True, help_text='Sztanie')
    surface = models.CharField(choices=surfaces, default="nt")
    description = models.TextField(null=True, blank=True, help_text='Specyfikacja obiektu')

    def __str__(self):
        return f"{self.name}, {self.addres}"

class Team(models.Model):
    categories = {
        ("U6","JUNIOR G2"),
        ("U7","JUNIOR G1"),
        ("U8","JUNIOR F2"),
        ("U9","JUNIOR F1"),
        ("U10","JUNIOR E2"),
        ("U11","JUNIOR E1"),
        ("U12","JUNIOR D2"),
        ("U13","JUNIOR D1"),
        ("U14","JUNIOR C2"),
        ("U15","JUNIOR C1"),
        ("U16","JUNIOR B2"),
        ("U17","JUNIOR B1"),
        ("U18","JUNIOR A2"),
        ("U19","JUNIOR A1"),
        ("SENIOR","SENIOR"),
    }
    name = models.CharField(max_length = 40, null = True, blank = False, help_text='Nazwa drużyny')
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    category = models.CharField(choices=categories, blank=True, default=None)

    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=['name', 'club'], name='unique_team_name_in_club'
                )
            ]

    def __str__(self):
        return f"{self.name} [{self.club.name}]"
    def name_without_spaces(self):
        return f"{self.name.replace(' ','_')}"
    

class Season(models.Model):
    name = models.CharField(max_length = 9, null = True, blank = False, help_text='Nazwa sezonu',unique=False)
    active = models.BooleanField(blank=False,null=False,default=True,help_text="Obecny sezon")
    player = models.ManyToManyField(Player,blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,blank=False, null = True)
    date_of_start = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Data rozpoczęcia sezonu')
    date_of_end = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Data zakończenia sezonu')

    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=['name', 'team'], name='unique_team_season'
                )
            ]

    def __str__(self):
        active_ = ""
        if self.active:
            active_="[Wybrany]"
        if self.date_of_end and self.date_of_end < date.today():
            status="Zakończony"
        else:
            status="Bieżący"
        return f"Sezon {self.name}-{status}{active_}"

    def name_and_status(self):
        return self


#treningi zaplanowane do kalendarza
class Training(models.Model):
    topic = models.CharField(max_length = 100, null = True, blank = False, help_text='Temat treningu',unique=False)
    goals = models.CharField(max_length = 100, null = True, blank = True, help_text='Cele',unique=False)
    rules = models.CharField(max_length = 100, null = True, blank = True, help_text='Zasady ',unique=False)
    actions = models.CharField(max_length = 100, null = True, blank = True, help_text='Działania',unique=False)
    start_datatime = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data i godzina rozpoczęcia')
    end_datatime = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data i godzina zakończenia')
    place = models.ForeignKey(Place, on_delete=models.SET_NULL,blank=False, null=True)
    #team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ManyToManyField(Player, through="Attendance")
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    implemented_mezocycle = models.ForeignKey("ImplementedMezocycle", blank=True, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return f"Trening {self.start_datatime} - {self.season.team.name}({self.place})[{self.implemented_mezocycle}]"
    
class Attendance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    present = models.BooleanField(blank=True,null=True,help_text="Obecny na zajęciach")

    class Meta:
        unique_together = ('player', 'training')
        
    def __str__(self):
        present_ = ''
        if self.present == None:
            present_ = "Nie określono"
        elif self.present:
            present_ = "Obecny"
        else:
            present_ = "Nieobecny"

        return f"[Trening {self.training.start_datatime}] - {self.player}({present_})"
    
    



class UsersClub(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    admin = models.BooleanField(default=False, help_text="Czy jest administratorem klubu")
    coach = models.BooleanField(default=False, help_text="Czy jest trenerem w klubie")
    employee = models.BooleanField(default=False, help_text="Czy jest pracownikiem w klubie")
    training_coordinator = models.BooleanField(default=False, help_text="Czy jest koordynatorem szkolenia w klubie")
    accepted = models.BooleanField(default=None, null = True, blank=True, help_text='Czy użytkownik zaakceptował zaproszenie' )
    
    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=['user', 'club'], name='unique_user_club'
                )
            ]
    def __str__(self):
        return f"{self.user} - {self.club}"
    def status(self):
        if self.accepted == None:
            return "(Oczekujące)"
        elif self.accepted == False:
            return "(Odrzucone)"
        else:
            return ""

    def roles(self):
        text =''
        if(self.admin == True):
            text += 'Administrator klubu, '
        if(self.coach == True):
            text += 'Trener, '
        if(self.employee == True):
            text += 'Pracownik klubu, '
        if(self.training_coordinator == True):
            text += 'Koordynator szkolenia, '

        if len(text)>0:
            return text[:len(text)-2]

    
class Coaching_Staff(models.Model):
    licenses = [
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
    license = models.CharField(choices=licenses,null=True,blank=False,default="null", help_text="Uprawnienia")
    license_expiry_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data wygaśnięcia uprawnień')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=['user', 'license'], name='unique_user_license'
                )
            ]

    def __str__(self):
        return f"{self.user} - trener {self.license}"

class TeamsCoaching_Staff(models.Model):
    roles = [
        ("PIERWSZY TRENER","PIERWSZY TRENER"),
        ("DRUGI TRENER","DRUGI TRENER"),
        ("ASYSTENT TRENERA","ASYSTENT TRENERA"),
        ("TRENER ANALITYK","TRENER ANALITYK"),
        ("TRENER BRAMKARZY","TRENER BRAMKARZY"),
        ("TRENER PRZYGOTOWANIA MOTORYCZNEGO","TRENER PRZYGOTOWANIA MOTORYCZNEGO"),
        ("TRENER MENTALNY","TRENER MENTALNY"),
        ("TRENER","TRENER "),
    ]
    coach = models.ForeignKey(User,on_delete=models.CASCADE)
    team = models.ForeignKey(Team,on_delete=models.CASCADE)
    takeover_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Data przejęcia druzyny')
    leaving_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data odejścia z druzyny')
    role_in_team = models.CharField(choices=roles,null=True,blank=False,default="null",help_text="Funkcja w drużynie")

    def __str__(self):
        return f"{self.team} - {self.coach.first_name} {self.coach.last_name}({self.role_in_team})"

    def display_team_role_and_since(self):
        return f"{self.team.name} - {self.role_in_team} od {self.takeover_date}"
    
    def display_role_and_since(self):
        return f"{self.role_in_team} od {self.takeover_date}"

class Grant(models.Model):
    name = models.CharField(max_length=100,null=False,blank=False,help_text="Nazwa dofinansowania")
    link = models.URLField(blank=True,null=True,help_text="Link do oferty")
    founder = models.CharField(max_length=100,null=True,blank=False,help_text="Nazwa fundacji/organizacji")
    max_amount = models.DecimalField(null=True,blank=True, max_digits=15,decimal_places=2, help_text='Maksymalna kwota dofinansowania')
    start_of_application = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Początek przyjmowania zgłoszeń')
    end_of_application = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Koniec przyjmowania zgłoszeń')
    date_of_application = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data wysłania zgłoszenia')
    end_of_processing = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Koniec przyjmowania zgłoszeń')
    description = models.TextField(null=True, blank=True, help_text='Opis o co wnioskowano w zadaniu i na jaką kwotę')
    grant_awarded = models.BooleanField(null=True,blank=True, help_text="Dofinansowanie przyznane")
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} - {self.founder}[{self.club}]"

class UsersGrant(models.Model):
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=['user', 'grant'], name='unique_user_grant'
                )
            ]
    def __str__(self):
        return f"{self.grant.name} - {self.user}"

class Task(models.Model):
    name = models.CharField(max_length=100,null=True,blank=False,help_text="Nazwa zadania")
    description = models.TextField(null=True, blank=True, help_text='Opis zadania')
    added = models.DateTimeField(auto_now=True, auto_now_add=False, null=False, blank=False, help_text='Data dodania')
    deadline = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Deadline')
    statuses = [
        ("TO DO", "Do zrobienia"),
        ("IN PROGRES", "W trakcie"),
        ("DONE", "Zrobione"),
    ]
    status = models.CharField(choices=statuses,default="TO DO",blank = False, null=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE,null=True, blank=False)

    def __str__(self):
        return f"{self.name}[{self.club}] - {self.user}({self.status})"

class Mezocycle(models.Model):
    name = models.CharField(max_length=60,null=True,blank=False,help_text="Nazwa mezocyklu")
    weeks = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Ile trwa tygodni")
    trainings_per_week = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Ilość treningów tygodniowo")
    team = models.ForeignKey(Team,on_delete=models.SET_NULL, null=True,blank = True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True,blank = True)

    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=['name', 'user'], name='unique_user_mezocycle'
                ),
                models.UniqueConstraint(
                    fields=['name', 'team'], name='unique_team_mezocycle'
                )
            ]

    def __str__(self):
        return f"{self.name}"

class Training_in_mezocycle(models.Model):
    mezocycle = models.ForeignKey(Mezocycle,on_delete=models.CASCADE, null=True,blank = False)
    week_number = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Numer tygodnia")
    training_number = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Numer treningu")
    topic = models.CharField(max_length = 100, null = True, blank = False, help_text='Temat treningu',unique=False)
    goals = models.CharField(max_length = 100, null = True, blank = True, help_text='Cele',unique=False)
    rules = models.CharField(max_length = 100, null = True, blank = True, help_text='Zasady ',unique=False)
    actions = models.CharField(max_length = 100, null = True, blank = True, help_text='Działania',unique=False)
    duration = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Czas trwania")

    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=['mezocycle','week_number', 'training_number'], name='unique_mezocycle_training'
                )
            ]

    def __str__(self):
        return f"{self.mezocycle.name} tydzień {self.week_number}, trening {self.training_number}"
    

class ImplementedMezocycle(models.Model):
    name = models.CharField(max_length=60,null=True,blank=False,help_text="Nazwa mezocyklu")
    weeks = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Ile trwa tygodni")
    trainings_per_week = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Ilość treningów tygodniowo")
    team = models.ForeignKey(Team,on_delete=models.SET_NULL, null=True,blank = True)

    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=['name', 'team'], name='unique_team_implemented_mezocycle'
                )
            ]

    def __str__(self):
        return f"{self.name}"
