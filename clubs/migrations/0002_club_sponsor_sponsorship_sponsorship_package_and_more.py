# Generated by Django 4.2.7 on 2023-11-11 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nazwa klubu', max_length=50, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nazwa Sponsora', max_length=50, null=True, unique=True)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
            ],
        ),
        migrations.CreateModel(
            name='Sponsorship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Kwota umowy sponsoringowej', max_digits=15, null=True)),
                ('start_date', models.DateField(help_text='Początek umowy', null=True)),
                ('end_date', models.DateField(help_text='Koniec umowy', null=True)),
                ('description', models.TextField(blank=True, help_text='Opis umowy', null=True)),
                ('sponsor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.sponsor')),
            ],
        ),
        migrations.CreateModel(
            name='Sponsorship_package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_amount', models.DecimalField(decimal_places=2, help_text='Dolna granica pakietu', max_digits=15, null=True)),
                ('max_amount', models.DecimalField(decimal_places=2, help_text='Górna granica pakietu', max_digits=15, null=True)),
                ('description', models.TextField(blank=True, help_text='Opis pakietu', null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Clubs',
        ),
        migrations.AddField(
            model_name='sponsorship',
            name='sponsorship_package',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='clubs.sponsorship_package'),
        ),
    ]