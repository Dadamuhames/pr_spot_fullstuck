from django.template.defaulttags import register


@register.filter
def get_index(lst, key):
    if key in lst:
        return list(lst).index(key)

    return 0
