from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

class Court(models.Model):
    name = models.CharField('Nombre', max_length=50)
    is_active = models.BooleanField('Activa', default=True)
    price_per_hour = models.DecimalField('Precio por hora', max_digits=8, decimal_places=2)
    image = models.ImageField('Imagen', upload_to='courts/', null=True, blank=True)
    opening_time = models.TimeField('Hora de apertura', default='07:00')
    closing_time = models.TimeField('Hora de cierre', default='22:00')
    available_days = models.CharField(
        'Días disponibles',
        max_length=7,
        default='1234567',  # 1=Lunes, 7=Domingo
        help_text='1=Lunes, 2=Martes, etc.'
    )
    
    class Meta:
        verbose_name = 'Cancha'
        verbose_name_plural = 'Canchas'

    def __str__(self):
        return self.name

    def is_available(self, date, start_time):
        # Validar día de la semana
        weekday = str(date.isoweekday())  # 1-7 (Lunes-Domingo)
        if weekday not in self.available_days:
            return False, "La cancha no está disponible este día"
            
        # Validar horario
        if start_time < self.opening_time or start_time >= self.closing_time:
            return False, "Horario fuera del horario de operación"
            
        return True, "Disponible"

class Membership(models.Model):
    MEMBERSHIP_TYPES = [
        ('BASIC', 'Básico'),
        ('PREMIUM', 'Premium'),
        ('VIP', 'VIP'),
    ]
    
    type = models.CharField('Tipo', max_length=10, choices=MEMBERSHIP_TYPES)
    name = models.CharField('Nombre', max_length=100)
    price = models.DecimalField('Precio', max_digits=8, decimal_places=2)
    duration_days = models.IntegerField('Duración en días')
    benefits = models.TextField('Beneficios')
    is_active = models.BooleanField('Activa', default=True)
    
    class Meta:
        verbose_name = 'Membresía'
        verbose_name_plural = 'Membresías'

    def __str__(self):
        return f"{self.get_type_display()} - {self.name}"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmada'),
        ('CANCELLED', 'Cancelada'),
        ('COMPLETED', 'Completada'),
    ]
    
    user = models.ForeignKey(User, verbose_name='Usuario', on_delete=models.CASCADE)
    court = models.ForeignKey(Court, verbose_name='Cancha', on_delete=models.CASCADE)
    date = models.DateField('Fecha')
    start_time = models.TimeField('Hora de inicio')
    end_time = models.TimeField('Hora de fin')
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00
    )
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.court} - {self.date} {self.start_time}"

    def clean(self):
        # Validar que la fecha no sea en el pasado
        if self.date < timezone.now().date():
            raise ValidationError('No se pueden hacer reservas en fechas pasadas')

        # Validar que la hora de fin sea posterior a la de inicio
        if self.end_time <= self.start_time:
            raise ValidationError('La hora de fin debe ser posterior a la hora de inicio')

        # Validar que no haya reservas superpuestas para la misma cancha
        overlapping = Reservation.objects.filter(
            court=self.court,
            date=self.date,
            status__in=['PENDING', 'CONFIRMED']
        ).exclude(id=self.id)

        for reservation in overlapping:
            if (self.start_time < reservation.end_time and 
                self.end_time > reservation.start_time):
                raise ValidationError('Ya existe una reserva para este horario')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('CARD', 'Tarjeta'),
        ('PAGOMOVIL', 'Pago Móvil'),
        ('ZELLE', 'Zelle'),
    ]
    
    BANK_CHOICES = [
        ('BANCO1', 'Banco 1'),
        ('BANCO2', 'Banco 2'),
        ('BANCO3', 'Banco 3'),
        ('BANCO4', 'Banco 4'),
        ('BANCO5', 'Banco 5'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PENDING_VALIDATION', 'Pendiente de Validación'),
        ('COMPLETED', 'Completado'),
        ('FAILED', 'Fallido'),
        ('REFUNDED', 'Reembolsado'),
    ]

    reservation = models.ForeignKey(
        'Reservation',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(
        max_length=20, 
        choices=PAYMENT_TYPES,
        default='CARD'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Para pagos con Stripe
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Para transferencias/pago móvil
    payment_proof = models.ImageField(
        upload_to='payment_proofs/', 
        null=True, 
        blank=True,
        verbose_name='Comprobante de pago'
    )
    bank_reference = models.CharField(max_length=50, null=True, blank=True)
    
    # Campos específicos para pago móvil
    reference_last_digits = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name='Últimos 4 dígitos de referencia'
    )
    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name='Número de teléfono'
    )
    bank = models.CharField(
        max_length=20,
        choices=BANK_CHOICES,
        null=True,
        blank=True,
        verbose_name='Banco'
    )
    
    # Para pagos en efectivo y validaciones
    received_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='payments_received',
        verbose_name='Recibido por'
    )
    validation_notes = models.TextField(blank=True)
    
    # Campos específicos para Zelle
    zelle_email = models.EmailField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text='Email de la cuenta Zelle que realizó el pago'
    )
    zelle_holder = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Nombre del titular de la cuenta Zelle'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def clean(self):
        super().clean()
        if self.payment_type == 'ZELLE':
            if not self.payment_proof:
                raise ValidationError('La captura de pantalla es requerida para pagos Zelle')
            if not self.zelle_email:
                raise ValidationError('El email de Zelle es requerido')
            if not self.zelle_holder:
                raise ValidationError('El nombre del titular de Zelle es requerido')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    phone = models.CharField('Teléfono', max_length=15)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Membresía')
    membership_expiry = models.DateField('Vencimiento de membresía', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('PAYMENT_PENDING', 'Pago Pendiente'),
        ('PAYMENT_STATUS', 'Estado de Pago'),
    ]

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"{self.title} - {self.user.username}"
