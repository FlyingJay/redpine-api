from django import forms
from django.conf import settings
from django.contrib.gis.forms import PointField
from django.contrib.gis.geos import GEOSException, GEOSGeometry
from django.utils.safestring import mark_safe
import json


class GeocodeLocationWidget(forms.Widget):
    def value_from_datadict(self, data, files, name):
        lat = data.get('lat')
        lng = data.get('lng')
        point_str = 'POINT({} {})'.format(lng, lat)
        return GEOSGeometry(point_str, srid=4326)

    def render(self, name, value, attrs=None):
        options = {
            'lat': 'null',
            'lng': 'null',
            'zoom': 14,
            'api_key': settings.GOOGLE_API_KEY
        }

        if value:
            options['lat'] = value.y
            options['lng'] = value.x

        raw_html = """
        <div style='width:400px;height:500px;'>
            <div style='margin-left:170px;' >
                <table>
                    <tr><td>Lat:</td><td><input type='text' id='id_lat' name='lat'></td></tr>
                    <tr><td>Lng:</td><td><input type='text' id='id_lng' name='lng'></td></tr>
                    <tr><td colspan="2"><a href='#' onclick='geocode()'>Geocode address</a></td></tr>
                </table>
            </div>
            <div id='map' style='width:100%;height:300px;margin-left:170px'></div>
        </div>
        <script>
        var map;
        var marker;

        function get(id) {{
            return document.getElementById(id);
        }}

        function initMap() {{
            var latLng = {{
                lat: {lat},
                lng: {lng}
            }};

            map = new google.maps.Map(document.getElementById('map'), {{
                'zoom': {zoom},
                'center': latLng
            }});

            if (latLng.lat && latLng.lng) {{
                marker = new google.maps.Marker({{
                    'position': latLng,
                    'map': map
                }});

                document.addEventListener('DOMContentLoaded', function () {{
                    get('id_lat').value = latLng.lat;
                    get('id_lng').value = latLng.lng;
                }});
            }}
        }}

        function geocode() {{
            var base = 'https://maps.googleapis.com/maps/api/geocode/json?';
            var address = encodeURIComponent(get('id_address').value);
            var city = $('#id_city > option[selected]').text()
            address += ' ' + city;
            var url = base + 'address=' + address + '&key={api_key}';

            $.get(url).then(function(data) {{
                var result = data.results[0];
                var geometry = result.geometry;
                var sw = geometry.viewport.southwest;
                var ne = geometry.viewport.northeast;
                var bounds = new google.maps.LatLngBounds(
                    new google.maps.LatLng(sw.lat, sw.lng),
                    new google.maps.LatLng(ne.lat, ne.lng)
                );

                if (marker) {{
                    marker.setMap(null);
                }}

                marker = new google.maps.Marker({{
                    'position': geometry.location,
                    'map': map
                }});

                map.fitBounds(bounds);

                get('id_lat').value = geometry.location.lat;
                get('id_lng').value = geometry.location.lng;
            }});
        }}
        </script>
        <script src='https://maps.googleapis.com/maps/api/js?key={api_key}&callback=initMap'></script>
        <script src='//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js'></script>
        """
        html = raw_html.format(**options)
        return mark_safe(html)

class GeocodeLocationForm(forms.ModelForm):
    location = PointField(widget=GeocodeLocationWidget)