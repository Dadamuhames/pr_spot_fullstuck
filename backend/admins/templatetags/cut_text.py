from django.template.defaulttags import register


@register.filter
def cut_text(strng):
    if strng is None:
        strng = ''

    if len(str(strng)) > 50:
        return strng[:50] + '...'
    else:
        return strng
