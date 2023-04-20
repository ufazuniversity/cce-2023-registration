from django import urls

from . import views

urlpatterns = [
    urls.path("", views.index, name="index"),
    urls.path("tickets/<int:pk>/buy", views.BuyTicketView.as_view(), name="buy-ticket"),
    urls.path("free-register", views.free_registration, name="free-register"),
    urls.path(
        "order-approved",
        views.KBStatusView.as_view(template_name="core/order_approved.html"),
        name="order-approved",
    ),
    urls.path(
        "order-declined",
        views.KBStatusView.as_view(template_name="core/order_declined.html"),
        name="order-declined",
    ),
    urls.path(
        "order-canceled",
        views.KBStatusView.as_view(template_name="core/order_canceled.html"),
        name="order-canceled",
    ),
    urls.path("account", views.account, name="account"),
]
