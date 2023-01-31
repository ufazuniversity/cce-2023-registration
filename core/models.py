from django.db import models
from django.contrib.auth import models as auth_models
from solo.models import SingletonModel
from ckeditor import fields as ck_fields


class RegistrationSettings(SingletonModel):
    is_registration_active = models.BooleanField(default=False)


class Ticket(models.Model):
    VARIANT_CHOICES = (("student", "Student"), ("other", "Other"))
    name = models.CharField(max_length=255)
    description = ck_fields.RichTextField(null=True, blank=True)
    is_paid = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    variant = models.CharField(
        max_length=20, choices=VARIANT_CHOICES, null=True, blank=True
    )

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("complete", "Complete"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    )
    user = models.ForeignKey(auth_models.User, on_delete=models.PROTECT)
    order_id = models.IntegerField(
        verbose_name="Payriff order ID", null=False, editable=False, unique=True
    )
    session_id = models.CharField(
        verbose_name="Payriff session ID",
        max_length=50,
        editable=False,
        null=True,
        unique=True,
    )
    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT)
    paid_amount = models.DecimalField(
        max_digits=8, decimal_places=2, null=False, editable=False
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=12, null=False, default="pending"
    )

    def __str__(self):
        return self.order_id


class Refund(models.Model):
    order = models.OneToOneField(Order, on_delete=models.PROTECT)
    datetime = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.order_id
