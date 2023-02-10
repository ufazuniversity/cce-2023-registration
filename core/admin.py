from django.contrib import admin
from solo.admin import SingletonModelAdmin

from core import models


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["name", "is_paid", "price", "is_active", "variant"]


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["user", "order_id", "session_id", "paid_amount", "updated", "status"]


admin.site.register(models.Refund, admin.ModelAdmin)
admin.site.register(models.RegistrationSettings, SingletonModelAdmin)
