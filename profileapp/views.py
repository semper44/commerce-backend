import json
import requests
import datetime
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
import os
# import pytz
from django.shortcuts import redirect, render
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser 
from django.db.models import Q
from django.contrib.auth.models import User, Group
from productapp.serializers import SimpleCartapi
from productapp.models import Cart, Product
from .models import Profile, Review, Relationship, Notifications
from productapp.serializers import productCartApi
from .serializers import (
    profileapi, 
    RelationshipApi, 
    ReviewApi, 
    NotificationApi,
    ProductNotificationApi,
    productNotifications,
    UserApi,
    SetNewPasswordSerializer, ResetPasswordEmailRequestSerializer)

# Create your views here.


# class CustomRedirect(HttpResponsePermanentRedirect):

#     allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        # print(user)
        # ...

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# class GetProfileDetails(generics.RetrieveAPIView):
#     permission_classes= [permissions.IsAuthenticated]
#     # queryset= Profile.objects.all()
#     serializer_class= profileapi

#     def  get_queryset(self):
#         user= self.request.user.id
#         return Profile.objects.filter(user=user)
        

class UserProfileDetails(APIView):
    # permission_classes=([permissions.IsAuthenticated | permissions.IsAdminUser])
    def  get(self, request, pk):
        # user= self.request.user.id
        print(pk)
        user= Profile.objects.filter(user=pk) 
        if user.exists():
            serializer= profileapi(user, many=True, context={'request':request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"error"}, status=status.HTTP_400_BAD_REQUEST)


class prof_pics_update(generics.UpdateAPIView):
    permission_classes= [permissions.IsAuthenticated & permissions.DjangoModelPermissions]
    serializer_class= profileapi
    queryset= Profile.objects.all()

class profileUpdate(generics.UpdateAPIView):
    permission_classes= [permissions.IsAuthenticated & permissions.DjangoModelPermissions]
    serializer_class= profileapi
    queryset= Profile.objects.all()

class UserProfileDelete(APIView):
    permission_classes=[permissions.IsAdminUser]
    def  delete(self, request, pk):
        # user= self.request.user.id
        print(pk)
        user= User.objects.filter(id=pk) 
        if user.exists():
            user.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"msg":"error"}, status=status.HTTP_400_BAD_REQUEST)

class BlockSeller(APIView):
    permission_classes=[permissions.IsAdminUser]
    def  post(self, request, pk):
        user= User.objects.get(id = pk)
        profile= Profile.objects.get(id = pk)
        sellersgroup= User.objects.filter(id = pk, groups__name= "bannedSellers")
        groups= Group.objects.get(name = "bannedSellers")
        # print(groups.users)

        if sellersgroup.exists()== False:
            groups.user_set.add(user)
            profile.blocked=True
            profile.save(update_fields=["blocked"])

            print("success")
        # user= self.request.user.id
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"msg":"User already blocked"}, status=status.HTTP_400_BAD_REQUEST)

class UnblockUser(APIView):
    def  post(self, request, pk):
        user= User.objects.get(id = pk)
        profile= Profile.objects.get(id = pk)
        sellersgroup= User.objects.filter(id = pk, groups__name= "bannedSellers")
        groups= Group.objects.get(name = "bannedSellers")
        # print(groups.users)

        if sellersgroup.exists()== True:
            groups.user_set.remove(user)
            profile.blocked=False
            profile.save(update_fields=["blocked"])
            print("success")
        # user= self.request.user.id
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"msg":"User not blocked"}, status=status.HTTP_400_BAD_REQUEST)

class UnblockSeller(APIView):
    def post(self, request, pk):
        print("unblockseller")
        return Response(status=status.HTTP_200_OK)

     
class BlockUser(APIView):
    # permission_classes=[permissions.IsAdminUser]
    def  post(self, request, pk):
        user= User.objects.get(id = pk)
        profile= Profile.objects.get(id = pk)
        sellersgroup= User.objects.filter(id = pk, groups__name= "bannedUsers")
        groups= Group.objects.get(name = "bannedUsers")
        # print(groups.users)

        if sellersgroup.exists()== False:
            groups.user_set.add(user)
            profile.blocked=True
            profile.save(update_fields=["blocked"])
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"msg":"error"}, status=status.HTTP_400_BAD_REQUEST)

class SellersProfileForm(generics.UpdateAPIView):
    permission_classes= [permissions.IsAuthenticated]
    def  patch(self, request, pk):
        user= Profile.objects.get(user=pk) 
        body=request.data
        accountNumber="0" +body["accountNumber"]
        bankAccount= "0"+body["bankAccount"]
        auth_token= "FLWSECK_TEST-3e7e9f013b9203d9aa80a4374c27a4eb-X"
        hed = {'Authorization': 'Bearer ' + auth_token}
        data = {
                "account_bank":bankAccount,
                "account_number":accountNumber,
                "business_name":body["businessName"],
                "business_mobile":body["phoneNumber"],
                "business_email":body["email"],
                "country":"NG",
                "split_type":"percentage",
                "split_value":0.5
                }
        url = ' https://api.flutterwave.com/v3/subaccounts'
        updateUrl = f"https://api.flutterwave.com/v3/subaccounts/{user.flutterWaveId}"
        # print(data)
        if user.flutterWaveId:
            response = requests.put(updateUrl, json=data, headers=hed)
            responses=response.json()
            # print(responses)
            serializer= profileapi(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        else:
            response = requests.post(url, json=data, headers=hed)
            responses=response.json()
            # print(responses)
            # response_data= response[]
            responseData=responses["data"]["id"]
            datas=request.data
            datas._mutable=True
            datas["flutterWaveId"]=responseData
            datas._mutable = False
            serializer= profileapi(user,data=datas, partial=True)
            if serializer.is_valid() and response.status_code==200:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

class createPaystackSubAccount(generics.CreateAPIView):

    # permission_classes= [permissions.IsAuthenticated]
    def  post(self, request, pk):
        body=request.data
        auth_token= "sk_test_a406879db48e521a8d467dd1f47c5fc4735bf263"
        hed = {'Authorization': 'Bearer ' + auth_token}
        updateUrl = "https://api.paystack.co/subaccount"
        response = requests.get(updateUrl, headers=hed)
        responses=response.json()
        # print(responses)
        return Response(responses["message"], status=status.HTTP_400_BAD_REQUEST)

class checkFlutterWave(generics.UpdateAPIView):
    # serializer_class= profileapi
    # queryset= Profile.objects.all()
    permission_classes= [permissions.IsAuthenticated]
    def  post(self, request, pk):
        body=request.data
        user=Profile.objects.get(user=pk)
        # print(user)
        # print(user.flutterWaveId)
        account_id=  "RS_6C99E13FAB81CF52D52AD40601CDE3DA"
        auth_token= "FLWSECK_TEST-3e7e9f013b9203d9aa80a4374c27a4eb-X"
        hed = {'Authorization': 'Bearer ' + auth_token}
        updateUrl = f"https://api.flutterwave.com/v3/subaccounts/{user.flutterWaveId}"

        updateUrl = "https://api.paystack.co/subaccount"
        response = requests.get(updateUrl, headers=hed)
        # print(response.status_code)
        # print(response)
        responses=response.json()
        # print(responses)
        return Response(responses["message"], status=status.HTTP_400_BAD_REQUEST)

class AllFollowers(APIView):
    def  get(self, request, pk):
        arr= []
        user= Profile.objects.get(user=pk)
        for i in user.followers.all():
            follower= Profile.objects.get(user=i)
            serializer= profileapi(follower)
            arr.append(serializer.data)
        return Response(arr, status=status.HTTP_200_OK)

class AllFollowing(APIView):
    def  get(self, request, pk):
        arr= []
        user= Profile.objects.get(user=pk)
        for i in user.following.all():
            following= Profile.objects.get(user=i)
            print(following)
            serializer= profileapi(following)
            arr.append(serializer.data)
        return Response(arr, status=status.HTTP_200_OK)

class Follow(APIView):
    permission_classes= [permissions.IsAuthenticated]
    def post(self, request, pk, format=None):
            sender = request.user.id
            receiver =pk
            receiver_followers= Profile.objects.filter(user=pk)
            followers=receiver_followers.values_list("followers")
            follow=len(followers)
            # print(follow)
            # profiles = friend.friends.get(id=id)
            data={"sender":sender, "receiver":receiver, "status":"accept", "followers":follow}
            serializer= RelationshipApi(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Unfollow(APIView):
    permission_classes= [permissions.IsAuthenticated]
    def post(self, request, pk, format=None):
            sender = request.user.id
            receiver =pk
            receiver_followers= Profile.objects.filter(user=pk)
            followers=receiver_followers.values_list("followers")
            follow=len(followers)
            # print(follow)
            # print(receiver.followers.all())
            data={"sender":sender, "receiver":receiver, "status":"delete", "followers":follow}
            serializer= RelationshipApi(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AllProfiles(generics.ListAPIView):
    # permission_classes= [permissions.IsAdminUser]
    queryset= Profile.objects.all()
    serializer_class= profileapi
    
class all_sellers_profile(generics.ListAPIView):
    permission_classes= [permissions.IsAdminUser]
    serializer_class= profileapi

    def  get_queryset(self):
        return Profile.objects.filter(tags="seller")
    

class RequestPasswordResetEmail(generics.GenericAPIView):
    parser_classes= [MultiPartParser, FormParser]
    # permission_classes= [permissions.IsAuthenticated]
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request, format=None):
        # serializer = self.serializer_class(data=request.data)
        email = request.data["email"]
        # print(request.data)
        username= request.user.username
        if User.objects.filter(Q(email=email) & Q(username=username)).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            # current_site = get_current_site(
            #     request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            redirect_url = request.data.get('redirect_url', '')
            url=" http://localhost:3000"

            absurl = 'http://'+url+ relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                absurl
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    # serializer_class = SetNewPasswordSerializer

    def get(self,request, uidb64, token):

        # redirect_url = request.GET.get('redirect_url')
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not validd, please request a new one'})
            # return Response({'success': True, 'message': 'Credentials Valid', 'uidb64':uidb64, 'token': token})
            datum={'uidb64':uidb64, 'token': token}
            print(token)
            # return reverse("password-change", args=(datum))

        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'token is not valid, please request a new one'})
                    
           
# def passwordChange(request):
#     # print(request.body)
#     # form=PasswordChangeForm()
#     if request.method == "POST":
#         password = request.POST.get("password")
#         encrypted_token= request.session["encrypted_token"]
#         encrypted_uidb64=request.session["encrypted_uidb64"]
#         data={"password":str(password), "token":str(encrypted_token), "uidb64":encrypted_uidb64}

#         print(data)
#         print(encrypted_token)
#         print(encrypted_uidb64)
#         print(password)
#     # context={'form':form}
#         url=" http://localhost:3000"
#         # url="http://127.0.0.1:8000/profile/password-reset-complete/"
#         req= requests.patch(url, data=data)
#         result= req.json()
#         if result["success"]==True:
#             return redirect()
#         # return redirect(url
#         else:
#             return render(request, "password.html",{})


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        token=request.data['token']
        uid=request.data['uid']
        password=request.data['password']
        data={"password":password, "token":token, "uidb64":uid}
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


# class Just_sellers(APIView):
#     def get(self, request, pk, format=None):
#         serializer= profileapi(pk)
            
#         return Response(serializer.data, status=status.HTTP_200_OK)
           



# class Reviews(generics.RetrieveUpdateAPIView):
#     serializer_class= ReviewApi
#     queryset= Review.objects.all()

class Critical(APIView):
    def get(self, request, pk, format=None):
        obj= Review.objects.filter(value__lte=3,receiver_id=pk)
        # print(obj.Profile.user)
        serializer= ReviewApi(obj, many=True)
        # print(obj)
        return Response( serializer.data,status=status.HTTP_200_OK)

class Positive(APIView):
    def get(self, request, pk, format=None):
        # print(request)
        obj= Review.objects.filter(value__gte=4,receiver=pk)
        serializer= ReviewApi(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateReview(APIView):
    parser_classes= [MultiPartParser, FormParser]
    permission_classes= [permissions.IsAuthenticated]

    def post(self, request, format=None):
        # permission_classes= [permissions.IsAuthenticated]
        serializer= ReviewApi(data=request.data)
        # print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class AllReviews(APIView):
#     def  get(self, request, pk):
#         print(pk)
#         user= Review.objects.filter(receiver=pk)
#         # sender= user.objects.only("sender")
#         error= {"msg":"error"}
#         jsonerror= json.dumps(error)
#         if user.exists():
#             print("review")
#             print(user)
#             serializer= ReviewApi(user, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(jsonerror, status=status.HTTP_200_OK)

#             # return Response({"msg":"error"}, status=status.HTTP_400_BAD_REQUEST)

class PostNotifications(APIView):
    parser_classes= [MultiPartParser, FormParser]
    permission_classes= [permissions.IsAuthenticated]

    def post(self, request, format=None):
        # permission_classes= [permissions.IsAuthenticated]
        serializer= NotificationApi(data=request.data)
        # print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# check this code dont forget
class EditNotification(APIView):
    permission_classes= [permissions.IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        notification=0
        # print(request.data)
        for i in request.data:
            if i['seen'] =="unseen":
                notification= Notifications.objects.get(id=i['id'])
                notification.seen="seen"
                notification.save(update_fields=["seen"])  
        serializer= NotificationApi(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetNotifications(APIView):
    permission_classes= [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        Followquery= Notifications.objects.filter(receiver=request.user.id).order_by("-time")[:10]
        serializer=NotificationApi(Followquery, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostProductNotifications(APIView):
    parser_classes= [MultiPartParser, FormParser]
    permission_classes= [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer= ProductNotificationApi(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductEditNotification(APIView):
    permission_classes= [permissions.IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs): 
        follower= pk
        prof=Profile.objects.get(user=pk)
        prof.notification.clear()
        return Response({"msg":"succes"}, status=status.HTTP_200_OK) 

class ProductGetNotifications(APIView):
    permission_classes= [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs): 
        arr=[] 
        productNotif= productNotifications.objects.all() 
        for i in productNotif:
            if str(request.user.id) in i.receiver:
                container={"id":i.id,"text":i.text, "time":i.time, "seen":i.seen}
                arr.append(container)
        # print(arr)
        return Response(arr, status=status.HTTP_200_OK) 

class MonthlyUsers(APIView):
    # serializer_class = UserApi
    # permission_classes= [permissions.IsAdminUser]

    def get(self, request):
        today= datetime.datetime.today()
        previous_month = today.month-1
        previous_two_month = today.month-2
        queryset= User.objects.filter(date_joined__month=today.month)
        serializers= UserApi(queryset, many=True)
        current=len(serializers.data)

        querysets= User.objects.filter(date_joined__month= previous_month)
        serializer= UserApi(querysets, many=True)
        previous=len(serializer.data)
        queryset1= User.objects.filter(date_joined__month= previous_two_month)
        serialized= UserApi(queryset1, many=True)
        previous_two_month=len(serialized.data)
        # queryset1= User.objects.filter(date_joined__month__range=[today.month, 1])
        data=[current, previous, previous_two_month]
       
        return Response(data, status=status.HTTP_200_OK)

class OrdersAUserMade(APIView):
    # permission_classes= [permissions.IsAuthenticated]
    # serializer_class= SimpleCartapi
    def  get(self, request, **kwargs):
        # profile=self.request.user.id
        cart=Cart.objects.filter(owners=4, completed="yes")
        arr=[]
        if cart.exists():
            for i in cart:
                cartProduct= i.item.all()
                # print(i.item_qty)
                item= productCartApi(cartProduct, many=True, context={'request':request})
                datas={"serializer":item.data,  "item_qty":i.item_qty}
                arr.append(datas)
            print(datas)
            # pass
            return Response(arr, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"No purchased product found"}, status=status.HTTP_400_BAD_REQUEST)

class TotalUsers(APIView):
    def get(self, request):
        total=Profile.objects.all()
        goods=Product.objects.all().count()
        print("goods")
        print(goods)
        user_counts={}
        for i in total:
            print(i)
            user_counts[i.tags] = user_counts.get(i.tags, 0) + 1
        user_counts.update({"goods":goods})
        return Response(user_counts, status=status.HTTP_200_OK)

