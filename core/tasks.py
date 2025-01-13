from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Reservation
from .services import NotificationService
import logging

logger = logging.getLogger(__name__)

@shared_task
def notify_reservation_created(reservation_id):
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        logger.info(f"Procesando notificación para reserva {reservation_id}")
        
        notification = NotificationService.notify_reservation_created(reservation=reservation)
        logger.info(f"Notificación {notification.id} creada para reserva {reservation_id}")
        
        return f"Notificación {notification.id} enviada para la reserva {reservation_id}"
    except Exception as e:
        logger.error(f"Error al notificar reserva {reservation_id}: {str(e)}")
        raise

@shared_task
def send_reservation_reminders():
    """Envía recordatorios para reservas próximas"""
    # Buscar reservas para mañana
    tomorrow = timezone.now().date() + timedelta(days=1)
    reservations = Reservation.objects.filter(
        date=tomorrow,
        status='CONFIRMED'
    )
    
    notification_service = NotificationService()
    
    for reservation in reservations:
        message = (
            f"¡Recordatorio!\n"
            f"Tienes una reserva mañana:\n"
            f"Cancha: {reservation.court}\n"
            f"Hora: {reservation.start_time} - {reservation.end_time}\n"
            f"¡Te esperamos!"
        )
        
        notification_service.create_notification(
            user=reservation.user,
            type='RESERVATION_REMINDER',
            title='Recordatorio de Reserva',
            message=message
        )

@shared_task
def send_payment_reminder():
    """Envía recordatorios de pagos pendientes"""
    # Buscar reservas con pagos pendientes
    reservations = Reservation.objects.filter(
        status='PENDING',
        date__gt=timezone.now().date()
    )
    
    notification_service = NotificationService()
    
    for reservation in reservations:
        message = (
            f"Recordatorio de pago pendiente:\n"
            f"Reserva: {reservation.court}\n"
            f"Fecha: {reservation.date}\n"
            f"Hora: {reservation.start_time} - {reservation.end_time}\n"
            f"Por favor, realiza el pago para confirmar tu reserva."
        )
        
        notification_service.create_notification(
            user=reservation.user,
            type='PAYMENT_REMINDER',
            title='Pago Pendiente',
            message=message
        )