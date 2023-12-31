# Generated by Django 4.2.7 on 2023-11-11 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0004_attendance_team_alter_place_surface_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nazwa sezonu', max_length=9, null=True)),
                ('active', models.BooleanField(default=True, help_text='Obecny sezon')),
            ],
        ),
    ]
