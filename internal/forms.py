from django import forms
from .models import *
import django.apps


class AdminNotificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        models = django.apps.apps.get_models()
        choices = ['{}.{}'.format(m.__module__, m.__name__) for m in models]
        self.fields['model'] = forms.ChoiceField(choices=[(c, c) for c in choices])

    class Meta:
        model = AdminNotification
        exclude = []