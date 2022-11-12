from django.apps import AppConfig
from django.db.models.signals import post_migrate
import sys


def load_signals(*args, **kwargs):
    import internal.signals


class InternalConfig(AppConfig):
    name = 'internal'

    def ready(self):
        if sys.argv[1] in ['test', 'migrate']:
            post_migrate.connect(load_signals, sender=self)
        else:
            load_signals()
