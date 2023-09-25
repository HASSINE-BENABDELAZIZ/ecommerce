
from django import template

register = template.Library()


@register.filter
def get_mongo_id(obj):
    return str(obj.get('_id'))
