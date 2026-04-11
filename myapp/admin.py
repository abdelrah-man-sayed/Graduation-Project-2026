from django.contrib import admin
from .models import Users, Fields, Bookings, FieldImages

admin.site.register(Users)
admin.site.register(Bookings)
admin.site.register(FieldImages)

class FieldImageInline(admin.TabularInline):
    model = FieldImages
    extra = 3

@admin.register(Fields)
class FieldsAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'price_per_hour', 'location')
    inlines = [FieldImageInline]