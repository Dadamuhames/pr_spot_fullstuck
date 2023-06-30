from rest_framework import serializers
from .models import *
from main.base_serializers import *
import main.serializers

# business account serialier
class BusinessUserViewSerializer(serializers.ModelSerializer):
    business_avatar = ThumbnailSerializer(alias='900x900')

    class Meta:
        model = BusinessProfile
        exclude = ['user']


# user view serializer
class UserViewSerializer(serializers.ModelSerializer):
    avatar = ThumbnailSerializer(alias='900x900')

    class Meta:
        model = CustomUser
        exclude = ['last_login', "is_staff", "is_superuser",
                   "is_active", "user_permissions", "groups", "date_joined", "email", "password", "tg_token", "chat_id"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['full_name'] = instance.full_name()

        if instance.get_business_profile():
            data['business_profile'] = BusinessUserViewSerializer(
                instance.business_profile, context=self.context).data

        return data


# user profile serializer
class UserProfileSerializer(UserViewSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        offers = instance.offers.filter(active=True)
        orders = instance.orders.filter(active=True)
        accepted_orders = instance.accepted_orders.filter(active=True)


        offers_list = paginate_related(offers, request)
        data['offers'] = main.serializers.OfferViewSerialzier(offers_list, many=True, context=self.context).data


        orders_list = paginate_related(orders, request)
        data['orders'] = main.serializers.OrderViewSerializer(orders_list, many=True, context=self.context).data


        accepted_orders_list = paginate_related(accepted_orders, request)
        data['accepted_orders'] = main.serializers.OrderViewSerializer(accepted_orders_list, many=True, context=self.context).data

        return data
    


# business account create
class BusinesProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = '__all__'

    def to_representation(self, instance):
        data = BusinessUserViewSerializer(instance, context=self.context).data
        return data