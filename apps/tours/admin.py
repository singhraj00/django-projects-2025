from django.contrib import admin
from .models import Tour

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'created_at')
    search_fields = ('title', 'location')
    list_filter = ('location', 'created_at')
    fieldsets = (
        ('Basic Info', {'fields': ('title', 'location', 'duration', 'price')}),
        ('Media', {'fields': ('image', 'image_url')}),
        ('Description', {'fields': ('description',)}),
    )
