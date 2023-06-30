from .base_views import *


# order category list
class OrderCategoryList(BasedListView):
    model = OrderCategories
    template_name = 'admin/order/order_ctg_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        query = self.request.GET.get("q", '')

        if query != '':
            queryset = queryset.filter(title_iregex=query.lower())
        
        return queryset


# order category form
class OrderCategoryForm(BasedUpdateOrCreateView):
    model = OrderCategories
    template_name = 'admin/order/order_ctg_form.html'
    image_field = 'image'
    success_url = 'order_ctg_list'



# order list
class OrderList(BasedListView):
    model = Order
    template_name = 'admin/order/orders_list.html'
    paginate_by = 3


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = CustomUser.objects.exclude(is_superuser=True)
        context['customers'] = users
        context['executors'] = users.filter(is_executor=True)
        context['statuses'] = Order.status.field.choices

        url = self.request.get_full_path()

        if '&page=' in url:
            index_a = url.index("page=")
            url = url[:index_a]

        context["url"] = url

        return context


    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "")
        status = self.request.GET.get("status", "")
        customer = self.request.GET.get("customer", "")
        executor = self.request.GET.get('executor', "")

        if query != '':
            queryset = queryset.filter(title__iregex=query.lower())

        if status != '':
            queryset = queryset.filter(status=status)
        
        if customer != '':
            queryset = queryset.filter(costumer__id=int(customer))

        if executor != '':
            queryset = queryset.filter(executor__id=int(executor))

        return queryset


# order form
class OrderForm(BasedUpdateOrCreateView):
    model = Order
    template_name = 'admin/order/orders_form.html'
    success_url = 'order_list'
    multiple_image_model = OrderImages
    related_model = OrderCategories

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()

        context['offers'] = []

        if obj:
            context['offers'] = obj.offers.all()

        users = CustomUser.objects.exclude(is_superuser=True)
        context['customers'] = users
        context['executors'] = users.filter(is_executor=True)
        context['statuses'] = Order.status.field.choices


        return context
    

    def form_error(self, data, error):
        print(error)
        return super().form_error(data, error)



# change offer visibility
def change_offer_status(request):
    id = request.POST.get("id", 0)

    try:
        offer = Offers.objects.get(id=int(id))
        offer.active = not offer.active
        offer.save()
    except:
        return JsonResponse({"message": "detail not found"}, status=404)

    return JsonResponse({"message": "success", "status": offer.active})