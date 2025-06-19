"""
Comprehensive timezone utilities for robust datetime handling across the application.
This module enforces a single rule: All datetimes in the database must be timezone-aware and in UTC.
All user input/display is converted between local time and UTC consistently.
"""

from datetime import datetime, timezone
from typing import Optional, Union
import zoneinfo
from flask import current_app, session
from flask_login import current_user

# Application default timezone
DEFAULT_TIMEZONE = timezone.utc
# User default timezone (Greece)
DEFAULT_USER_TIMEZONE = 'Europe/Athens'

def get_user_timezone() -> str:
    """
    Get the user's timezone preference.
    Priority: 1. User profile setting 2. Session 3. Default (Europe/Athens)
    """
    # Check if user has timezone in their profile
    if current_user and current_user.is_authenticated and hasattr(current_user, 'timezone') and current_user.timezone:
        return current_user.timezone
    
    # Check session
    if 'user_timezone' in session:
        return session['user_timezone']
    
    # Default timezone
    return DEFAULT_USER_TIMEZONE

def set_user_timezone(timezone_str: str) -> None:
    """Set user timezone in session and optionally in user profile."""
    session['user_timezone'] = timezone_str
    
    # Also save to user profile if authenticated
    if current_user and current_user.is_authenticated:
        try:
            current_user.timezone = timezone_str
            from app import db
            db.session.commit()
        except:
            pass  # Don't fail if user model doesn't have timezone field yet

def now_utc() -> datetime:
    """Get current datetime in UTC timezone."""
    return datetime.now(timezone.utc)

def now_local() -> Optional[datetime]:
    """Get current datetime in user's local timezone."""
    utc_now = now_utc()
    return to_local(utc_now)

def to_utc(dt: Optional[datetime], from_timezone: Optional[str] = None) -> Optional[datetime]:
    """
    Convert a datetime to UTC.
    
    Args:
        dt: The datetime to convert
        from_timezone: Source timezone string (if None, uses user's timezone for naive datetimes)
    
    Returns:
        UTC datetime or None
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # Naive datetime - assume it's in user's timezone
        if from_timezone is None:
            from_timezone = get_user_timezone()
        
        try:
            local_tz = zoneinfo.ZoneInfo(from_timezone)
            dt_aware = dt.replace(tzinfo=local_tz)
            return dt_aware.astimezone(timezone.utc)
        except Exception:
            # Fallback: assume UTC
            return dt.replace(tzinfo=timezone.utc)
    
    # Already timezone-aware, convert to UTC
    return dt.astimezone(timezone.utc)

def to_local(dt: Optional[datetime], to_timezone: Optional[str] = None) -> Optional[datetime]:
    """
    Convert a UTC datetime to user's local timezone.
    
    Args:
        dt: UTC datetime to convert
        to_timezone: Target timezone string (if None, uses user's timezone)
    
    Returns:
        Local datetime or None
    """
    if dt is None:
        return None
    
    if to_timezone is None:
        to_timezone = get_user_timezone()
    
    try:
        # Ensure datetime is UTC first
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        elif dt.tzinfo != timezone.utc:
            dt = dt.astimezone(timezone.utc)
        
        # Convert to target timezone
        target_tz = zoneinfo.ZoneInfo(to_timezone)
        return dt.astimezone(target_tz)
    except Exception:
        # Fallback: return original datetime
        return dt

def make_aware(dt: Optional[datetime], tz: Optional[str] = None) -> Optional[datetime]:
    """
    Convert a timezone-naive datetime to timezone-aware.
    If datetime is already timezone-aware, return as-is.
    If datetime is None, return None.
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # Timezone-naive datetime, make it aware
        if tz is None:
            tz = get_user_timezone()
        
        try:
            timezone_obj = zoneinfo.ZoneInfo(tz)
            return dt.replace(tzinfo=timezone_obj)
        except Exception:
            # Fallback to UTC
            return dt.replace(tzinfo=timezone.utc)
    
    # Already timezone-aware
    return dt

def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Ensure datetime is in UTC timezone.
    If timezone-naive, assume it's in user's timezone and convert to UTC.
    If timezone-aware, convert to UTC.
    If None, return None.
    """
    if dt is None:
        return None
    
    return to_utc(dt)

def format_datetime(dt: Optional[datetime], format_str: str = '%d/%m/%Y %H:%M', to_local_time: bool = True) -> str:
    """
    Safely format a datetime object for display.
    
    Args:
        dt: Datetime to format (assumed to be UTC if timezone-aware)
        format_str: strftime format string
        to_local_time: Whether to convert to user's local time before formatting
    
    Returns:
        Formatted datetime string or 'N/A' if None
    """
    if dt is None:
        return 'N/A'
    
    try:
        if to_local_time:
            # Convert UTC datetime to user's local time for display
            local_dt = to_local(dt)
            if local_dt is not None:
                return local_dt.strftime(format_str)
        else:
            # Format as-is
            if dt.tzinfo is None:
                dt = make_aware(dt)
            if dt is not None:
                return dt.strftime(format_str)
    except Exception:
        pass
    
    return 'N/A'

def format_date(dt: Optional[datetime]) -> str:
    """Format datetime as date only in user's local timezone."""
    return format_datetime(dt, '%d/%m/%Y', to_local_time=True)

def format_datetime_full(dt: Optional[datetime]) -> str:
    """Format datetime with time in user's local timezone."""
    return format_datetime(dt, '%d/%m/%Y %H:%M', to_local_time=True)

def format_datetime_iso(dt: Optional[datetime]) -> str:
    """Format datetime as ISO string in UTC."""
    if dt is None:
        return ''
    
    utc_dt = ensure_utc(dt)
    if utc_dt:
        return utc_dt.isoformat()
    return ''

def compare_datetimes(dt1: Optional[datetime], dt2: Optional[datetime]) -> Optional[int]:
    """
    Safely compare two datetime objects in UTC.
    Returns -1 if dt1 < dt2, 0 if equal, 1 if dt1 > dt2, None if either is None.
    """
    if dt1 is None or dt2 is None:
        return None
    
    # Ensure both are in UTC for comparison
    dt1_utc = ensure_utc(dt1)
    dt2_utc = ensure_utc(dt2)
    
    if dt1_utc is None or dt2_utc is None:
        return None
    
    if dt1_utc < dt2_utc:
        return -1
    elif dt1_utc > dt2_utc:
        return 1
    else:
        return 0

def is_overdue(due_date: Optional[datetime], current_time: Optional[datetime] = None) -> bool:
    """
    Check if a due date is overdue.
    Handles timezone-aware comparison safely in UTC.
    """
    if due_date is None:
        return False
    
    if current_time is None:
        current_time = now_utc()
    
    # Ensure both dates are in UTC for comparison
    due_date_utc = ensure_utc(due_date)
    current_time_utc = ensure_utc(current_time)
    
    if due_date_utc is None or current_time_utc is None:
        return False
    
    return due_date_utc < current_time_utc

def parse_user_datetime(date_str: str, format_str: str = '%Y-%m-%d %H:%M') -> Optional[datetime]:
    """
    Parse a datetime string from user input and convert to UTC.
    Assumes the input is in user's local timezone.
    
    Args:
        date_str: Date string to parse
        format_str: Expected format of the input string
    
    Returns:
        UTC datetime or None if parsing fails
    """
    if not date_str:
        return None
    
    try:
        # Parse as naive datetime (assume user's timezone)
        naive_dt = datetime.strptime(date_str, format_str)
        # Convert to UTC assuming it's in user's timezone
        return to_utc(naive_dt)
    except Exception:
        return None

def parse_user_date(date_str: str) -> Optional[datetime]:
    """Parse a date string from user input (date only) and convert to UTC."""
    return parse_user_datetime(date_str, '%Y-%m-%d')

def datetime_for_input(dt: Optional[datetime], input_type: str = 'datetime-local') -> str:
    """
    Format a UTC datetime for HTML input fields in user's local timezone.
    
    Args:
        dt: UTC datetime
        input_type: Type of HTML input ('datetime-local', 'date', 'time')
    
    Returns:
        Formatted string for input field
    """
    if dt is None:
        return ''
    
    local_dt = to_local(dt)
    if local_dt is None:
        return ''
    
    try:
        if input_type == 'datetime-local':
            return local_dt.strftime('%Y-%m-%dT%H:%M')
        elif input_type == 'date':
            return local_dt.strftime('%Y-%m-%d')
        elif input_type == 'time':
            return local_dt.strftime('%H:%M')
        else:
            return local_dt.strftime('%Y-%m-%dT%H:%M')
    except Exception:
        return ''