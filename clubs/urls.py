from django.urls import path

from . import views

urlpatterns = [
    path("", views.user_panel, name='user_panel'),
    path("create/", views.create_club, name='create_club'),
    path("staff/create_player/<int:club_id>", views.create_player, name='create_player'),
    path("staff/edit_player/<int:player_id>", views.edit_player, name='edit_player'),
    path("staff/<int:club_id>", views.club_staff, name='club_staff'),
    path("coaching_staff/<int:club_id>", views.club_coaching_staff, name='club_coaching_staff'),
    path("staff/delete/<int:player_id>", views.delete_player_from_club, name='delete_player_from_club'),
    path("staff/hide/<int:player_id>", views.hide_player_in_club, name='hide_player_in_club'),
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
    path("teams/season/<int:team_id>", views.add_season, name='add_season'),
    path("teams/season/edit/<int:team_id>", views.edit_active_season, name='edit_active_season'),
    path("teams/coaching_staff/<int:team_id>", views.team_coaching_staff, name='team_coaching_staff'),
    path("teams/coaching_staff/edit/<int:team_id>;<int:coach_id>", views.edit_team_coaching_staff, name='edit_team_coaching_staff'),
    path("teams/coaching_staff/add/<int:team_id>", views.add_coach_to_team, name='add_coach_to_team'),
    path("teams/staff/delete/<int:season_id>;<int:player_id>", views.delete_player_from_team, name='delete_player_from_team'),
    path("teams/staff/add/<int:team_id>", views.add_player, name='add_player'),
    path("teams/edit/<int:team_id>", views.edit_team, name='edit_team'),
    path("teams/delete/<int:team_id>", views.delete_team, name='delete_team'),
    path("equipment/<int:club_id>", views.clubs_equipment, name='clubs_equipment'),
    path("equipment/create/<int:club_id>", views.create_equipment, name='create_equipment'),
    path("equipment/edit/<int:item_id>", views.edit_equipment, name='edit_equipment'),
    path("equipment/delete/<int:item_id>", views.delete_equipment, name='delete_equipment'),
    path("equipment/rent/<int:item_id>", views.rent_equipment, name='rent_equipment'),
    path("equipment/raport/<int:item_id>", views.rented_equipment, name='rented_equipment'),
    path("equipment/return/<int:rent_id>", views.return_equipment, name='return_equipment'),
    path("equipment/player/<int:player_id>", views.players_equipment, name='players_equipment'),
    
]

