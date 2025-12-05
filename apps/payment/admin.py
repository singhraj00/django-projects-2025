from django.contrib import admin
from .models import Booking, Passenger, Tour
from decimal import Decimal


class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 1
    fields = ("full_name", "age", "gender", "nationality", "id_type", "id_number", "special_requirements")
    readonly_fields = ()
    min_num = 0
    can_delete = True


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "tour",
        "travel_date",
        "number_of_people",
        "total_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "travel_date", "tour__location")
    search_fields = ("id", "user__username", "user__email", "tour__title")
    
    readonly_fields = (
        "created_at",
        "updated_at",
        "payment_order_id",
        "payment_id",
        "payment_signature",
    )

    inlines = [PassengerInline]

    fieldsets = (
        ("Booking Info", {
            "fields": ("user", "tour", "travel_date", "number_of_people", "notes")
        }),
        ("Pickup / Drop", {
            "fields": ("pickup_city", "drop_city", "pickup_point")
        }),
        ("Contact Information", {
            "fields": ("contact_name", "contact_phone", "emergency_contact_name", "emergency_contact_phone")
        }),
        ("Payment & Invoice", {
            "fields": (
                "total_amount",
                "currency",
                "invoice",
                "status",
                "payment_order_id",
                "payment_id",
                "payment_signature",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Auto-update total_amount based on number_of_people * tour.price + GST.
        (Only update if admin is editing booking.)
        """
        if not obj.total_amount or "number_of_people" in form.changed_data:
            obj.update_total_amount()

        super().save_model(request, obj, form, change)


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "booking", "gender", "age", "id_type", "id_number")
    list_filter = ("gender", "id_type", "nationality")
    search_fields = ("full_name", "id_number")



