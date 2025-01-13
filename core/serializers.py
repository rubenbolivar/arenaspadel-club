from rest_framework import serializers
from .models import Court, Membership, Reservation, Payment, UserProfile, Notification
from django.contrib.auth.models import User
from django.utils import timezone
from .services import NotificationService
from .tasks import notify_reservation_created

class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = '__all__'

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'date', 'start_time', 'end_time', 'status', 'created_at', 'updated_at', 'user', 'court']

    def create(self, validated_data):
        reservation = Reservation.objects.create(**validated_data)
        notify_reservation_created.delay(reservation.id)
        return reservation

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('sent_via_whatsapp', 'sent_via_email')