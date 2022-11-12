from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import *
from .forms import GeocodeLocationForm
from internal.admin_filters import CapacityListFilter, AmenityListFilter
from internal.exports import export_csv
from .admin_actions import refresh_subscription

admin.site.empty_value_display = 'Unknown'


class NotificationInline(admin.TabularInline):
    model = Notification
    extra = 1


class ActPaymentInline(admin.TabularInline):
    model = ActPayment
    extra = 1


class UserPaymentInline(admin.TabularInline):
    model = UserPayment
    can_delete = False
    extra = 1


@admin.register(ActPayment)
class ActPaymentAdmin(admin.ModelAdmin):
    actions = [export_csv]

    model = ActPayment
    list_filter = ('paid',)
    search_fields = (
        'band__name',
    )

    def has_add_permission(self, *args, **kwargs):
        return False
        

@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    actions = [export_csv]

    model = PaymentRequest
    list_filter = ('paid',)
    readonly_fields = [
        'user',
        'amount'
    ]  
    search_fields = (
        'user__username',
    )

    def has_add_permission(self, *args, **kwargs):
        return False


@admin.register(GenreParent)
class GenreParentAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('parent','genre',)
    search_fields = (
        'genre',
        'parent'
        )


class GenreParentInline(admin.TabularInline):
    model = Genre.genres.through
    fk_name = "genre"
    can_delete = False
    extra = 1


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('name',)
    inlines = (GenreParentInline,)
    search_fields = (
        'name',
        )


@admin.register(AdminMail)
class AdminMailAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('sender','template','recipient_email','data','resend')


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('sender','recipient_email','is_successful','data','join_token')

class GenreInline(admin.TabularInline):
    model = Genre
    extra = 1

@admin.register(Band)
class BandAdmin(admin.ModelAdmin): 
    actions = [export_csv]

    list_display = ('name','owner','hometown')
    search_fields = (
        'name',
        'owner__username',
        'genres__name',
        'hometown__name',
        )

    list_filter = (
        'is_featured',
        ('hometown', admin.RelatedOnlyFieldListFilter),
        ('genres', admin.RelatedOnlyFieldListFilter),
    )

class TicketInline(admin.TabularInline):
    model = Ticket
    readonly_fields = [
        'code',
        'pledge',
        'details'
    ]
    extra = 1


class WebTransactionInline(admin.TabularInline):
    model = Pledge
    exclude = [
        'customer',
        'user'
    ]
    readonly_fields = [
        'user_anchor',
        'total',
        'redpine_fee',
        'count',
        'campaign',
        'bands',
        'is_processed',
        'is_cancelled',
        'stripe_customer_anchor',
    ]
    extra = 1

    def has_delete_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False


class WebTransactionPurchaseInline(admin.TabularInline):
    model = PledgePurchase
    readonly_fields = [
        'item',
        'quantity',
    ]

    def has_delete_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False


@admin.register(Pledge)
class WebTransactionAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('user', 'campaign','count','total')
    inlines = (WebTransactionPurchaseInline,TicketInline)
    exclude = [
        'customer'
    ]
    readonly_fields = [
        'user_anchor',
        'total',
        'redpine_fee',
        'count',
        'campaign',
        'bands',
        'is_processed',
        'is_cancelled',
        'stripe_customer_anchor',
    ]
    search_fields = (
        'campaign__title',
        'user__username',
        )

    def has_delete_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False


class OrganizationInline(admin.TabularInline):
    model = Campaign.organizations.through
    extra = 1


class BandInline(admin.TabularInline):
    model = Campaign.bands.through
    extra = 1


class DocumentInline(admin.TabularInline):
    model = CampaignDocument
    extra = 1


class PhotoInline(admin.TabularInline):
    model = CampaignPhoto
    extra = 1


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('title', 'goal_amount', 'goal_count', 'funding_end', 'is_successful', 'service_fee')
    inlines = (BandInline, OrganizationInline, PurchaseItemInline, DocumentInline,)
    readonly_fields = [
        'get_attendee_csv_anchor',
        'total_earned',
        'tickets_sold',
        'campaign_page',
        'campaign_feed',
        'campaign_sales',
        'total_count',
        'total_raised'
    ]
    search_fields = (
        'title',
        'bands__name',
        'bands__owner__username',
        )


class TimeslotInline(admin.TabularInline):
    model = Timeslot
    extra = 1


class VenueManagersInline(admin.TabularInline):
    model = Venue.managers.through
    extra = 1


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('title', 'city', 'capacity', 'is_featured')
    inlines = (VenueManagersInline, TimeslotInline,)
    form = GeocodeLocationForm
    search_fields = (
        'title',
        'managers__username',
        )

    list_filter = (
        'is_hidden',
        ('city', admin.RelatedOnlyFieldListFilter),
        CapacityListFilter,
        ('genres', admin.RelatedOnlyFieldListFilter),
        AmenityListFilter
    )


@admin.register(VenueStats)
class VenueStatsAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('venue','historical_headcounts')
    search_fields = (
        'venue__title',
        )
    readonly_fields = [
        'historical_headcounts'
    ]

class OrganizationManagersInline(admin.TabularInline):
    model = Organization.managers.through
    extra = 1

class OrganizationBandsInline(admin.TabularInline):
    model = Organization.bands.through
    extra = 1


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('title', 'city',)
    inlines = (OrganizationManagersInline, OrganizationBandsInline)
    form = GeocodeLocationForm
    search_fields = (
        'title',
        'managers__username',
        )


@admin.register(Opening)
class OpeningAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('title','timeslot','is_open')
    search_fields = (
        'title',
        'timeslot__venue__title',
        )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    actions = [export_csv]

    form = GeocodeLocationForm
    search_fields = (
        'name',
        'province__name',
        'province__country__name'
        )

    list_filter = (
        ('province', admin.RelatedOnlyFieldListFilter),
    )


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    actions = [export_csv]

    search_fields = (
        'name',
        'country__name',
        )

    list_filter = (
        ('country', admin.RelatedOnlyFieldListFilter),
    )

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    actions = [export_csv]

    search_fields = (
        'name',
        )


class CampaignInline(admin.TabularInline):
    model = Tour.campaigns.through
    extra = 1


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    actions = [export_csv]
    list_display = ('title', 'headliner', 'created_by',)
    inlines = (CampaignInline,)
    search_fields = (
        'title',
        )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_filter = ('is_artist','is_member_artist','is_ultimate_artist','is_venue','is_member_venue','is_ultimate_venue',)
    search_fields = ('user__username',)


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    actions = [export_csv]

    readonly_fields = [
        'campaign_feed',
        'created',
        'modified',
        'user',
        'organization',
        'venue',
        'campaign',
        'when',
        'who',
        'extra_details'
    ]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    actions = [export_csv]

    readonly_fields = [
        'pledge'
    ]
    search_fields = (
        'pledge__campaign__title',
        'pledge__user__username',
        )


class SurveyResponseInline(admin.TabularInline):
    model = SurveyResponse
    readonly_fields = [
        'user', 
        'response'
    ]
    extra = 1


@admin.register(SurveyQuestion)
class SurveyQuestion(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('text',)
    inlines = (SurveyResponseInline,)
    search_fields = (
        'text',
        )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('profile','text','subject_type','is_read','created_date',)

    list_filter = (
        ('subject_type'),
    )


@admin.register(Hint)
class HintAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('text',)
    search_fields = (
        'text',
        )


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    actions = [export_csv]


@admin.register(AccountSubscription)
class AccountSubscriptionAdmin(admin.ModelAdmin):
    actions = [export_csv,refresh_subscription]

    list_display = ('user','product_name','account_type','is_cancelled','is_processed','is_processing_failed',)

    list_filter = (
        ('product_name'),
        ('account_type'),
        ('is_cancelled'),
        ('is_processed'),
        ('is_processing_failed'),
    )
    search_fields = (
        'user__username',
        ),


@admin.register(BandSubscription)
class BandSubscriptionAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('band','user','subscribed_date',)


@admin.register(OrganizationSubscription)
class OrganizationSubscriptionAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('organization','user','subscribed_date',)


@admin.register(VenueSubscription)
class VenueSubscriptionAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('venue','user','subscribed_date',)


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    actions = [export_csv]


class AppCashTransactionPurchaseInline(admin.TabularInline):
    model = AppCashTransactionPurchase


@admin.register(AppCashTransaction)
class AppCashTransactionAdmin(admin.ModelAdmin):
    inlines = [
        AppCashTransactionPurchaseInline
    ]


class AppCardTransactionPurchaseInline(admin.TabularInline):
    model = AppCardTransactionPurchase


@admin.register(AppCardTransaction)
class AppCardTransactionAdmin(admin.ModelAdmin):
    inlines = [
        AppCardTransactionPurchaseInline
    ]

@admin.register(NavigationFeedback)
class NavigationFeedbackAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('created_by','category','text',)

@admin.register(VenueToBandReview)
class VenueToBandReviewAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('band','reviewer','overall','is_completed','is_responded',)

@admin.register(BandToBandReview)
class BandToBandReviewAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('band','reviewer','overall','is_completed','is_responded',)

@admin.register(BandToVenueReview)
class BandToVenueReviewAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('venue','reviewer','overall','is_completed','is_responded',)