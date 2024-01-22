from .models import Product, Cart
from profileapp.models import Profile
from profileapp.serializers import profileapi
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
        fields= ["id", "image","category", "price", "sellers", ]


class Cartapi(serializers.ModelSerializer):
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
       
# Assuming you have serializers for Product and Profile models, create or update them as follows:

class ProductSerializer(serializers.ModelSerializer):
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
        model = Product
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        # Assuming obj.pics is a Cloudinary resource
        if obj.pics:
            # Extract the Cloudinary public ID
            public_id = obj.pics.public_id
            # Construct the full Cloudinary image URL
            cloudinary_url = f'http://res.cloudinary.com/dboagqxsq/image/upload/{public_id}'
            return cloudinary_url
        return None 
    class Meta:
        model = Profile
        fields = '__all__'


class SearchResultsSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    profiles = ProfileSerializer(many=True)

    def to_representation(self, instance):
        return {
            'products': ProductSerializer(instance.get('products', []), many=True).data,
            'profiles': ProfileSerializer(instance.get('profiles', []), many=True).data,
        }

