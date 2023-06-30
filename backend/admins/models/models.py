from .base_models import *
from easy_thumbnails.templatetags.thumbnail import get_thumbnailer
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator
import re
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
# telephone nbm validator



def is_numeric_validator(value):
    if str(value).isnumeric() is False:
        raise ValidationError(
            ("Your telephone number is invalid"),
            params={'value': value}
        )


class MetaTags(models.Model):
    meta_deck = models.JSONField('Meta desk', blank=True, null=True)
    meta_keys = models.JSONField('Meta keys', blank=True, null=True)



def telephone_validator(value):
    number_temp = r"\+998\d{9}"
    if bool(re.match(number_temp, value)) == False:
        raise ValidationError(
            ("Your telephone number is invalid"),
            params={'value': value}
        )


# Create your models here.
class StaticInformation(models.Model):
    title = models.JSONField('Заголовок сайта', blank=True, null=True, validators=[json_field_validate])
    subtitle = models.JSONField('Подзаголовок сайта', blank=True, null=True)
    description = models.JSONField("Описание сайта", blank=True, null=True)
    about_us = models.JSONField("О нас", blank=True, null=True)
    adres = models.JSONField("Адрес", blank=True, null=True)
    logo_first = ThumbnailerImageField("Лого сайта", blank=True, null=True, upload_to='site_logo')
    logo_second = ThumbnailerImageField("Второе лого", blank=True, null=True, upload_to='site_logo')
    email = models.EmailField("Эмейл", blank=True, null=True)
    telegram = models.URLField("Ссылка на телеграм", blank=True, null=True, max_length=255)
    instagram = models.URLField("Ссылка на инстаграм", blank=True, null=True, max_length=255)
    facebook = models.URLField("Ссылка на фэйсбук", blank=True, null=True, max_length=255)
    youtube = models.URLField("Ютуб", blank=True, null=True, max_length=255)
    nbm = models.CharField("Номер телефона", blank=True, null=True, max_length=255)
    map = models.TextField('Iframe карты', blank=True, null=True)
    work_time = models.JSONField('Время работы', blank=True, null=True)


    class Meta:
        verbose_name = 'static_inf'


    def __str__(self):
        return 'Static information'

    
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)



# translation groups
class TranlsationGroups(models.Model):
    title = models.CharField('Название', max_length=255, unique=True)
    sub_text = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'transl_group'


# translations
class Translations(models.Model):
    group = models.ForeignKey(TranlsationGroups, on_delete=models.CASCADE, related_name='translations')
    key = models.CharField(max_length=255)
    value = models.JSONField("Значение")


    def __str__(self):
        return f'{self.group.sub_text}.{self.key}'

    class Meta:
        verbose_name = 'transl'
        unique_together = ['key', 'group']
