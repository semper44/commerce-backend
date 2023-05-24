from django.contrib import admin 
# from .models import  

from .models import ( 
    Product, 
    Cart, 
    MostBoughtData, 
    
    )

# Register your models here.
admin.site.register((Product))
admin.site.register((Cart))
admin.site.register(MostBoughtData)
# admin.site.register(KeyVal)
# admin.site.register((Your_rder))


