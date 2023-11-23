from django.urls import path

from . import views

urlpatterns = [
    path("", views.user_panel, name='user_panel'),
    path("create/", views.create_club, name='create_club'),
    path("settings/<int:club_id>", views.club_settings, name='club_settings'),
    path("settings/roles/<int:club_id>", views.roles_in_club, name='roles_in_club'),
    path("settings/roles/add_user<int:club_id>", views.add_user_to_club, name='add_user_to_club'),
    path('profile/', views.user_profile, name= 'user_profile'),
    path('profile/delete/', views.delete_profile, name= 'delete_profile'),
    path('delete/<int:club_id>', views.delete_club, name= 'delete_club'),

]

