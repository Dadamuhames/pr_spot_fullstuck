from django.template.defaulttags import register


@register.filter
def get_qd_item(item, key):
    dict_data = item.__dict__
    return dict_data[key]
