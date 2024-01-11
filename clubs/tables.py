import django_tables2 as tables
from .models import Equipment, Rented_equipment

class PlayerDataTable(tables.Table):
    name = tables.Column(verbose_name='Imię')
    surname = tables.Column(verbose_name='Nazwisko')
    date_of_birth = tables.Column(verbose_name='Data urodzin')
    teams = tables.Column(accessor='teams', verbose_name='Drużyny')
    

    actions = tables.TemplateColumn(template_name='clubs/player_actions_column.html', orderable=False, verbose_name='')

    class Meta:
        template_name = 'tables/bootstrap_htmx.html'
        #attrs = {'class': 'table table-striped'}
        order_by = ('surname',)  
        row_attrs = {
            'class': lambda record: 'hidden-row' if record['hidden'] else ''
        }

class CoachingStaffTable(tables.Table):
    name = tables.Column(verbose_name='Imię')
    surname = tables.Column(verbose_name='Nazwisko')
    license = tables.Column(verbose_name='Licencja')
    license_expiry_date = tables.Column(verbose_name='Data ważności')
    teams = tables.Column(accessor='teams', verbose_name='Drużyny')
    class Meta:
        template_name = 'tables/bootstrap_htmx.html'
        order_by = ('license',)  

class ClubEquipmentTable(tables.Table):

    name = tables.Column(verbose_name='Nazwa')
    producer = tables.Column(verbose_name='Producent')
    all_quantity = tables.Column(verbose_name='Ogólnie [szt]')
    available_quantity = tables.Column(accessor='available_quantity', verbose_name='Dostępne [szt]')
    description = tables.Column(verbose_name='Dodatkowe informacje')
    actions = tables.TemplateColumn(template_name='clubs/equipment_actions_column.html', orderable=False, verbose_name='')

    class Meta:
        model = Equipment
        template_name = 'tables/bootstrap_htmx.html'
        exclude = ['id', 'club']
        sequence = ('name', 'producer', 'all_quantity', 'available_quantity', 'description', 'actions')




class RentedEquipmentTable(tables.Table):
    player = tables.Column(verbose_name='Nazwisko Imię')
    quantity = tables.Column(verbose_name='Ilość [szt]')
    date_of_rental = tables.Column(verbose_name='Data wypożyczenia')
    description = tables.Column(verbose_name='Dodatkowe informacje')

    actions = tables.TemplateColumn(template_name='clubs/rented_equipment_actions_column.html', orderable=False, verbose_name='')

    class Meta:
        model = Rented_equipment
        template_name = 'tables/bootstrap_htmx.html'
        exclude = ['id', 'date_of_return', 'equipment']

class PlayersEquipmentTable(tables.Table):
    equipment = tables.Column(accessor='equipment__name',verbose_name='Sprzęt')
    quantity = tables.Column(verbose_name='Ilość')
    date_of_rental = tables.Column(verbose_name='Data wypożyczenia')
    description = tables.Column(verbose_name='Dodatkowe informacje')

    actions = tables.TemplateColumn(template_name='clubs/rented_equipment_actions_column.html', orderable=False, verbose_name='')

    class Meta:
        model = Rented_equipment
        template_name = 'tables/bootstrap_htmx.html'
        exclude = ['id', 'date_of_return', 'player']



# tables.py
from .models import Player

class AttendanceTable(tables.Table):
    player = tables.Column(verbose_name='Player Name')

    class Meta:
        model = Player  # Assuming you have a Player model
        fields = ['player']  # Add other fields as needed
        attrs = {"class": "table table-striped"}  # Optional: add Bootstrap styling

    def __init__(self, *args, **kwargs):
        attendance_dates = kwargs.pop('attendance_dates', [])
        for date in attendance_dates:
            self.base_columns[date.strftime('%Y-%m-%d')] = tables.Column(verbose_name=date.strftime('%Y-%m-%d'))
        self.base_columns['average'] = tables.Column(verbose_name='Average')
        super(AttendanceTable, self).__init__(*args, **kwargs)

class TeamStaffTable(tables.Table):
    name = tables.Column(verbose_name='Imię')
    surname = tables.Column(verbose_name='Nazwisko')
    date_of_birth = tables.Column(verbose_name='Data urodzin')

    actions = tables.TemplateColumn(template_name='clubs/team_player_actions_column.html', orderable=False, verbose_name='')

    class Meta:
        template_name = 'tables/bootstrap_htmx.html'
        order_by = ('surname',)  


class TeamEquipmentTable(tables.Table):
    player = tables.Column(verbose_name='Nazwisko Imię')
    equipment = tables.Column(accessor='equipment__name',verbose_name='Sprzęt')
    quantity = tables.Column(verbose_name='Ilość')
    date_of_rental = tables.Column(verbose_name='Data wypożyczenia')
    description = tables.Column(verbose_name='Dodatkowe informacje')
    class Meta:
        model = Rented_equipment
        template_name = 'tables/bootstrap_htmx.html'
        exclude = ['id', 'date_of_return']
