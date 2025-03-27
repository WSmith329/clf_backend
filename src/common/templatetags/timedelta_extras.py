from django import template

register = template.Library()


@register.filter
def timedelta_hours(td):
    """Returns the total hours from a timedelta"""
    return int(td.total_seconds() // 3600) if td else td


@register.filter
def timedelta_remaining_minutes(td):
    """Returns the remaining minutes after hours in a timedelta."""
    return (int(td.total_seconds()) % 3600) // 60 if td else td
