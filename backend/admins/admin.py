from django.contrib import admin
from .models.models import *
from django.contrib.auth.models import Permission
# Register your models here.



admin.site.register(StaticInformation)
admin.site.register(Translations)
admin.site.register(TranlsationGroups)
admin.site.register(MetaTags)
admin.site.register(Permission)