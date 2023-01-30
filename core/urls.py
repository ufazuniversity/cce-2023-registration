from django import urls
from . import views

urlpatterns = [
    urls.path("", views.index, name="index"),
    urls.path("tickets/buy/<int:pk>", views.buy_ticket, name="buy-ticket"),
]
