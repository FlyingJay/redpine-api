from django.contrib import admin
from .models import *

class ChargeInline(admin.TabularInline):
    model = Charge
    exclude = [ 'square_response' ]

    readonly_fields = [
        'created_at',
        'amount',
        'currency',
        'success',
        'square_id',
        'square_anchor',
        'debug_charge',
    ]

    def has_delete_permission(*args, **kwargs):
        return False

    def has_add_permission(*args, **kwargs):
        return False


class CardInline(admin.TabularInline):
    model = Card

    readonly_fields = [
        'square_id',
        'customer',
        'brand',
        'exp_month',
        'exp_year',
    ]

    def has_delete_permission(*args, **kwargs):
        return False

    def has_add_permission(*args, **kwargs):
        return False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'square_id',
        'created_at'
    ]

    readonly_fields = [
        'square_id',
        'email',
        'created_at',
        'square_anchor',
    ]

    inlines = [
        ChargeInline,
        CardInline
    ]

    def has_delete_permission(*args, **kwargs):
        return False