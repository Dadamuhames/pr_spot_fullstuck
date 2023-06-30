from django.template.defaulttags import register


@register.filter
def list_len(lst):
    return range(6 - len(lst))
