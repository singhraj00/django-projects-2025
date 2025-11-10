from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('tours/', views.tours_list_view, name='tours_list'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
] 

