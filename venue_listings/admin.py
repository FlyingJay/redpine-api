from django.contrib import admin
from internal.admin_filters import CapacityListFilter, AmenityListFilter
from .models import *

admin.site.empty_value_display = 'Unknown'


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):

    def has_delete_permission(self, *args, **kwargs):
        return False

    def has_edit_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False

    list_display = ('title', 'city', 'capacity')
    search_fields = (
        'title',
        'city__name',
        'city__province__name',
        'city__province__country__name',
        )

    list_filter = (
        ('city', admin.RelatedOnlyFieldListFilter),
        CapacityListFilter,
        ('primary_genre', admin.RelatedOnlyFieldListFilter),
        ('secondary_genre', admin.RelatedOnlyFieldListFilter),
        AmenityListFilter
    )

    exclude = [
        'core_id',
        'location',
        'archived',

        'address',
        'description',
        
        'website',
        'facebook',
        'twitter',
        'soundcloud',
        'instagram',
        'youtube',
        'spotify',
        'bandcamp',

        'has_wifi',
        'is_accessible_by_transit',
        'has_atm_nearby',
        'has_free_parking_nearby',
        'has_paid_parking_nearby',
        'is_wheelchair_friendly',
        'allows_smoking',
        'allows_all_ages',
        'has_stage',
        'has_microphones',
        'has_drum_kit',
        'has_piano',
        'has_wires_and_cables',
        'has_front_load_in',
        'has_back_load_in',
        'has_soundtech',
        'has_lighting',
        'has_drink_tickets',
        'has_meal_vouchers',
        'has_merch_space',
        'has_cash_box',
        'has_float_cash'
    ]

    readonly_fields = [
        'title',
        'capacity',
        'city',
        'province',
        'postal_code',
        'primary_genre',
        'secondary_genre',
        'email_address',
        'facebook_link',
        'website_link',
        'website_embed'
    ]  
