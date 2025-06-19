"""
Custom Jinja2 template filters for safe datetime handling.
"""

from datetime import datetime
from timezone_utils import format_datetime, make_aware

def safe_strftime(dt, format_str='%d/%m/%Y'):
    """
    Safe strftime filter that handles None values and timezone issues.
    Usage in templates: {{ some_date|safe_strftime('%Y-%m-%d') }}
    """
    return format_datetime(dt, format_str)

def safe_date(dt):
    """
    Safe date formatting filter.
    Usage in templates: {{ some_date|safe_date }}
    """
    return format_datetime(dt, '%d/%m/%Y')

def safe_datetime_format(dt):
    """
    Safe datetime formatting filter.
    Usage in templates: {{ some_datetime|safe_datetime_format }}
    """
    return format_datetime(dt, '%d/%m/%Y %H:%M')

def register_filters(app):
    """Register all custom filters with the Flask app."""
    app.jinja_env.filters['safe_strftime'] = safe_strftime
    app.jinja_env.filters['safe_date'] = safe_date
    app.jinja_env.filters['safe_datetime_format'] = safe_datetime_format