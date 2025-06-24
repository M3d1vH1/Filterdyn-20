"""
Forms for Settings Management
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SelectField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, Email
from flask_babel import lazy_gettext as _l


class BusinessSettingsForm(FlaskForm):
    company_name = StringField(_l('Company Name'), validators=[DataRequired(), Length(max=100)])
    default_currency = SelectField(_l('Default Currency'), choices=[
        ('EUR', 'Euro (EUR)'),
        ('USD', 'US Dollar (USD)'),
        ('GBP', 'British Pound (GBP)')
    ], validators=[DataRequired()])
    default_tax_rate = IntegerField(_l('Default Tax Rate (%)'), validators=[DataRequired(), NumberRange(min=0, max=100)])
    quote_validity_days = IntegerField(_l('Quote Validity (Days)'), validators=[DataRequired(), NumberRange(min=1, max=365)])
    order_delivery_days = IntegerField(_l('Default Delivery (Days)'), validators=[DataRequired(), NumberRange(min=1, max=365)])


class UISettingsForm(FlaskForm):
    items_per_page = IntegerField(_l('Items Per Page'), validators=[DataRequired(), NumberRange(min=5, max=100)])
    default_language = SelectField(_l('Default Language'), choices=[
        ('en', 'English'),
        ('el', 'Ελληνικά')
    ], validators=[DataRequired()])
    theme_primary_color = StringField(_l('Primary Color'), validators=[DataRequired(), Length(max=7)])
    theme_secondary_color = StringField(_l('Secondary Color'), validators=[DataRequired(), Length(max=7)])
    enable_dark_mode = BooleanField(_l('Enable Dark Mode'))


class EmailSettingsForm(FlaskForm):
    smtp_enabled = BooleanField(_l('Enable Email Notifications'))
    smtp_server = StringField(_l('SMTP Server'), validators=[Optional(), Length(max=255)])
    smtp_port = IntegerField(_l('SMTP Port'), validators=[Optional(), NumberRange(min=1, max=65535)], default=587)
    smtp_username = StringField(_l('SMTP Username'), validators=[Optional(), Length(max=255)])
    smtp_password = PasswordField(_l('SMTP Password'), validators=[Optional()])
    from_email = StringField(_l('From Email'), validators=[Optional(), Email(), Length(max=255)])


class SecuritySettingsForm(FlaskForm):
    session_timeout = IntegerField(_l('Session Timeout (Minutes)'), validators=[DataRequired(), NumberRange(min=5, max=480)])
    password_min_length = IntegerField(_l('Minimum Password Length'), validators=[DataRequired(), NumberRange(min=4, max=50)])
    require_password_change = BooleanField(_l('Require Password Change on First Login'))
    max_login_attempts = IntegerField(_l('Max Login Attempts'), validators=[DataRequired(), NumberRange(min=1, max=20)])


class SystemSettingsForm(FlaskForm):
    backup_enabled = BooleanField(_l('Enable Automatic Backups'))
    backup_frequency = SelectField(_l('Backup Frequency'), choices=[
        ('daily', _l('Daily')),
        ('weekly', _l('Weekly')),
        ('monthly', _l('Monthly'))
    ], validators=[DataRequired()])
    debug_mode = BooleanField(_l('Debug Mode'))
    maintenance_mode = BooleanField(_l('Maintenance Mode'))


class RolePermissionForm(FlaskForm):
    role = SelectField(_l('Role'), choices=[
        ('user', _l('User')),
        ('manager', _l('Manager')),
        ('admin', _l('Admin')),
        ('superadmin', _l('Super Admin'))
    ], validators=[DataRequired()])
    resource = SelectField(_l('Resource'), choices=[
        ('customers', _l('Customers')),
        ('products', _l('Products')),
        ('quotes', _l('Quotes')),
        ('orders', _l('Orders')),
        ('tasks', _l('Tasks')),
        ('users', _l('Users')),
        ('settings', _l('Settings')),
        ('system', _l('System'))
    ], validators=[DataRequired()])
    permission = SelectField(_l('Permission'), choices=[
        ('create', _l('Create')),
        ('read', _l('Read')),
        ('update', _l('Update')),
        ('delete', _l('Delete')),
        ('approve', _l('Approve')),
        ('export', _l('Export'))
    ], validators=[DataRequired()])
    granted = BooleanField(_l('Granted'), default=True)