from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Court(models.Model):
    name = models.CharField('Nombre', max_length=50)
    is_active = models.BooleanField('Activa', default=True)
    price_per_hour = models.DecimalField('Precio por hora', max_digits=8, decimal_places=2)
    image = models.ImageField('Imagen', upload_to='courts/', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Cancha'
        verbose_name_plural = 'Canchas'

    def __str__(self):
        return self.name

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
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.court} - {self.date} {self.start_time}"

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('CASH', 'Efectivo'),
        ('TRANSFER', 'Transferencia'),
        ('ONLINE', 'Pago en línea'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('COMPLETED', 'Completado'),
        ('FAILED', 'Fallido'),
        ('REFUNDED', 'Reembolsado'),
    ]
    
    reservation = models.ForeignKey(Reservation, verbose_name='Reserva', on_delete=models.CASCADE)
    amount = models.DecimalField('Monto', max_digits=8, decimal_places=2)
    payment_type = models.CharField('Tipo de pago', max_length=10, choices=PAYMENT_TYPES)
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_proof = models.ImageField('Comprobante de pago', upload_to='payments/', null=True, blank=True)
    notes = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f"{self.reservation} - {self.amount}"
