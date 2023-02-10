import json
import typing

import requests
from django.conf import settings


def request_header(secret: str):
    return {"Authorization": secret, "Content-type": "application/json"}


def order_payload(
    amount: float,
    currency: str,
    description: str,
    merchant_id: str,
    approve_url: str,
    cancel_url: str,
    decline_url: str,
    language: str,
) -> str:
    ret = {
        "body": {
            "amount": amount,
            "currencyType": currency,
            "description": description,
            "language": language,
            "approveURL": approve_url,
            "cancelURL": cancel_url,
            "declineURL": decline_url,
        },
        "merchant": merchant_id,
    }

    print(ret)
    return json.dumps(ret)


def create_order(
    amount: float,
    currency: str = settings.PAYRIFF_CURRENCY,
    description: str = settings.PAYRIFF_ORDER_DESCRIPTION,
    secret: str = settings.PAYRIFF_SECRET,
    merchant_id: str = settings.PAYRIFF_MERCHANT_ID,
    timeout: int = settings.PAYRIFF_REQUEST_TIMEOUT,
    approve_url: str = settings.PAYRIFF_APPROVE_URL,
    cancel_url: str = settings.PAYRIFF_CANCEL_URL,
    decline_url: str = settings.PAYRIFF_DECLINE_URL,
    language: str = settings.PAYRIFF_LANGUAGE,
) -> typing.Tuple[str, str, str]:
    payload = order_payload(
        amount=amount,
        currency=currency,
        description=description,
        merchant_id=merchant_id,
        approve_url=approve_url,
        cancel_url=cancel_url,
        decline_url=decline_url,
        language=language,
    )
    r = requests.post(
        settings.PAYRIFF_CREATE_ORDER_URL,
        headers=request_header(secret),
        data=payload,
        timeout=timeout,
    )
    # raise an exception when status code is other than 200
    r.raise_for_status()

    payload = r.json()["payload"]
    return payload["orderId"], payload["sessionId"], payload["paymentUrl"]
