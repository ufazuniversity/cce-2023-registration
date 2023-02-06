from django.contrib import admin
from core import models
from solo.admin import SingletonModelAdmin


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["name", "is_paid", "price", "is_active", "variant"]


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Refund, admin.ModelAdmin)
admin.site.register(models.RegistrationSettings, SingletonModelAdmin)
