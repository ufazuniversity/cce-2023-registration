import json
import typing

import requests
from django.conf import settings

KEY_ORDER_ID = "orderID"
KEY_SESSION_ID = "sessionId"
KEY_AMOUNT = "amount"
KEY_MERCHANT_ID = "merchant"
KEY_DESCRIPTION = "description"
KEY_CURRENCY_TYPE = "currencyType"
KEY_LANGUAGE = "language"
KEY_APPROVE_URL = "approveURL"
KEY_DECLINE_URL = "declineURL"
KEY_CANCEL_URL = "cancelURL"
KEY_ORDER_STATUS = "orderStatus"


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
            KEY_AMOUNT: amount,
            KEY_CURRENCY_TYPE: currency,
            KEY_DESCRIPTION: description,
            KEY_LANGUAGE: language,
            KEY_APPROVE_URL: approve_url,
            KEY_CANCEL_URL: cancel_url,
            KEY_DECLINE_URL: decline_url,
        },
        KEY_MERCHANT_ID: merchant_id,
    }

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


def get_order_result_details(payload: str) -> typing.Tuple[str, str, str]:
    data = json.loads(payload)['payload']
    order_id = data[KEY_ORDER_ID]
    session_id = data[KEY_SESSION_ID]
    status = data[KEY_ORDER_STATUS]
    return order_id, session_id, status
