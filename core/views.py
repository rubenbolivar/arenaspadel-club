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
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

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
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'payments/create_payment.html'
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reservation_id = request.query_params.get('reservation')
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            return Response({
                'reservation': reservation,
                'amount': reservation.total_amount,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY
            })
        except Reservation.DoesNotExist:
            return Response({'error': 'Reserva no encontrada'}, status=404)

    def post(self, request):
        try:
            reservation_id = request.data.get('reservation_id')
            reservation = Reservation.objects.get(id=reservation_id)
            
            # Crear el PaymentIntent en Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=int(reservation.total_amount * 100),  # Convertir a centavos
                currency='usd',
                metadata={
                    'reservation_id': reservation.id
                }
            )
            
            # Guardar el pago en la base de datos
            Payment.objects.create(
                reservation=reservation,
                amount=reservation.total_amount,
                stripe_payment_intent_id=intent.id,
                payment_type='STRIPE',
                status='PENDING'
            )
            
            return Response({
                'client_secret': intent.client_secret,
                'payment_url': f'/api/payments/process/{intent.id}/',
                'reservation_id': reservation_id
            })
            
        except Reservation.DoesNotExist:
            return Response({'error': 'Reserva no encontrada'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

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

class CourtAvailabilityView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'courts/availability.html'

    def get(self, request):
        # Si es una petición AJAX, devolver JSON
        if request.accepted_renderer.format == 'json':
            court_id = request.query_params.get('court')
            date_str = request.query_params.get('date')
            
            try:
                if date_str:
                    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                else:
                    selected_date = timezone.now().date()
                    
                reservations = Reservation.objects.filter(
                    court_id=court_id,
                    date=selected_date,
                    status__in=['PENDING', 'CONFIRMED']
                ).values('start_time', 'end_time')
                
                court = Court.objects.get(id=court_id)
                opening_time = datetime.strptime(str(court.opening_time), '%H:%M:%S').time()
                closing_time = datetime.strptime(str(court.closing_time), '%H:%M:%S').time()
                
                current_time = opening_time
                available_slots = []
                
                while current_time < closing_time:
                    slot_end = (datetime.combine(selected_date, current_time) + timedelta(hours=1)).time()
                    
                    is_available = True
                    for reservation in reservations:
                        if (current_time >= reservation['start_time'] and 
                            current_time < reservation['end_time']) or (
                            slot_end > reservation['start_time'] and 
                            slot_end <= reservation['end_time']):
                            is_available = False
                            break
                    
                    if is_available:
                        available_slots.append({
                            'start_time': current_time.strftime('%H:%M'),
                            'end_time': slot_end.strftime('%H:%M')
                        })
                    
                    current_time = slot_end
                
                return Response({
                    'court_id': court_id,
                    'date': selected_date,
                    'available_slots': available_slots
                })
                
            except Court.DoesNotExist:
                return Response(
                    {'error': 'Cancha no encontrada'}, 
                    status=404
                )
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, 
                    status=400
                )
        
        # Si es una petición normal, mostrar el template
        return Response({
            'courts': Court.objects.filter(is_active=True),
            'today': timezone.now().date()
        })

class CreateReservationView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'reservations/create.html'
    
    def get(self, request):
        court_id = request.query_params.get('court')
        date = request.query_params.get('date')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        
        try:
            court = Court.objects.get(id=court_id)
            total_amount = float(court.price_per_hour)
            
            context = {
                'court': court,
                'date': date,
                'start_time': start_time,
                'end_time': end_time,
                'total_amount': total_amount
            }
            return Response(context)
        except Court.DoesNotExist:
            return Response({'error': 'Cancha no encontrada'}, status=404)

    def post(self, request):
        try:
            court = Court.objects.get(id=request.POST.get('court'))
            serializer = ReservationSerializer(data={
                'court': court.id,
                'date': request.POST.get('date'),
                'start_time': request.POST.get('start_time'),
                'end_time': request.POST.get('end_time'),
                'user': request.user.id,
                'status': 'PENDING',
                'total_amount': float(court.price_per_hour)
            })
            
            if serializer.is_valid():
                reservation = serializer.save()
                return redirect(f'/api/payments/create/?reservation={reservation.id}')
            return Response(serializer.errors, status=400)
        except Court.DoesNotExist:
            return Response({'error': 'Cancha no encontrada'}, status=404)

class ProcessPaymentView(APIView):
    def get(self, request, payment_intent_id):
        try:
            # Mantenemos la lógica existente
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Obtener la reserva
            payment = Payment.objects.filter(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if not payment:
                return Response({
                    'error': 'Pago no encontrado'
                }, status=404)
                
            reservation = payment.reservation
            
            # Devolver datos en formato JSON
            return Response({
                'reservation': {
                    'court': reservation.court.name,
                    'date': reservation.date.strftime('%d/%m/%Y'),
                    'start_time': reservation.start_time.strftime('%H:%M'),
                    'end_time': reservation.end_time.strftime('%H:%M'),
                    'total_amount': float(reservation.total_amount)
                },
                'payment': {
                    'client_secret': intent.client_secret,
                    'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                    'payment_intent_id': payment_intent_id
                },
                'payment_methods': {
                    'zelle': {
                        'email': 'payment@arenaspadel.com',
                        'holder': 'Arenas Padel Club'
                    },
                    'pago_movil': {
                        'phone': '0414-1234567',
                        'id': 'V-12345678',
                        'bank': 'Banesco'
                    }
                }
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=400)

class ConfirmPaymentView(APIView):
    def post(self, request):
        try:
            payment_type = request.data.get('payment_type')
            payment_intent_id = request.data.get('payment_intent_id')
            
            # Validar datos requeridos
            if not payment_type or not payment_intent_id:
                return Response({
                    'error': 'Faltan datos requeridos'
                }, status=400)
                
            # Obtener el pago
            payment = Payment.objects.filter(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if not payment:
                return Response({
                    'error': 'Pago no encontrado'
                }, status=404)
            
            # Procesar según el tipo de pago
            if payment_type == 'STRIPE':
                # Stripe se maneja con webhooks
                pass
                
            elif payment_type == 'ZELLE':
                payment.payment_type = 'ZELLE'
                payment.reference_last_digits = request.data.get('reference')[-4:]
                payment.zelle_email = request.data.get('email')
                payment.status = 'PENDING_VALIDATION'
                payment.save()
                
            elif payment_type == 'PAGO_MOVIL':
                payment.payment_type = 'PAGO_MOVIL'
                payment.reference_last_digits = request.data.get('reference')[-4:]
                payment.bank = request.data.get('bank')
                payment.phone_number = request.data.get('phone')
                payment.status = 'PENDING_VALIDATION'
                payment.save()
            
            return Response({
                'status': 'success',
                'message': 'Pago registrado correctamente',
                'redirect_url': '/payment/success/'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=400)

@api_view(['GET'])
def get_courts(request):
    courts = Court.objects.all()
    serializer = CourtSerializer(courts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def check_court_availability(request, court_id):
    date = request.query_params.get('date')
    court = get_object_or_404(Court, id=court_id)
    
    # Obtener reservas existentes para esa fecha
    existing_bookings = Reservation.objects.filter(
        court=court,
        date=date
    )
    
    # Generar todos los slots disponibles
    available_slots = generate_available_slots(existing_bookings)
    
    return Response(available_slots)

@api_view(['POST'])
def create_reservation(request):
    serializer = ReservationSerializer(data=request.data)
    if serializer.is_valid():
        reservation = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def process_payment(request):
    payment_serializer = PaymentSerializer(data=request.data)
    if payment_serializer.is_valid():
        payment = payment_serializer.save()
        return Response(payment_serializer.data, status=status.HTTP_201_CREATED)
    return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def generate_available_slots(existing_bookings):
    """
    Genera los slots disponibles para un día, considerando las reservas existentes
    """
    # Horario de operación (7am a 11pm)
    OPENING_HOUR = 7
    CLOSING_HOUR = 23
    
    # Crear lista de todos los slots posibles
    all_slots = []
    for hour in range(OPENING_HOUR, CLOSING_HOUR):
        slot = {
            'hour': hour,
            'time': f"{hour:02d}:00",
            'available': True
        }
        all_slots.append(slot)
    
    # Marcar slots ocupados
    for booking in existing_bookings:
        booking_hour = booking.time.hour
        for slot in all_slots:
            if slot['hour'] == booking_hour:
                slot['available'] = False
                break
    
    return all_slots
