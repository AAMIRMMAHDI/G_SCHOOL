# templatetags/form_filters.py کامل
from django import template

register = template.Library()

@register.filter
def lookup(dict_obj, key):
    return dict_obj.get(key)

@register.filter
def dictget(dict_obj, key):
    return dict_obj.get(key)