from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """دسترسی به مقدار دیکشنری با کلید و مقدار پیش‌فرض 'P'"""
    return dictionary.get(key, 'P')