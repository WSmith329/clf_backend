from django import template

register = template.Library()


@register.filter
def keyvalue(d, key):
    """Get a dictionary value by key in a Django template."""
    if isinstance(d, dict):
        return d.get(key, '')
    return ''
