from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    path('', views.home, name='home'),
    path('tours/', views.tours_list_view, name='tours_list'),
    path('tours/<int:tour_id>/', views.tour_detail_view, name='tour_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
] 

