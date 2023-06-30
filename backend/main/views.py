from django.shortcuts import render
from .serializers import *
from rest_framework import views, viewsets, generics, response, pagination, filters, permissions
from .models import *
from admins.models.models import *
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction, DatabaseError, IntegrityError
from admins.utils import get_random_string
from .custom_perms import *
# Create your views here.


# pagination
class BasePagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000


# static information
class StaticInfView(views.APIView):
    def get(self, request, format=None):
        obj, created = StaticInformation.objects.get_or_create(id=1)
        serializer = StaticInformationSerializer(
            obj, context={'request': request})

        return response.Response(serializer.data)


# translations
class TranslationsView(views.APIView):
    def get(self, request, fromat=None):
        translations = Translations.objects.all()
        serializer = TranslationSerializer(
            translations, context={'request': request})
        return response.Response(serializer.data)


# langs list
class LangsList(generics.ListAPIView):
    queryset = Languages.objects.filter(active=True)
    serializer_class = LangsSerializer
    pagination_class = BasePagination



# businesses list
class BusinessesList(generics.ListAPIView):
    queryset = CustomUser.objects.filter(is_executor=True, is_active=True, is_superuser=False, business_profile__active=True)
    serializer_class = UserViewSerializer
    pagination_class = BasePagination


# order category list
class OrderCategoryList(generics.ListAPIView):
    queryset = OrderCategories.objects.all()
    serializer_class = OrderCategorySerializer
    pagination_class = BasePagination



# orders view
class OrdersView(viewsets.ModelViewSet):
    queryset = Order.objects.filter(active=True)
    serializer_class = OrderViewSerializer
    pagination_class = BasePagination
    http_method_names = ['get', "put", "post"]
    permission_classes = [IsOrderCostumerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']


    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = OrderDetailSerializer
        obj = self.get_object()
        obj.views += 1
        obj.save()
        return super().retrieve(request, *args, **kwargs)
    
    
    # save images
    def save_images(self, images_list, instance):
        if images_list:
            for image_data in images_list:
                image_data['parent'] = instance

                try:
                    image = OrderImages(**image_data)
                    image.full_clean()
                    image.save()
                except ValidationError as e:
                    return response.Response(status=403, data=e.message_dict)

    
    # create method
    def create(self, request, *args, **kwargs):
        self.serializer_class = OrderCreateSerializer
        try:
            with transaction.atomic():
                return super().create(request, *args, **kwargs)

        except Exception as e:
            error = str(e)

            if type(e) is ValidationError:
                error = e.message_dict

            return response.Response({'message': error}) 
        

    # update method
    def update(self, request, *args, **kwargs):
        self.serializer_class = OrderCreateSerializer

        try:
            with transaction.atomic():
                return super().update(request, *args, **kwargs)   

        except Exception as e:
            error = str(e)

            if type(e) is ValidationError:
                error = e.message_dict

            return response.Response({'message': error})


    # perform create
    def perform_create(self, serializer):
        instance = serializer.save()

        images = self.request.POST.getlist("images")

        self.save_images(images, instance)

        return instance


    # perform update
    def perform_update(self, serializer):
        instance = serializer.save()

        # update old images order
        updated_imges = self.request.data.get("images_old", [])
        instance_images = instance.images.all()

        for image_data in updated_imges:
            image = get_object_or_404(instance_images, id=int(image_data.get('id', 0)))
            image.order = int(image_data.get("order"))
            image.save()

        # add new images
        new_images = self.request.data.get("images_new", [])

        self.save_images(new_images, instance)

        return instance
    


# upload image
class UploadFile(views.APIView):
    def post(self, request, format=None):
        file = request.data.get("file")
        key = request.data.get("key", 'all')

        now = datetime.now()

        file_name = get_random_string(30) + f"{now.time().hour}_{now.time().minute}_{now.time().second}"
        suff = file.name.split('.')[-1]


        file_path = default_storage.save(
            f'images/{key}/{now.year}/{now.month}/{now.day}/' + f"{file_name[:50]}.{suff}", file)

        return response.Response(file_path)
    

    def delete(self, request, format=None):
        file = request.data.get("file")

        if default_storage.exists(file):
            default_storage.delete(file)
        else:
            return response.Response(status=404, data={"message": "file not found"})

        return response.Response({'message': "success"})



# offer create view
class OfferView(viewsets.ModelViewSet):
    queryset = Offers.objects.filter(active=True)
    serializer_class = OffersCreateSerializer
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsExecutorOrReadOnly]


# choose offer
class ChooseOffer(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, reqeust, format=None):
        id = reqeust.data.get("id")
        order_id = reqeust.data.get("order_id")

        order = get_object_or_404(Order.objects.filter(active=True), id=int(order_id))
        offer = get_object_or_404(order.offers.filter(active=True), id=int(id))


        if reqeust.user != order.costumer:
            return response.Response({"message": "This use has not permissions to choose offer for this order"})

        try:
            offer.executor_offer = True
            offer.full_clean()
            offer.save()
        except ValidationError as e:
            return response.Response(e.message_dict)
        
        return response.Response({"message": "success"})
