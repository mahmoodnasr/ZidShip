from django.conf import settings


def global_settings(request):
    """Adds global templates parameters to the templates"""

    d = {
        'STATIC_URL': settings.STATIC_URL,
        'APP_NAME': settings.APP_NAME
    }

    return d
