# w twoim pliku tables.py

import django_tables2 as tables
from .models import Player, Player_data

class PlayerDataTable(tables.Table):
    name = tables.Column(verbose_name='Imię')
    surname = tables.Column(verbose_name='Nazwisko')
    date_of_birth = tables.Column(verbose_name='Data urodzin')
    teams = tables.Column(accessor='teams', verbose_name='Drużyny')
    

    actions = tables.TemplateColumn(template_name='clubs/player_actions_column.html', orderable=False, verbose_name='')

    class Meta:
        template_name = 'tables/bootstrap_htmx.html'
        #attrs = {'class': 'table table-striped'}
        row_attrs = {
            'class': lambda record: 'hidden-row' if record['hidden'] else ''
        }
