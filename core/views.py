import functools
import logging
import random
import typing

from django import http
from django import shortcuts
from django import urls
from django.contrib.auth import decorators
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators import http as http_decorators
from requests import exceptions

from . import forms
from . import models

logger = logging.getLogger(__name__)


def index(request):
    tickets = models.Ticket.objects.all()
    free_tickets = tickets.filter(is_paid=False)
    paid_tickets = tickets.filter(is_paid=True)
    ctx = {
        "tickets": tickets,
        "free_tickets": free_tickets,
        "paid_tickets": paid_tickets,
        "user": request.user,
    }
    return shortcuts.render(request, "core/index.html", context=ctx)


@decorators.login_required
def account(request):
    user = request.user
    orders = user.order_set.all()
    data = {
        'orders': []
    }
    for order in orders:
        ot_set = order.orderticket_set.all()
        order_data = {
            "details": {
                "Order id": order.order_id,
                "Status": order.status,
                "Price": order.paid_amount,
                "Created": order.created,
                "Updated": order.updated,
            },
            "tickets": []
        }
        for ot in ot_set:
            ticket = ot.ticket
            participant = ot.participant
            try:
                participant = participant.studentparticipant
            except models.StudentParticipant.DoesNotExist:
                pass
            p_fields = ['title', 'fullname', 'email', 'phone_number', 'nationality', 'id_no', 'institution',
                        'student_id']
            participant_data = {k.capitalize().replace("_", " "): getattr(participant, k) for k in p_fields if
                                hasattr(participant, k)}
            ticket_data = {
                "name": ticket.name,
                "participant": {
                    "details": participant_data,
                }
            }
            try:
                mp = participant.mealpreference
                mp_fields = ['allergies', 'special_request']
                ticket_data["participant"]["meal_preference"] = {k.capitalize().replace("_", " "): getattr(mp, k) for k
                                                                 in mp_fields}
            except models.MealPreference.DoesNotExist:
                pass
            order_data['tickets'].append(ticket_data)
        data['orders'].append(order_data)
    ctx = {"data": data, "user": user}
    return shortcuts.render(request, "core/account.html", ctx)


def invoice(request):
    return shortcuts.render(request, "core/invoice.html")


def user_has_free_registration(user):
    return not models.FreeRegistration.objects.filter(user=user).exists()


@http_decorators.require_POST
@decorators.login_required
@decorators.user_passes_test(user_has_free_registration)
def free_registration(request):
    models.FreeRegistration.objects.create(user=request.user)
    return shortcuts.redirect(urls.reverse("account"))


@method_decorator(decorators.login_required, name="dispatch")
class BuyTicketView(generic.FormView, generic.detail.SingleObjectMixin):
    template_name = "core/buy_ticket.html"
    model = models.Ticket
    form_class = forms.ParticipantForm

    def get_form(self, form_class=None):
        ticket = self.object
        if ticket.variant == models.TICKET_VARIANT_STUDENT:
            form_class = forms.StudentParticipantForm

        return super().get_form(form_class)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object.is_paid:
            kwargs["includes_meal"] = self.object.includes_dinner
        return kwargs

    def _approve_url(self):
        return self.request.build_absolute_uri(urls.reverse("order-approved"))

    def _decline_url(self):
        return self.request.build_absolute_uri(urls.reverse("order-declined"))

    def _cancel_url(self):
        url = self.request.build_absolute_uri(urls.reverse("order-canceled"))
        return url

    def save_participant(self, order_ticket, form_data):
        ticket = self.object
        participant_model = models.Participant
        if ticket.variant == models.TICKET_VARIANT_STUDENT:
            participant_model = models.StudentParticipant
        allergies = form_data.pop("allergies", None)
        special_request = form_data.pop("special_request", None)
        participant = participant_model.objects.create(order_ticket=order_ticket, **form_data)
        if ticket.includes_dinner:
            models.MealPreference.objects.create(
                participant=participant,
                allergies=allergies,
                special_request=special_request,
            )

    def form_valid(self, form):
        ticket = self.object
        try:

            user = self.request.user
            price = float(ticket.price)

            # Generate 6 digit random number
            order_id = random.randint(100000, 999999)
            order = models.Order.objects.create(
                user=user,
                order_id=order_id,
                # session_id=session_id,
                paid_amount=ticket.price,
            )
            ot = models.OrderTicket.objects.create(ticket=ticket, order=order)
            self.save_participant(ot, form.cleaned_data)
            return shortcuts.redirect(urls.reverse("order-approved"))
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


def referer_only(function):
    @functools.wraps(function)
    def wrap(request, *args, **kwargs):
        if request.method == "GET" and request.headers.get("referer") is None:
            return http.HttpResponseNotFound()
        else:
            return function(request, *args, **kwargs)

    return wrap


# def update_order_status(json_payload: str):
#     # order_id, session_id, status = payriff.get_order_result_details(json_payload)
#     order = models.Order.objects.filter(order_id=order_id, session_id=session_id)
#     if status == models.ORDER_STATUS_CANCELED:
#         order.delete()
#     else:
#         order.update(status=status)


# @csrf.csrf_exempt
def order_approved(request):
    # if request.method == "POST":
    #     update_order_status(request.body)
    return shortcuts.render(request, "core/order_approved.html")

# @csrf.csrf_exempt
# def order_declined(request):
#     if request.method == "POST":
#         update_order_status(request.body)
#     return shortcuts.render(request, "core/order_declined.html")


# @csrf.csrf_exempt
# def order_canceled(request):
#     if request.method == "POST":
#         update_order_status(request.body)
#     return shortcuts.render(request, "core/order_canceled.html")
