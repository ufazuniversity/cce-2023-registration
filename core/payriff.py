import typing

import requests
import json
import logging
from django.conf import settings


def request_header(secret: str):
    return {"Authorization": secret, "Content-type": "application/json"}


def order_payload(
    amount: float,
    currency: str,
    description: str,
    merchant_id: str,
    approveURL: str,
    cancelURL: str,
    declineURL: str,
    language: str,
) -> str:
    ret = {
        "body": {
            "amount": amount,
            "currencyType": currency,
            "description": description,
            "language": language,
            "approveURL": approveURL,
            "cancelURL": cancelURL,
            "declineURL": declineURL,
        },
        "merchant": merchant_id,
    }
    return json.dumps(ret)


def create_order(
    amount: float,
    currency: str = settings.PAYRIFF_CURRENCY,
    description: str = settings.PAYRIFF_ORDER_DESCRIPTION,
    secret: str = settings.PAYRIFF_SECRET,
    merchant_id: str = settings.PAYRIFF_MERCHANT_ID,
    timeout: int = settings.PAYRIFF_REQUEST_TIMEOUT,
    approveURL: str = settings.PAYRIFF_APPROVE_URL,
    cancelURL: str = settings.PAYRIFF_CANCEL_URL,
    declineURL: str = settings.PAYRIFF_DECLINE_URL,
    language: str = settings.PAYRIFF_LANGUAGE,
) -> typing.Tuple[str, str, str]:
    payload = order_payload(
        amount=amount,
        currency=currency,
        description=description,
        merchant_id=merchant_id,
        approveURL=approveURL,
        cancelURL=cancelURL,
        declineURL=declineURL,
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
