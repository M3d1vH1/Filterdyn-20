"""
Timezone utilities for consistent datetime handling across the application.
This module provides functions to standardize timezone handling and prevent
timezone-naive/timezone-aware comparison errors.
"""

from datetime import datetime, timezone
from typing import Optional, Union
import pytz

# Application default timezone (can be configured via environment)
DEFAULT_TIMEZONE = timezone.utc

def now_utc() -> datetime:
    """Get current datetime in UTC timezone."""
    return datetime.now(timezone.utc)

def make_aware(dt: Optional[datetime], tz: Optional[timezone] = None) -> Optional[datetime]:
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
            tz = DEFAULT_TIMEZONE
        return dt.replace(tzinfo=tz)
    
    # Already timezone-aware
    return dt

def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Ensure datetime is in UTC timezone.
    If timezone-naive, assume it's UTC.
    If timezone-aware, convert to UTC.
    If None, return None.
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        return dt.replace(tzinfo=timezone.utc)
    
    # Convert to UTC if not already
    return dt.astimezone(timezone.utc)

def format_datetime(dt: Optional[datetime], format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Safely format a datetime object.
    Returns 'N/A' if datetime is None.
    """
    if dt is None:
        return 'N/A'
    
    # Ensure timezone-aware
    dt = make_aware(dt)
    if dt is not None:
        return dt.strftime(format_str)
    return 'N/A'

def compare_datetimes(dt1: Optional[datetime], dt2: Optional[datetime]) -> Optional[int]:
    """
    Safely compare two datetime objects.
    Returns -1 if dt1 < dt2, 0 if equal, 1 if dt1 > dt2, None if either is None.
    """
    if dt1 is None or dt2 is None:
        return None
    
    # Ensure both are timezone-aware
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
    Handles timezone-aware comparison safely.
    """
    if due_date is None:
        return False
    
    if current_time is None:
        current_time = now_utc()
    
    # Ensure both dates are timezone-aware for comparison
    due_date_utc = ensure_utc(due_date)
    current_time_utc = ensure_utc(current_time)
    
    if due_date_utc is None or current_time_utc is None:
        return False
    
    return due_date_utc < current_time_utc