from django.core import exceptions
from django import dispatch
from django.db.models import signals
from . import models


@dispatch.receiver(signals.pre_save, sender=models.KBOrder)
def cancel_if_order_is_approved(sender, instance: models.KBOrder, **kwargs):
    # cancel order if it is already approved
    if not instance.pk:
        order = instance.my_order
        if models.KBOrder.objects.filter(my_order=order, status=models.ORDER_STATUS_APPROVED).exists():
            raise exceptions.ValidationError("Order is already approved")
