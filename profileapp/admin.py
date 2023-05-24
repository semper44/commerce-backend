from django.contrib import admin
from .models import (
    Profile, 
    Relationship,
    Review, 
    Notifications,
    productNotifications)

# Register your models here.
admin.site.register((Profile))
admin.site.register((productNotifications))
admin.site.register((Relationship))
admin.site.register((Review))
admin.site.register((Notifications))
