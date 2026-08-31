from django import template
from storeApp.views import format_clp

register = template.Library()

@register.filter(name='clp')
def clp_filter(value):
    return format_clp(value)
