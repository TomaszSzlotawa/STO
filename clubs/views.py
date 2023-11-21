from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import UsersClub, Club, Team

def signup(request):
    pass

def index(request):
    clubs = Club.objects.all()
    usersClubs = UsersClub.objects.all()
    teams = Team.objects.all()
    return render(request,'clubs\main.html',{'clubs':clubs,'usersClubs':usersClubs,'teams':teams})

