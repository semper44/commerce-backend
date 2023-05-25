import json, asyncio
# import math
import datetime
from django.shortcuts import render, redirect
from .serializers import productapi,productCartApi, Cartapi, MostBoughtCategoryapi
from .models import Product, Cart
from profileapp.models import Profile
from profileapp.serializers import profileapi
from .permissions import Sellerspermission
from django.http import HttpResponse
import requests
import secrets
import random
import os
from django.views.decorators.csrf import csrf_exempt
import environ
from drf_multiple_model.views import FlatMultipleModelAPIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions, filters
# from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser 

env= environ.Env()
environ.Env.read_env()
# Create your views here.
class CreatePost(APIView):
    parser_classes= [MultiPartParser, FormParser]
    permission_classes= [Sellerspermission]

    def post(self, request, format=None):
        print(request.data)
        serializer= productapi(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetProducts(generics.ListCreateAPIView):
    queryset= Product.objects.all()
    serializer_class= productapi

class DeleteProducts(APIView):
    permission_classes= [Sellerspermission]

    # permission_classes= ([permissions.IsAdminUser | permissions.IsAuthenticated])
    def delete(self, request, pk):
        print("request.user.is_superuser")
        print(request.user.is_superuser)
        item= Product.objects.get(id=pk)
        print(item.sellers)
        error= json.dumps({"msg":"Sorry you do not have the necessary permissions"})
        if request.user == item.sellers or request.user.is_superuser==True:
            item.delete()
            print("deleted")
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ListAllProductsByCategory(generics.ListAPIView):
    # permission_classes= [permissions.IsAuthenticated]
    serializer_class= productapi
    def  get_queryset(self):
        category= self.kwargs.get("pk")
        # cart=Cart.objects.filter(owners_id=4, completed="no")
        # print(cart.completed)
        print(category)
        return Product.objects.filter(category=category)
    
class ListProductsDetails(APIView):

    def  get(self, request, pk):
        user= Product.objects.filter(id=pk)
        serializer= productapi(user,many=True, context={'request':request})
        print(user)
        if user.exists():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"product not found"}, status=status.HTTP_404_NOT_FOUND)


class ListProductsBSellers(APIView):

    def  get(self, request, pk):
        user= Product.objects.filter(sellers=pk)
        serializer= productapi(user, many=True, context={'request':request})
        print(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EditProducts(generics.RetrieveUpdateAPIView):
    serializer_class= productapi
    permission_classes= ([permissions.IsAdminUser | permissions.DjangoModelPermissions])
    def  get_queryset(self):
        user= self.request.user.id
        return Product.objects.filter(sellers=user)

class EditSingleUserProduct(generics.RetrieveUpdateAPIView):
    serializer_class= productapi
    permission_classes= ([permissions.IsAdminUser | permissions.DjangoModelPermissions])
    def  get_queryset(self):
        user= self.request.user.id
        return Product.objects.filter(sellers=user)

class sellers_product(generics.ListAPIView):
    serializer_class= productapi
    def get(self, request, pk, *args, **kwargs):
                requester=self.request.user.id
                user=pk
                print(self.request.user)
                obj= Product.objects.filter(user=pk)
                serializer= productapi(obj, many=True, context={'request':request})
                return Response(serializer.data, status=status.HTTP_200_OK)

class AddToCart(APIView):
    parser_classes= [MultiPartParser, FormParser]
    permission_classes= [permissions.IsAuthenticated]
    def post(self, request, format=None):
        print(request.data)
        if request.user.id:
            profile=Profile.objects.get(user=request.user.id)
            items= json.loads(request.data["item"])
            qty= request.data["item_qty"]
            cartSize= json.loads(request.data["cartSize"])
            print(qty)
            cart= Cart.objects.filter(owners=request.user.id, completed="no")
            # cart.form()
            if cart.exists():
                print("next")
                cart.delete()
            carts= Cart.objects.create(owners=profile, item_qty= qty, cartSize=cartSize)
            for i in items:
                itemz=Product.objects.get(id=i)
                carts.item.add(itemz)
            carts.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"msg": "Sorry, you dont have the necessary permissions for this"},status=status.HTTP_401_UNATHOURIZED)

class RetrieveCart(APIView):
    # permission_classes= [permissions.IsAuthenticated]
    def  get(self, request, **kwargs):
        cart=Cart.objects.filter(owners_id=request.user.id, completed="no")
        print(cart)
        if cart.exists():
            for i in cart:
                cartProduct= i.item.all()
                # print(i.item_qty)
                item= productCartApi(cartProduct, many=True, context={'request':request})
            #     print("i.item_qty")

            datas={"serializer":item.data, "id":i.id, "cartSize":i.cartSize, "item_qty":i.item_qty}
            print(datas)
            return Response(datas, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"cart not found"}, status=status.HTTP_201_CREATED)

class PlaceOrder(APIView):
    def post(self, request, *args, **kwargs):       
        auth_token = env("PAYSTACK_AUTH_TOKEN")
        print(request.data)
        hed = {'Authorization': 'Bearer' + auth_token}
        metadata= json.dumps({"cart_id":2})
        cartId=request.data["cartId"]
        print(cartId)
        if cartId==None:
            profile=Profile.objects.get(user=request.user.id)
            items= json.loads(request.data["item"])
            qty= request.data["item_qty"]
            cartSize= json.loads(request.data["cartSize"])
            print(qty)
            carts= Cart.objects.create(owners=profile, item_qty= qty, cartSize=cartSize)
            for i in items:
                itemz=Product.objects.get(id=i)
                carts.item.add(itemz)
            carts.save()
            # carts.save()
        else:
        # cartId=59
            datum={    
                "email":"emmanuelcopeters@gmail.com",
                "amount":6000,
                'callback_url': f"http://localhost:3000/confirmandupdateorder/{cartId}/",
                "metadata":metadata
                }
            # print(datum)
            url = 'https://api.paystack.co/transaction/initialize'        
            response = requests.post(url, data=datum, headers=hed)
            responses=response.json()
            # link=response['data']['link']
            print(response)
            print(responses)
            # print("link")
            if responses["status"]==True:
                return Response({"link":responses["data"]["authorization_url"], "code":200}, status=status.HTTP_200_OK)
            else:
                return Response({"message":response["message"], "code":400}, status=status.HTTP_200_BAD_REQUEST)
       

class ConfirmAndUpdateOrder(APIView):
   def post(self, request):
        # cart=request.session['cart_id']
        print(request.data)
        reference=None
        auth_token = env("PAYSTACK_AUTH_TOKEN")
        hed = {'Authorization': 'Bearer' + auth_token}
       
        try:
            reference=request.data['reference']
            cart_id=request.data['cart_id']
            url = f"https://api.paystack.co/transaction/verify/{reference}"        
            response = requests.get(url, headers=hed)
            responses=response.json()
            print(responses)
            if responses["data"]["status"]=="success":
                cart= Cart.objects.get(id=int(cart_id))
                cart.completed= "yes"
                cart.reference= reference
                cart.save(update_fields=["completed", "reference"])  
                return Response({"msg":"purchase made successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"msg":"purchase failed, please try again later"}, status=status.HTTP_400_BAD_REQUEST)


class MonthlyOrders(APIView):
    # serializer_class = UserApi
    # permission_classes= [peCartrmissions.IsAdminUser]
    def get(self, request):
        today= datetime.datetime.today()
        print(today)
        previous_month = today.month-1
    
        previous_two_month = today.month-2
        # previous_two_month_date= datetime.datetime(today.year, previous_two_month, today.day)
        print("queryset")

        queryset= Cart.objects.filter(completed="yes", date_created__month= today.month)
        # serialized= UserApi(queryset1, many=True)
        current=len(queryset)
        queryset1= Cart.objects.filter(completed="yes", date_created__month=previous_month)
        print(queryset1)
        previous=len(queryset1)

        querysets2= Cart.objects.filter(completed="yes", date_created__month= previous_two_month)
        previous_two_month=len(querysets2)
        
        data=[current, previous, previous_two_month]
       
        return Response(data, status=status.HTTP_200_OK)

class MostBoughtCategory(APIView):
    def  get(self, request):
        cart1=Cart.objects.exclude(completed="no")
        category_counts={}
        for i in cart1:
            product=i.item.all()
            for x in product:
                category_counts[x.category] = category_counts.get(x.category, 0) + 1
        return Response(category_counts, status=status.HTTP_200_OK)


class AllCategories(APIView):
    def  get(self, request):
        pro= Product()
        arr=[]
        products= pro._meta.get_field('category').choices
        print(products)
        for products_value, products_label in products:
            arr.append(products_label)
            print(products_label)
        return Response(arr, status=status.HTTP_200_OK)
        

# lass MostBoughtCategory(APIView):
#     def  get(self, request):
#         # profile=self.request.user.id
#         # cart=Cart.objects.filter(completed="yes")
#         items=Cart.objects.filter(completed="yes")
#         data=[]
#         serializer=None
#         for i in items:
#             print(i.item)
#             serializer= MostBoughtCategoryapi(i.item, many=True)
#             data.append(serializer.data)
#             print(serializer)
#         return Response(data, status=status.HTTP_200_OK)     


# class SearchAPIView(generics.ListCreateAPIView):
#     queryset= Product.objects.all()
#     serializer_class= productapi
#     filter_class = ProductSearchFilter
#     search_fields=['category', 'price', 'size', 'description' ]

    # filterset_backends=(DjangoFilterBackend)
class SearchApiview(FlatMultipleModelAPIView):
    def get_querylist(self):
        category=self.request.query_params.get("category", None)
        size=self.request.query_params.get("size", None)
        price=self.request.query_params.get("price", None)
        color=self.request.query_params.get("color", None)
        profile=self.request.query_params.get("profile", None)
        product=self.request.query_params.get("product", None)

        print(type(color))
        print(color)
        # print(price)
        # print(product)
        # print(profile)
        # print(category)
        # print(size)
        
        if (category==None or category=='') and (price==None or price=='') and (size==None or len(size)==0) and (color==None or color=='')and (profile==None or profile==''):
            return
        elif category and (price==None or price=='') and (size==None or size=='') and (color==None or color=='')and (profile==None or profile==''):
            return [{'queryset':Product.objects.filter(category=category), 'serializer_class':productapi}]
        
        elif (size) and (price==None or price=='') and (category==None or category=='') and (color==None or color=='')and (profile==None or profile==''):
            print("re")
            return [{'queryset':Product.objects.filter(size=int(size)), 'serializer_class':productapi}]
        
        elif price and (category==None or category=='') and (size==None or size=='') and (color==None or color=='')and (profile==None or profile==''):
            print(type(price))
            return [{'queryset':Product.objects.filter(price__lte=int(price)), 'serializer_class':productapi}   ]
        
        elif color and (price==None or price=='') and (size==None or size=='') and (category==None or category=='')and (profile==None or profile==''):
            return  [{'queryset':Product.objects.filter(color=color), 'serializer_class':productapi}]
        
        elif profile and (price==None or price=='') and (size==None or size=='') and (color==None or color=='')and (category==None or category==''):
            print("hy")
            return [{'queryset':Profile.objects.filter(user=int(profile)), 'serializer_class':profileapi}
    ]
        elif price and category and size==None and color==None and profile==None:
            return  [{'queryset':Product.objects.filter(category=category, price__range=(1, int(price))), 'serializer_class':productapi}]
        # elif category and price
        #     return Product.objects.filter(category=category)
        elif category and price and color  and size==None and profile==None:
            return [{'queryset':Product.objects.filter(category=category, color=color, price__range=(1, int(price))), 'serializer_class':productapi}]
       
        elif price and color and size and category==None and profile==None:
            print("lat")
            return [{'queryset':Product.objects.filter(color=color, size=int(size), price__range=(1, int(price))), 'serializer_class':productapi}]
        
        
# In a Django-like app:

# class CreateCheckOutSession(APIView):
#     def post(self, request, *args, **kwargs):
#         prod_id=self.kwargs["pk"]
#         try:
#             product=Product.objects.get(id=prod_id)
#             checkout_session = stripe.checkout.Session.create(
#                 line_items=[
#                     {
#                         # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
#                         'price_data': {
#                             'currency':'usd',
#                              'unit_amount':int(product.price) * 100,
#                              'product_data':{
#                                  'name':product.name,
#                                  'images':[f"{API_URL}/{product.product_image}"]

#                              }
#                         },
#                         'quantity': 1,
#                     },
#                 ],
#                 metadata={
#                     "product_id":product.id
#                 },
#                 mode='payment',
#                 success_url=settings.SITE_URL + '?success=true',
#                 cancel_url=settings.SITE_URL + '?canceled=true',
#             )
#             return redirect(checkout_session.url)
#         except Exception as e:
#             return Response({'msg':'something went wrong while creating stripe session','error':str(e)}, status=500)

# @csrf_exempt
# def stripe_webhook_view(request):
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     event = None

#     try:
#         event = stripe.Webhook.construct_event(
#         payload, sig_header, settings.STRIPE_SECRET_WEBHOOK
#         )
#     except ValueError as e:
#         # Invalid payload
#         return Response(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         # Invalid signature
#         return Response(status=400)

#     if event['type'] == 'checkout.session.completed':
#         session = event['data']['object']

#         print(session)
#         customer_email=session['customer_details']['email']
#         prod_id=session['metadata']['product_id']
#         product=Product.objects.get(id=prod_id)
#         #sending confimation mail
#         send_mail(
#             subject="payment sucessful",
#             message=f"thank for your purchase your order is ready.  download url {product.book_url}",
#             recipient_list=[customer_email],
#             from_email="henry2techgroup@gmail.com"
#         )

#         #creating payment history
#         # user=User.objects.get(email=customer_email) or None

#         PaymentHistory.objects.create(product=product, payment_status=True)
#     # Passed signature verification
#     return HttpResponse(status=200)

# class CartView(APIView):
#     parser_classes= [MultiPartParser, FormParser]

#     def post(self, request, pk, format=None):
#         print(request.data)
#         user = Cart.objects.filter(owners=pk)
#         # owner = Cart.objects.get(owners=pk)
#         print(user)
#         if user.exists():
#             request.data._mutable= True
#             user.item= request.data["item"]
#             request.data._mutable= False
#         else:
#             serializer= cartapi(data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



