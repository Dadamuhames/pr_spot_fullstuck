from typing import Any
from django.db import models
from .base_views import *


# user list view
class CustomerList(BasedListView):
    model = CustomUser
    template_name = 'admin/user/user_list.html'
    executor = False

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = queryset.exclude(is_superuser=True)

        query = self.request.GET.get("q", "").lower()

        if query != "":
            if not self.executor:
                queryset = queryset.filter(Q(first_name__iregex=query) | Q(last_name__iregex=query))
            else:
                queryset = queryset.filter(
                    Q(first_name__iregex=query) | Q(last_name__iregex=query) | Q(business_profile__organization__iregex=query))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['executor'] = self.executor
        return context


# executor list
class ExecutorList(CustomerList):
    template_name = 'admin/user/user_list.html'
    executor = True

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_executor=self.executor)
        return queryset


# user detail view
class UserDetailView(DetailView):
    model = CustomUser
    template_name = "admin/user/user_view.html"

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        context['lang'] = Languages.objects.filter(default=True).first()
        context['dropzone_key'] = self.model._meta.verbose_name

        obj = self.get_object()

        orders = obj.orders.order_by("-id")
        accepted_orders = obj.accepted_orders.order_by("-id")
        offers = obj.offers.order_by('-id')

        context['orders'] = dict(
            pairs=zip(range(1, orders.count() + 1), orders))
        context['accepted_orders'] = dict(pairs=zip(range(1, accepted_orders.count() + 1), accepted_orders))
        context['offers'] = dict(
            pairs=zip(range(1, offers.count() + 1), offers))

        return context


# user form view
class UserFormView(BasedUpdateOrCreateView):
    model = CustomUser
    template_name = 'admin/user/user_form.html'
    success_url = 'customer_list'
    image_field = 'avatar'
    queryset = CustomUser.objects.exclude(is_superuser=True)
    exclude_fields = ['username', 'password', 'date_joined']

    def get(self, request, *args, **kwargs):
        business_key = BusinessProfile._meta.verbose_name
        predelete_image([business_key], self.request, str(self.get_id()))
        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busines_key'] = BusinessProfile._meta.verbose_name

        return context


    def clean_data(self, key):
        business_key = BusinessProfile._meta.verbose_name
        clean_session(business_key, self.request, id=str(self.get_id()))
        return super().clean_data(key)
    

    def get_request_data(self):
        data = super().get_request_data()

        if data.get('is_executor', False):
            self.success_url = 'executor_list'

        return data
    

    def busines_profile_data(self, user=None):
        business_profile_data = serialize_request(BusinessProfile, self.request)
        business_profile_data['user'] = user

        id = self.get_id()
        key = BusinessProfile._meta.verbose_name

        # save business account avatar
        try:
            file = [it for it in self.request.session.get(
                key, []) if it['id'] == str(id)][0]
        except:
            file = None

        if file:
            business_profile_data["business_avatar"] = file['name']

        return business_profile_data



    def form_isvalid(self, form):
        user = super().form_isvalid(form)
        
        is_bus_prof = self.request.POST.get("is_executor")

        if is_bus_prof is None and user.is_executor:
            is_bus_prof = 'on'

        is_bus = boolize(is_bus_prof)

        if is_bus or user.is_executor:
            self.success_url = 'executor_list' # set succes_url for business account
            business_profile_data = self.busines_profile_data(user)
            data = self.get_context_data()
            
            # save business account
            try:
                bus_profile = user.get_business_profile()

                if bus_profile: # update business account if its exists
                    for attr, value in business_profile_data.items():
                        setattr(bus_profile, attr, value)
                else: # create business account
                    bus_profile = BusinessProfile(**business_profile_data)
                    
                bus_profile.full_clean()
                bus_profile.save()
            except ValidationError as e:
                raise e
        
        return user
    

    def form_error(self, data, error):
        business_profile_data = self.busines_profile_data()
        
        for key, val in business_profile_data.items():
            data['request_post'][key] = val

        return super().form_error(data, error)