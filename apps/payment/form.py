from django import forms
from .models import Booking,Passenger

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "travel_date",
            "number_of_people",
            "pickup_city",
            "drop_city",
            "pickup_point",
            "contact_name",
            "contact_phone",
            "emergency_contact_name",
            "emergency_contact_phone",
            "notes",
        ]

        widgets = {
            "travel_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = [
            "full_name", "age", "gender",
            "nationality", "id_type", "id_number",
            "special_requirements"
        ]
