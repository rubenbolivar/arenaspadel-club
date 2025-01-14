from django.shortcuts import render
from rest_framework import viewsets
from .models import Court, Membership, Reservation, Payment, UserProfile, Notification
from .serializers import (
    CourtSerializer,
    MembershipSerializer,
    ReservationSerializer,
    PaymentSerializer,
    UserProfileSerializer,
    NotificationSerializer,
    PaymentIntentSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import stripe
from .services import PaymentService, PaymentNotificationService
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.urls import reverse
from django.http import HttpResponseRedirect

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

class CreatePaymentIntentView(APIView):
    serializer_class = PaymentIntentSerializer
    
    def get(self, request):
        # Para mostrar el formulario HTML
        return Response({'message': 'Use POST to create a payment intent'})
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            reservation = serializer.validated_data['reservation']
            payment_service = PaymentService()
            
            try:
                intent = payment_service.create_payment_intent(reservation)
                return Response({
                    'client_secret': intent.client_secret,
                    'publicKey': settings.STRIPE_PUBLIC_KEY,
                    'amount': str(reservation.total_amount)
                })
            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StripeWebhookView(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            if event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent.id
                )
                payment.status = 'COMPLETED'
                payment.save()
                
                # Actualizar estado de la reserva
                reservation = payment.reservation
                reservation.status = 'CONFIRMED'
                reservation.save()
                
            return Response({'status': 'success'})
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class MobilePaymentView(APIView):
    serializer_class = PaymentSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['payment_type'] != 'PAGOMOVIL':
                return Response(
                    {'error': 'Esta vista es solo para pagos móviles'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            payment = serializer.save(status='PENDING_VALIDATION')
            
            # Notificar a los administradores
            notification_service = PaymentNotificationService()
            notification_service.notify_admin_pending_validation(payment)
            notification_service.notify_payment_status(payment)
            
            return Response({
                'id': payment.id,
                'message': 'Pago registrado y pendiente de validación',
                'status': payment.status
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidatePaymentView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
            action = request.data.get('action')
            
            if action not in ['approve', 'reject']:
                return Response(
                    {'error': 'Acción inválida. Use "approve" o "reject"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if action == 'approve':
                payment.status = 'COMPLETED'
                payment.received_by = request.user
                payment.reservation.status = 'CONFIRMED'
                payment.reservation.save()
            else:
                payment.status = 'FAILED'
            
            payment.validation_notes = request.data.get('notes', '')
            payment.save()
            
            # Notificar al usuario del resultado
            notification_service = PaymentNotificationService()
            notification_service.notify_payment_status(payment)
            
            return Response({
                'message': f'Pago {payment.id} {"aprobado" if action == "approve" else "rechazado"}',
                'status': payment.status
            })
            
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Pago no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

class PendingPaymentsView(APIView):
    def get(self, request):
        pending_payments = Payment.objects.filter(
            status__in=['PENDING', 'PENDING_VALIDATION'],
            payment_type__in=['PAGOMOVIL', 'ZELLE']  # Agregamos ZELLE
        )
        serializer = PaymentSerializer(pending_payments, many=True)
        return Response(serializer.data)

class PaymentHistoryView(APIView):
    def get(self, request):
        payments = Payment.objects.filter(
            reservation__user=request.user
        ).select_related('reservation').order_by('-created_at')
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

class RetryPaymentView(APIView):
    def post(self, request, payment_id):
        try:
            old_payment = Payment.objects.get(
                id=payment_id, 
                reservation__user=request.user,
                status='FAILED'
            )
            
            # Verificar que la reserva no tiene un pago exitoso
            existing_successful_payment = Payment.objects.filter(
                reservation=old_payment.reservation,
                status='COMPLETED'
            ).exists()
            
            if existing_successful_payment:
                return Response(
                    {'error': 'Esta reserva ya tiene un pago exitoso'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear nuevo pago copiando todos los campos relevantes
            new_payment = Payment.objects.create(
                reservation=old_payment.reservation,
                amount=old_payment.amount,
                payment_type=old_payment.payment_type,
                status='PENDING_VALIDATION',
                payment_proof=old_payment.payment_proof,
                bank_reference=old_payment.bank_reference,
                reference_last_digits=old_payment.reference_last_digits,
                phone_number=old_payment.phone_number,
                bank=old_payment.bank
            )
            
            return Response({
                'message': 'Pago creado para reintento',
                'payment_id': new_payment.id
            })
            
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Pago no encontrado o no puede ser reintentado'},
                status=status.HTTP_404_NOT_FOUND
            )

class DeletePaymentView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, payment_id):
        try:
            payment = Payment.objects.get(
                id=payment_id,
                status__in=['FAILED', 'PENDING_VALIDATION']  # Solo estos estados
            )
            payment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Payment.DoesNotExist:
            return Response({
                'error': 'Pago no encontrado o no puede ser eliminado'
            }, status=status.HTTP_404_NOT_FOUND)

class ZellePaymentView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'payments/zelle_payment.html'

    def get(self, request):
        reservations = Reservation.objects.filter(
            user=request.user,
            status='PENDING'
        )
        return Response({
            'reservations': reservations,
            'payment_types': Payment.PAYMENT_TYPES,
            'message': request.GET.get('message')  # Para mostrar mensajes
        })

    def post(self, request):
        data = request.data.copy()
        data['status'] = 'PENDING_VALIDATION'
        data['payment_type'] = 'ZELLE'
        
        # Manejar el archivo subido
        payment_proof = request.FILES.get('payment_proof')
        if payment_proof:
            data['payment_proof'] = payment_proof
        
        serializer = PaymentSerializer(data=data)
        if serializer.is_valid():
            payment = serializer.save()
            
            # Notificar a los administradores
            notification_service = PaymentNotificationService()
            notification_service.notify_admin_pending_validation(payment)
            
            # Redirigir con mensaje de éxito
            return HttpResponseRedirect(
                f'{reverse("zelle-payment")}?message=Pago registrado correctamente'
            )
        
        # Si hay errores, mostrar el formulario con los errores
        return Response({
            'reservations': Reservation.objects.filter(user=request.user, status='PENDING'),
            'payment_types': Payment.PAYMENT_TYPES,
            'errors': serializer.errors
        })
