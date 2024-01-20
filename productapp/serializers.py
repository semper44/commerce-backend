from .models import Product, Cart
from profileapp.models import Profile
from rest_framework import serializers
import json




class productapi(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        # Assuming obj.pics is a Cloudinary resource
        if obj.image:
            # Extract the Cloudinary public ID
            public_id = obj.image.public_id
            # Construct the full Cloudinary image URL
            cloudinary_url = f'http://res.cloudinary.com/dboagqxsq/image/upload/{public_id}'
            return cloudinary_url
        return None  
    
    class Meta:
        model= Product
        fields= "__all__"

class productCartApi(serializers.ModelSerializer):
    
    class Meta:
        model= Product
        fields= ["id", "image", 'image_url',"category", "price", "sellers", ]


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
        fields=["item_qty", "item", "totalAmount"]
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
       
       
     
        
        

