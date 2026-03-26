from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:vehicle_id>/', views.book_vehicle, name='book_vehicle'),
    path('history/', views.rental_history, name='rental_history'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('cancel/<int:rental_id>/', views.cancel_rental, name='cancel_rental'),
    path('modify/<int:rental_id>/', views.modify_rental, name='modify_rental'),
    path('review/<int:rental_id>/', views.review_rental, name='review_rental'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('support/', views.support, name='support'),
]