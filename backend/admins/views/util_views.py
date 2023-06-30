from .base_views import *


# delete model item
def delete_item(request):
    model_name = request.POST.get("model_name_del")
    app_name = request.POST.get('app_name_del')
    id = request.POST.get('item_id')
    url = request.POST.get("url")

    try:
        with transaction.atomic():
            model = apps.get_model(model_name=model_name, app_label=app_name)
            model.objects.get(id=int(id)).delete()
            messages.add_message(request, messages.SUCCESS, 'Объект успешно удален')
    except:
        messages.add_message(request, messages.ERROR,
                             'Ошибка при удалении объекта')

    return redirect(url)




# save images
def save_images(request):
    if request.method == 'POST':
        key = request.POST.get("key")
        file = request.FILES.get('file')
        id = request.POST.get("id", '')

        now = datetime.now()

        file_name = get_random_string(30) + f"{now.time().hour}_{now.time().minute}_{now.time().second}"
        suff = file.name.split('.')[-1]

        request.session[key] = request.session.get(key, [])
        file_name = default_storage.save(
            f'dropzone/{key}/{now.year}/{now.month}/{now.day}/' + f"{file_name[:50]}.{suff}", file)

        data = {
            'id': id,
            'name': file_name
        }

        request.session[key].append(data)
        request.session.modified = True

    return JsonResponse(file_name, safe=False)


# delete image
def delete_image(request):
    if request.method == 'POST':
        key = request.POST.get('key')
        file = request.POST.get("file")

        if request.session.get(key):
            for it in list(request.session[key]):
                if it['name'] == file:
                    if default_storage.exists(it['name']):
                        default_storage.delete(it['name'])
                    request.session[key].remove(it)
                    request.session.modified = True

    return redirect(request.META.get("HTTP_REFERER"))


# logout
def logout_view(request):
    logout(request)

    return redirect('login_admin')



# delete model image
def delete_model_image(request):
    obj_id = request.POST.get("obj_id")
    field = request.POST.get('field')
    model_name = request.POST.get("model_name")
    app_name = request.POST.get('app_name')

    try:
        model = apps.get_model(model_name=model_name, app_label=app_name)
        obj = model.objects.get(id=int(obj_id))

        data_dict = obj.__dict__

        data_dict[field] = None

        for key, value in data_dict.items():
            setattr(obj, key, value)

        obj.full_clean()
        obj.save()

    except ValidationError as e:
        return JsonResponse(status=403, data={'error': str(e)})

    return JsonResponse({'message': "success"})
