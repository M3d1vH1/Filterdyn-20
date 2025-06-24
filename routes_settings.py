"""
Settings Management Routes
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_babel import _
from models import db
from settings_manager import SettingsManager, RBACManager, initialize_default_settings
from forms_settings import (
    BusinessSettingsForm, UISettingsForm, EmailSettingsForm, 
    SecuritySettingsForm, SystemSettingsForm, RolePermissionForm
)

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


def require_admin():
    """Decorator to require admin access"""
    if not current_user.is_authenticated or current_user.role not in ['admin', 'superadmin']:
        flash(_('Access denied. Administrator privileges required.'), 'error')
        return redirect(url_for('main.dashboard'))
    return None


@settings_bp.route('/')
@login_required
def index():
    """Settings dashboard"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    settings_manager = SettingsManager()
    rbac_manager = RBACManager()
    
    # Get overview of settings by category
    categories = ['business', 'ui', 'email', 'security', 'system']
    settings_overview = {}
    
    for category in categories:
        settings_overview[category] = settings_manager.get_category_settings(category)
    
    # Get RBAC overview
    rbac_overview = rbac_manager.get_all_permissions()
    
    return render_template('settings/index.html', 
                         settings_overview=settings_overview,
                         rbac_overview=rbac_overview)


@settings_bp.route('/business', methods=['GET', 'POST'])
@login_required
def business():
    """Business settings management"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    settings_manager = SettingsManager()
    form = BusinessSettingsForm()
    
    if form.validate_on_submit():
        # Save business settings
        settings_manager.set_setting('business', 'company_name', form.company_name.data, 'string')
        settings_manager.set_setting('business', 'default_currency', form.default_currency.data, 'string')
        settings_manager.set_setting('business', 'default_tax_rate', form.default_tax_rate.data, 'integer')
        settings_manager.set_setting('business', 'quote_validity_days', form.quote_validity_days.data, 'integer')
        settings_manager.set_setting('business', 'order_delivery_days', form.order_delivery_days.data, 'integer')
        
        flash(_('Business settings updated successfully.'), 'success')
        return redirect(url_for('settings.business'))
    
    # Load current settings
    business_settings = settings_manager.get_category_settings('business')
    if business_settings:
        form.company_name.data = business_settings.get('company_name', {}).get('value', 'Filterdyn')
        form.default_currency.data = business_settings.get('default_currency', {}).get('value', 'EUR')
        form.default_tax_rate.data = business_settings.get('default_tax_rate', {}).get('value', 24)
        form.quote_validity_days.data = business_settings.get('quote_validity_days', {}).get('value', 30)
        form.order_delivery_days.data = business_settings.get('order_delivery_days', {}).get('value', 15)
    
    return render_template('settings/business.html', form=form)


@settings_bp.route('/ui', methods=['GET', 'POST'])
@login_required
def ui():
    """UI settings management"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    settings_manager = SettingsManager()
    form = UISettingsForm()
    
    if form.validate_on_submit():
        # Save UI settings
        settings_manager.set_setting('ui', 'items_per_page', form.items_per_page.data, 'integer')
        settings_manager.set_setting('ui', 'default_language', form.default_language.data, 'string')
        settings_manager.set_setting('ui', 'theme_primary_color', form.theme_primary_color.data, 'string')
        settings_manager.set_setting('ui', 'theme_secondary_color', form.theme_secondary_color.data, 'string')
        settings_manager.set_setting('ui', 'enable_dark_mode', form.enable_dark_mode.data, 'boolean')
        
        flash(_('UI settings updated successfully.'), 'success')
        return redirect(url_for('settings.ui'))
    
    # Load current settings
    ui_settings = settings_manager.get_category_settings('ui')
    if ui_settings:
        form.items_per_page.data = ui_settings.get('items_per_page', {}).get('value', 20)
        form.default_language.data = ui_settings.get('default_language', {}).get('value', 'en')
        form.theme_primary_color.data = ui_settings.get('theme_primary_color', {}).get('value', '#1ba3a3')
        form.theme_secondary_color.data = ui_settings.get('theme_secondary_color', {}).get('value', '#ffffff')
        form.enable_dark_mode.data = ui_settings.get('enable_dark_mode', {}).get('value', False)
    
    return render_template('settings/ui.html', form=form)


@settings_bp.route('/email', methods=['GET', 'POST'])
@login_required
def email():
    """Email settings management"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    settings_manager = SettingsManager()
    form = EmailSettingsForm()
    
    if form.validate_on_submit():
        # Save email settings
        settings_manager.set_setting('email', 'smtp_enabled', form.smtp_enabled.data, 'boolean')
        settings_manager.set_setting('email', 'smtp_server', form.smtp_server.data, 'string', is_sensitive=True)
        settings_manager.set_setting('email', 'smtp_port', form.smtp_port.data, 'integer')
        settings_manager.set_setting('email', 'smtp_username', form.smtp_username.data, 'string', is_sensitive=True)
        if form.smtp_password.data:  # Only update password if provided
            settings_manager.set_setting('email', 'smtp_password', form.smtp_password.data, 'string', is_sensitive=True)
        settings_manager.set_setting('email', 'from_email', form.from_email.data, 'string')
        
        flash(_('Email settings updated successfully.'), 'success')
        return redirect(url_for('settings.email'))
    
    # Load current settings
    email_settings = settings_manager.get_category_settings('email')
    if email_settings:
        form.smtp_enabled.data = email_settings.get('smtp_enabled', {}).get('value', False)
        form.smtp_server.data = email_settings.get('smtp_server', {}).get('value', '')
        form.smtp_port.data = email_settings.get('smtp_port', {}).get('value', 587)
        form.smtp_username.data = email_settings.get('smtp_username', {}).get('value', '')
        form.from_email.data = email_settings.get('from_email', {}).get('value', '')
    
    return render_template('settings/email.html', form=form)


@settings_bp.route('/security', methods=['GET', 'POST'])
@login_required
def security():
    """Security settings management"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    settings_manager = SettingsManager()
    form = SecuritySettingsForm()
    
    if form.validate_on_submit():
        # Save security settings
        settings_manager.set_setting('security', 'session_timeout', form.session_timeout.data, 'integer')
        settings_manager.set_setting('security', 'password_min_length', form.password_min_length.data, 'integer')
        settings_manager.set_setting('security', 'require_password_change', form.require_password_change.data, 'boolean')
        settings_manager.set_setting('security', 'max_login_attempts', form.max_login_attempts.data, 'integer')
        
        flash(_('Security settings updated successfully.'), 'success')
        return redirect(url_for('settings.security'))
    
    # Load current settings
    security_settings = settings_manager.get_category_settings('security')
    if security_settings:
        form.session_timeout.data = security_settings.get('session_timeout', {}).get('value', 30)
        form.password_min_length.data = security_settings.get('password_min_length', {}).get('value', 6)
        form.require_password_change.data = security_settings.get('require_password_change', {}).get('value', False)
        form.max_login_attempts.data = security_settings.get('max_login_attempts', {}).get('value', 5)
    
    return render_template('settings/security.html', form=form)


@settings_bp.route('/rbac')
@login_required
def rbac():
    """RBAC permissions management"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    rbac_manager = RBACManager()
    permissions = rbac_manager.get_all_permissions()
    
    return render_template('settings/rbac.html', permissions=permissions)


@settings_bp.route('/initialize')
@login_required
def initialize():
    """Initialize default settings"""
    if current_user.role != 'superadmin':
        flash(_('Access denied. Super administrator privileges required.'), 'error')
        return redirect(url_for('settings.index'))
    
    try:
        initialize_default_settings(current_user.tenant_id)
        flash(_('Default settings initialized successfully.'), 'success')
    except Exception as e:
        flash(_('Error initializing settings: %(error)s', error=str(e)), 'error')
    
    return redirect(url_for('settings.index'))