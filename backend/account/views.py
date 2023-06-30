from django.shortcuts import render
from .serializers import *
from .models import *
from rest_framework import permissions, views, viewsets, generics, response
from rest_framework_simplejwt.tokens import RefreshToken
from telebot import TeleBot
from admins.utils import get_random_string
from hashlib import sha256
import hmac
# Create your views here.



# profile view
class UserProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user = request.user

        serializer = UserProfileSerializer(user, context={'request': request})

        return response.Response(serializer.data)


# create business account
class CreateBusinessAccount(generics.CreateAPIView):
    queryset = BusinessProfile.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinesProfileCreateSerializer


# sing in or sing up
class LoginOrSingUp(views.APIView):
    def post(self, request, format=None):
        user_data = request.data.get("user_data", {})

        if type(user_data) is not dict:
            return response.Response({'message': "user_data should be dict"})

        data_check_list = []
        tg_hash = user_data.pop("hash")
        for key, val in user_data.items():
            data_check_list.append(f"{key}={val}")

        
        data_check_list = sorted(data_check_list)
        data_check_string = '\n'.join(data_check_list)


        secret_key = sha256(settings.SOCIAL_AUTH_TELEGRAM_BOT_TOKEN, usedforsecurity=True).digest()
        hash = hmac.new(secret_key, data_check_string.encode(), sha256)

        if hash.hexdigest() != tg_hash:
            return response.Response({'message': "This data is not from  Telegram"})


        user_data['chat_id'] = user_data.get("id")
        user_data['username'] = user_data.get('user_name', user_data.get("first_name", ""))
        # user_data['avatar'] = request.data.get("photo_url")


        user_fields = ['username', "first_name", "last_name", "chat_id"]
        auth_data = user_data.copy()

        for key in auth_data.keys():
            if key not in user_fields:
                del user_data[key]

        

        try:
            user = CustomUser.objects.get(chat_id=user_data.get("chat_id"))
            # if user_data.get("avatar") is None and user.avatar is not None:
            #     del user_data['avatar']
        except:
            user = None


        try:
            if user:
                for attr, value in user_data.items():
                    setattr(user, attr, value)
            else:
                user = CustomUser(**user_data)
                user.set_password(get_random_string(30))                

            user.full_clean()
            user.save()

        except ValidationError as e:
            return response.Response(e.message_dict)

        refresh = RefreshToken.for_user(user)

        return response.Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
