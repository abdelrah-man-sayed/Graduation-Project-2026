from django.urls import path, include
from .views import *

urlpatterns = [
    path('users/', ApiUsers.as_view(), name='api_users'),
    path('user/<int:user_id>/', ApiUser.as_view(), name='api_user'),
    path('bookings/', ApiBookings.as_view(), name='api_bookings'),
    path('booking/<int:booking_id>/', ApiBooking.as_view(), name='api_booking'),
    path('fields/', ApiFields.as_view(), name='api_fields'),
    path('field/<int:field_id>/', ApiField.as_view(), name='api_field'),
]