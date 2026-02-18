from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('users', UsersViewSet)
router.register('bookings', BookingsViewSet)
router.register('fields', FieldsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
]