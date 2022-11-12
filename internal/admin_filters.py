from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class CapacityListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('capacity')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'capacity'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('< 100', _('< 100')),
            ('100 - 250', _('100 - 250')),
            ('250 - 700', _('250 - 700')),
            ('700+', _('700+')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '< 100':
            return queryset.filter(capacity__lt=100)
        if self.value() == '100 - 250':
            return queryset.filter(capacity__gte=100, capacity__lte=250)
        if self.value() == '250 - 700':
            return queryset.filter(capacity__gte=250, capacity__lte=700)
        if self.value() == '700+':
            return queryset.filter(capacity__gte=700)


class AmenityListFilter(admin.SimpleListFilter):
    title = _('amenities')
    parameter_name = 'amenities'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)

        if qs.filter(has_wifi=True).exists():
            yield ('has_wifi', _('wifi'))
        if qs.filter(is_accessible_by_transit=True).exists():
            yield ('is_accessible_by_transit', _('accessible by transit'))
        if qs.filter(has_atm_nearby=True).exists():
            yield ('has_atm_nearby', _('atm nearby'))
        if qs.filter(has_free_parking_nearby=True).exists():
            yield ('has_free_parking_nearby', _('free parking nearby'))
        if qs.filter(has_paid_parking_nearby=True).exists():
            yield ('has_paid_parking_nearby', _('paid parking nearby'))
        if qs.filter(is_wheelchair_friendly=True).exists():
            yield ('is_wheelchair_friendly', _('wheelchair friendly'))
        if qs.filter(allows_smoking=True).exists():
            yield ('allows_smoking', _('allows smoking'))
        if qs.filter(allows_all_ages=True).exists():
            yield ('allows_all_ages', _('allows all ages'))
        if qs.filter(has_stage=True).exists():
            yield ('has_stage', _('stage'))
        if qs.filter(has_microphones=True).exists():
            yield ('has_microphones', _('microphones'))
        if qs.filter(has_drum_kit=True).exists():
            yield ('has_drum_kit', _('drum kit'))
        if qs.filter(has_piano=True).exists():
            yield ('has_piano', _('piano'))
        if qs.filter(has_wires_and_cables=True).exists():
            yield ('has_wires_and_cables', _('wires and cables'))
        if qs.filter(has_front_load_in=True).exists():
            yield ('has_front_load_in', _('front load in'))
        if qs.filter(has_back_load_in=True).exists():
            yield ('has_back_load_in', _('back load in'))
        if qs.filter(has_soundtech=True).exists():
            yield ('has_soundtech', _('soundtech'))
        if qs.filter(has_lighting=True).exists():
            yield ('has_lighting', _('lighting'))
        if qs.filter(has_drink_tickets=True).exists():
            yield ('has_drink_tickets', _('drink tickets'))
        if qs.filter(has_meal_vouchers=True).exists():
            yield ('has_meal_vouchers', _('meal vouchers'))
        if qs.filter(has_merch_space=True).exists():
            yield ('has_merch_space', _('merch space'))
        if qs.filter(has_cash_box=True).exists():
            yield ('has_cash_box', _('cash box'))
        if qs.filter(has_float_cash=True).exists():
            yield ('has_float_cash', _('float cash'))

    def queryset(self, request, queryset):
        if self.value() == 'has_wifi':
            return queryset.filter(has_wifi=True)
        if self.value() == 'is_accessible_by_transit':
            return queryset.filter(is_accessible_by_transit=True)
        if self.value() == 'has_atm_nearby':
            return queryset.filter(has_atm_nearby=True)
        if self.value() == 'has_free_parking_nearby':
            return queryset.filter(has_free_parking_nearby=True)
        if self.value() == 'has_paid_parking_nearby':
            return queryset.filter(has_paid_parking_nearby=True)
        if self.value() == 'is_wheelchair_friendly':
            return queryset.filter(is_wheelchair_friendly=True)
        if self.value() == 'allows_smoking':
            return queryset.filter(allows_smoking=True)
        if self.value() == 'allows_all_ages':
            return queryset.filter(allows_all_ages=True)
        if self.value() == 'has_stage':
            return queryset.filter(has_stage=True)
        if self.value() == 'has_microphones':
            return queryset.filter(has_microphones=True)
        if self.value() == 'has_drum_kit':
            return queryset.filter(has_drum_kit=True)
        if self.value() == 'has_piano':
            return queryset.filter(has_piano=True)
        if self.value() == 'has_wires_and_cables':
            return queryset.filter(has_wires_and_cables=True)
        if self.value() == 'has_front_load_in':
            return queryset.filter(has_front_load_in=True)
        if self.value() == 'has_back_load_in':
            return queryset.filter(has_back_load_in=True)
        if self.value() == 'has_soundtech':
            return queryset.filter(has_soundtech=True)
        if self.value() == 'has_lighting':
            return queryset.filter(has_lighting=True)
        if self.value() == 'has_drink_tickets':
            return queryset.filter(has_drink_tickets=True)
        if self.value() == 'has_meal_vouchers':
            return queryset.filter(has_meal_vouchers=True)
        if self.value() == 'has_float_cash':
            return queryset.filter(has_float_cash=True)
