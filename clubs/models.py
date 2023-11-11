from django.db import models

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

class Players(models.Model):
    name = models.CharField(max_length = 60, null = True, blank = True, help_text='Imię',unique=False)
    surname = models.CharField(max_length = 60, null = True, blank = True, help_text='Nazwisko',unique=False)
    club = models.ManyToManyField(Club)
    equipment = models.ManyToManyField(Equipment,through="Rented_equipment")
    #players_data

class Rented_equipment(models.Model):
    player = models.ForeignKey(Players, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(null=True,blank=False, help_text="Ilość pożyczonego sprzętu")
    date_of_rental = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, help_text='Data wypożyczenia')
    date_of_return = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data zwrócenia')


class Player_data(models.Model):
    player = models.OneToOneField(Players, on_delete=models.CASCADE, primary_key=True)
    pesel = models.CharField(max_length = 11, null = True, blank = True, help_text='Pesel',unique=True)
    extranet = models.CharField(max_length = 7, null = True, blank = True, help_text='nr extranet',unique=True)
    date_of_birth = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text='Data urodzenia')
    place_of_birth = models.CharField(max_length = 60, null = True, blank = True, help_text='Miejsce urodzenia',unique=False)
    addres = models.CharField(max_length = 60, null = True, blank = True, help_text='Adres zamieszkania',unique=False)

class Place(models.Model):
    surfaces = [
    ("1","murawa naturalna"),
    ("2","murawa sztuczna"),
    ("3","parkiet")
    ]
    club = models.ManyToManyField(Club)
    name = models.CharField(max_length = 60, null = True, blank = False, help_text='Nazwa Obiektu',unique=False)
    addres = models.CharField(max_length = 60, null = True, blank = True, help_text='Adres obiektu',unique=False)
    lights = models.BooleanField(null=True,blank=True, help_text='Oświetlenie')
    surface = models.CharField(choices=surfaces, default="1")
    description = models.TextField(null=True, blank=True, help_text='Specyfikacja obiektu')
    

