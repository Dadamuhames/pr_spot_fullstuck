from django.urls import path, include
from .views import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
     path('', views.home, name='home'),
     path('langs', views.LangsList.as_view(), name='langs_list'),
     path('langs/create', views.LngCreateView.as_view(), name='create_lang'),
     path('langs/<int:pk>/edit', views.LangsUpdate.as_view(), name='lang_update'),
     path('langs/delete', views.delete_langs, name='lang_del'),
     path("site_infos", views.StaticUpdate.as_view(), name='static_info'),
     path('images/save', views.save_images, name='images_save'),
     path("images/delete", views.delete_image, name='del-img'),
     path('translations', views.TranslationList.as_view(), name='translation_list'),
     path("translations/<int:pk>", views.TranslationGroupDetail.as_view(), name='transl_group_detail'),
     path('translation/edit', views.translation_update, name='translation_edit'),
     path("translations/<int:pk>/edit", views.TranslationGroupUdpate.as_view(), name='transl_group_edit'),
     path("translation_group/create", views.add_trans_group, name='transl_group_create'),
     path("delete", views.delete_item, name='delete'),
     path("lang_icon_delete", views.del_lang_icon, name='lang_icon_del'),
     path("add_static_image", views.add_static_image, name='add_static_logos'),
     path("delete_static_image", views.del_statics_image, name='del_static_image'),
     path('login', LoginView.as_view(
          template_name='admin/sing-in.html',
          success_url='/admin/',
     ), name='login_admin'),
     path('logout', views.logout_view, name='logout_url'),
     path('admins', views.AdminsList.as_view(), name='admin_list'),
     path("admins/create", views.AdminCreate.as_view(), name='admins_create'),
     path("admins/<int:pk>/edit", views.AdminUpdate.as_view(), name='admins_edit'),
     path("delete_model_field", views.delete_model_image, name='delete_model_field'),
     
     # users 
     path("costumers", views.CustomerList.as_view(), name='customer_list'),
     path("executors", views.ExecutorList.as_view(), name='executor_list'),
     path("users/create", views.UserFormView.as_view(), name='user_create'),
     path("users/<int:pk>/edit", views.UserFormView.as_view(), name='user_edit'),
     path('users/<int:pk>', views.UserDetailView.as_view(), name='user_detail'),


     # orders
     path('orders', views.OrderList.as_view(), name='order_list'),
     # path("order/create", views.OrderForm.as_view(), name='order_create'),
     path("orders/<int:pk>/edit", views.OrderForm.as_view(), name='order_edit'),


     # order categories
     path('orders/categories', views.OrderCategoryList.as_view(), name='order_ctg_list'),
     path("orders/categories/create", views.OrderCategoryForm.as_view(), name="order_ctg_create"),
     path("orders/categories/<int:pk>/edit", views.OrderCategoryForm.as_view(), name="order_ctg_edit"),


     # offer
     path('offers/change_status', views.change_offer_status, name='hide_offers'),


     # test
     path("test_page", views.tg_login, name="test_page")
]
