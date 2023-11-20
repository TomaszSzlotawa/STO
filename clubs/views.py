from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse



def index(request):
    return render(request,'clubs\main.html',{})
