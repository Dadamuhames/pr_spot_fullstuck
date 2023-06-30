import random
import string
from .models.models import Languages, Translations, TranlsationGroups, StaticInformation, models, ThumbnailerImageField
import datetime
from django.db.models import Q
import json
from django.apps import apps
from django.core.paginator import Paginator
from django.http import JsonResponse, QueryDict
import re
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.conf import settings


# get request.data in JSON
def serialize_request(model, request, exclude_fields: list = []):
    langs = Languages.objects.filter(active=True)
    data_dict = {}

    exclude_fields.append("id")

    field_list = [item for item in model._meta.fields if item.name not in exclude_fields]

    for field in field_list:
        field_dict = {}
        if isinstance(field, models.JSONField):
            for lang in langs:
                field_dict[lang.code] = request.POST.get(f'{field.name}#{lang.code}')
            data_dict[str(field.name)] = field_dict

        elif isinstance(field, models.ForeignKey):
            related_model = field.related_model
            id = request.POST.get(str(field.name))

            if id:
                model = related_model.objects.get(id=int(id))
                data_dict[field.name] = model
            else:
                data_dict[field.name] = None

        else:
            value = request.POST.get(str(field.name))
            if value and not isinstance(field, models.BooleanField):
                data_dict[str(field.name)] = value
                
            elif isinstance(field, models.BooleanField):
                if field.name in request.POST:
                    data_dict[str(field.name)] = True
                elif field.name not in request.POST:
                    data_dict[str(field.name)] = False
            elif not isinstance(field, models.FileField):
                data_dict[str(field.name)] = None
            
    return data_dict


# search_paginate
def search_pagination(request):
    url = request.path + '?'

    if 'q=' in request.get_full_path():
        if '&' in request.get_full_path():
            url = request.get_full_path().split('&')[0] + '&'
        else:
            url = request.get_full_path() + '&'

    return url



# list to queryset
def list_to_queryset(model_list):
    if len(model_list) > 0:
        return model_list[0].__class__.objects.filter(
            pk__in=[obj.pk for obj in model_list])
    else:
        return []


# list of dicts to queryset
def list_of_dicts_to_queryset(list, model):
    if len(list) > 0:
        return model.objects.filter(id__in=[int(obj['id']) for obj in list])
    else:
        return []



# search translations
def search_translation(query, queryset, *args, **kwargs):
    langs = Languages.objects.all()
    endlist = []
    if query and query != '':
        query = query.lower()
        for item in queryset:
            for lang in langs:
                if query in str(item.value.get(lang.code, '')).lower() or query in str(item.key).lower() or query in str(item.group.sub_text + '.' + item.key).lower():
                    endlist.append(item)
                continue
    
        queryset = list_to_queryset(endlist)
    
    return queryset



# pagination
def paginate(queryset, request, number):
    paginator = Paginator(queryset, number)

    try:
        page_obj = paginator.get_page(request.GET.get("page"))
    except:
        page_obj = paginator.get_page(request.GET.get(1))

    return page_obj


# get lst data
def get_lst_data(queryset, request, number):
    lst_one = paginate(queryset, request, number)
    page = request.GET.get('page')

    if page is None or int(page) == 1:
        lst_two = range(1, number + 1)
    else:
        start = (int(page) - 1) * number + 1
        end = int(page) * number

        if end > len(queryset):
            end = len(queryset)

        lst_two = range(start, end + 1)


    return dict(pairs=zip(lst_one, lst_two))


# langs save
def lang_save(form, request):
    lang = form.save()
    key = request.POST.get('dropzone-key')
    sess_image = request.session.get(key)

    if sess_image:
        lang.icon = sess_image[0]['name']
        request.session[key].remove(sess_image[0])
        request.session.modified = True
        lang.save()

    if lang.default:
        for lng in Languages.objects.exclude(id=lang.id):
            lng.default = False
            lng.save()

    return lang




# is valid
def is_valid_field(data, field):
    lang = Languages.objects.filter(default=True).first()
    try:
        val = data.get(field, {}).get(lang.code, '')
    except:
        return False

    return val != ''



# clean text
def clean_text(str):
    for char in string.punctuation:
        str = str.replace(char, ' ')

    return str.replace(' ', '')



# requeired field errors
def required_field_validate(fields: list, data):
    error = {}

    for field in fields:
        if field not in data:
            error[field] = 'This field is reuqired'

    return error


# get option from request
def get_option_from_post(i, req):
    langs = Languages.objects.filter(active=True)
    data_dict = {}
    for lang in langs:
        option = req.POST.get(f'option[{lang.code}][{i}]')
        data_dict[lang.code] = option

    return {'name': data_dict}


# collect options
def collect_options(nbm, req):
    end_data = []
    for i in range(1, nbm+1):
        data_dict = get_option_from_post(i, req)
        end_data.append(data_dict)

    return end_data


# get baners
def get_baner(key, id, request, def_data=None):
    langs = Languages.objects.filter(active=True)
    baner_data = {}

    if langs.exists():
        for lang in langs:
            files = request.session.get(f'{key}_{lang.code}')

            if files:
                images = [it for it in list(files) if str(it['id']) == str(id)]
                image = images[0]
                images.remove(image)
                
                request.session.get(f'{key}_{lang.code}').remove(image)
                request.session.modified = True
                
                baner_data[lang.code] = image['name']
                for it in images:
                    default_storage.delete(it['name'])
                    request.session.get(f'{key}_{lang.code}').remove(it)
                    request.session.modified = True
            elif def_data:
                baner_data[lang.code] = def_data.get(lang.code, '')

    return baner_data



# request itemto bool
def boolize(item):
    data = {'on': True, 'off': False}

    return data.get(item)

# pre delete ctg images
def predelete_image(keys :list, request, id):
    for key in keys:
        files = request.session.get(key)

        if files:
            for it in list(files):
                if it['id'] == str(id):
                    if default_storage.exists(it['name']):
                        default_storage.delete(it['name'])

                    request.session[key].remove(it)
                    request.session.modified = True

    

# clean session
def clean_session(key, request, id=''):
    sess_images = request.session.get(key)

    if sess_images:
        for item in list(sess_images):
            if str(item['id']) == str(id):
                request.session.get(key).remove(item)
                request.session.modified = True


def get_object_or_none(queryset, id):
    try:
        return queryset.get(id=int(id))
    except:
        return None



# collect specif data
def collect_specif_data(req):
    langs = Languages.objects.filter(active=True)

    specifications_id = req.POST.getlist("specification", [])
    specif_data = []

    for id in specifications_id:
        data_dict = {}

        data_dict['specification'] = id
        data_dict['name'] = req.POST.get(f"spec_name[{id}]", '')
        data_dict['value'] = {}

        for lang in langs:
            lang_value = req.POST.get(f"spec_value[{lang.code}][{id}]", '')
            data_dict['value'][lang.code] = lang_value

        specif_data.append(data_dict)

    return specif_data


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str
