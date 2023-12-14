# Generated by Django 4.2.7 on 2023-12-11 14:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0042_alter_attendance_unique_together_alter_team_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.player'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='training',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.training'),
        ),
        migrations.AlterField(
            model_name='team',
            name='category',
            field=models.CharField(blank=True, choices=[('SENIOR', 'SENIOR'), ('U12', 'JUNIOR D2'), ('U13', 'JUNIOR D1'), ('U8', 'JUNIOR F2'), ('U11', 'JUNIOR E1'), ('U16', 'JUNIOR B2'), ('U17', 'JUNIOR B1'), ('U6', 'JUNIOR G2'), ('U14', 'JUNIOR C2'), ('U18', 'JUNIOR A2'), ('U9', 'JUNIOR F1'), ('U10', 'JUNIOR E2'), ('U7', 'JUNIOR G1'), ('U15', 'JUNIOR C1'), ('U19', 'JUNIOR A1')], default=None),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('player', 'training')},
        ),
    ]