from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Cart, MostBoughtData, Product

# @receiver(post_save, sender=Cart)
# def most_bought(sender, instance, created, **kwargs):
#     if created:
#         # product_id=instance.item.all()
#         cart1=Cart.objects.exclude(completed="no")
#         for i in cart1:
#             product1=i.item.all()
#             # print(cart1)
#             # print(cart1.category)
#             print(product1.category)

#         # cart=Cart.objects.get(item__category__in=product_id)
#         # print(product1)
#         # print(product.category)
#         # print(vars(cart))
#         # print(cart._meta.get_fields())
#         # product=Product.objects.filter(id=instance.item)
#         # print(product)
#         # MostBoughtData.objects.all().delete()
#         # MostBoughtData.objects.create(most_bought=instance)

