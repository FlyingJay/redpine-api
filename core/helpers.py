from django.db.models import Q
from maas.models import Mail
from core import models
import core.tasks
import datetime


def midnight_day_before(date):
    #End ticket sales at midnight the night before.
    midnight = datetime.datetime.combine(date, datetime.time(23,59,59,999999)) - datetime.timedelta(days=1)
    return midnight


def create_mail_from_template(**kwargs):
    """ creates an email message from a template & schedules it for delivery """
    mail = Mail.objects.create_from_template(**kwargs)
    core.tasks.send_mail(mail.id)
    return mail


import time
def print_runtime(f):
    def get_runtime(*args,**kwargs):
        start_time = time.time()
        x = f(*args,**kwargs)
        end_time = time.time()
        print("Elapsed Time = {0} seconds".format(end_time-start_time,2))
        return x
    return get_runtime


def has_subscription(user,account_type,product_name):
    kwargs = {
        'user': user,
        'account_type': account_type,
        'is_processed': True,
        'is_cancelled': False
    }

    if product_name == models.AccountSubscription.ULTIMATE: 
        return models.AccountSubscription.objects.filter(
            product_name=models.AccountSubscription.ULTIMATE,
            **kwargs).count() > 0

    elif product_name == models.AccountSubscription.MEMBER:
        return models.AccountSubscription.objects.filter(
            Q(product_name=models.AccountSubscription.ULTIMATE) | Q(product_name=models.AccountSubscription.MEMBER),
            **kwargs).count() > 0
