from django.conf import settings
from .models import Notification
import requests
import stripe
from .exceptions import PaymentError
import logging
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.base_url = settings.WHATSAPP_API_URL
        self.token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID

    def send_message(self, to_phone, message):
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "text": {"body": message}
            }
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            response = requests.post(url, json=data, headers=headers)
            
            return response.status_code == 200, response.json()
        except Exception as e:
            return False, str(e)

class NotificationService:
    def __init__(self):
        self.whatsapp = WhatsAppService()

    @staticmethod
    def create_notification(user, type, title, message):
        notification = Notification.objects.create(
            user=user,
            type=type,
            title=title,
            message=message
        )
        return notification

    @staticmethod
    def notify_reservation_created(reservation):
        """Notificar cuando se crea una reserva"""
        message = (
            f"¡Hola! Tu reserva ha sido creada:\n"
            f"Cancha: {reservation.court}\n"
            f"Fecha: {reservation.date}\n"
            f"Hora: {reservation.start_time} - {reservation.end_time}\n"
            f"Estado: {reservation.get_status_display()}"
        )
        return NotificationService.create_notification(
            user=reservation.user,
            type='RESERVATION_CREATED',
            title='Reserva Creada',
            message=message
        )

class PaymentService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment_intent(self, reservation):
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(float(reservation.total_amount) * 100),  # Convertir a centavos
                currency='usd',
                metadata={'reservation_id': reservation.id}
            )
            return intent
        except stripe.error.StripeError as e:
            raise PaymentError(str(e))

class PaymentNotificationService:
    def notify_admin_pending_validation(self, payment):
        """Notifica a los administradores sobre un nuevo pago pendiente"""
        admins = User.objects.filter(is_staff=True)
        
        for admin in admins:
            Notification.objects.create(
                user=admin,
                type='PAYMENT_PENDING',
                title='Nuevo pago pendiente de validación',
                message=f'El pago #{payment.id} requiere validación.\n'
                        f'Reserva: {payment.reservation}\n'
                        f'Monto: ${payment.amount}\n'
                        f'Método: {payment.get_payment_type_display()}'
            )

    def notify_payment_status(self, payment):
        """Notifica al usuario sobre el estado de su pago"""
        status_messages = {
            'PENDING_VALIDATION': 'Tu pago está pendiente de validación',
            'COMPLETED': 'Tu pago ha sido aprobado',
            'FAILED': 'Tu pago ha sido rechazado'
        }
        
        Notification.objects.create(
            user=payment.reservation.user,
            type='PAYMENT_STATUS',
            title=f'Estado de pago actualizado',
            message=f'{status_messages[payment.status]}\n'
                    f'Reserva: {payment.reservation}\n'
                    f'Monto: ${payment.amount}'
        )