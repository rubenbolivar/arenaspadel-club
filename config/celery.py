import os
from celery import Celery
from celery.schedules import crontab

# Configurar variables de entorno para Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Crear instancia de Celery
app = Celery('arenaspadel')

# Configuración usando objeto
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar tareas automáticamente
app.autodiscover_tasks()

# Configurar tareas programadas después de que Django esté listo
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=9, minute=0),  # Todos los días a las 9:00 AM
        'core.tasks.send_reservation_reminders'
    )
    
    sender.add_periodic_task(
        crontab(hour='*/4'),  # Cada 4 horas
        'core.tasks.send_payment_reminder'
    )