from django.db import models
from django.contrib.auth.models import User 

# Create your models here.
class Club(models.Model):
    name = models.CharField(max_length = 50, null = True, blank = False, help_text='Nazwa klubu',unique=True)
    
    def __str__(self):
        return f"{self.name}"

class Sponsor(models.Model):
    name = models.CharField(max_length = 50, null = True, blank = False, help_text='Nazwa Sponsora',unique=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    #numer telefonu, dane kontaktowe
    
    def __str__(self):
        return f"{self.name}"

class Sponsorship_package(models.Model):
    min_amount = models.DecimalField(null=True,blank=False, max_digits=15,decimal_places=2, help_text='Dolna granica pakietu')
    max_amount = models.DecimalField(null=True,blank=False, max_digits=15,decimal_places=2, help_text='Górna granica pakietu')
    description = models.TextField(null=True, blank=True, help_text='Opis pakietu')

class Sponsorship(models.Model):
    amount = models.DecimalField(null=True,blank=False, max_digits=15,decimal_places=2, help_text='Kwota umowy sponsoringowej')
    start_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Początek umowy')
    end_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Koniec umowy')
    description = models.TextField(null=True, blank=True, help_text='Opis umowy')
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE)
    sponsorship_package = models.ForeignKey(Sponsorship_package, on_delete=models.RESTRICT,blank=True, null=True)

class Equipment(models.Model):
    name = models.CharField(max_length = 50, null = True, blank = False, help_text='Nazwa Sprzętu',unique=True)
    producer = models.CharField(max_length = 50, null = True, blank = False, help_text='Nazwa producenta',unique=False)
    all_quantity = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Ilość sprzętu")
    #quantity_available = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Dostępna ilość sprzętu")
    description = models.TextField(null=True, blank=True, help_text='Specyfikacja sprzętu')
    #drużyna, która jest "właścicielem" sprzętu, może być sprzęt nie przypisany do drużyny
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

class Player(models.Model):
    name = models.CharField(max_length = 60, null = True, blank = True, help_text='Imię',unique=False)
    surname = models.CharField(max_length = 60, null = True, blank = True, help_text='Nazwisko',unique=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE,blank=False,null=True)
    equipment = models.ManyToManyField(Equipment,through="Rented_equipment")
    joining_date = models.DateField(auto_now=True, auto_now_add=False, null=True, blank=False, help_text='Data dołącznia do klubu')



class Rented_equipment(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Ilość pożyczonego sprzętu")
    date_of_rental = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Data wypożyczenia')
    date_of_return = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data zwrócenia')
    #description = models.TextField(null=True, blank=True, help_text='Specyfikacja sprzętu')



class Player_data(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, primary_key=True)
    pesel = models.CharField(max_length = 11, null = True, blank = True, help_text='Pesel',unique=True)
    extranet = models.CharField(max_length = 7, null = True, blank = True, help_text='nr extranet',unique=True)
    date_of_birth = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data urodzenia')
    place_of_birth = models.CharField(max_length = 60, null = True, blank = True, help_text='Miejsce urodzenia',unique=False)
    addres = models.CharField(max_length = 60, null = True, blank = True, help_text='Adres zamieszkania',unique=False)

class Place(models.Model):
    surfaces = [
    ("nt","murawa naturalna"),
    ("at","murawa sztuczna"),
    ("fs","płaska powierzchnia")
    ]
    club = models.ManyToManyField(Club)
    name = models.CharField(max_length = 60, null = True, blank = False, help_text='Nazwa Obiektu',unique=False)
    addres = models.CharField(max_length = 60, null = True, blank = True, help_text='Adres obiektu',unique=False)
    lights = models.BooleanField(null=True,blank=True, help_text='Oświetlenie')
    surface = models.CharField(choices=surfaces, default="nt")
    description = models.TextField(null=True, blank=True, help_text='Specyfikacja obiektu')

class Team(models.Model):
    name = models.CharField(max_length = 40, null = True, blank = False, help_text='Nazwa drużyny',unique=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)


#treningi zaplanowane do kalendarza
class Training(models.Model):
    topic = models.CharField(max_length = 100, null = True, blank = False, help_text='Temat treningu',unique=False)
    goals = models.CharField(max_length = 100, null = True, blank = True, help_text='Cele',unique=False)
    rules = models.CharField(max_length = 100, null = True, blank = True, help_text='Zasady ',unique=False)
    actions = models.CharField(max_length = 100, null = True, blank = True, help_text='Działania',unique=False)
    start_datatime = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data i godzina rozpoczęcia')
    end_datatime = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data i godzina zakończenia')
    place = models.ForeignKey(Place, on_delete=models.SET_NULL,blank=False, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ManyToManyField(Player, through="Attendance")
    
class Attendance(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    training = models.OneToOneField(Training, on_delete=models.CASCADE)
    present = models.BooleanField(blank=True,null=True,help_text="Obecny na zajęciach")
    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=['player', 'training'], name='unique_player_training_attendence'
                )
            ]

class Season(models.Model):
    name = models.CharField(max_length = 9, null = True, blank = False, help_text='Nazwa sezonu',unique=False)
    active = models.BooleanField(blank=False,null=False,default=True,help_text="Obecny sezon")
    player = models.ManyToManyField(Player,blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,blank=False, null = True)

class UsersClub(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Coach(models.Model):
    licenses = [
    ("D","UEFA D"),
    ("C_F","UEFA FUTSAL C"),
    ("C","UEFA C"),
    ("B_F","UEFA FUTSAL B"),
    ("B_GK","UEFA GOALKEEPER B"),
    ("B","UEFA B"),
    ("B_EY","UEFA B ELITE YOUTH"),
    ("A_GK","UEFA GOALKEEPER A"),
    ("A","UEFA A"),
    ("A_EY","UEFA A ELITE YOUTH"),
    ("PRO","UEFA PRO"),
    ]
    license = models.CharField(choices=licenses,null=True,blank=False,default="null", help_text="Uprawnienia")
    license_expiry_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data wygaśnięcia uprawnień')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class TeamsCoach(models.Model):
    roles = [
        ("I","PIERWSZY TRENER"),
        ("II","DRUGI TRENER"),
        ("AS","ASYSTENT TRENERA"),
        ("AN","TRENER ANALITYK"),
        ("GK","TRENER BRAMKARZY"),
        ("PM","TRENER PRZYGOTOWANIA MOTORYCZNEGO"),
        ("TM","TRENER MENTALNY"),
        ("TR","TRENER "),
    ]
    coach = models.ForeignKey(Coach,on_delete=models.CASCADE)
    team = models.ForeignKey(Team,on_delete=models.CASCADE)
    takeover_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Data przejęcia druzyny')
    leaving_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data odejścia z druzyny')
    role_in_team = models.CharField(choices=roles,null=True,blank=False,default="null",help_text="Funkcja w drużynie")


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
    

class UsersGrant(models.Model):
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)