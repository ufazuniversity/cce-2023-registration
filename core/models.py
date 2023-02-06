from django.db import models
from django.contrib.auth import models as auth_models
from solo.models import SingletonModel
from ckeditor import fields as ck_fields
from django.conf import settings
from phonenumber_field import modelfields as pn_fields


class RegistrationSettings(SingletonModel):
    is_registration_active = models.BooleanField(default=False)


class Ticket(models.Model):
    VARIANT_CHOICES = (("student", "Student"), ("other", "Other"))
    SITE_CHOICES = (("online", "Online"), ("in-person", "In-person"))
    name = models.CharField(max_length=255)
    summary = models.CharField(max_length=255, null=True, blank=True)
    description = ck_fields.RichTextField(null=True, blank=True)
    is_paid = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    price_text = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    variant = models.CharField(
        max_length=20, choices=VARIANT_CHOICES, null=True, blank=True
    )
    is_limited = models.BooleanField(default=False)
    no_available = models.PositiveIntegerField(
        "Number of available tickets", null=True, blank=True
    )
    site = models.CharField(max_length=20, choices=SITE_CHOICES, default="online")
    includes_dinner = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def visual_price(self):
        return self.price_text or f"{self.price} {settings.PAYRIFF_CURRENCY}"


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
        max_digits=8, decimal_places=2, null=True, editable=False
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=12, null=False, default="pending"
    )

    def __str__(self):
        return self.order_id


class OrderTicket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT)


class Participant(models.Model):
    order_ticket = models.OneToOneField(OrderTicket, on_delete=models.PROTECT)
    fullname = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = pn_fields.PhoneNumberField(null=True, blank=True)
    id_no = models.CharField(
        "Passport number / ID number", max_length=20, null=True, blank=True
    )
    institution = models.CharField(max_length=100, null=True, blank=True)


class StudentParticipant(models.Model):
    participant = models.OneToOneField(Participant, on_delete=models.PROTECT)
    student_id = models.CharField(max_length=50)


class MealPreference(models.Model):
    participant = models.OneToOneField(Participant, on_delete=models.PROTECT)
    allergies = models.TextField(null=True, blank=True)
    special_request = models.TextField(
        null=True, blank=True, help_text="E.g halal, kosher, vegetarian etc."
    )


class Refund(models.Model):
    order = models.OneToOneField(Order, on_delete=models.PROTECT)
    datetime = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.order_id
