# Generated by Django 4.2.7 on 2023-11-27 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0026_usersclub_admin_usersclub_coach_usersclub_employee_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='birth_date',
            field=models.DateField(blank=True, help_text='Data urodzin', null=True),
        ),
    ]