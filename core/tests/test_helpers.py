from django.test import TestCase
from unittest.mock import patch
from core.tests import helpers
import core.helpers


class CreateMailFromTemplateTest(TestCase):
    def setUp(self):
        pass

    def test_schedules_mail_delivery(self):
        """ should schedule mail delivery when called """
        mail = core.helpers.create_mail_from_template(
            recipient='test',
            subject='Your RedPine Email',
            template='mail/charge_success.html',
            context={}
        )

        helpers.verify_task('core.tasks.send_mail', [[mail.id], {}])
