from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:vehicle_id>/', views.book_vehicle, name='book_vehicle'),
    path('history/', views.rental_history, name='rental_history'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]