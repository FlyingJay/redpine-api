from django.db import models

#################
# HELPER MODELS #
#################

class ArchiveableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archived=False)


class ArchiveOnDelete(models.Model):
    objects = ArchiveableManager()
    all_objects = models.Manager()
    archived = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        self.archived = True
        self.save()

    class Meta:
        abstract = True


################
# OTHER MODELS #
################

class AdminNotification(models.Model):
    email = models.EmailField(help_text='The user to send the email to')
    model = models.CharField(max_length=100, help_text='The model to monitor')
    fields = models.CharField(max_length=200, help_text='Comma separated list of fields to serialize on the model')
    on_create = models.BooleanField(default=False, help_text='Send a notification on create')
    on_update = models.BooleanField(default=False, help_text='Send a notification on update')

    def __str__(self):
        return '{} - {}'.format(self.email, self.model)

