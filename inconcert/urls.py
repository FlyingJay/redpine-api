"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.routers import DefaultRouter
from inconcert.auth.views import *
from .views import *

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'artists', ArtistViewSet)
router.register(r'venues', VenueViewSet)
router.register(r'events', EventViewSet)
router.register(r'artist-updates', ArtistUpdateViewSet)
router.register(r'venue-updates', VenueUpdateViewSet)

urlpatterns = [
    url(r'^me/', MeView.as_view(), name='v1-inconcert-me'),
    url(r'^registration/password/', PasswordRegistrationView.as_view(), name='v1-inconcert-registration-password'),
    url(r'^auth/password/', PasswordAuthView.as_view(), name='v1-inconcert-auth-password')	,
    url(r'^auth/logout/', LogoutView.as_view(), name='v1-inconcert-auth-logout'),
]

if settings.ENV == settings.ENVS.DEVELOPMENT:
    urlpatterns += static(settings.MEDIA_URL.replace(settings.REDPINE_API_BASE_URL, ''), document_root=settings.MEDIA_ROOT)