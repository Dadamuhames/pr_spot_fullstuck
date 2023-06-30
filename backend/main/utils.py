from django.core.paginator import Paginator



def paginate_related(queryset, request):
    page_zise = request.GET.get("page_size", 20)

    page = request.GET.get('page', 1)

    queryset_paginator = Paginator(queryset, int(page_zise))
    queryset_list = queryset_paginator.page(int(page))

    return queryset_list
