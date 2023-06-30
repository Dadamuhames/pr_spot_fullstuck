from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('orders', views.OrdersView)
router.register('offers', views.OfferView)


urlpatterns = [
    path("static_infos", views.StaticInfView.as_view()),
    path("translations", views.TranslationsView.as_view()),
    path("businesses", views.BusinessesList.as_view()),
    path('upload_image', views.UploadFile.as_view()),
    path("choose_offer", views.ChooseOffer.as_view()),
    path("categories", views.OrderCategoryList.as_view())
]


urlpatterns += router.urls