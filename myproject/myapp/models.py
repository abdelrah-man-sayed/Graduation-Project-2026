# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

USER_TYPES = [
        ('player', 'Player'),
        ('owner', 'Owner'),
        ('admin', 'Admin'),
    ]

class Academies(models.Model):
    academy_id = models.AutoField(primary_key=True)
    admin = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    academy_name = models.CharField(max_length=100)
    sport_type = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=50, blank=True, null=True)
    fees = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    schedule = models.TextField(blank=True, null=True)  # This field type is a guess.
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.academy_name

    class Meta:
        managed = False
        db_table = 'academies'


class AcademyEnrollments(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    academy = models.ForeignKey(Academies, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    joined_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'academy_enrollments'


class Bookings(models.Model):
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    field = models.ForeignKey('Fields', models.DO_NOTHING, blank=True, null=True)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, blank=True, null=True)
    payment_status = models.CharField(max_length=20, blank=True, null=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Booking {self.booking_id} by {self.user}"
    
    class Meta:
        managed = False
        db_table = 'bookings'


class Challenges(models.Model):
    challenge_id = models.AutoField(primary_key=True)
    creator_team = models.ForeignKey('Teams', models.DO_NOTHING, blank=True, null=True)
    opponent_team = models.ForeignKey('Teams', models.DO_NOTHING, related_name='challenges_opponent_team_set', blank=True, null=True)
    field = models.ForeignKey('Fields', models.DO_NOTHING, blank=True, null=True)
    challenge_date = models.DateField()
    start_time = models.TimeField()
    status = models.CharField(max_length=20, blank=True, null=True)
    result = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'challenges'


class Fields(models.Model):
    field_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=100)
    sport_type = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    images = models.TextField(blank=True, null=True)  # This field type is a guess.
    rating_avg = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        managed = False
        db_table = 'fields'


class Messages(models.Model):
    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    receiver = models.ForeignKey('Users', models.DO_NOTHING, related_name='messages_receiver_set', blank=True, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(blank=True, null=True)
    is_read = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
    
    class Meta:
        managed = False
        db_table = 'messages'


class Notifications(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notifications'


class Payments(models.Model):
    payment_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Bookings, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payments'


class Ratings(models.Model):
    rating_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    field = models.ForeignKey(Fields, models.DO_NOTHING, blank=True, null=True)
    rating_value = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'ratings'


class TeamMembers(models.Model):
    team_member_id = models.AutoField(primary_key=True)
    team = models.ForeignKey('Teams', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    role = models.CharField(max_length=20, blank=True, null=True)
    joined_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} in {self.team}"
    
    class Meta:
        managed = False
        db_table = 'team_members'


class Teams(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=100)
    captain = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    sport_type = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.team_name
    
    class Meta:
        managed = False
        db_table = 'teams'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=100)
    password_hash = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    user_type = models.CharField(max_length=20, blank=True, null=True, choices=USER_TYPES)
    profile_image = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.full_name

    class Meta:
        managed = False
        db_table = 'users'
