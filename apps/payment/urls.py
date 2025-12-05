from django.urls import path
from . import views
app_name = 'payment'
urlpatterns = [
    path('create_payment/<int:tour_id>/', views.create_payment, name='create_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_failed/<int:booking_id>/', views.payment_failed, name='payment_failed_api'),
    path('failed/<int:booking_id>/', views.failed_page, name='payment_failed_page'),
    path('success/<int:booking_id>/', views.booking_success, name='booking_success'),   
]