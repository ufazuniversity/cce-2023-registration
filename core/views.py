import logging
import datetime

from django import http
from django import shortcuts
from django.utils import timezone
from django import urls
from django.contrib.auth import decorators
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators import http as http_decorators
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from requests import exceptions

from . import forms
from . import models
from . import ecommerce
from . import tasks

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
    data = {"orders": []}
    for order in orders:
        ot_set = order.orderticket_set.all()
        order_data = {
            "is_approved": order.is_approved,
            "id": order.pk,
            "details": {
                "Order id": order.order_id,
                "Status": order.status,
                "Price": order.amount,
                "Created": order.created,
            },
            "tickets": [],
        }
        for ot in ot_set:
            ticket = ot.ticket
            participant = ot.participant
            try:
                participant = participant.studentparticipant
            except models.StudentParticipant.DoesNotExist:
                pass
            p_fields = [
                "title",
                "fullname",
                "email",
                "phone_number",
                "nationality",
                "id_no",
                "institution",
                "student_id",
            ]
            participant_data = {
                k.capitalize().replace("_", " "): getattr(participant, k)
                for k in p_fields
                if hasattr(participant, k)
            }
            ticket_data = {
                "name": ticket.name,
                "participant": {
                    "details": participant_data,
                },
            }
            try:
                mp = participant.mealpreference
                mp_fields = ["allergies", "special_request"]
                ticket_data["participant"]["meal_preference"] = {
                    k.capitalize().replace("_", " "): getattr(mp, k) for k in mp_fields
                }
            except models.MealPreference.DoesNotExist:
                pass
            order_data["tickets"].append(ticket_data)
        data["orders"].append(order_data)
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


def create_kb_payment_order_and_redirect(order):
    try:
        order_id, session_id, url = order.create_kapital_ecomm_order()
        eta = timezone.now() + datetime.timedelta(seconds=settings.KB_ECOMM_ORDER_EXPIRY_SECONDS)
        tasks.check_and_update_order_status.apply_async((order_id, session_id), eta=eta)
        return shortcuts.redirect(url)
    except ValidationError as e:
        logger.error(e)
        return HttpResponseBadRequest(e.message)


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
        participant = participant_model.objects.create(
            order_ticket=order_ticket, **form_data
        )
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
            order = models.Order.objects.create(user=user, amount=ticket.price)
            ot = models.OrderTicket.objects.create(ticket=ticket, order=order)
            self.save_participant(ot, form.cleaned_data)
            return create_kb_payment_order_and_redirect(order)
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


@method_decorator(csrf_exempt, name="dispatch")
class KBStatusView(generic.TemplateView):
    def post(self, request, *args, **kwargs):
        if urls.resolve(request.path).url_name == "order-approved":
            order_id, session_id, status = ecommerce.get_order_status_from_response_xml(request.POST)
            kb_order = shortcuts.get_object_or_404(models.KBOrder, order_id=order_id)
            kb_order.status = status
            kb_order.save()
            if status == models.ORDER_STATUS_APPROVED:
                order = kb_order.my_order
                tasks.send_payment_approved_email.delay(order.user.email, order.order_id)
        return shortcuts.redirect(request.path)




@http_decorators.require_POST
def retry_payment(request, pk):
    order = shortcuts.get_object_or_404(models.Order, pk=pk)
    return create_kb_payment_order_and_redirect(order)
