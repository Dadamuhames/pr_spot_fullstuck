from django.template.defaulttags import register
from admins.models.models import StaticInformation

@register.inclusion_tag("admin/tags/site_logo.html", takes_context=True)
def show_site_logo(context):
    object, created = StaticInformation.objects.get_or_create(id=1)
    context['logo'] = object.logo_first
    return context


@register.inclusion_tag("admin/tags/site_icon.html", takes_context=True)
def show_site_icon(context):
    object, created = StaticInformation.objects.get_or_create(id=1)
    context['favicon'] = object.logo_second
    return context
