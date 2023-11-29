from django.urls import path

from . import views

urlpatterns = [
    path("", views.user_panel, name='user_panel'),
    path("create/", views.create_club, name='create_club'),
    path("staff/create_player/<int:club_id>", views.create_player, name='create_player'),
    path("staff/<int:club_id>", views.club_staff, name='club_staff'),
    path("staff/delete/<int:player_id>", views.delete_player_from_club, name='delete_player_from_club'),
    path("settings/<int:club_id>", views.club_settings, name='club_settings'),
    path("settings/roles/<int:club_id>", views.roles_in_club, name='roles_in_club'),
    path("settings/roles/add_user<int:club_id>", views.add_user_to_club, name='add_user_to_club'),
    path('profile/', views.user_profile, name= 'user_profile'),
    path('profile/roles', views.user_roles, name= 'user_roles'),
    path('profile/roles/delete<int:club_id>', views.user_role_delete, name= 'user_role_delete'),
    path('profile/roles/answer<int:club_id>', views.user_role_answer, name= 'user_role_answer'),
    path('profile/delete/', views.delete_profile, name= 'delete_profile'),
    path('delete/<int:club_id>', views.delete_club, name= 'delete_club'),
    path("teams/<int:club_id>", views.create_team, name='create_team'),
    path("teams/staff/<int:team_id>", views.team_staff, name='team_staff'),
    path("teams/staff/add/<int:team_id>", views.add_player, name='add_player'),
    path("teams/edit/<int:team_id>", views.edit_team, name='edit_team'),
    path("teams/delete/<int:team_id>", views.delete_team, name='delete_team'),
]

