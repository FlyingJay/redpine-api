from django.contrib import admin
from .models import *

class ChargeInline(admin.TabularInline):
    model = Charge
    exclude = [ 'stripe_response' ]

    readonly_fields = [
        'created_at',
        'amount',
        'currency',
        'success',
        'stripe_id',
        'stripe_anchor',
        'debug_charge',
    ]

    def has_delete_permission(*args, **kwargs):
        return False

    def has_add_permission(*args, **kwargs):
        return False

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'stripe_id',
        'created_at'
    ]

    readonly_fields = [
        'stripe_id',
        'email',
        'created_at',
        'stripe_anchor',
    ]

    inlines = [
        ChargeInline
    ]

    def has_delete_permission(*args, **kwargs):
        return False