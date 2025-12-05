from django.db import models
from django.conf import settings
from apps.tours.models import Tour
from decimal import Decimal
from django.core.validators import MinValueValidator

# Create your models here.
class Booking(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_FAILED, 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='bookings')

    # Trip details
    travel_date = models.DateField(null=True, blank=True)
    number_of_people = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    pickup_city = models.CharField(max_length=120, null=True, blank=True)
    drop_city = models.CharField(max_length=120, null=True, blank=True)
    pickup_point = models.CharField(max_length=255, null=True, blank=True, help_text="Exact pickup landmark or hotel")
    notes = models.TextField(null=True, blank=True)

    # Contact & emergency
    contact_name = models.CharField(max_length=150, null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=150, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, null=True, blank=True)

    # Pricing & invoice
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=6, default='INR')  
    invoice = models.FileField(upload_to="invoices/", null=True, blank=True)

    # Razorpay / payment fields
    payment_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_signature = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def __str__(self):
        return f"Booking #{self.id} — {self.tour.title} — {self.user}"

    def calculate_base_amount(self):
        """
        Returns base amount (per person price * number_of_people).
        Use Decimal for arithmetic to avoid Decimal/float mixing errors.
        """
        base_price = Decimal(self.tour.price or Decimal('0.00'))
        return (base_price * Decimal(self.number_of_people)).quantize(Decimal('0.01'))

    def calculate_gst(self, gst_percent=Decimal('5.0')):
        """
        Calculate GST amount. gst_percent given in percent (e.g. 5.0 for 5%).
        Returns Decimal rounded to 2 decimal places.
        """
        base = self.calculate_base_amount()
        gst_rate = (gst_percent / Decimal('100'))
        return (base * gst_rate).quantize(Decimal('0.01'))

    def calculate_total(self, gst_percent=Decimal('5.0')):
        base = self.calculate_base_amount()
        gst = self.calculate_gst(gst_percent=gst_percent)
        total = (base + gst).quantize(Decimal('0.01'))
        return total

    def update_total_amount(self, gst_percent=Decimal('5.0'), save=True):
        """
        Helper to set total_amount from tour.price and number_of_people.
        Call this when booking is created or when number_of_people changes.
        """
        self.total_amount = self.calculate_total(gst_percent=gst_percent)
        if save:
            self.save(update_fields=['total_amount', 'updated_at'])
        return self.total_amount


class Passenger(models.Model):
    GENDER_MALE = 'MALE'
    GENDER_FEMALE = 'FEMALE'
    GENDER_OTHER = 'OTHER'

    GENDER_CHOICES = [
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    ]

    ID_AADHAR = 'AADHAR'
    ID_PAN = 'PAN'
    ID_PASSPORT = 'PASSPORT'
    ID_DL = 'DL'  # driving license
    ID_VOTER = 'VOTER'

    ID_TYPE_CHOICES = [
        (ID_AADHAR, 'Aadhar Card'),
        (ID_PAN, 'PAN Card'),
        (ID_PASSPORT, 'Passport'),
        (ID_DL, 'Driving License'),
        (ID_VOTER, 'Voter ID'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    full_name = models.CharField(max_length=150)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=12, choices=GENDER_CHOICES, default=GENDER_MALE)
    nationality = models.CharField(max_length=100, default='Indian')
    id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES, default=ID_AADHAR)
    id_number = models.CharField(max_length=120, blank=True, null=True)

    special_requirements = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = "Passenger"
        verbose_name_plural = "Passengers"

    def __str__(self):
        return f"{self.full_name} ({self.id_type}: {self.id_number})"