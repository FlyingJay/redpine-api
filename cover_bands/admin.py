from django.contrib import admin
from internal.admin_filters import CapacityListFilter, AmenityListFilter
from internal.exports import export_csv
from .models import *


admin.site.empty_value_display = 'Unknown'

@admin.register(CoverLead)
class CoverLeadAdmin(admin.ModelAdmin):
    actions = [export_csv]

    list_display = ('email','price','message',)
    search_fields = (
        'email',
        'price',
        'message',
        )
