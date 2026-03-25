from django.db import models
from django.contrib.auth.models import User
from vehicles.models import Vehicle

class Rental(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.customer} - {self.vehicle}"

class RegistrationRequest(models.Model):
    username = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    password = models.CharField(max_length=254)
    role = models.CharField(max_length=10)  # 'admin' or 'user'
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)