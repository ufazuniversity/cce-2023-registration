from django import urls

from . import views

urlpatterns = [
    urls.path("", views.index, name="index"),
    urls.path("tickets/<int:pk>/buy", views.BuyTicketView.as_view(), name="buy-ticket"),
    urls.path("order-approved", views.order_approved(), name="order-approved"),
    urls.path("order-declined", views.order_declined(), name="order-declined"),
    urls.path("order-cancelled", views.order_cancelled(), name="order-cancelled"),
]
