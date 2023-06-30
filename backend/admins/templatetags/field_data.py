from django.template.defaulttags import register
from django.core.files.storage import default_storage
import os
from django.conf import settings
import json
from easy_thumbnails.templatetags.thumbnail import thumbnail_url, get_thumbnailer
from admins.models.models import Languages


@register.simple_tag(takes_context=True)
def field_data(context, **kwargs):
    request_post = context.get("request_post")
    object = kwargs.get('object', context.get('object'))
    lang = kwargs.get('lang')
    field = kwargs.get("field")

    if request_post:
        data_dict = request_post
    elif object:
        data_dict = object.__dict__
    else:
        return ''
    

    field_data = data_dict.get(field, {})

    if type(field_data) != dict:
        if field_data is None:
            return ''

        return field_data

    data = field_data.get(lang.code, '')
    
    return data
