from django.conf import settings


def app_context(*args, **kwargs):
    return {
        'REDPINE_STATIC_FILES': settings.REDPINE_STATIC_FILES,
        'REDPINE_API_BASE_URL': settings.REDPINE_API_BASE_URL,
        'REDPINE_WEBAPP_BASE_URL': settings.REDPINE_WEBAPP_BASE_URL,
        'REDPINE_INSTAGRAM_URL': settings.REDPINE_INSTAGRAM_URL,
        'REDPINE_FACEBOOK_URL': settings.REDPINE_FACEBOOK_URL,
        'REDPINE_TWITTER_URL': settings.REDPINE_TWITTER_URL,
        'REDPINE_DOMAIN_NAME': settings.REDPINE_DOMAIN_NAME,
        'REDPINE_WEBAPP_URLS': settings.REDPINE_WEBAPP_URLS,
        'GOOGLE_PUBLIC_API_KEY': settings.GOOGLE_PUBLIC_API_KEY
    }