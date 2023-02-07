from django import urls

from . import views

urlpatterns = [
    urls.path("", views.index, name="index"),
    urls.path("tickets/<int:pk>/buy", views.BuyTicketView.as_view(), name="buy-ticket"),
]
