from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.serializers import serialize
from internal.helpers import create_mail_from_template
from .models import AdminNotification


@receiver(post_save)
def send_admin_notifications(sender, instance, created, **kwargs):
    full_path = '{}.{}'.format(sender.__module__, sender.__name__)
    notifications = AdminNotification.objects.filter(model=full_path)
    for notification in notifications:
        if ((created and notification.on_create)
            or (not created and notification.on_update)):
            fields = notification.fields.split(',')
            serialized = serialize('yaml', [instance], fields=fields)
            create_mail_from_template(
                recipient=notification.email,
                subject='RedPine state monitor -- {} has been {}'.format(sender.__name__, 'created' if created else 'updated'),
                template='mail/admin_notification.html',
                context={
                    'summary': 'A {} ({}) has been {}'.format(sender.__name__, full_path, 'created' if created else 'updated'),
                    'model': serialized
                }
            )
