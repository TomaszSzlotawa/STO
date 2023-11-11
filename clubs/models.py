from django.db import models

# Create your models here.
class Club(models.Model):
    name = models.CharField(max_length = 50, null = True, blank = False, help_text='Nazwa klubu',unique=True)


class Sponsor(models.Model):
    name = models.CharField(max_length = 50, null = True, blank = False, help_text='Nazwa Sponsora',unique=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

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


