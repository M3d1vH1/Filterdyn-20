from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, IntegerField, BooleanField, DateTimeField, PasswordField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange
from flask_babel import lazy_gettext as _l

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))

class UserForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[Optional(), Length(min=6)])
    role = SelectField(_l('Role'), choices=[
        ('user', _l('User')),
        ('manager', _l('Manager')),
        ('admin', _l('Admin'))
    ], validators=[DataRequired()])
    first_name = StringField(_l('First Name'), validators=[Optional(), Length(max=50)])
    last_name = StringField(_l('Last Name'), validators=[Optional(), Length(max=50)])
    phone = StringField(_l('Phone'), validators=[Optional(), Length(max=20)])
    is_active = BooleanField(_l('Active'), default=True)

class CustomerForm(FlaskForm):
    name = StringField(_l('Company Name'), validators=[DataRequired(), Length(max=100)])
    contact_person = StringField(_l('Contact Person'), validators=[Optional(), Length(max=100)])
    email = StringField(_l('Email'), validators=[Optional(), Email(), Length(max=120)])
    phone = StringField(_l('Phone'), validators=[Optional(), Length(max=20)])
    mobile = StringField(_l('Mobile'), validators=[Optional(), Length(max=20)])
    address = TextAreaField(_l('Address'), validators=[Optional()])
    city = StringField(_l('City'), validators=[Optional(), Length(max=50)])
    postal_code = StringField(_l('Postal Code'), validators=[Optional(), Length(max=10)])
    country = StringField(_l('Country'), validators=[Optional(), Length(max=50)], default='Greece')
    tax_number = StringField(_l('Tax Number'), validators=[Optional(), Length(max=20)])
    industry = StringField(_l('Industry'), validators=[Optional(), Length(max=50)])
    notes = TextAreaField(_l('Notes'), validators=[Optional()])

class ProductCategoryForm(FlaskForm):
    name_en = StringField(_l('Name (English)'), validators=[DataRequired(), Length(max=100)])
    name_el = StringField(_l('Name (Greek)'), validators=[DataRequired(), Length(max=100)])
    description_en = TextAreaField(_l('Description (English)'), validators=[Optional()])
    description_el = TextAreaField(_l('Description (Greek)'), validators=[Optional()])

class ProductForm(FlaskForm):
    category_id = SelectField(_l('Category'), coerce=int, validators=[DataRequired()])
    code = StringField(_l('Product Code'), validators=[DataRequired(), Length(max=50)])
    name_en = StringField(_l('Name (English)'), validators=[DataRequired(), Length(max=100)])
    name_el = StringField(_l('Name (Greek)'), validators=[DataRequired(), Length(max=100)])
    description_en = TextAreaField(_l('Description (English)'), validators=[Optional()])
    description_el = TextAreaField(_l('Description (Greek)'), validators=[Optional()])
    unit_price = DecimalField(_l('Unit Price'), validators=[Optional(), NumberRange(min=0)], places=2)
    cost_price = DecimalField(_l('Cost Price'), validators=[Optional(), NumberRange(min=0)], places=2)
    unit = StringField(_l('Unit'), validators=[Optional(), Length(max=20)], default='piece')
    specifications = TextAreaField(_l('Specifications (JSON)'), validators=[Optional()])

class QuoteForm(FlaskForm):
    customer_id = SelectField(_l('Customer'), coerce=int, validators=[DataRequired()])
    quote_type = SelectField(_l('Quote Type'), choices=[
        ('new_columns', _l('New Columns')),
        ('filtration_equipment', _l('Filtration Equipment')),
        ('emergency_repair', _l('Emergency Repair')),
        ('technical_analysis', _l('Technical Analysis'))
    ], validators=[DataRequired()])
    title = StringField(_l('Title'), validators=[DataRequired(), Length(max=200)])
    description = TextAreaField(_l('Description'), validators=[Optional()])
    validity_days = IntegerField(_l('Validity (Days)'), validators=[DataRequired(), NumberRange(min=1)], default=30)
    delivery_days = IntegerField(_l('Delivery (Days)'), validators=[DataRequired(), NumberRange(min=1)], default=15)
    payment_terms = StringField(_l('Payment Terms'), validators=[DataRequired(), Length(max=100)], default='30 days')
    tax_rate = DecimalField(_l('Tax Rate (%)'), validators=[DataRequired(), NumberRange(min=0, max=100)], default=24, places=2)

class OrderForm(FlaskForm):
    customer_id = SelectField(_l('Customer'), coerce=int, validators=[DataRequired()])
    quote_id = SelectField(_l('Quote (Optional)'), coerce=int, validators=[Optional()])
    order_type = SelectField(_l('Order Type'), choices=[
        ('phone_order', _l('Phone Order')),
        ('quote_conversion', _l('Quote Conversion'))
    ], validators=[DataRequired()])
    title = StringField(_l('Title'), validators=[DataRequired(), Length(max=200)])
    description = TextAreaField(_l('Description'), validators=[Optional()])
    delivery_address = TextAreaField(_l('Delivery Address'), validators=[Optional()])
    delivery_date = DateTimeField(_l('Delivery Date'), validators=[Optional()], format='%Y-%m-%d')
    delivery_notes = TextAreaField(_l('Delivery Notes'), validators=[Optional()])

class TaskForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired(), Length(max=200)])
    description = TextAreaField(_l('Description'), validators=[Optional()])
    status = SelectField(_l('Status'), choices=[
        ('pending', _l('Pending')),
        ('in_progress', _l('In Progress')),
        ('completed', _l('Completed')),
        ('cancelled', _l('Cancelled'))
    ], validators=[DataRequired()], default='pending')
    priority = SelectField(_l('Priority'), choices=[
        ('low', _l('Low')),
        ('medium', _l('Medium')),
        ('high', _l('High')),
        ('urgent', _l('Urgent'))
    ], validators=[DataRequired()], default='medium')
    category = SelectField(_l('Category'), choices=[
        ('follow_up', _l('Follow Up')),
        ('service_reminder', _l('Service Reminder')),
        ('general', _l('General'))
    ], validators=[DataRequired()], default='general')
    assigned_to = SelectField(_l('Assigned To'), coerce=int, validators=[DataRequired()])
    customer_id = SelectField(_l('Customer (Optional)'), coerce=int, validators=[Optional()])
    due_date = DateTimeField(_l('Due Date'), validators=[Optional()], format='%Y-%m-%dT%H:%M')
    notes = TextAreaField(_l('Notes'), validators=[Optional()])
