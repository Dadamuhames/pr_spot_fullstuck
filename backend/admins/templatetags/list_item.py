from django.template.defaulttags import register


@register.filter
def list_item(list, i):
    return list[int(i)]
