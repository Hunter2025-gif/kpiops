"""
Custom template filters for dashboard templates
"""
from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def nice_phase_name(value):
    """Convert phase_name with underscores to readable format"""
    if value:
        # Replace underscores with spaces
        value = value.replace("_", " ")
        # Capitalize each word
        return value.title()
    return value

@register.filter
def duration(start_date, end_date):
    """Calculate duration between two dates"""
    if start_date and end_date:
        duration = end_date - start_date
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    return "N/A"

@register.filter
def duration_from_now(start_date):
    """Calculate duration from start_date to now"""
    if start_date:
        now = timezone.now()
        duration = now - start_date
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    return "N/A"

@register.filter
def duration_from_now_hours(start_date):
    """Calculate duration from start_date to now in hours (for priority calculation)"""
    if start_date:
        now = timezone.now()
        duration = now - start_date
        return duration.total_seconds() / 3600
    return 0
