from django.urls import path

from . import views

urlpatterns = [
    path("", views.user_panel, name='user_panel'),
    path("create/<int:user_id>", views.create_club, name='create_club'),
    path('profile/<int:user_id>', views.user_profile, name= 'user_profile'),
    path('profile/delete/<int:user_id>', views.delete_profile, name= 'delete_profile'),

]