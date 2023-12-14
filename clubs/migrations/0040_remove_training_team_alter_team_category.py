# Generated by Django 4.2.7 on 2023-12-11 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0039_training_season_alter_team_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='training',
            name='team',
        ),
        migrations.AlterField(
            model_name='team',
            name='category',
            field=models.CharField(blank=True, choices=[('U14', 'JUNIOR C2'), ('U12', 'JUNIOR D2'), ('U6', 'JUNIOR G2'), ('U16', 'JUNIOR B2'), ('U17', 'JUNIOR B1'), ('SENIOR', 'SENIOR'), ('U9', 'JUNIOR F1'), ('U10', 'JUNIOR E2'), ('U7', 'JUNIOR G1'), ('U13', 'JUNIOR D1'), ('U15', 'JUNIOR C1'), ('U19', 'JUNIOR A1'), ('U11', 'JUNIOR E1'), ('U18', 'JUNIOR A2'), ('U8', 'JUNIOR F2')], default=None),
        ),
    ]