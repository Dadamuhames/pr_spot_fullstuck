from . import views
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("me", views.UserProfileView.as_view()),
    path("create_business", views.CreateBusinessAccount.as_view()),
    path('login', views.LoginOrSingUp.as_view()),
    path("login/refresh", TokenRefreshView.as_view())
]