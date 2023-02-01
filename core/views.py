import logging

from django import shortcuts
from django import http
from django.shortcuts import render
from django.views.decorators import http as http_decorators
from django.contrib.auth import decorators
from requests import exceptions

from . import payriff
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
    }
    return shortcuts.render(request, "core/index.html", context=ctx)


def account(request):
    return shortcuts.render(request, "core/account.html")


def invoice(request):
    return shortcuts.render(request, "core/invoice.html")


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

    return render(request, "core/ticket.html", context={"ticket": ticket})
