import requests
from django.conf import settings
from django.template import loader

CREATE_ORDER_TEMPLATE_NAME='ecommerce/create_order.xml'
CREATE_ORDER_HEADERS = {
    'Content-Type': 'application/xml
}
def create_order(
    amount,
    approve_url=settings.KB_ECOMM_ORDER_APPROVE_URL,
    cancel_url=settings.KB_ECOMM_ORDER_CANCEL_URL,
    decline_url=settings.KB_ECOMM_ORDER_DECLINE_URL,
    description=settings.KB_ECOMMERCE_ORDER_DESCRIPTION,
    url=settings.KB_ECOMMERCE_URL,
    merchant_id=settings.KB_ECOMMERCE_MERCHANT_ID,
    currency=settings.KB_ECOMMERCE_CURRENCY,
):
    """Sending order request to Kapital Ecommerce API"""
    data = {
        "amount": amount,
        "approve_url": approve_url,
        "cancel_url": cancel_url,
        "decline_url": decline_url,
        "description": description,
        "merchant_id": merchant_id,
        "currency": currency,
    }
    xml_out = loader.render_to_string(CREATE_ORDER_TEMPLATE_NAME, data)
    response = requests.post(url, data=xml_out, headers=CREATE_ORDER_HEADERS, verify=False)
