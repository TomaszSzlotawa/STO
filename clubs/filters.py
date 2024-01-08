# products/filters.py
from decimal import Decimal
from django.db.models import Q
import django_filters
from .models import Player

class ShowHiddenFilter(django_filters.FilterSet):
    hidden_boolean = django_filters.BooleanFilter(method='show_hidden', label='Pokaż ukrytych zawodników')

    class Meta:
        model = Player
        fields = ['hidden']

    def universal_search(self, queryset, name, value):
        print("name:",name)
        print("value:",value)
        print("qu:",queryset)
        return