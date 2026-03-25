from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model', 'price_per_day', 'available']
    list_filter = ['available']
    search_fields = ['brand', 'model']