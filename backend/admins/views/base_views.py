from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView, TemplateView
from ..models.models import *
from main.models import *
from django.core.exceptions import ValidationError, FieldError
from ..utils import *
from django.contrib.auth import logout
import os
from django.db import transaction, DatabaseError, IntegrityError
from django.contrib import messages
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from account.models import *
# Create your views here.



# <== update or create view START ==>
class BasedUpdateOrCreateView(SingleObjectTemplateResponseMixin, ModelFormMixin, ProcessFormView):
    related_model = None
    fields = '__all__'
    image_field = None
    meta = False
    multiple_image_model = None
    file_field = None
    object = None
    extra_images = []
    exclude_fields = []

    def form_valid(self, form):
        return None
    
    def form_invalid(self, form):
        return None

    def get_success_url(self):
        return self.success_url

    def get_object(self, queryset=None):
        try:
            return super(BasedUpdateOrCreateView, self).get_object(queryset)
        except AttributeError:
            return None

    def get_id(self):
        obj = self.get_object()
        id = ''
        if obj:
            id = obj.id

        return id

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        key = self.model._meta.verbose_name
        id = self.get_id()

        images_list = [key, f'{key}_multiple']
        if self.extra_images:
            for item in self.extra_images:
                images_list.append(f'{key}_{item}')
        

        predelete_image(images_list, request, id)
        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(BasedUpdateOrCreateView, self).get_context_data(**kwargs)
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        context['lang'] = Languages.objects.filter(default=True).first()

        if self.related_model is not None:
            context['relateds'] = self.related_model.objects.order_by('-id')

        context['dropzone_key'] = self.model._meta.verbose_name
        context['success_url'] = self.success_url

        return context

    def get_request_data(self):
        data_dict = serialize_request(self.model, self.request, self.exclude_fields)
        key = self.model._meta.verbose_name

        id = self.get_id()

        if self.image_field:
            self.extra_images.append(key)
        
        for item in self.extra_images:
            if item == key:
                image_key = key
            else:
                image_key = f'{key}_{item}'

            try:
                file = [it for it in self.request.session.get(
                    image_key, []) if it['id'] == str(id)][0]
            except:
                file = None

            if file:
                if item == key:
                    data_dict[self.image_field] = file['name']
                else:
                    data_dict[item] = file['name']


        if self.file_field:
            file = self.request.FILES.get(self.file_field)

            if file:
                data_dict[self.file_field] = file

        return data_dict

    def clean_data(self, key):
        id = self.get_id()
        clean_session(key, self.request, id=str(id))
        clean_session(f'{key}_multiple', self.request, str(id))

        if self.extra_images:
            for item in self.extra_images:
                clean_session(f'{key}_{item}', self.request, id=str(id))


    def post(self, request, *args, **kwargs):
        context = super().post(request, *args, **kwargs)
        self.object = self.get_object()
        data_dict = self.get_request_data()
        data = self.get_context_data()
        instance = self.get_object()

        try:
            with transaction.atomic():
                if instance:
                    for attr, value in data_dict.items():
                        setattr(instance, attr, value)
                else:
                    instance = self.model(**data_dict)
                    
                instance.full_clean()
                instance.save()
                self.form_isvalid(instance)
                key = self.model._meta.verbose_name
                id = self.get_id()

                if self.multiple_image_model:
                    files = self.request.session.get(f'{key}_multiple', [])
                    for file in [it for it in list(files) if it['id'] == str(id)]:
                        image = self.multiple_image_model(
                            parent=instance, image=file['name'])
                        image.full_clean()
                        image.save()

                self.clean_data(key)
        except Exception as e:
            data['request_post'] = data_dict
            return self.form_error(data, e)

        if self.get_object():
            messages.add_message(request, messages.SUCCESS,
                                 'Обьект успешно обновлен')
        else:
            messages.add_message(request, messages.SUCCESS,
                                'Обьект успешно создан')

        if self.get_success_url():
            return redirect(self.get_success_url())
        else:
            return JsonResponse({'message': 'success'})

    def form_isvalid(self, form):
        if self.meta:
            meta_dict = serialize_request(MetaTags, self.request)

            meta = form.meta
            if meta is None:
                meta = MetaTags.objects.create()
                form.meta = meta
                form.save()

            try:
                for attr, value in meta_dict.items():
                    setattr(form.meta, attr, value)
                form.meta.save()
            except:
                pass

        return form


    def form_error(self, data, error):
        if type(error) is ValidationError:
            error = error.message_dict
        elif type(error) is dict:
            error = error
        else:
            error = str(error)
        data['errors'] = error

        if self.multiple_image_model:
            key = self.model._meta.verbose_name
            files = self.request.session.get(f'{key}_multiple', [])
            data['images'] = files

        if self.success_url and self.template_name:
            return render(self.request, self.template_name, context=data)
        else:
            return JsonResponse({'error': error}, status=403)


# <== update or create view END ==>


# based list view
class BasedListView(ListView):
    search_fields = list()
    paginate_by = 20

    def search(self, queryset, fields: list, *args, **kwargs):
        query = self.request.GET.get("q", '')

        if query == '':
            return queryset
        
        if len(fields) > 0:
            end_set = set()
            for field in fields:
                qs = queryset.extra(where=[f'LOWER({field}) LIKE %s'], params=[f'%{query.lower()}%'])
                for item in qs:
                    end_set.add(item)

            queryset = list_to_queryset(list(end_set))

        return queryset

    def get_queryset(self):
        queryset = self.model.objects.order_by('-id')
        queryset = self.search(queryset, self.search_fields)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(BasedListView, self).get_context_data(**kwargs)

        context['objects'] = get_lst_data(
            self.get_queryset(), self.request, self.paginate_by)
        context['lang'] = Languages.objects.filter(
            active=True).filter(default=True).first()
        context['page_obj'] = paginate(self.get_queryset(), self.request, self.paginate_by)
        context['url'] = search_pagination(self.request)

        return context