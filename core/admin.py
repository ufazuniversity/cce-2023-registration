from django.contrib import admin
from django.utils.safestring import mark_safe
from solo.admin import SingletonModelAdmin
from django import urls
from django.utils import encoding

from core import models


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["get_title", "is_paid", "price", "is_active", "variant", "site"]

    def get_title(self, obj):
        return f"{obj.site.capitalize()} - {obj.name}"


@admin.register(models.FreeRegistration)
class FreeRegistrationAdmin(admin.ModelAdmin):
    list_display = ["user", "datetime"]


class OrderTicketInlineAdmin(admin.StackedInline):
    model = models.Order.tickets.through

    readonly_fields = [
        "get_edit_link",
        "fullname",
        "email",
        "phone",
        "nationality",
        "id_no",
        "institution",
        "allergies",
        "special_request",
    ]

    def fullname(self, obj):
        return f"{obj.participant.title} {obj.participant.fullname}"

    def email(self, obj):
        return obj.participant.email

    def phone(self, obj):
        return obj.participant.phone_number

    def nationality(self, obj):
        return obj.participant.nationality

    def id_no(self, obj):
        return obj.participant.id_no

    id_no.short_description = "Passport / ID No."

    def institution(self, obj):
        return obj.participant.institution

    def allergies(self, obj):
        try:
            return obj.participant.mealpreference.allergies
        except models.MealPreference.DoesNotExist:
            return None

    def special_request(self, obj):
        try:
            return obj.participant.mealpreference.special_request
        except models.MealPreference.DoesNotExist:
            return None

    def get_edit_link(self, obj=None):
        if obj.pk:
            # if object has already been saved and has a primary key, show link to it
            model_name = (
                "studentparticipant"
                if obj.ticket.variant == models.TICKET_VARIANT_STUDENT
                else "participant"
            )

            url = urls.reverse(
                f"admin:{obj._meta.app_label}_{model_name}_change",
                args=[encoding.force_str(obj.pk)],
            )
            return mark_safe(f"<a href='{url}'>Edit this participant separately</a>")
        return "(save and continue editing to create a link)"

        return self.readonly_fields + ["ticket"]

    get_edit_link.short_description = "Edit link"
    get_edit_link.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("ticket")
        return qs

    can_delete = False


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "order_id",
        "session_id",
        "paid_amount",
        "updated",
        "status",
    ]
    inlines = [OrderTicketInlineAdmin]

    def has_change_permission(self, request, obj=None):
        return False


class MealPreferenceInline(admin.StackedInline):
    model = models.MealPreference
    can_delete = False
    verbose_name_plural = "Meal preference"
    fields = ["allergies", "special_request"]


@admin.register(models.Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = [
        "get_fullname",
        "email",
        "phone_number",
        "nationality",
        "id_no",
        "institution",
        "has_meal_preference",
    ]

    exclude = ["order_ticket"]

    inlines = [MealPreferenceInline]

    def get_fullname(self, obj):
        return f"{obj.title} {obj.fullname}"

    def has_meal_preference(self, obj: models.Participant):
        return obj.mealpreference is not None and (
            obj.mealpreference.allergies is not None
            or obj.mealpreference.special_request is not None
        )

    has_meal_preference.boolean = True

    get_fullname.short_description = "Full name"

    class Meta:
        model = models.Participant


@admin.register(models.StudentParticipant)
class StudentParticipantAdmin(ParticipantAdmin):
    def get_list_display(self, request):
        return super().get_list_display(request) + ["student_id"]

    class Meta:
        model = models.StudentParticipant


admin.site.register(models.Refund, admin.ModelAdmin)
admin.site.register(models.RegistrationSettings, SingletonModelAdmin)
