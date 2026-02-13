from django.urls import path

from .payment_api_views import (
    PaymentPublicConfigAPI,
    YooKassaCreatePaymentAPI,
    YooKassaPaymentStatusAPI,
    YooKassaWebhookAPI,
)

urlpatterns = [
    path("config/", PaymentPublicConfigAPI.as_view()),
    path("create/", YooKassaCreatePaymentAPI.as_view()),
    path("<int:pk>/status/", YooKassaPaymentStatusAPI.as_view()),
    path("yookassa/webhook/", YooKassaWebhookAPI.as_view()),
]
