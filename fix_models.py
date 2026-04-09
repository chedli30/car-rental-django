#!/usr/bin/env python
"""Fix the rentals/models.py file"""

models_content = '''from django.db import models
from django.contrib.auth.models import User
from vehicles.models import Vehicle
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

class Rental(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.customer} - {self.vehicle}"

    def save(self, *args, **kwargs):
        # Always recalculate total_price when dates change
        days = (self.end_date - self.start_date).days
        self.total_price = days * self.vehicle.price_per_day
        super().save(*args, **kwargs)

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("Start date must be before end date")

class Review(models.Model):
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1 étoile'), (2, '2 étoiles'), (3, '3 étoiles'), (4, '4 étoiles'), (5, '5 étoiles')])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.username} for {self.vehicle.brand} {self.vehicle.model}"

    class Meta:
        ordering = ['-created_at']


class RegistrationRequest(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    password = models.CharField(max_length=254)  # Stored as hash via make_password
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('user', 'User')])
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"Profil de {self.user.username}"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile when a new User is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Automatically save Profile when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.get_or_create(user=instance)
'''

with open('rentals/models.py', 'w', encoding='utf-8') as f:
    f.write(models_content)

print("✅ Fixed rentals/models.py successfully")
