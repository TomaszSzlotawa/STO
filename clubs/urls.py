from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('profile/<int:user_id>', views.user_profile, name= 'user_profile'),

]