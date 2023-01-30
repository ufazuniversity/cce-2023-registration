import logging

from django import shortcuts
from django.shortcuts import render
from django.views.decorators import http
from django.contrib.auth import decorators
from requests import exceptions

from . import payriff
from . import models

logger = logging.getLogger(__name__)


def index(request):
    shortcuts.render("core/index.html")


@http.require_http_methods(["GET", "POST"])
@decorators.login_required()
def buy_ticket(request, pk):
    user = request.user
    ticket = models.Ticket.objects.get(pk=pk)
    if request.method == "POST":
        try:
            order_id, session_id, payment_url = payriff.create_order(ticket.price)
            order = models.Order.objects.create(
                user=user, order_id=order_id, session_id=session_id, ticket=ticket
            )
            return shortcuts.redirect(payment_url)
        except exceptions.Timeout:
            logger.error("Request timed out")
        except exceptions.HTTPError as e:
            logger.error(e)
    return render(request, "core/ticket.html", context={"ticket": ticket})
