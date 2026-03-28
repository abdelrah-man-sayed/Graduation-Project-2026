from django.contrib import admin

# Register your models here.
from .models import Users, Fields, Bookings
admin.site.register(Users)
admin.site.register(Fields)
admin.site.register(Bookings)
