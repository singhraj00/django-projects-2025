from django.urls import path
from apps.payment import views
app_name = 'payment'

urlpatterns = [
    path('book_now/<int:tour_id>/', views.book_now, name='book_now'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('booking_detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path("invoice/<int:booking_id>/", views.download_invoice, name="download_invoice"),
    path('passenger_details/<int:booking_id>/', views.passenger_details, name='passenger_details'),
    path('create_payment/<int:booking_id>/', views.create_payment, name='create_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_failed/<int:booking_id>/', views.payment_failed, name='payment_failed_api'),
    path('failed/<int:booking_id>/', views.failed_page, name='payment_failed_page'),
    path('success/<int:booking_id>/', views.booking_success, name='booking_success'),   
]