import rest_framework_filters as filters
from django.contrib.auth.models import User

from core.filters import UserFilter
from socan import models


class VerificationFilter(filters.FilterSet):
    user = filters.RelatedFilter(UserFilter, queryset=User.objects.all(), distinct=True)

    class Meta:
        model = models.Verification
        fields = {
            'id': ['exact'],
            'is_successful': ['exact']
        }