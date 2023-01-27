import requests
import json
import dataclasses
from django.conf import settings

AUTHORIZATION_HEADER = "Authorization"


def request_header(secret: str = settings.PAYRIFF_SECRET):
    return {AUTHORIZATION_HEADER: secret, "Content-type": "application/json"}


def order_json_payload(
    amount: float,
    currency: str = settings.ORDER_CURRENCY,
    description: str = settings.ORDER_DESCRIPTION,
    merchant_id=settings.PAYRIFF_MERCHANT_ID,
):
    pass


def post_create_order(amount: float):
    r = requests.post(
        settings.PAYRIFF_BASE_URL,
        headers=request_header(settings.secret),
        data=order_json_payload(amount),
    )
