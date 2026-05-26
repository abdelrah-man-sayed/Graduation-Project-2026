from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Users(AbstractUser):
    full_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    user_type = models.CharField(
        max_length=20, 
        choices=[('player', 'Player'), ('owner', 'Owner'), ('admin', 'Admin')],
        default='player'
    )
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    email = models.EmailField(unique=True)

    instagram_link = models.URLField(max_length=200, null=True, blank=True)
    tiktok_link = models.URLField(max_length=200, null=True, blank=True)
    facebook_link = models.URLField(max_length=200, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

class Fields(models.Model):
    field_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    sport_type = models.CharField(max_length=50, default='Football')
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    
    has_lights = models.BooleanField(default=False)
    has_showers = models.BooleanField(default=False)
    has_cafe = models.BooleanField(default=False)
    has_equipment = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'fields'

class Bookings(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]
    
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='bookings')
    field = models.ForeignKey(Fields, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookings'

class Payments(models.Model):
    payment_id = models.AutoField(primary_key=True)
    booking = models.OneToOneField(Bookings, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'

class Notifications(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'

class Messages(models.Model):
    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'messages'

class Review(models.Model):
    field = models.ForeignKey(Fields, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('field', 'user')
        
    def __str__(self):
        return f"Review by {self.user.full_name} for {self.field.name}"

class FieldImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    field = models.ForeignKey(Fields, on_delete=models.CASCADE, related_name='field_images')
    image = models.ImageField(upload_to='field_photos/')
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'field_images'

class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.email} - {self.otp}"