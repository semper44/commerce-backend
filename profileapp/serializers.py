from .models import Profile, Relationship,Review,Notifications,productNotifications, User
from rest_framework import serializers
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError



from django.contrib.auth.models import User
from rest_framework import serializers

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user
    # def to_representation(self, instance):
    #     representation= super().to_representation(instance)
    #     return{'user':representation}


class profileapi(serializers.ModelSerializer):
    class Meta:
        model= Profile
        fields= "__all__"

class FollowersApi(serializers.ModelSerializer):
    class Meta:
        model= Profile
        fields=("pics", "location", "businessName", "name")



class RelationshipApi(serializers.ModelSerializer):
    class Meta:
        model= Relationship
        fields= "__all__"

class ReviewApi(serializers.ModelSerializer):
    class Meta:
        model= Review
        fields= "__all__"

class NotificationApi(serializers.ModelSerializer):
    class Meta:
        model= Notifications
        fields= "__all__"

class ProductNotificationApi(serializers.ModelSerializer):
    class Meta:
        model= productNotifications
        fields= "__all__"

class UserApi(serializers.ModelSerializer):
    class Meta:
        model= User
        fields= "__all__"


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)
