from .models import Product, Cart
from profileapp.models import Profile
from rest_framework import serializers
import json




class productapi(serializers.ModelSerializer):
    class Meta:
        model= Product
        fields= "__all__"

class productCartApi(serializers.ModelSerializer):
    # qty= serializers.SerializerMethodField("product_qty")

    # def product_qty(self, id):
    #     
    class Meta:
        model= Product
        fields= ["id", "image", "category", "price", "sellers"]


# class ProfileSerialized(serializers.ModelSerializer):
#     class Meta:
#         model= Profile
#         fields= ['user']



# class ProductSerialized(serializers.ModelSerializer):
#     UserProfile = serializers.SerializerMethodField()  
#     class Meta:
#         model = Product
#         fields =['description', 'price', 'size', 'UserProfile']

#     def get_UserProfile(self, obj):
#         # value = obj.get_values()
#         # UserProfile = Profile.objects.filter(mergefields_contained_by=value)
#         return "ProductSerialized"
        
    

class Cartapi(serializers.ModelSerializer):
    item_qty = serializers.SerializerMethodField("_get_item_qty")  
    # item=("id", "image", "category", "price")
    def _get_item_qty(self, obj):
        qty={}
        for i in json.loads(obj.item_qty):
            qty[i] = qty.get(i, 0) + 1
        return qty
    # value = obj.get_values(
    # UserProfile = Profile.objects.filter(mergefields_contained_by=value)
        # 
    # product= productCartApi(many=True)
    class Meta:
        model= Cart
        fields=["item_qty", "item"]
        depth= 1

class SimpleCartapi(serializers.ModelSerializer):
    class Meta:
        model= Cart
        fields=["item_qty", "item", "reference"]
        depth= 1

class MostBoughtCategoryapi(serializers.ModelSerializer):
    # item_qty = serializers.SerializerMethodField("_get_item_category")  
    # def _get_item_category(self, obj):
    #     qty={}
    #     # for i in json.loads(obj.item_qty):
    #     for i in obj.category:
    #         qty[i] = qty.get(i, 0) + 1
    #             #     return qty
    class Meta:
        model= Product
        fields=["category"]
        # depth= 1
       
       
     
        
        

