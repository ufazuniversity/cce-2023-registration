import logging
import typing

from django import http
from django import shortcuts
from django.contrib.auth import decorators
from django.utils.decorators import method_decorator
from django.views import generic
from requests import exceptions

from . import forms
from . import models
from . import payriff

logger = logging.getLogger(__name__)


def index(request):
    tickets = models.Ticket.objects.all()
    free_tickets = tickets.filter(is_paid=False)
    paid_tickets = tickets.filter(is_paid=True)
    ctx = {
        "tickets": tickets,
        "free_tickets": free_tickets,
        "paid_tickets": paid_tickets,
    }
    return shortcuts.render(request, "core/index.html", context=ctx)


def account(request):
    return shortcuts.render(request, "core/account.html")


def invoice(request):
    return shortcuts.render(request, "core/invoice.html")


@method_decorator(decorators.login_required, name="dispatch")
class BuyTicketView(generic.FormView, generic.detail.SingleObjectMixin):
    template_name = "core/ticket_detail.html"
    model = models.Ticket
    form_class = forms.ParticipantForm

    def get_form(self, form_class=None):
        ticket = self.object
        if ticket.variant == models.TICKET_VARIANT_STUDENT:
            form_class = forms.StudentParticipantForm

        return super().get_form(form_class)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["includes_meal"] = self.object.includes_dinner
        return kwargs

    def _create_meal_preference(
        self, participant: models.Participant, form_data: dict
    ) -> typing.Optional[models.MealPreference]:
        allergies = form_data.pop("allergies", None)
        special_request = form_data.pop("special_request", None)
        if allergies or special_request:
            return models.MealPreference(
                participant=participant,
                allergies=allergies,
                special_request=special_request,
            )
        return None

    def _create_participant(
        self, order_ticket: models.OrderTicket, form_data: dict
    ) -> models.Participant:
        ticket = self.object
        fullname = form_data.get("fullname")
        email = form_data.get("email")
        phone_number = form_data.get("phone_number")
        id_no = form_data.get("id_no")
        institution = form_data.get("institution")
        if ticket.variant == models.TICKET_VARIANT_STUDENT:
            return models.StudentParticipant(order_ticket=order_ticket, **form_data)
        return models.Participant(order_ticket=order_ticket, **form_data)

    def form_valid(self, form):
        ticket = self.object
        try:

            user = self.request.user
            price = float(ticket.price)
            # Create pending order and redirect to the acquired paymentUrl
            order_id, session_id, payment_url = payriff.create_order(price)
            order = models.Order.objects.create(
                user=user, order_id=order_id, session_id=session_id
            )
            ot = models.OrderTicket.objects.create(ticket=ticket, order=order)
            participant = self._create_participant()
            meal_pref = self._create_meal_preference()
            return shortcuts.redirect(payment_url)
        except (exceptions.Timeout, exceptions.HTTPError) as e:
            logger.error(e)

        return super().form_valid(form)

    def form_invalid(self, form):
        for field in form.errors:
            form[field].field.widget.attrs["class"] += " is-invalid"

        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return http.HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)
