from django.shortcuts import render
from rest_framework import viewsets
from .models import Court, Membership, Reservation, Payment, UserProfile, Notification
from .serializers import (
    CourtSerializer,
    MembershipSerializer,
    ReservationSerializer,
    PaymentSerializer,
    UserProfileSerializer,
    NotificationSerializer
)

class CourtViewSet(viewsets.ModelViewSet):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        # Filtrar notificaciones por usuario actual
        return Notification.objects.filter(user=self.request.user)
