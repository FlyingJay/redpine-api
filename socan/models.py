from django.contrib.auth.models import User
from django.db import models


class Verification(models.Model):
	number = models.CharField(max_length=16,help_text='The SOCAN member number submitted in the request.')
	legal_name = models.CharField(max_length=200)
	response_code = models.CharField(max_length=10)
	is_successful = models.BooleanField(default=False)
