import json
import requests
import datetime
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from django.core.cache import cache
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
    UserRegistrationSerializer,
    FollowersApi,
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
        #         # ...

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    # parser_classes= [MultiPartParser, FormParser]


# class GetProfileDetails(generics.RetrieveAPIView):
#     permission_classes= [permissions.IsAuthenticated]
#     # queryset= Profile.objects.all()
#     serializer_class= profileapi

#     def  get_queryset(self):
#         user= self.request.user.id
#         return Profile.objects.filter(user=user)
        

class UserProfileDetails(APIView):
    def  get(self, request, username):
        # user= self.request.user.id
        try:
            prof= User.objects.get(username=username)
            user= Profile.objects.filter(user=prof) 
            serializer= profileapi(user, many=True, context={'request':request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"msg":"Profile does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class prof_pics_update(generics.UpdateAPIView):
    permission_classes= [permissions.IsAuthenticated ]
    serializer_class= profileapi
    queryset= Profile.objects.all()

class profileUpdate(generics.UpdateAPIView):
    permission_classes= [permissions.IsAuthenticated]
    serializer_class= profileapi
    queryset= Profile.objects.all()

class UserProfileDelete(APIView):
    permission_classes=[permissions.IsAdminUser | permissions.IsAuthenticated]
    def  delete(self, request, pk):
        # user= self.request.user.id
        admin=User.objects.get(id=request.user.id)
        if request.user.id==pk or admin.is_superuser:
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
        # 
        if sellersgroup.exists()== False:
            groups.user_set.add(user)
            profile.blocked=True
            profile.save(update_fields=["blocked"])

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
        # 
        if sellersgroup.exists()== True:
            groups.user_set.remove(user)
            profile.blocked=False
            profile.save(update_fields=["blocked"])
                    # user= self.request.user.id
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"msg":"User not blocked"}, status=status.HTTP_400_BAD_REQUEST)

class UnblockSeller(APIView):
    def post(self, request, username):
                return Response(status=status.HTTP_200_OK)

     
class BlockUser(APIView):
    permission_classes=[permissions.IsAdminUser]
    def  post(self, request, pk):
        user= User.objects.get(id = pk)
        profile= Profile.objects.get(id = pk)
        sellersgroup= User.objects.filter(id = pk, groups__name= "bannedUsers")
        groups= Group.objects.get(name = "bannedUsers")
        # 
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
        if user.tags == "seller":
            return Response("already a seller", status=status.HTTP_226_IM_USED)
        else:
            serializer= profileapi(user,data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                user.tags="seller"
                user.save(update_fields=["tags"]) 
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




ALL_FOLLOWERS_CACHE="tasks.followers"
class AllFollowers(APIView):
    def  get(self, request, username):
        # tasks=cache.get(ALL_FOLLOWERS_CACHE)
        tasks=False
        if not tasks:
            arr= []
            prof = User.objects.get(username=username )
            user= Profile.objects.get(user=prof)
            for i in user.followers.all():
                follower= Profile.objects.get(user=i)
                serializer= FollowersApi(follower, context={'request':request})
                arr.append(serializer.data)
            cache.set(ALL_FOLLOWERS_CACHE, arr)
            length=len(arr)
            if length<1:
                return Response({"msg":"No followers yet"},status=status.HTTP_417_EXPECTATION_FAILED)
            else:
                return Response(arr, status=status.HTTP_200_OK)
        length=len(tasks)
        if length<1:
            return Response({"msg":"No followers yet"},status=status.HTTP_417_EXPECTATION_FAILED)
        else:
            return Response(tasks, status=status.HTTP_200_OK)

ALL_FOLLOWING="tasks.following"
class AllFollowing(APIView):
    def  get(self, request, username):
        tasks=cache.get(ALL_FOLLOWING)
        arr= []
        if not tasks:
            prof = User.objects.get(username=username )
            user= Profile.objects.get(user=prof)
            for i in user.following.all():
                following= Profile.objects.get(user=i)
                serializer= FollowersApi(following, context={'request':request})
                arr.append(serializer.data)
            cache.set(ALL_FOLLOWING, arr)
            if len(arr)<1:
                return Response({"msg":"Following no one yet"},status=status.HTTP_417_EXPECTATION_FAILED)
            else:
                return Response(arr, status=status.HTTP_200_OK)
        if len(tasks)<1:
            return Response({"msg":"Following no one yet"},status=status.HTTP_417_EXPECTATION_FAILED)
        else:
            return Response(tasks, status=status.HTTP_200_OK)


class Follow(APIView):
    permission_classes= [permissions.IsAuthenticated]
    def post(self, request, username, format=None):
            sender = request.user.id
            user= User.objects.get(username=username)
            receiver =user.id
            receiver_followers= Profile.objects.filter(user=user)
            followers=receiver_followers.values_list("followers")
            follow=len(followers)
            #             # profiles = friend.friends.get(id=id)
            data={"sender":sender, "receiver":receiver, "status":"accept", "followers":follow}
            serializer= RelationshipApi(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Unfollow(APIView):
    permission_classes= [permissions.IsAuthenticated]
    def post(self, request, username, format=None):
            sender = request.user.id
            user= User.objects.get(username=username)
            receiver =user.id
            receiver_followers= Profile.objects.filter(user=user)
            followers=receiver_followers.values_list("followers")
            follow=len(followers)
            #             # print(receiver.followers.all())
            data={"sender":sender, "receiver":receiver, "status":"delete", "followers":follow}
            serializer= RelationshipApi(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AllProfiles(generics.ListAPIView):
    queryset= Profile.objects.all()
    serializer_class= profileapi
    
class all_sellers_profile(generics.ListAPIView):
    serializer_class= profileapi
    def  get_queryset(self):
        return Profile.objects.filter(tags="seller")
    

class RequestPasswordResetEmail(generics.GenericAPIView):
    parser_classes= [MultiPartParser, FormParser]
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request, format=None):
        # serializer = self.serializer_class(data=request.data)
        email = request.data["email"]
        username= request.user.username
        if User.objects.filter(email=email).exists():
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
                        # return reverse("password-change", args=(datum))

        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'token is not valid, please request a new one'})
                    
           
# def passwordChange(request):
#     # #     # form=PasswordChangeForm()
#     if request.method == "POST":
#         password = request.POST.get("password")
#         encrypted_token= request.session["encrypted_token"]
#         encrypted_uidb64=request.session["encrypted_uidb64"]
#         data={"password":str(password), "token":str(encrypted_token), "uidb64":encrypted_uidb64}

#         #         #         #         #     # context={'form':form}
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
    def get(self, request, username, format=None):
        user=User.objects.get(username=username)
        obj= Review.objects.filter(value__lte=3,receiver_id=user.id)
        serializer= ReviewApi(obj, many=True)
        length= len(serializer.data)
        if length==0:
            return Response({"msg":"No reviews"},status=status.HTTP_417_EXPECTATION_FAILED)
        else:
            return Response( serializer.data,status=status.HTTP_200_OK)

class Positive(APIView):
    def get(self, request, username, format=None):
        user=User.objects.get(username=username)
        obj= Review.objects.filter(value__gte=4,receiver=user.id)
        serializer= ReviewApi(obj, many=True)
        length= len(serializer.data)
        if length==0:
            return Response({"msg":"No reviews"},status=status.HTTP_417_EXPECTATION_FAILED)
        else:
            return Response( serializer.data,status=status.HTTP_200_OK)

class CreateReview(APIView):
    parser_classes= [MultiPartParser, FormParser]
    permission_classes= [permissions.IsAuthenticated]

    def post(self, request, format=None):
        receiver= User.objects.get(username=request.data["receiver"])
        data={
            "value":request.data["value"],
            "text":request.data["text"],
            "sender":request.data["sender"],
            "receiver":receiver.id
        }
        serializer= ReviewApi(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class AllReviews(APIView):
#     def  get(self, request, pk):
#         #         user= Review.objects.filter(receiver=pk)
#         # sender= user.objects.only("sender")
#         error= {"msg":"error"}
#         jsonerror= json.dumps(error)
#         if user.exists():
#             #             #             serializer= ReviewApi(user, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(jsonerror, status=status.HTTP_200_OK)

#             # return Resonse({"msg":"error"}, status=status.HTTP_400_BAD_REQUEST)

class PostNotifications(APIView):
    parser_classes= [MultiPartParser, FormParser]
    permission_classes= [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer= NotificationApi(data=request.data)
        # print(request.data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# check this code dont forget
class EditNotification(APIView):
    permission_classes= [permissions.IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        notification=None
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
        Followquery= Notifications.objects.filter(receiver=request.user.id).order_by('-id')[:10]
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
        prof=Profile.objects.get(user=pk)
        prof.notification.clear()
        return Response({"msg":"succes"}, status=status.HTTP_200_OK) 

ALL_PRODUCT_NOTIF="tasks.productnotif"
class ProductGetNotifications(APIView):
    permission_classes= [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs): 
        tasks=cache.get(ALL_FOLLOWERS_CACHE)
        if not tasks:
            arr=[] 
            productNotif= productNotifications.objects.all() 
            for i in productNotif:
                if str(request.user.id) in i.receiver:
                    container={"id":i.id,"text":i.text, "time":i.time, "seen":i.seen}
                    arr.append(container)
            cache.set(ALL_FOLLOWERS_CACHE, arr)
            return Response(arr, status=status.HTTP_200_OK) 
        
        return Response(tasks, status=status.HTTP_200_OK) 

class MonthlyUsers(APIView):
    # serializer_class = UserApi
    permission_classes= [permissions.IsAdminUser]

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

class YourOrders(APIView):
    permission_classes= [permissions.IsAuthenticated]
    # serializer_class= SimpleCartapi
    def  get(self, request, **kwargs):
        profile=self.request.user.id
        cart=Cart.objects.filter(owners=profile, completed="yes")
        arr=[]
        if cart.exists():
            for i in cart:
                cartProduct= i.item.all()
                item= productCartApi(cartProduct, many=True, context={'request':request})
                datas={"serializer":item.data,  "item_qty":i.item_qty}
                arr.append(datas)
                        # pass
            return Response(arr, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"No purchased product found"}, status=status.HTTP_417_EXPECTATION_FAILED)

TOTAL_USERS="tasks.users"
class TotalUsers(APIView):
    def get(self, request):
        tasks= cache.get(TOTAL_USERS)
        user_counts={}
        if not tasks:
            total=Profile.objects.all()
            goods=Product.objects.all().count()
            for i in total:
                user_counts[i.tags] = user_counts.get(i.tags, 0) + 1
            user_counts.update({"goods":goods})
            cache.set(TOTAL_USERS, user_counts)
            return Response(user_counts, status=status.HTTP_200_OK)
        return Response(tasks, status=status.HTTP_200_OK)

