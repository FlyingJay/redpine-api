from django.contrib.auth.models import User
from django.dispatch import receiver
from directmessages.apps import Inbox
from directmessages.models import Message
from directmessages.signals import message_read, message_sent
from core import mail
from datetime import datetime


@receiver(message_sent)
def message_reminder_email(sender, from_user, to, **kwargs):
	min_email_delay = 180#seconds
	messages = Inbox.get_conversation(user1=from_user,user2=to).order_by('-sent_at')

	if to.profile.receives_emails:
		if messages.count() == 1:
			mail.new_message_conversation(email=to.email, data={'user':from_user,'text':sender})
		else: 
			last_message = messages[1]
			if (datetime.now() - last_message.sent_at).seconds >= min_email_delay:
				mail.new_message_reminder(email=to.email, data={'user':from_user,'text':sender})