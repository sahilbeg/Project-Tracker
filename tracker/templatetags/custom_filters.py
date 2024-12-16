# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def split_name(value):
    """Returns the initials of a full name."""
    name_parts = value.split()
    initials = ''.join([part[0].upper() for part in name_parts if part])
    return initials
