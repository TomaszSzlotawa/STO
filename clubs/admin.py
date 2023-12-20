from django.contrib import admin
#from .models import Club,Player,Place,Team, Training,Season,Sponsor, Sponsorship,Sponsorship_package,Equipment,Rented_equipment,Player_data,Attendance
# Register your models here.
from .models import *

admin.site.register(Club)
admin.site.register(Player)
admin.site.register(Team)
admin.site.register(Equipment)
admin.site.register(Rented_equipment)
admin.site.register(Season)
admin.site.register(Training)
admin.site.register(Attendance)
admin.site.register(Place)
admin.site.register(Sponsor)
admin.site.register(Sponsorship)
admin.site.register(Sponsorship_package)
admin.site.register(Player_data)
admin.site.register(UsersClub)
admin.site.register(Coaching_Staff)
admin.site.register(TeamsCoaching_Staff)
admin.site.register(Grant)
admin.site.register(UsersGrant)
admin.site.register(Task)
admin.site.register(Mezocycle)
admin.site.register(ImplementedMezocycle)
admin.site.register(Training_in_mezocycle)
admin.site.register(Profile)



