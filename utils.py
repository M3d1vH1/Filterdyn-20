from functools import wraps
from flask import abort, request, url_for
from flask_login import current_user
from flask_babel import get_locale
import os

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'superadmin']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['manager', 'admin', 'superadmin']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'superadmin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_next_number(model_class, tenant_id, prefix=''):
    """Generate next sequential number for quotes, orders, etc."""
    from datetime import datetime
    year = datetime.now().year
    
    last_record = model_class.query.filter_by(tenant_id=tenant_id).order_by(model_class.id.desc()).first()
    number = (last_record.id + 1) if last_record else 1
    
    return f"{prefix}{year}{number:04d}"

def format_currency(amount, currency='€'):
    """Format currency amount"""
    if amount is None:
        return f"0.00 {currency}"
    return f"{amount:,.2f} {currency}"

def format_date(date, format='medium'):
    """Format date according to locale"""
    if not date:
        return ''
    
    from babel.dates import format_datetime
    locale = get_locale()
    
    try:
        if format == 'short':
            return format_datetime(date, 'short', locale=locale)
        elif format == 'medium':
            return format_datetime(date, 'medium', locale=locale)
        elif format == 'long':
            return format_datetime(date, 'long', locale=locale)
        else:
            return format_datetime(date, format, locale=locale)
    except (ValueError, TypeError):
        return ''

def safe_datetime_format(dt, format_str='%Y-%m-%d %H:%M'):
    """Safely format datetime, returning empty string if None or invalid"""
    if dt is None:
        return ''
    try:
        return dt.strftime(format_str)
    except (AttributeError, ValueError):
        return ''

def safe_date_format(dt, format_str='%Y-%m-%d'):
    """Safely format date, returning empty string if None or invalid"""
    if dt is None:
        return ''
    try:
        if hasattr(dt, 'date'):
            return dt.date().strftime(format_str)
        return dt.strftime(format_str)
    except (AttributeError, ValueError):
        return ''

def get_status_badge_class(status):
    """Get Bootstrap badge class for status"""
    status_classes = {
        'draft': 'bg-secondary',
        'pending': 'bg-warning',
        'pending_approval': 'bg-warning',
        'approved': 'bg-success',
        'rejected': 'bg-danger',
        'sent': 'bg-info',
        'accepted': 'bg-success',
        'expired': 'bg-dark',
        'completed': 'bg-success',
        'cancelled': 'bg-danger',
        'in_progress': 'bg-primary',
        'confirmed': 'bg-success',
        'processing': 'bg-info',
        'shipped': 'bg-primary',
        'delivered': 'bg-success'
    }
    return status_classes.get(status, 'bg-secondary')

def get_priority_badge_class(priority):
    """Get Bootstrap badge class for priority"""
    priority_classes = {
        'low': 'bg-secondary',
        'medium': 'bg-info',
        'high': 'bg-warning',
        'urgent': 'bg-danger'
    }
    return priority_classes.get(priority, 'bg-secondary')

def generate_pdf_quote(quote):
    """Generate PDF for quote"""
    from pdf_generator import QuotePDFGenerator
    generator = QuotePDFGenerator()
    return generator.generate(quote)

def allowed_file(filename, allowed_extensions={'png', 'jpg', 'jpeg', 'gif', 'pdf'}):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def secure_filename(filename):
    """Secure filename for upload"""
    import re
    filename = re.sub(r'[^\w\s-]', '', filename).strip()
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename

def pagination_links(pagination, endpoint, **kwargs):
    """Generate pagination links"""
    links = []
    
    # Previous page
    if pagination.has_prev:
        links.append({
            'url': url_for(endpoint, page=pagination.prev_num, **kwargs),
            'text': '‹',
            'class': ''
        })
    
    # Page numbers
    for page in pagination.iter_pages():
        if page:
            if page != pagination.page:
                links.append({
                    'url': url_for(endpoint, page=page, **kwargs),
                    'text': str(page),
                    'class': ''
                })
            else:
                links.append({
                    'url': '#',
                    'text': str(page),
                    'class': 'active'
                })
        else:
            links.append({
                'url': '#',
                'text': '…',
                'class': 'disabled'
            })
    
    # Next page
    if pagination.has_next:
        links.append({
            'url': url_for(endpoint, page=pagination.next_num, **kwargs),
            'text': '›',
            'class': ''
        })
    
    return links
