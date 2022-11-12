from maas.models import Mail
import internal.tasks


def create_mail_from_template(**kwargs):
    """ creates an email message from a template & schedules it for delivery """
    mail = Mail.objects.create_from_template(**kwargs)
    internal.tasks.send_mail(mail.id)
    return mail