from django.shortcuts import render
from rest_framework import viewsets
from .models import Court, Membership, Reservation, Payment
from .serializers import (
    CourtSerializer,
    MembershipSerializer,
    ReservationSerializer,
    PaymentSerializer
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
