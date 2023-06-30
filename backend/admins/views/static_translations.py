from ..forms import LngForm, UserForm
from ..serializers import TranslationSerializer
from .base_views import *

# static update
class StaticUpdate(BasedUpdateOrCreateView):
    model = StaticInformation
    fields = "__all__"
    template_name = 'admin/static_add.html'
    success_url = 'static_info'

    def get(self, request, *args, **kwargs):
        k = self.model._meta.verbose_name
        keys = [f'{k}_image', f'{k}_icon']
        predelete_image(keys, self.request, self.get_object().id)
        return super().get(request, *args, **kwargs)

    def get_object(self):
        try:
            object = StaticInformation.objects.get(id=1)
        except:
            object = StaticInformation.objects.create()

        return object

    def get_request_data(self):
        data_dict = super().get_request_data()
        cotalog = self.request.FILES.get("cotalog")

        if cotalog:
            data_dict['cotalog'] = cotalog

        return data_dict


# translations list
class TranslationList(ListView):
    model = Translations
    template_name = 'admin/translation_list.html'

    def get_queryset(self):
        queryset = Translations.objects.order_by("-id")
        query = self.request.GET.get("q")
        queryset = search_translation(query, queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(TranslationList, self).get_context_data(**kwargs)
        context['groups'] = TranlsationGroups.objects.all()
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        context['url'] = search_pagination(self.request)

        # pagination
        context['translations'] = get_lst_data(
            self.get_queryset(), self.request, 20)
        context['page_obj'] = paginate(self.get_queryset(), self.request, 20)

        return context


# translation group
class TranslationGroupDetail(DetailView):
    model = TranlsationGroups
    template_name = 'admin/translation_list.html'

    def get_context_data(self, **kwargs):
        context = super(TranslationGroupDetail,
                        self).get_context_data(**kwargs)
        context['groups'] = TranlsationGroups.objects.all()
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        lst_one = self.get_object().translations.order_by('-id')

        # search
        query = self.request.GET.get("q")
        lst_one = search_translation(query, lst_one)

        # range
        lst_two = range(1, len(lst_one) + 1)

        # zip 2 lst
        context['translations'] = dict(pairs=zip(lst_one, lst_two))

        return context


# transtion update
def translation_update(request):
    if request.method == 'GET':
        id = request.GET.get('id')

        try:
            translation = Translations.objects.get(id=int(id))
            serializer = TranslationSerializer(translation)

            return JsonResponse(serializer.data)
        except:
            return JsonResponse({'error': 'error'}, safe=False)

    elif request.method == 'POST':
        data = serialize_request(Translations, request)
        id = request.POST.get("id")
        lang = Languages.objects.filter(
            active=True).filter(default=True).first()

        if data.get('value').get(lang.code, '') == '':
            return JsonResponse({'lng_error': 'This language is required'})

        try:
            translation = Translations.objects.get(id=int(id))
            key = data.get('key', '')

            if key == '':
                return JsonResponse({'key_error': 'Key is required'})

            if str(key) in [str(it.key) for it in Translations.objects.filter(group=translation.group).exclude(id=translation.pk)]:
                return JsonResponse({'key_error': 'Key is already in use'})

            translation.key = key
            translation.value = data['value']
            translation.full_clean()
            translation.save()
        except:
            return JsonResponse('some error', safe=False)

        serializer = TranslationSerializer(translation)

        return JsonResponse(serializer.data)


# add translation group
def add_trans_group(request):
    if request.method == 'POST':
        data_dict = serialize_request(TranlsationGroups, request)

        if data_dict.get('sub_text', '') == '':
            return JsonResponse({'key_error': 'Sub text is required'})
        elif (data_dict.get('sub_text'), ) in TranlsationGroups.objects.values_list('sub_text'):
            return JsonResponse({'key_error': 'This key is already in use'})

        try:
            transl_group = TranlsationGroups(**data_dict)
            transl_group.full_clean()
            transl_group.save()
        except ValidationError:
            return JsonResponse({'title_error': 'This title is empty or already in use'})

        data = {
            'id': transl_group.id,
            'name': transl_group.title,
            'key': transl_group.sub_text
        }
        return JsonResponse(data)


# translation group udate
class TranslationGroupUdpate(UpdateView):
    model = TranlsationGroups
    template_name = 'admin/translation_edit.html'
    fields = '__all__'
    success_url = '/admin/translations'

    def get_context_data(self, **kwargs):
        context = super(TranslationGroupUdpate,
                        self).get_context_data(**kwargs)
        context['groups'] = TranlsationGroups.objects.all()
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        context['lng'] = Languages.objects.filter(
            active=True).filter(default=True).first()
        lst_one = self.get_object().translations.all()

        # range
        lst_two = range(1, len(lst_one) + 1)

        # zip 2 lst
        context['translations'] = dict(pairs=zip(lst_one, lst_two))

        return context

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                transls = list(self.get_object().translations.all())
                langs = Languages.objects.filter(
                    active=True).order_by('-default')
                lang = Languages.objects.filter(
                    active=True).filter(default=True).first()
                items_count = request.POST.get("item_count")

                data = []
                for l in range(1, int(items_count) + 1):
                    new_data = {}
                    new_data['id'] = l
                    new_data['key'] = request.POST.get(f'key[{l}]', '')
                    new_data['values'] = []
                    for lng in langs:
                        new_data['values'].append(
                            {'key': f'value[{l}][{lng.code}]', 'value': request.POST.get(f'value[{l}][{lng.code}]', ''), 'def_lang': lang.code, 'lng': lng.code})

                    data.append(new_data)

                objects = dict(pairs=zip(data, list(
                    range(1, int(items_count) + 1))))

                context_data = {
                    'new_objects': objects,
                    'langs': langs,
                    'len': int(items_count) + 1,
                    'object': self.get_object()
                }

                for i in range(len(transls)):
                    transls[i].key = request.POST.get(f'key[{i + 1}]', '')

                    if transls[i].key == '':
                        transaction.set_rollback(True)
                        context_data['key_errors'] = {
                            str(i+1): 'Key is required'}
                        return render(request, template_name=self.template_name, context=context_data)

                    in_default_lng = request.POST.get(
                        f'value[{i+1}][{lang.code}]', '')

                    if in_default_lng == '':
                        transaction.set_rollback(True)
                        context_data['lng_errors'] = {
                            str(i+1): 'This language is required'}
                        return render(request, template_name=self.template_name, context=context_data)

                    value_dict = {}
                    for lng in langs:
                        value_dict[str(lng.code)
                                   ] = request.POST[f'value[{i + 1}][{lng.code}]']

                    transls[i].value = value_dict
                    try:
                        transls[i].full_clean()
                        transls[i].save()
                    except:
                        transaction.set_rollback(True)
                        context_data['key_errors'] = {
                            str(i): 'Key is alredy in use'}
                        return render(request, template_name=self.template_name, context=context_data)

                for i in range(len(transls) + 1, int(items_count) + 1):
                    new_trans = Translations()
                    data = {}
                    new_trans.key = request.POST.get(f'key[{i}]', '')

                    context_data['len'] = items_count

                    if new_trans.key == '':
                        transaction.set_rollback(True)
                        context_data['key_errors'] = {
                            str(i): 'Key is required'}
                        return render(request, template_name=self.template_name, context=context_data)

                    value_dict = {}
                    in_default_lng = request.POST.get(
                        f'value[{i}][{lang.code}]', '')

                    if in_default_lng == '':
                        transaction.set_rollback(True)
                        context_data['lng_errors'] = {
                            str(i): 'This language is required'}
                        return render(request, template_name=self.template_name, context=context_data)

                    for lng in langs:
                        value_dict[str(lng.code)
                                   ] = request.POST[f'value[{i}][{lng.code}]']

                    new_trans.value = value_dict
                    new_trans.group = self.get_object()

                    try:
                        new_trans.full_clean()
                        new_trans.save()
                    except:
                        transaction.set_rollback(True)
                        context_data['key_errors'] = {
                            str(i): 'Key is alredy in use'}
                        return render(request, template_name=self.template_name, context=context_data)

                return redirect('transl_group_detail', pk=self.get_object().id)

        except Exception as e:
            context_data['server_error'] = str(e)
            return render(request, template_name=self.template_name, context=context_data)


# super users list
class AdminsList(BasedListView):
    model = CustomUser
    template_name = 'admin/moterators_list.html'

    def get_queryset(self):
        queryset = CustomUser.objects.filter(is_superuser=True)
        query = self.request.GET.get("q", '')

        if query != '':
            queryset = queryset.filter(Q(username__iregex=query) | Q(
                first_name__iregex=query) | Q(last_name__iregex=query))

        return queryset


# super user create
class AdminCreate(CreateView):
    model = CustomUser
    form_class = UserForm
    success_url = '/'
    template_name = 'admin/moder_form.html'

    def form_valid(self, form):
        new_user = form.save()
        new_user.is_superuser = True
        full_name = self.request.POST.get("name")

        if full_name:
            if len(full_name.split(' ')) > 0:
                new_user.first_name = full_name.split(' ')[0]

            if len(full_name.split(' ')) == 2:
                new_user.last_name = full_name.split(' ')[1]

        new_user.save()

        return redirect('admin_list')


# admin udate
class AdminUpdate(UpdateView):
    model = CustomUser
    form_class = UserForm
    success_url = '/'
    template_name = 'admin/moder_form.html'

    def get_context_data(self, **kwargs):
        context = super(AdminUpdate, self).get_context_data(**kwargs)
        context['full_name'] = ""

        if self.get_object().first_name:
            context['full_name'] = self.get_object().first_name + " "

        if self.get_object().last_name:
            context['full_name'] += self.get_object().last_name

        return context

    def form_valid(self, form):
        user = form.save()
        user.is_superuser = True
        full_name = self.request.POST.get("name")
                                                 

        if full_name:
            full_name = full_name.split(' ')
            print(full_name)
            if len(full_name) > 0:
                user.first_name = full_name[0]

            if len(full_name) == 2:
                user.last_name = full_name[1]

        user.save()

        return redirect('admin_list')


# del lang icond
def del_lang_icon(request):
    id = request.POST.get("item_id")
    url = request.POST.get('url')
    try:
        Languages.objects.get(id=int(id)).icon.delete()
    except:
        pass

    return redirect(url)

# add static image


def add_static_image(request):
    url = request.POST.get('url')
    key = request.POST.get("key")
    file = request.FILES.get('file')

    try:
        model = StaticInformation.objects.get(id=1)

        if key == 'logo1':
            model.logo_first = file
        elif key == 'logo2':
            model.logo_second = file

        model.save()
    except:
        pass

    return redirect(url)


# delete article images
def del_statics_image(request):
    url = request.POST.get('url')
    key = request.POST.get("key")

    try:
        model = StaticInformation.objects.get(id=1)

        if key == 'logo1':
            model.logo_first.delete()
        elif key == 'logo2':
            model.logo_second.delete()
        elif key == 'cotalog':
            model.cotalog.delete()

        model.save()
    except:
        pass

    return redirect(url)


# langs list
class LangsList(ListView):
    model = Languages
    context_object_name = 'langs'
    template_name = 'admin/lang_list.html'

    def get_queryset(self):
        queryset = Languages.objects.all().order_by('-default')
        query = self.request.GET.get("q")
        if query == '':
            query = None

        if query:
            queryset = queryset.filter(
                Q(name__iregex=query) | Q(code__iregex=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LangsList, self).get_context_data(**kwargs)
        context['q'] = self.request.GET.get("q")
        context['langs'] = get_lst_data(self.get_queryset(), self.request, 20)
        context['page_obj'] = paginate(self.get_queryset(), self.request, 20)
        context['url'] = search_pagination(self.request)

        return context


# langs create
class LngCreateView(CreateView):
    model = Languages
    form_class = LngForm
    success_url = '/admin/langs'
    template_name = "admin/lng_create.html"

    def form_valid(self, form):
        lang_save(form, self.request)

        return redirect('langs_list')

    def get_context_data(self, **kwargs):
        context = super(LngCreateView, self).get_context_data(**kwargs)
        context['dropzone_key'] = self.model._meta.verbose_name
        context['images'] = []

        if self.request.session.get(context['dropzone_key']):
            context['images'] = list({'name': it['name'], 'id': clean_text(str(
                it['name']))} for it in self.request.session[context['dropzone_key']] if it['id'] == '')

        return context


# langs update
class LangsUpdate(UpdateView):
    model = Languages
    form_class = LngForm
    success_url = '/admin/langs'
    template_name = "admin/lng_create.html"

    def get_context_data(self, **kwargs):
        context = super(LangsUpdate, self).get_context_data(**kwargs)
        context['dropzone_key'] = self.model._meta.verbose_name

        return context

    def form_valid(self, form):
        lang_save(form, self.request)

        return redirect('langs_list')


# langs delete
def delete_langs(request):
    if request.method == 'POST':
        lng_id = request.POST.get("id")
        try:
            Languages.objects.get(id=int(lng_id)).delete()
        except:
            pass

        url = request.POST.get("url", request.META.get('HTTP_REFERER'))

        return redirect(url)
