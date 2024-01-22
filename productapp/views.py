import json
# import math
import datetime
from django.shortcuts import render, redirect
from .serializers import productapi,productCartApi, SearchResultsSerializer
from .models import Product, Cart
from profileapp.models import Profile
from profileapp.serializers import profileapi
from .permissions import SellersPermission
import requests
from django.db.models import Q
from django.contrib.auth.models import User

# import secrets
# import random
# import os
from django.views.decorators.csrf import csrf_exempt
import environ
from drf_multiple_model.views import FlatMultipleModelAPIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions, filters
# from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser 
from django.core.cache import cache


env= environ.Env()
environ.Env.read_env()
# Create your views here.
class CreatePost(APIView):
    parser_classes= [MultiPartParser, FormParser]
    permission_classes= [SellersPermission, permissions.IsAuthenticated]

    def post(self, request, format=None):
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
    permission_classes= [SellersPermission|permissions.IsAdminUser]

    # permission_classes= ([permissions.IsAdminUser | permissions.IsAuthenticated])
    def delete(self, request, pk):
        item= Product.objects.get(id=pk)
        error= json.dumps({"msg":"Sorry you do not have the necessary permissions"})
        if request.user.username == item.sellers.user.username or request.user.is_superuser==True:
            item.delete()
            return Response({"msg": "deleted"}, status=status.HTTP_200_OK)
        else:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

class ListAllProductsByCategory(generics.ListAPIView):
    serializer_class= productapi
    def  get_queryset(self):
        category= self.kwargs.get("pk")
        # cart=Cart.objects.filter(owners_id=4, completed="no")
        return Product.objects.filter(category=category)
    
class ListProductsDetails(APIView):

    def  get(self, request, pk):
        user= Product.objects.filter(id=pk)
        serializer= productapi(user,many=True, context={'request':request})
        if user.exists():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"product not found"}, status=status.HTTP_404_NOT_FOUND)


class ListProductsBSellers(APIView):

    def  get(self, request, username):
        prof=  User.objects.get(username=username)
        profuser=  Profile.objects.get(user=prof)
        user= Product.objects.filter(sellers=profuser)
        serializer= productapi(user, many=True, context={'request':request})
        length=(len(user))
        if length==0:
            return Response({"msg":"No products yet"}, status=status.HTTP_417_EXPECTATION_FAILED)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

class EditProducts(generics.RetrieveUpdateAPIView):
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
        obj= Product.objects.filter(user=pk)
        serializer= productapi(obj, many=True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class AddToCart(APIView):
    parser_classes= [MultiPartParser, FormParser]
    permission_classes= [permissions.IsAuthenticated]
    def post(self, request, format=None):
        if request.user.id:
            profile=Profile.objects.get(user=request.user.id)
            items= json.loads(request.data["item"])
            
            qty= request.data["item_qty"]
            cartSize= json.loads(request.data["cartSize"])
            totalAmount= json.loads(request.data["totalAmount"])            
            cart= Cart.objects.filter(owners=request.user.id, completed="no")
            if cart.exists():
                cart.delete()
            carts= Cart.objects.create(owners=profile, item_qty= qty, cartSize=cartSize, totalAmount=totalAmount)
            for i in items:
                itemz=Product.objects.get(id=i)
                carts.item.add(itemz)
            carts.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"msg": "Sorry, you dont have the necessary permissions for this"},status=status.HTTP_401_UNATHOURIZED)

RETRIEVE_CART="taks.retrievecart"
class RetrieveCart(APIView):
    permission_classes= [permissions.IsAuthenticated]
    def  get(self, request, **kwargs):
        tasks=cache.get(RETRIEVE_CART)
        if not tasks:
            cart=Cart.objects.filter(owners_id=request.user.id, completed="no")
            if cart.exists():
                for i in cart:
                    cartProduct= i.item.all()
                    item= productCartApi(cartProduct, many=True, context={'request':request})
                #     preserint("i.item_qty")
                datas={"serializer":item.data, "id":i.id, "cartSize":i.cartSize, "item_qty":i.item_qty, "totalAmount":i.totalAmount}
                cache.set(RETRIEVE_CART, datas)
                return Response(datas, status=status.HTTP_200_OK)
            else:
                return Response({"msg":"cart not found"}, status=status.HTTP_201_CREATED)
            
        return Response(tasks, status=status.HTTP_200_OK)

class PlaceOrder(APIView):
    permission_classes= [SellersPermission,  permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):       
        hed2 = {'Authorization': 'Bearer sk_test_339102877aede0b62c4c8baa085b424e84dcb0ce'}      
        cartId=request.data["cartId"]
        if cartId==None or cartId=="null":
            profile=Profile.objects.get(user=request.user.id)
            items= json.loads(request.data["item"])
            qty= request.data["item_qty"]
            cartSize= json.loads(request.data["cartSize"])
            carts= Cart.objects.create(owners=profile, item_qty= qty, cartSize=cartSize)
            for i in items:
                itemz=Product.objects.get(id=i)
                carts.item.add(itemz)
            carts.save()
            metadata= json.dumps({"cart_id":carts.id})
            datum={    
                "email":"emmanuelcopeters@gmail.com",
                "amount":6000,
                'callback_url': f"http://localhost:3000/confirmandupdateorder/{carts.id}/",
                "metadata":metadata
                }
            url = 'https://api.paystack.co/transaction/initialize' 
            response = requests.post(url, data=datum, headers=hed2)
            responses=response.json()
            # link=response['data']['link']
            if responses["status"]==True:
                return Response({"link":responses["data"]["authorization_url"], "code":200}, status=status.HTTP_200_OK)
            else:
                return Response({"message":response["message"], "code":400}, status=status.HTTP_200_BAD_REQUEST)
        else:
        # cartId=59
            cartId=request.data["cartId"]
            metadata= json.dumps({"cart_id":cartId})
            datum={    
                "email":"emmanuelcopeters@gmail.com",
                "amount":6000,
                'callback_url': f"http://localhost:3000/confirmandupdateorder/{cartId}/",
                "metadata":metadata
                }
            url = 'https://api.paystack.co/transaction/initialize'        
            response = requests.post(url, data=datum, headers=hed2)
            responses=response.json()
            # link=response['data']['link']
            if responses["status"]==True:
                return Response({"link":responses["data"]["authorization_url"], "code":200}, status=status.HTTP_200_OK)
            else:
                return Response({"message":response["message"], "code":400}, status=status.HTTP_200_BAD_REQUEST)
       

class ConfirmAndUpdateOrder(APIView):
   def post(self, request):
        # cart=request.session['cart_id']
        reference=None
        auth_token = env("PAYSTACK_AUTH_TOKEN")
        hed = {'Authorization': 'Bearer' + auth_token}
       
        try:
            reference=request.data['reference']
            cart_id=request.data['cart_id']
            url = f"https://api.paystack.co/transaction/verify/{reference}"        
            response = requests.get(url, headers=hed)
            responses=response.json()
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
    permission_classes= [permissions.IsAdminUser]
    def get(self, request):
        today= datetime.datetime.today()
        previous_month = today.month-1
    
        previous_two_month = today.month-2
        # previous_two_month_date= datetime.datetime(today.year, previous_two_month, today.day)
        
        queryset= Cart.objects.filter(completed="yes", date_created__month= today.month)
        # serialized= UserApi(queryset1, many=True)
        current=len(queryset)
        queryset1= Cart.objects.filter(completed="yes", date_created__month=previous_month)
        previous=len(queryset1)

        querysets2= Cart.objects.filter(completed="yes", date_created__month= previous_two_month)
        previous_two_month=len(querysets2)
        
        data=[current, previous, previous_two_month]
       
        return Response(data, status=status.HTTP_200_OK)

class MostBoughtCategory(APIView):
    permission_classes= [permissions.IsAdminUser]

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
        for products_value, products_label in products:
            arr.append(products_label)
        return Response(arr, status=status.HTTP_200_OK)
        

# lass MostBoughtCategory(APIView):
#     def  get(self, request):
#         # profile=self.request.user.id
#         # cart=Cart.objects.filter(completed="yes")
#         items=Cart.objects.filter(completed="yes")
#         data=[]
#         serializer=None
#         for i in items:
#             #             serializer= MostBoughtCategoryapi(i.item, many=True)
#             data.append(serializer.data)
#             #         return Response(data, status=status.HTTP_200_OK)     


# class SearchAPIView(generics.ListCreateAPIView):
#     queryset= Product.objects.all()
#     serializer_class= productapi
#     filter_class = ProductSearchFilter
#     search_fields=['category', 'price', 'size', 'description' ]
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Product, Profile
# from .serializers import SearchResultsSerializer

# views.py

class SearchResultsView(APIView):
    serializer_class = SearchResultsSerializer

    def get(self, request, *args, **kwargs):
        query = self.request.query_params.get('query', '')
        size = self.request.query_params.get('size', '')
        color = self.request.query_params.get('color', '')
        price = self.request.query_params.get('price', '')

        # Perform separate queries for Product and Profile
        product_results = Product.objects.filter(Q(description__icontains=query )| Q(category__icontains=query ))
        profile_results = Profile.objects.filter(
            Q(user__username__icontains=query) |
            Q(location__icontains=query)
        )

        # Add optional filters for Product
        if size:
            product_results = product_results.filter(size=size)
        if color:
            product_results = product_results.filter(color=color)
        if price:
            product_results = product_results.filter(price=price)

        # Serialize the combined results
        serializer = SearchResultsSerializer({
            'products': product_results,
            'profiles': profile_results
        })

        return Response(serializer.data, status=status.HTTP_200_OK)
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

#         #         customer_email=session['customer_details']['email']
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
#         #         user = Cart.objects.filter(owners=pk)
#         # owner = Cart.objects.get(owners=pk)
#         #         if user.exists():
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



