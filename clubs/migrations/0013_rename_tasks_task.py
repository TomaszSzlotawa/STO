# Generated by Django 4.2.7 on 2023-11-13 10:35

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clubs', '0012_mezocycle_training_in_mezocycle_tasks'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tasks',
            new_name='Task',
        ),
    ]
