from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'courts', views.CourtViewSet)
router.register(r'memberships', views.MembershipViewSet)
router.register(r'reservations', views.ReservationViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 