import random
import typing

from ckeditor import fields as ck_fields
from django.conf import settings
from django.contrib.auth import models as auth_models
from django import shortcuts
from django.db import models
from phonenumber_field import modelfields as pn_fields
from solo.models import SingletonModel
from . import ecommerce
from . import managers


class RegistrationSettings(SingletonModel):
    is_registration_active = models.BooleanField(default=False)


TICKET_VARIANT_STUDENT = "student"
TICKET_VARIANT_OTHER = "other"

ORDER_STATUS_APPROVED = "APPROVED"
ORDER_STATUS_DECLINED = "DECLINED"
ORDER_STATUS_CANCELED = "CANCELED"
ORDER_STATUS_REFUNDED = "REFUNDED"
ORDER_STATUS_PENDING = "PENDING"


class Ticket(models.Model):
    VARIANT_CHOICES = (
        (TICKET_VARIANT_STUDENT, "Student"),
        (TICKET_VARIANT_OTHER, "Other"),
    )
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
        return f"{self.site} - {self.name}"

    @property
    def visual_price(self):
        return self.price_text or f"{self.price} {settings.CURRENCY}"


class FreeRegistration(models.Model):
    user = models.OneToOneField(auth_models.User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)


def random_id():
    # generates 6 digit random number
    return str(random.randint(100000, 999999))


class Order(models.Model):
    user = models.ForeignKey(auth_models.User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=10, unique=True, default=random_id)
    tickets = models.ManyToManyField(Ticket, through="OrderTicket")
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return str(self.id)

    @property
    def status(self):
        try:
            return self.kborder_set.last().status
        except AttributeError:
            return None

    @property
    def is_approved(self):
        return self.kborder_set.filter(status=ORDER_STATUS_APPROVED).exists()

    def create_kapital_ecomm_order(self) -> typing.Tuple[str, str, str]:
        # Creates a Kapital Bank order and returns the URL to redirect to
        kb_order = KBOrder.objects.create(my_order=self, amount=self.amount)
        return kb_order.order_id, kb_order.session_id, kb_order.url


class OrderTicket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.ticket)


class Participant(models.Model):
    TITLE_CHOICES = (
        ("Mr", "Mr"),
        ("Mrs", "Mrs"),
        ("Ms", "Ms"),
        ("Miss", "Miss"),
        ("Dr", "Dr"),
        ("Prof", "Prof"),
        ("Sir", "Sir"),
    )
    order_ticket = models.OneToOneField(OrderTicket, on_delete=models.CASCADE)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, null=True)
    fullname = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = pn_fields.PhoneNumberField(null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    id_no = models.CharField(
        "Passport number / ID number", max_length=20, null=True, blank=True
    )
    institution = models.CharField(
        "Institution name", max_length=100, null=True, blank=True
    )

    def __str__(self):
        return f"{self.title} {self.fullname} <{self.email}>"

    @property
    def fields(self):
        return self._meta.get_fields()


class StudentParticipant(Participant):
    student_id = models.CharField(max_length=50)


class MealPreference(models.Model):
    participant = models.OneToOneField(Participant, on_delete=models.PROTECT)
    allergies = models.TextField(null=True, blank=True)
    special_request = models.TextField(
        null=True, blank=True, help_text="E.g halal, kosher, vegetarian etc."
    )

    @property
    def fields(self):
        return self._meta.get_fields()


class Refund(models.Model):
    order = models.OneToOneField(Order, on_delete=models.PROTECT)
    datetime = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.order_id


KB_ORDER_STATUS_PENDING = "PENDING"
KB_ORDER_STATUS_APPROVED = "APPROVED"
KB_ORDER_STATUS_CANCELED = "CANCELED"
KB_ORDER_STATUS_DECLINED = "DECLINED"


class KBOrder(models.Model):
    STATUS_CHOICES = (
        (KB_ORDER_STATUS_PENDING, "Pending"),
        (KB_ORDER_STATUS_APPROVED, "Approved"),
        (KB_ORDER_STATUS_CANCELED, "Canceled"),
        (KB_ORDER_STATUS_DECLINED, "Declined"),
    )
    my_order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    order_id = models.CharField(max_length=10, unique=True)
    session_id = models.CharField(max_length=50, unique=True)
    url = models.URLField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=KB_ORDER_STATUS_PENDING
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = managers.KBOrderManager()

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return f"Order ID = {self.order_id}, Session ID = {self.session_id}"

    def save(self, *args, **kwargs):
        if not self.pk:
            # send request to Kapitalbank Ecommerce the first time the order is saved
            order_id, session_id, url = ecommerce.create_order(self.amount)
            self.order_id = order_id
            self.session_id = session_id
            self.url = url
        super().save(*args, **kwargs)

    def is_approved(self):
        return self.status == KB_ORDER_STATUS_APPROVED
