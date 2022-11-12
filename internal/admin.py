from django.contrib import admin
from .models import *
from .forms import *


# Register your models here.
@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    form = AdminNotificationForm