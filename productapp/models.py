from datetime import datetime
from django.db import models
from profileapp.models import Profile

# from django.contrib.postgres.fields.jsonb import JSONField

# Create your models here.

def upload_to(instance, filename):
    return 'posts/{filename}'.format(filename=filename)

PRODUCT_CHOICES=(
    ("electronics", "electronics"),
    ("computing", "computing"),
    ("home & office", "home & office"),
    ("baby product", "baby product"),
    ("game", "game"),
    ("fashion", "fashion"),
)

class Product(models.Model):
    category= models.CharField( max_length= 50, choices= PRODUCT_CHOICES)
    description = models.CharField(max_length=70, blank=True, null=True)
    image = models.ImageField(null = True, blank =True, upload_to=upload_to, default='/posts/default.png')
    price = models.FloatField()
    sellers= models.ForeignKey(Profile, on_delete= models.CASCADE,  related_name= "sellers")
    size = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=70, blank=True, null=True)
    sellerName = models.CharField(max_length=70,default="kosi")

    def __str__(self):
        return self.category

CART_CHOICES=(
    ("yes", "yes"),
    ("no", "no"))

class Cart(models.Model):
    item= models.ManyToManyField(Product, related_name= "orders")
    date_created = models.DateTimeField(auto_now_add=True)
    owners= models.ForeignKey(Profile, on_delete=models.CASCADE)
    completed= models.CharField(max_length=20, choices=CART_CHOICES, default="no")
    item_qty= models.TextField()
    cartSize= models.TextField(default=0)
    reference=models.CharField(max_length=20, blank=True, null=True)
    # def __str__(self):
    #     return f"{self.owners}-{self.date_created}"



class MostBoughtData(models.Model):
    electronics=models.IntegerField(default=0)
    computing=models.IntegerField(default=0)
    homeandoffice=models.IntegerField(default=0)
    phonesandcomputers=models.IntegerField(default=0)
    womens_fashion=models.IntegerField(default=0)
    mens_fashion=models.IntegerField(default=0)
    baby_product=models.IntegerField(default=0)
    game=models.IntegerField(default=0)
    sports_wears=models.IntegerField(default=0)
    automobiles=models.IntegerField(default=0)
   
# class Data(models.Model):
#     data=PickledObjectField()

# class Dicty(models.Model):
#     name      = models.CharField(max_length=70)
#     def __str__(self):
#         return self.name

# class KeyVal(models.Model):
#     container = models.ForeignKey(Dicty,on_delete=models.CASCADE, db_index=True)
#     key       = models.CharField(max_length=200, db_index=True)
#     value     = models.CharField(max_length=200, db_index=True)
#     def __str__(self):
#         return self.container

# class Order(models.Model):
#     ordered=models.ForeignKey(Product, on_delete= models.CASCADE,  related_name= "orders")
#     sellers= models.ForeignKey(Profile, on_delete= models.CASCADE,  related_name= "order_sellers")
#     buyers= models.ForeignKey(Profile, on_delete= models.CASCADE,  related_name= "order_buyers")
#     date_created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.ordered}-{self.date_created}"

# class OrderRelationship(models.Model):
#     order_sellers = models.ForeignKey(Profile, on_delete= models.CASCADE,  related_name= "order_sellers")
#     order_buyers = models.ForeignKey(Profile, on_delete= models.CASCADE, related_name= 'order_relationship_buyers')

# class Your_rder(models.Model):
#     your_orders=models.ForeignKey(Order, on_delete= models.CASCADE,  related_name= "your_orders")
#     def __str__(self):
#         return f"{self.your_orders}"
    
    # date_created = models.DateTimeField(auto_now_add=True)
    # seller= models.OneToOneField(Profile, on_delete= models.CASCADE)
    # buyers= models.ForeignKey(Profile, on_delete= models.CASCADE,  related_name= "your_order_buyers")
