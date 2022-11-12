from django.contrib import admin
from internal.admin_filters import CapacityListFilter, AmenityListFilter
from internal.exports import export_csv
from .forms import GeocodeLocationForm
from .models import *
from .admin_actions import update_artist, update_venue

admin.site.empty_value_display = 'Unknown'


@admin.register(ArtistImport)
class ArtistImportAdmin(admin.ModelAdmin):
    actions = [export_csv]  

@admin.register(VenueImport)
class VenueImportAdmin(admin.ModelAdmin):
    actions = [export_csv]

@admin.register(EventImport)
class EventImportAdmin(admin.ModelAdmin):
    actions = [export_csv]

    search_fields = (
        'profile_link',
        )


@admin.register(Subscription)
class ProfileAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('user','square_customer','is_processed','is_cancelled','is_processing_failed','created_date',)

    search_fields = (
        'user__username',
        'user__email',
        'square_customer',
        )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('user','referrer','premium_months','has_lifetime_membership','created','modified',)

    search_fields = (
        'user__username',
        'user__email',
        )

    readonly_fields = [
        'referral_url',
    ]


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('name','email','phone','likes',)
    form = GeocodeLocationForm

    search_fields = (
        'name',
        'email',
        'facebook'
        )


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('name','email','phone','likes',)

    search_fields = (
        'name',
        'email',
        'facebook',
        )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('link',)

    search_fields = (
        'artists__name',
        'venues__name',
        'artists__facebook',
        'venues__facebook',
        'link',
        )


@admin.register(ArtistUpdate)
class ArtistUpdateAdmin(admin.ModelAdmin):
    actions = [export_csv,update_artist]

    list_display = ('artist','is_applied',)
    search_fields = (
        'artist__name',
        )

    list_filter = (
        'is_applied',
    )


@admin.register(VenueUpdate)
class VenueUpdateAdmin(admin.ModelAdmin):
    actions = [export_csv,update_venue]

    list_display = ('venue','is_applied',)
    search_fields = (
        'venue__name',
        )

    list_filter = (
        'is_applied',
    )


@admin.register(UserQuery)
class UserQueryAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('user','model','genre','city','name','results_count',)
    search_fields = (
        'user__username',
        'user__email',
        'name',
        'genre__name',
        'city__name',
        )

    list_filter = (
        'model',
    )