from django.db import models
from django.core.exceptions import ValidationError


def validate_positive_price(value):
    if value <= 0:
        raise ValidationError("Price per day must be positive")


class Vehicle(models.Model):
    model = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_positive_price])
    available = models.BooleanField(default=True)  # Kept for legacy, but logic changed
    image = models.ImageField(upload_to='vehicles/', blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.model}"

    def is_available_for_dates(self, start_date, end_date):
        from rentals.models import Rental
        overlapping = Rental.objects.filter(
            vehicle=self,
            start_date__lt=end_date,
            end_date__gt=start_date
        ).exists()
        return not overlapping

    @property
    def average_rating(self):
        from rentals.models import Review
        reviews = Review.objects.filter(vehicle=self)
        if reviews.exists():
            return round(reviews.aggregate(avg=models.Avg('rating'))['avg'], 1)
        return None

    @property
    def review_count(self):
        from rentals.models import Review
        return Review.objects.filter(vehicle=self).count()

    def clean(self):
        if self.price_per_day <= 0:
            raise ValidationError("Price per day must be positive")