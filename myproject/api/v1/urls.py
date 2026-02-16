from django.urls import path, include
from .views import *

urlpatterns = [
    path('users/', ApiUsers.as_view(), name='api_users'),
    path('user/<int:pk>/', ApiUser.as_view(), name='api_user'),
    path('bookings/', ApiBookings.as_view(), name='api_bookings'),
    path('booking/<int:pk>/', ApiBooking.as_view(), name='api_booking'),
    path('fields/', ApiFields.as_view(), name='api_fields'),
    path('field/<int:pk>/', ApiField.as_view(), name='api_field'),
]