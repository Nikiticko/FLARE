from django.urls import path

from .payment_api_views import (
    YooKassaCreatePaymentAPI,
    YooKassaPaymentStatusAPI,
    YooKassaWebhookAPI,
)

urlpatterns = [
    path("create/", YooKassaCreatePaymentAPI.as_view()),
    path("<int:pk>/status/", YooKassaPaymentStatusAPI.as_view()),
    path("yookassa/webhook/", YooKassaWebhookAPI.as_view()),
]
