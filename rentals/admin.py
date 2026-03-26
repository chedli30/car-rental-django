from django.contrib import admin
from .models import Rental, RegistrationRequest, Profile, Review

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['customer', 'vehicle', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    actions = ['end_rental']

    def end_rental(self, request, queryset):
        for rental in queryset:
            if rental.is_active:
                rental.is_active = False
                rental.save()
                rental.vehicle.available = True
                rental.vehicle.save()
        self.message_user(request, "Location(s) terminée(s) avec succès!")
    end_rental.short_description = "🔚 Terminer la location sélectionnée"

@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'approved']
    list_filter = ['approved', 'role']
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        for req in queryset:
            if not req.approved:
                from django.contrib.auth.models import User
                user = User.objects.create_user(
                    username=req.username,
                    email=req.email,
                    password=req.password
                )
                if req.role == 'admin':
                    user.is_staff = True
                    user.save()
                req.approved = True
                req.save()
        self.message_user(request, "Demandes approuvées avec succès!")
    approve_requests.short_description = "✅ Approuver les demandes sélectionnées"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'photo']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['customer', 'vehicle', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    readonly_fields = ['created_at']