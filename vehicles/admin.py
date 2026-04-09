from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model', 'price_per_day', 'available', 'get_average_rating', 'get_review_count']
    list_filter = ['available', 'brand']
    search_fields = ['brand', 'model']
    readonly_fields = ['get_average_rating', 'get_review_count']
    fieldsets = (
        ('Vehicle Information', {
            'fields': ['brand', 'model', 'price_per_day', 'available', 'image']
        }),
        ('Statistics', {
            'fields': ['get_average_rating', 'get_review_count'],
            'classes': ('collapse',)
        }),
    )

    def get_average_rating(self, obj):
        """Display the average rating for the vehicle."""
        avg = obj.average_rating
        return f"{avg} ⭐" if avg else "No ratings"
    get_average_rating.short_description = "Average Rating"

    def get_review_count(self, obj):
        """Display the count of reviews for the vehicle."""
        return f"{obj.review_count} reviews"
    get_review_count.short_description = "Review Count"