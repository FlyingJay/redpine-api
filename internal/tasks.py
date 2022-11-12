from background_task import background
from maas.models import Mail


@background(schedule=0)
def send_mail(mail_id):
    """ schedules an email for sending """
    mail = Mail.objects.get(id=mail_id)
    mail.send()