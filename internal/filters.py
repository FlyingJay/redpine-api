from django.contrib.gis.measure import D
from core import models as core_models


def gps_searchable(self,queryset,location):
    #If center and radius are both included in a request, reduce the queryset
    center = self.request.GET.get('center')#City id, center of the circle
    radius = self.request.GET.get('radius')#Radius (km)

    if center and radius:
        current_city = core_models.City.objects.get(pk=center)        
        #Avoids failure if city has no coordinates.
        if current_city.location:
        	queryset = queryset.filter(**{location:(current_city.location, D(km=radius))})

    return queryset