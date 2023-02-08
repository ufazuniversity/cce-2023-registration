import logging

from django import http
from django import shortcuts
from django.contrib.auth import decorators
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators import http as http_decorators
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
        kwargs['includes_meal'] = self.object.includes_dinner
        return kwargs

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        for field in form.errors:
            form[field].field.widget.attrs['class'] += ' is-invalid'
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return http.HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


@http_decorators.require_http_methods(["GET", "POST"])
@decorators.login_required()
def buy_ticket(request, pk):
    user = request.user

    try:
        # Return 404 if ticket is not found
        ticket = models.Ticket.objects.get(pk=pk)
    except models.Ticket.DoesNotExist:
        return http.HttpResponseNotFound(f"Did not find a ticket with the ID, {pk}")

    if request.method == "POST":
        try:
            # Create pending order and redirect to the acquired paymentUrl
            order_id, session_id, payment_url = payriff.create_order(ticket.price)
            models.Order.objects.create(
                user=user, order_id=order_id, session_id=session_id, ticket=ticket
            )
            return shortcuts.redirect(payment_url)
        except (exceptions.Timeout, exceptions.HTTPError) as e:
            logger.error(e)

    form = forms.ParticipantForm(initial={"order_ticket": pk})
    ctx = {"ticket": ticket, "form": form}

    return render(request, "core/ticket_detail.html", context=ctx)
