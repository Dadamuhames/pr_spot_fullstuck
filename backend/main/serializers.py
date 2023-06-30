from .models import *
from admins.models.models import *
from .base_serializers import *
from account.models import *
from account.serializers import *


# meta serializer
class MetaFieldSerializer(BaseModelSerializer):
    class Meta:
        model = MetaTags
        exclude = ['id']


# static information
class StaticInformationSerializer(BaseModelSerializer):
    logo_first = ThumbnailSerializer(alias='prod_photo')
    logo_second = ThumbnailSerializer(alias='prod_photo')

    class Meta:
        model = StaticInformation
        exclude = ['id']


# translation serializer
class TranslationSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {}

        for item in instance:
            val = JsonFieldSerializer(
                item.value, context={'request': self.context.get('request')}).data
            key = str(item.group.sub_text) + '.' + str(item.key)
            data[key] = val

        return data


# langs serializer
class LangsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = '__all__'
    

# order offers serializer
class OfferViewSerialzier(serializers.ModelSerializer):
    executor = UserViewSerializer()
    date = serializers.DateTimeField()

    class Meta:
        model = Offers
        exclude = ['order']


# offers create serializer
class OffersCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offers
        fields = '__all__'

    
    def to_representation(self, instance):
        data = OfferViewSerialzier(instance, context=self.context).data
        return data
    

    def create(self, validated_data):
        request = self.context.get("reqeust")
        validated_data['executor'] = request.user
        return super().create(validated_data)
    

# offer update serializer
class OfferUpdateSerializer(OffersCreateSerializer):
    class Meta:
        fields = ['executor_offer']



# order images serializer
class OrderImageSerializer(serializers.ModelSerializer):
    image = ThumbnailSerializer(alias='900x900')
    
    class Meta:
        model = OrderImages
        exclude = ['parent']


# order category serializer
class OrderCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderCategories
        fields = '__all__'


# order view serializer
class OrderViewSerializer(serializers.ModelSerializer):
    category = OrderCategorySerializer()
    costumer = UserViewSerializer()
    executor = UserViewSerializer()
    images = OrderImageSerializer(many=True)
    date = serializers.DateTimeField()

    class Meta:
        model = Order
        fields = '__all__'


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['status'] = instance.get_status_display()
        data['offers_count'] = instance.offers.count()
        return data
    



# order detail serializer
class OrderDetailSerializer(OrderViewSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        offers = instance.offers.filter(active=True)

        offers_list = paginate_related(offers, request)
        data['offers'] = OfferViewSerialzier(offers_list, many=True, context=self.context).data

        return data


# order create view
class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def to_representation(self, instance):
        data = OrderDetailSerializer(instance, context=self.context).data
        return data
    

