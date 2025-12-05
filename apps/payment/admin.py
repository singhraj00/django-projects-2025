from django.contrib import admin
from .models import Booking

# Register your models here.
from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'tour', 'total_amount', 'status', 'payment_order_id', 'payment_id', 'created_at'
    )
    list_filter = ('status', 'created_at', 'tour')
    search_fields = ('user__username', 'user__email', 'tour__title', 'status', 'payment_order_id', 'payment_id')
    readonly_fields = ('created_at', 'updated_at', 'payment_order_id', 'payment_id', 'payment_signature')

    fieldsets = (
        ('Booking Info', {
            'fields': ('user', 'tour', 'total_amount', 'status')
        }),
        ('Payment Details', {
            'fields': ('payment_order_id', 'payment_id', 'payment_signature')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    ordering = ('-created_at',)
    list_per_page = 20
    
