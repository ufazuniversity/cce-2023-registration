from django.db import models
from django.contrib.auth import models as auth_models
from solo.models import SingletonModel


class RegistrationSettings(SingletonModel):
    is_registration_active = models.BooleanField(default=False)


class TicketType(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=50)


class Ticket(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    type = models.ForeignKey(
        TicketType, on_delete=models.PROTECT, null=True, blank=False
    )
    is_paid = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=True)


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("complete", "Complete"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    )
    user = models.ForeignKey(auth_models.User, on_delete=models.PROTECT)
    order_id = models.IntegerField(
        verbose_name="Payriff order id", null=False, editable=False
    )
    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT)
    paid_amount = models.DecimalField(
        max_digits=8, decimal_places=2, null=False, editable=False
    )
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=12, null=False, default="pending"
    )


class Refund(models.Model):
    order = models.OneToOneField(Order, on_delete=models.PROTECT)
    datetime = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(null=True, blank=True)