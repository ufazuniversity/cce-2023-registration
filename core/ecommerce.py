import requests
from django.conf import settings
from django.template import loader
import dataclasses
from xml.etree import ElementTree as ET

CREATE_ORDER_TEMPLATE_NAME = "ecommerce/create-order.xml"
CREATE_ORDER_HEADERS = {"Content-Type": "application/xml"}


@dataclasses.dataclass
class CreateOrderPayload:
    amount: int
    approve_url: str
    cancel_url: str
    decline_url: str
    description: str
    merchant_id: str
    currency: str

    def to_xml(self):
        return loader.render_to_string(
            CREATE_ORDER_TEMPLATE_NAME, dataclasses.asdict(self)
        )


def create_order(
    amount,
    approve_url=settings.KB_ECOMM_ORDER_APPROVE_URL,
    cancel_url=settings.KB_ECOMM_ORDER_CANCEL_URL,
    decline_url=settings.KB_ECOMM_ORDER_DECLINE_URL,
    description=settings.KB_ECOMM_ORDER_DESCRIPTION,
    url=settings.KB_ECOMM_URL,
    merchant_id=settings.KB_ECOMM_MERCHANT_ID,
    currency=settings.KB_ECOMM_CURRENCY,
):
    """Sending order request to Kapital Ecommerce API"""
    payload = CreateOrderPayload(
        amount, approve_url, cancel_url, decline_url, description, merchant_id, currency
    ).to_xml()
    response = requests.post(
        url,
        data=payload,
        headers=CREATE_ORDER_HEADERS,
        verify=False,
        cert=(settings.KB_ECOMM_CERT_PATH, settings.KB_ECOMM_CERT_KEY_PATH),
    )

    root = ET.fromstring(response.text)
    order_id = root.find("**/OrderID").text
    session_id = root.find("**/SessionID").text
    base_url = root.find("**/URL").text
    url = f"{base_url}?ORDERID={order_id}&SESSIONID={session_id}"
    return order_id, session_id, url
