from django.contrib import admin
from .models import Rental, RegistrationRequest, Profile, Review

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['customer', 'vehicle', 'start_date', 'end_date', 'is_active', 'total_price']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['customer__username', 'vehicle__brand', 'vehicle__model']
    readonly_fields = ['total_price']
    fieldsets = (
        ('Rental Details', {
            'fields': ['customer', 'vehicle', 'start_date', 'end_date', 'total_price']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
    )
    actions = ['mark_as_inactive']

    def mark_as_inactive(self, request, queryset):
        """Mark selected rentals as inactive using date-based availability system."""
        updated_count = queryset.update(is_active=False)
        self.message_user(request, f"{updated_count} rental(s) marked as inactive successfully!")
    mark_as_inactive.short_description = "🔚 Mark selected rentals as inactive"

@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'approved', 'created_at']
    list_filter = ['approved', 'role', 'created_at']
    search_fields = ['username', 'email']
    readonly_fields = ['created_at', 'password']
    fieldsets = (
        ('Request Information', {
            'fields': ['username', 'email', 'role', 'password', 'created_at']
        }),
        ('Status', {
            'fields': ['approved']
        }),
    )
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        """Approve registration requests and create corresponding Django users."""
        from django.contrib.auth.models import User
        approved_count = 0
        for req in queryset:
            if not req.approved:
                # Check if user already exists to avoid duplicates
                if not User.objects.filter(username=req.username).exists():
                    # Create user without create_user to avoid re-hashing the password
                    user = User(
                        username=req.username,
                        email=req.email,
                        password=req.password  # Already hashed from make_password() in views.py
                    )
                    if req.role == 'admin':
                        user.is_staff = True
                        user.is_superuser = True
                    user.save()
                req.approved = True
                req.save()
                approved_count += 1
        
        if approved_count > 0:
            self.message_user(request, f"✅ {approved_count} registration request(s) approved successfully!")
        else:
            self.message_user(request, "ℹ️ No new requests to approve.")
    approve_requests.short_description = "✅ Approve selected registration requests"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'photo']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['customer', 'vehicle', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    readonly_fields = ['created_at']