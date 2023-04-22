from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from . import models


@shared_task
def send_payment_approved_email(email: str, order_id: str):
    send_mail(
        subject="[CCE'23 Registration] Your payment has been approved",
        message=f"Your payment for order {order_id} has been approved. Thank you for registering for CCE'23.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
