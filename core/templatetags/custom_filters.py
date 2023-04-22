from datetime import timedelta
from django import template

register = template.Library()

@register.filter(name='add_days')
def add_days(value, days):
    return value + timedelta(days=days)