from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'connection', ConnectionViewSet)

urlpatterns = []

if settings.ENV == settings.ENVS.DEVELOPMENT:
    urlpatterns += static(settings.MEDIA_URL.replace(settings.REDPINE_API_BASE_URL, ''), document_root=settings.MEDIA_ROOT)