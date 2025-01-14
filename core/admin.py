from django.contrib import admin
from .models import Court, Membership, Reservation, Payment, UserProfile

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'price_per_hour')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'price', 'duration_days', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('court', 'user', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date', 'court')
    search_fields = ('user__username', 'court__name')
    date_hierarchy = 'date'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'reservation', 'payment_type', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_type']
    search_fields = ['reservation__id', 'stripe_payment_intent_id', 'phone_number']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('reservation', 'amount', 'payment_type', 'status')
        }),
        ('Pago Móvil', {
            'fields': ('reference_last_digits', 'phone_number', 'bank', 'payment_proof'),
            'classes': ('collapse',),
        }),
        ('Stripe', {
            'fields': ('stripe_payment_intent_id',),
            'classes': ('collapse',),
        }),
        ('Validación', {
            'fields': ('received_by', 'validation_notes'),
            'classes': ('collapse',),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'membership', 'membership_expiry')
    list_filter = ('membership',)
    search_fields = ('user__username', 'phone')
    raw_id_fields = ('user', 'membership')
