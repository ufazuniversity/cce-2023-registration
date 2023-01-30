from django import urls
from . import views

urlpatterns = [
    urls.path("", views.index, name="index"),
    urls.path("tickets/<int:pk>/buy", views.buy_ticket, name="buy-ticket"),
]
