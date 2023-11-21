# Generated by Django 4.2.7 on 2023-11-19 17:28

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clubs', '0018_rename_mezocycle_training_in_mezocycle_mezocycle_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Coach',
            new_name='CoachingStaff',
        ),
        migrations.RenameModel(
            old_name='TeamsCoach',
            new_name='TeamsCoachingStaff',
        ),
        migrations.RenameField(
            model_name='teamscoachingstaff',
            old_name='coach',
            new_name='coachingStaff',
        ),
        migrations.AddField(
            model_name='club',
            name='addres',
            field=models.CharField(blank=True, help_text='Adres klubu', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='legal_form',
            field=models.CharField(blank=True, help_text='Forma prawna', max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='nip',
            field=models.CharField(blank=True, help_text='REGON klubu', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='regon',
            field=models.CharField(blank=True, help_text='REGON klubu', max_length=14, null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='yeor_of_foundation',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Rok założenia klubu', null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rented_equipment',
            name='description',
            field=models.TextField(blank=True, help_text='Opis do wypożyczonego sprzętu - np. nr, rozmiar', null=True),
        ),
    ]