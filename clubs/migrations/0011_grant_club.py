# Generated by Django 4.2.7 on 2023-11-13 09:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0010_coach_grant_player_joining_date_usersgrant_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='grant',
            name='club',
            field=models.ForeignKey(default=14, on_delete=django.db.models.deletion.CASCADE, to='clubs.club'),
            preserve_default=False,
        ),
    ]
