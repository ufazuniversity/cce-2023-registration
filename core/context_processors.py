from django.conf import settings


def kapital_ecommerce_defaults(request):
    return {
        "KAPITAL_ECOMMERCE_DEFAULTS": {
            "CURRENCY": settings.CURRENCY,
            "CURRENCY_SYMBOL": settings.CURRENCY_SYMBOL,
        }
    }