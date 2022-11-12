from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel
from django.contrib.gis.db.models import PointField
from django.utils.html import mark_safe


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


class CoverLead(ArchiveOnDelete, TimeStampedModel):
    email = models.CharField(max_length=200, blank=True, null=True, default=None)
    price = models.CharField(max_length=100, db_index=True)
    message = models.TextField(max_length=10000, null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.email
