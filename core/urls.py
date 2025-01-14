from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ReservationViewSet,
    CreatePaymentIntentView,
    MobilePaymentView,
    PendingPaymentsView,
    ValidatePaymentView,
    StripeWebhookView,
    PaymentHistoryView,
    RetryPaymentView,
    DeletePaymentView,
    ZellePaymentView
)

router = DefaultRouter()
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = router.urls + [
    path('payments/create-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('payments/mobile/', MobilePaymentView.as_view(), name='mobile-payment'),
    path('payments/pending/', PendingPaymentsView.as_view(), name='pending-payments'),
    path('payments/<int:payment_id>/validate/', ValidatePaymentView.as_view(), name='validate-payment'),
    path('payments/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('payments/history/', PaymentHistoryView.as_view(), name='payment-history'),
    path('payments/<int:payment_id>/retry/', 
         RetryPaymentView.as_view(), 
         name='retry-payment'),
    path('payments/<int:payment_id>/', 
         DeletePaymentView.as_view(), 
         name='delete-payment'),
    path('payments/zelle/', 
         ZellePaymentView.as_view(), 
         name='zelle-payment'),
]