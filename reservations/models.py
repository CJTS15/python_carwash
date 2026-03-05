from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime

class AddOn(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.name} (+₱{self.price})"

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    min_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    max_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    duration_minutes = models.IntegerField(default=60)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)

    def clean(self):
        if self.min_price > self.max_price:
            raise ValidationError("Minimum price cannot be higher than maximum price.")

    def __str__(self):
        return f"{self.name} (₱{self.min_price} - ₱{self.max_price})"

class Appointment(models.Model):
    # Use constants for status to avoid typos in views.py
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_IN_PROGRESS = 'progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELED = 'canceled' # Standardized to one 'L' for consistency

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELED, 'Canceled'),
    ]

    TIME_CHOICES = [
        (datetime.time(hour, 0), f"{hour if hour <= 12 else hour-12}:00 {'AM' if hour < 12 else 'PM'}")
        for hour in range(8, 18)
    ]

    # NEW: Assign a specific staff member (user with is_staff=True)
    assigned_staff = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_jobs',
        limit_choices_to={'is_staff': True} # Only show staff in the dropdown
    )

    # Guest Info
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField()
    car_plate = models.CharField(max_length=20)
    car_model = models.CharField(max_length=100)

    # Internal Logic
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    add_ons = models.ManyToManyField(AddOn, blank=True)
    date = models.DateField()
    time_slot = models.TimeField(choices=TIME_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time_slot'] # Default sort: newest first

    def __str__(self):
        # FIXED: Removed the duplicate method that caused the crash.
        # This version safely handles guest bookings.
        return f"{self.customer_name} - {self.car_plate} ({self.date} @ {self.time_slot})"

    def clean(self):
        """Logic for booking rules."""
        # 1. Past Date Check
        if self.date < datetime.date.today():
            raise ValidationError("You cannot book an appointment in the past.")

        # 2. Availability Check
        active_bookings = Appointment.objects.filter(
            date=self.date,
            time_slot=self.time_slot,
            status__in=[self.STATUS_PENDING, self.STATUS_CONFIRMED]
        ).exclude(id=self.id)

        if active_bookings.exists():
            raise ValidationError(f"The slot {self.time_slot.strftime('%I:%M %p')} is already reserved.")

    def save(self, *args, **kwargs):
        # Auto-uppercase plate numbers for a cleaner database
        self.car_plate = self.car_plate.upper()
        self.full_clean()
        super().save(*args, **kwargs)

    # --- Properties ---

    @property
    def total_addons_price(self):
        # Using a check to ensure we don't crash if the object isn't saved yet
        if not self.id: return 0
        return sum(addon.price for addon in self.add_ons.all())

    @property
    def total_price_range(self):
        """Returns the full estimated range including add-ons."""
        min_total = self.service.min_price + self.total_addons_price
        max_total = self.service.max_price + self.total_addons_price
        return f"₱{min_total:,.2f} - ₱{max_total:,.2f}"

    def get_datetime(self):
        return datetime.datetime.combine(self.date, self.time_slot)

    @property
    def can_cancel(self):
        """Allows cancellation only if appointment is > 2 hours away."""
        now = datetime.datetime.now()
        appointment_dt = self.get_datetime()
        return appointment_dt > (now + datetime.timedelta(hours=2))
    
    @property
    def expected_finish_time(self):
        """Calculates finish time based on service duration."""
        start_dt = self.get_datetime()
        finish_dt = start_dt + datetime.timedelta(minutes=self.service.duration_minutes)
        return finish_dt.time().strftime('%I:%M %p')
    
    final_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    commission_earned = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    def calculate_commission(self):
        """Calculates the washer's cut based on the final price."""
        percentage = self.service.commission_percentage / 100
        self.commission_earned = self.final_price * percentage

    def save(self, *args, **kwargs):
        # Auto-calculate commission if a final price is provided
        if self.final_price > 0:
            self.calculate_commission()
        super().save(*args, **kwargs)