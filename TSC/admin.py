from django.contrib import admin
from .models import*

admin.site.register(UserProfile)
admin.site.register(Notice)
admin.site.register(Room_Type)
admin.site.register(Room)
admin.site.register(Booking)


# Register your models here.
