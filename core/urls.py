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
from django.contrib import admin
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from core.auth.views import *
from .views import *
from analysis.urls import router as analysis_router
from spotify.urls import router as spotify_router
from maas.views import WebhookView as MailWebhookView
from django.views.decorators.csrf import csrf_exempt
from venue_listings.auth import views as venue_listings_views 
from venue_listings.urls import router as venue_listings_router
from cover_bands.urls import router as cover_bands_router
from inconcert.urls import router as inconcert_router
from inconcert.urls import urlpatterns as inconcert_urlpatterns


router = DefaultRouter()
router.register(r'global-settings', GlobalSettingsViewSet)
router.register(r'users', UserViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'bands', BandViewSet)
router.register(r'campaigns', CampaignViewSet)
router.register(r'campaign-bands', CampaignBandViewSet)
router.register(r'purchase-items', PurchaseItemViewSet)
router.register(r'campaign-feed', CampaignFeedViewSet)
router.register(r'campaign-documents', CampaignDocumentViewSet)
router.register(r'pledges', WebTransactionViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'guest-list', GuestListViewSet)
router.register(r'tour-campaigns', TourCampaignViewSet)
router.register(r'tours', TourViewSet)
router.register(r'venues', VenueViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'organization-bands', OrganizationBandViewSet)
router.register(r'cities', CityViewSet)
router.register(r'provinces', ProvinceViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'timeslots', TimeslotViewSet)
router.register(r'openings', OpeningViewSet)
router.register(r'events', EventViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'invitations', InvitationViewSet)
router.register(r'hints', HintViewSet)
router.register(r'booking-requests', BookingRequestViewSet)
router.register(r'band-to-band-reviews', BandToBandReviewViewSet)
router.register(r'band-to-venue-reviews', BandToVenueReviewViewSet)
router.register(r'venue-to-band-reviews', VenueToBandReviewViewSet) 
router.register(r'survey-response', SurveyResponseViewSet)
router.register(r'act-payments', ActPaymentViewSet)
router.register(r'payment-requests', PaymentRequestViewSet)
router.register(r'rewards', RewardViewSet)
router.register(r'account-subscriptions', AccountSubscriptionViewSet)
router.register(r'band-subscriptions', BandSubscriptionViewSet)
router.register(r'organization-subscriptions', OrganizationSubscriptionViewSet)
router.register(r'venue-subscriptions', VenueSubscriptionViewSet)
router.register(r'app-cash-transactions', AppCashTransactionViewSet)
router.register(r'app-card-transactions', AppCardTransactionViewSet)
router.register(r'push-tokens', PushTokenViewSet)
router.register(r'messages', MessagesViewSet)
router.register(r'navigation-feedback', NavigationFeedbackViewSet)


urlpatterns = [
    url(r'^v1/', include(router.urls, namespace='api',)),
    url(r'^v1/analysis/', include(analysis_router.urls, namespace='analysis-api',)),
    url(r'^v1/spotify/', include(spotify_router.urls, namespace='spotify-api',)),
    url(r'^v1/registration/password/', PasswordRegistrationView.as_view(), name='v1-registration-password'),
    url(r'^v1/registration/facebook/', FacebookRegistrationView.as_view(), name='v1-registration-facebook'),
    url(r'^v1/auth/password/', PasswordAuthView.as_view(), name='v1-auth-password'),
    url(r'^v1/auth/facebook/', FacebookAuthView.as_view(), name='v1-auth-facebook'),
    url(r'^v1/auth/forgot-password/', ForgotPasswordView.as_view(), name='v1-auth-forgot-password'),
    url(r'^v1/auth/reset-password/', ResetPasswordView.as_view(), name='v1-auth-forgot-password'),
    url(r'^v1/auth/confirm-email/', ConfirmEmailView.as_view(), name='v1-auth-confirm-email'),
    url(r'^v1/auth/logout/', LogoutView.as_view(), name='v1-auth-logout'),
    url(r'^v1/just-tickets/', JustTicketsView.as_view(), name='v1-just-tickets'),
    url(r'^v1/show-requests/', ShowRequestView.as_view(), name='v1-show-requests'),
    url(r'^v1/tasks/', TaskView.as_view(), name='v1-tasks'),
    url(r'^v1/me/', MeView.as_view(), name='v1-me'),
    url(r'^v1/job-runner-status/', JobRunnerStatusView.as_view(), name='v1-job-runner-status'),
    url(r'^mail/webhook/', csrf_exempt(MailWebhookView.as_view())),
    url(r'^admin/', admin.site.urls),
    url(r'^square-pos-callback/', SquarePOSCallbackView.as_view()),

    url(r'^v1/cover-bands/', include(cover_bands_router.urls, namespace='cover-bands-api',)),
    url(r'^v1/inconcert/', include([*inconcert_router.urls, *inconcert_urlpatterns], namespace='inconcert-api')),

    url(r'^v1/venue-listings/', include(venue_listings_router.urls, namespace='venue-listings-api',)),
    url(r'^v1/venue-listings/registration/password/', venue_listings_views.PasswordRegistrationView.as_view(), name='v1-venue-listings-registration-password'),
]


if settings.ENV == settings.ENVS.DEVELOPMENT:
    urlpatterns += static(settings.MEDIA_URL.replace(settings.REDPINE_API_BASE_URL, ''), document_root=settings.MEDIA_ROOT)
    urlpatterns += [url(r'^debug/email/', EmailDebugView.as_view())]