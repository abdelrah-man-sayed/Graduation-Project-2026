from django.urls import path, include
from .views import *

urlpatterns = [
    path('users/', api_users, name='api_users'),
    path('user/<int:user_id>/', api_user, name='api_user'),
    path('bookings/', api_bookings, name='api_bookings'),
    path('booking/<int:booking_id>/', api_booking, name='api_booking'),
    path('fields/', api_fields, name='api_fields'),
    path('field/<int:field_id>/', api_field, name='api_field'),
]