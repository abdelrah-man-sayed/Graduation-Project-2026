from django.contrib import admin

# Register your models here.
from .models import Users, Fields, Bookings, Teams
admin.site.register(Users)
admin.site.register(Fields)
admin.site.register(Bookings)
admin.site.register(Teams)
