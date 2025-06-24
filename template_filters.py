"""
Custom Jinja2 template filters for robust timezone-aware datetime handling.
All filters automatically convert UTC datetimes to user's local timezone for display.
"""

import json
from datetime import datetime
from timezone_utils import (
    format_datetime, format_date, format_datetime_full, 
    datetime_for_input, to_local, get_user_timezone
)

def safe_strftime(dt, format_str='%d/%m/%Y'):
    """
    Safe strftime filter that handles None values and timezone conversion.
    Converts UTC datetime to user's local timezone before formatting.
    Usage in templates: {{ some_date|safe_strftime('%Y-%m-%d') }}
    """
    return format_datetime(dt, format_str, to_local_time=True)

def safe_date(dt):
    """
    Safe date formatting filter (date only in user's local timezone).
    Usage in templates: {{ some_date|safe_date }}
    """
    return format_date(dt)

def safe_datetime_format(dt):
    """
    Safe datetime formatting filter (date and time in user's local timezone).
    Usage in templates: {{ some_datetime|safe_datetime_format }}
    """
    return format_datetime_full(dt)

def datetime_input(dt):
    """
    Format datetime for HTML datetime-local input fields.
    Converts UTC to user's local timezone.
    Usage in templates: {{ some_datetime|datetime_input }}
    """
    return datetime_for_input(dt, 'datetime-local')

def date_input(dt):
    """
    Format datetime for HTML date input fields.
    Converts UTC to user's local timezone.
    Usage in templates: {{ some_datetime|date_input }}
    """
    return datetime_for_input(dt, 'date')

def user_timezone():
    """
    Get user's timezone for display.
    Usage in templates: {{ user_timezone() }}
    """
    return get_user_timezone()

def register_filters(app):
    """Register all custom filters with the Flask app."""
    app.jinja_env.filters['safe_strftime'] = safe_strftime
    app.jinja_env.filters['safe_date'] = safe_date
    app.jinja_env.filters['safe_datetime_format'] = safe_datetime_format
    app.jinja_env.filters['datetime_input'] = datetime_input
    app.jinja_env.filters['date_input'] = date_input
    app.jinja_env.filters['from_json'] = from_json
    app.jinja_env.globals['user_timezone'] = user_timezone