from rest_framework import serializers
from .models import Court, Membership, Reservation, Payment, UserProfile, Notification
from django.contrib.auth.models import User
from django.utils import timezone
from .services import NotificationService
from .tasks import notify_reservation_created
from django.conf import settings

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
        fields = [
            'id', 
            'date', 
            'start_time', 
            'end_time', 
            'status', 
            'created_at', 
            'updated_at', 
            'user', 
            'court',
            'total_amount'
        ]

    def create(self, validated_data):
        reservation = Reservation.objects.create(**validated_data)
        notify_reservation_created.delay(reservation.id)
        return reservation

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'reservation', 'amount', 'payment_type', 'status',
            'stripe_payment_intent_id', 'payment_proof',
            # Campos Pago Móvil
            'bank_reference', 'reference_last_digits', 'phone_number', 'bank',
            # Campos Zelle
            'zelle_email', 'zelle_holder',
            # Campos administrativos
            'received_by', 'validation_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'received_by', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('payment_type') == 'ZELLE':
            if not data.get('payment_proof'):
                raise serializers.ValidationError(
                    'La captura de pantalla es requerida para pagos Zelle'
                )
            if not data.get('zelle_email'):
                raise serializers.ValidationError(
                    'El email de Zelle es requerido'
                )
            if not data.get('zelle_holder'):
                raise serializers.ValidationError(
                    'El nombre del titular de Zelle es requerido'
                )
        return data

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

class PaymentIntentSerializer(serializers.Serializer):
    reservation = serializers.PrimaryKeyRelatedField(queryset=Reservation.objects.all())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        # Agregar el monto automáticamente desde la reserva
        internal_value['amount'] = internal_value['reservation'].total_amount
        return internal_value

    def to_representation(self, instance):
        if isinstance(instance, dict):
            return {
                'clientSecret': instance.get('client_secret'),
                'publicKey': settings.STRIPE_PUBLIC_KEY,
                'amount': str(instance.get('amount'))
            }
        return {
            'reservation': instance.reservation.id,
            'amount': str(instance.reservation.total_amount)
        }