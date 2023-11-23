from django.urls import path

from . import views

urlpatterns = [
    path("", views.user_panel, name='user_panel'),
    path("create/<int:user_id>", views.create_club, name='create_club'),
    path("settings/<int:club_id>", views.club_settings, name='club_settings'),
    path('profile/', views.user_profile, name= 'user_profile'),
    path('profile/delete/', views.delete_profile, name= 'delete_profile'),

]