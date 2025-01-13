from django.contrib import admin
from .models import Court, Membership, Reservation, Payment

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
    list_display = ('reservation', 'amount', 'payment_type', 'status', 'created_at')
    list_filter = ('payment_type', 'status', 'created_at')
    search_fields = ('reservation__user__username', 'notes')
    date_hierarchy = 'created_at'
