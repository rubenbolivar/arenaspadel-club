from django.conf import settings
from .models import Notification
import requests

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