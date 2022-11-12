from django.shortcuts import render
from analysis import tasks, permissions
from analysis.models import *
from analysis.serializers import *
from rest_framework import viewsets, response, generics, decorators, permissions as rest_framework_permissions, exceptions as rest_framework_exceptions
from django.core import serializers
from django.db.models import Count


class CampaignFactViewSet(viewsets.ModelViewSet):
    queryset = Campaign_Fact.objects.filter(archived=False)
    serializer_class = CampaignFactSerializer
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.AnalysisPermission,
    ]

class PledgeFactViewSet(viewsets.ModelViewSet):
    queryset = Pledge_Fact.objects.filter(archived=False)
    serializer_class = PledgeFactSerializer
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.AnalysisPermission,
    ]
    filter_fields = {
        'user': ('in', 'exact',),
        'band': ('in', 'exact',),
    }

    @decorators.detail_route(methods=['get'])
    def related_bands(self, request, pk=None):
        if(request.GET.get('core')):
            pk = Band.objects.filter(core_id=pk)

        pledge_facts = Pledge_Fact.objects.filter(band=pk).distinct('user')

        fans = []
        for pledge_fact in pledge_facts:
            fans.append(pledge_fact.user)

        related_bands = Pledge_Fact.objects.filter(user__in=fans).exclude(band=pk).annotate(Count('band',distinct=True)).order_by()

        bands = []
        relation_strength = []
        for related_band in related_bands:
            if(bands == [] or not bands[-1] == str(related_band.band.id)):
                bands.append(str(related_band.band.id))
                relation_strength.append(related_band.count)
            else:
                relation_strength[-1] = relation_strength[-1] + related_band.count

        band_info = Band.objects.filter(id__in=bands)

        index = 0
        for band in band_info:
            band_info[index].strength = relation_strength[index]
            index = index + 1

        strength_sorted = sorted(band_info, key=lambda x: x.strength, reverse=True)
        serialized = RelatedBandSerializer(strength_sorted,many=True)
        
        return response.Response(serialized.data, status=200)

class TimeslotFactViewSet(viewsets.ModelViewSet):
    queryset = Timeslot_Fact.objects.filter(archived=False)
    serializer_class = TimeslotFactSerializer
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.AnalysisPermission,
    ]

