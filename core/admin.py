from django.contrib import admin
from core import models
from solo.admin import SingletonModelAdmin


admin.site.register(models.Ticket, admin.ModelAdmin)
admin.site.register(models.Order, admin.ModelAdmin)
admin.site.register(models.Refund, admin.ModelAdmin)
admin.site.register(models.RegistrationSettings, SingletonModelAdmin)
