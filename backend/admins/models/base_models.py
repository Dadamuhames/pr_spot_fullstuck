from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from django.utils.text import slugify
import random
import string
import cyrtranslit
from django.core.exceptions import ValidationError


# json validation
def json_field_validate(value):
    lang = Languages.objects.filter(default=True).first()

    if value.get(lang.code, '') == '':
        raise ValidationError(
            ("This field is required"),
            params={'value': value}
        )

# languages
class Languages(models.Model):
    name = models.CharField('Названия', max_length=255, blank=True, null=True)
    code = models.CharField('Код языка', max_length=255,
                            blank=True, null=True, unique=True)
    icon = ThumbnailerImageField(upload_to='lng_icon', blank=True, null=True)
    active = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'lang'

    
    def save(self, *args, **kwargs) -> None:
        def_lang = Languages.objects.filter(default=True)

        if self.id and not self.default:
            def_lang = def_lang.exclude(id=self.id)

        if not def_lang.exists():
            self.default = True 

        return super().save(*args, **kwargs)



# random string generate
def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))



# unique string generate
def unique_slug_generator(instance, slug, id=None, extra_class=None, i=1):
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug)

    if id:
        qs_exists = qs_exists.exclude(id=id)
    qs_exists = qs_exists.exists()
    if qs_exists or (extra_class and extra_class.objects.filter(slug=slug)):
        slug_lst = slug.split('-')

        if str(i-1) == slug_lst[-1]:
            slug = '-'.join(slug_lst[:-1])

        new_slug = "{slug}-{int}".format(slug=slug, int=i)
        l = i + 1
        return unique_slug_generator(instance, new_slug, id=id, extra_class=extra_class,  i=l)

    return slug



# === BASE SLUG FIELD MODEL | START | ===
class BaseSlugFieldModel(models.Model):
    slug_fields = []

    slug = models.SlugField('Slug', editable=False, unique=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):  # new
        lng = Languages.objects.filter(
            active=True).filter(default=True).first()

        data_dict = self.__dict__
        slug_string = ''
        slug_fields = self.slug_fields

        for field in slug_fields:
            add_str = data_dict.get(field, '')

            if add_str == None:
                add_str = ''

            if type(add_str) == dict:
                add_str = add_str.get(lng.code, '')

            slug_string += add_str

            if len(slug_fields) > 1 and slug_fields.index(field) != len(slug_fields):
                slug_string += '_'

        str = cyrtranslit.to_latin(slug_string[:40])
        slug = slugify(str)

        if not self.slug:
            self.slug = unique_slug_generator(self, slug)
        else:
            self.slug = unique_slug_generator(self, slug, id=self.id)

        return super().save(*args, **kwargs)

# === BASE SLUG FIELD MODEL | END | ===
