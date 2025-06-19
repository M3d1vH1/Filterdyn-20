from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class Tenant(db.Model):
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(50), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Settings
    logo_url = db.Column(db.String(255))
    primary_color = db.Column(db.String(7), default='#1ba3a3')
    secondary_color = db.Column(db.String(7), default='#ffffff')
    company_address = db.Column(db.Text)
    company_phone = db.Column(db.String(20))
    company_email = db.Column(db.String(100))
    
    # Relationships
    users = db.relationship('User', backref='tenant', lazy=True)
    customers = db.relationship('Customer', backref='tenant', lazy=True)
    products = db.relationship('Product', backref='tenant', lazy=True)
    quotes = db.relationship('Quote', backref='tenant', lazy=True)
    orders = db.relationship('Order', backref='tenant', lazy=True)
    tasks = db.relationship('Task', backref='tenant', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default='user')  # superadmin, admin, manager, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Profile info
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    
    # Unique constraint per tenant
    __table_args__ = (db.UniqueConstraint('tenant_id', 'username', name='_tenant_username_uc'),
                      db.UniqueConstraint('tenant_id', 'email', name='_tenant_email_uc'))
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Basic info
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    
    # Address
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    country = db.Column(db.String(50), default='Greece')
    
    # Business info
    tax_number = db.Column(db.String(20))
    industry = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    quotes = db.relationship('Quote', backref='customer', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    name_el = db.Column(db.String(100), nullable=False)
    description_en = db.Column(db.Text)
    description_el = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'), nullable=False)
    
    # Product info
    code = db.Column(db.String(50), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    name_el = db.Column(db.String(100), nullable=False)
    description_en = db.Column(db.Text)
    description_el = db.Column(db.Text)
    
    # Pricing
    unit_price = db.Column(db.Numeric(10, 2))
    cost_price = db.Column(db.Numeric(10, 2))
    unit = db.Column(db.String(20), default='piece')
    
    # Technical specs
    specifications = db.Column(db.JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Unique constraint per tenant
    __table_args__ = (db.UniqueConstraint('tenant_id', 'code', name='_tenant_product_code_uc'),)

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Quote info
    quote_number = db.Column(db.String(50), nullable=False)
    quote_type = db.Column(db.String(50), nullable=False)  # new_columns, filtration_equipment, emergency_repair, technical_analysis
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Pricing
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    tax_rate = db.Column(db.Numeric(5, 2), default=24)  # Greek VAT
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    
    # Terms
    validity_days = db.Column(db.Integer, default=30)
    delivery_days = db.Column(db.Integer, default=15)
    payment_terms = db.Column(db.String(100), default='30 days')
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, pending_approval, approved, rejected, sent, accepted, expired
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    approved_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_quotes')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_quotes')
    items = db.relationship('QuoteItem', backref='quote', lazy=True, cascade='all, delete-orphan')
    
    # Unique constraint per tenant
    __table_args__ = (db.UniqueConstraint('tenant_id', 'quote_number', name='_tenant_quote_number_uc'),)

class QuoteItem(db.Model):
    __tablename__ = 'quote_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    # Item details
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Optional product reference
    product = db.relationship('Product', backref='quote_items')

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Order info
    order_number = db.Column(db.String(50), nullable=False)
    order_type = db.Column(db.String(50), nullable=False)  # phone_order, quote_conversion
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Pricing
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    tax_rate = db.Column(db.Numeric(5, 2), default=24)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    
    # Delivery
    delivery_address = db.Column(db.Text)
    delivery_date = db.Column(db.DateTime)
    delivery_notes = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, processing, shipped, delivered, cancelled
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    creator = db.relationship('User', backref='created_orders')
    quote = db.relationship('Quote', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    # Unique constraint per tenant
    __table_args__ = (db.UniqueConstraint('tenant_id', 'order_number', name='_tenant_order_number_uc'),)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    # Item details
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Delivery status
    quantity_delivered = db.Column(db.Numeric(10, 2), default=0)
    
    # Optional product reference
    product = db.relationship('Product', backref='order_items')

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Task info
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    category = db.Column(db.String(50))  # follow_up, service_reminder, general
    
    # References
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_tasks')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_tasks')
    customer = db.relationship('Customer', backref='tasks')
    quote = db.relationship('Quote', backref='tasks')
    order = db.relationship('Order', backref='tasks')
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            now = datetime.now(timezone.utc)
            if self.due_date.tzinfo is None:
                # If due_date is naive, make it timezone-aware
                due_date_aware = self.due_date.replace(tzinfo=timezone.utc)
                return due_date_aware < now
            return self.due_date < now
        return False

class PDFTemplate(db.Model):
    __tablename__ = 'pdf_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    template_type = db.Column(db.String(50), nullable=False)  # quote, order, invoice
    is_default = db.Column(db.Boolean, default=False)
    
    # Template settings
    header_html = db.Column(db.Text)
    footer_html = db.Column(db.Text)
    css_styles = db.Column(db.Text)
    logo_position = db.Column(db.String(20), default='top-left')
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class TaskBoard(db.Model):
    __tablename__ = 'task_boards'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Board info
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    board_type = db.Column(db.String(50), default='personal')  # personal, team, project, company
    is_default = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    
    # Settings
    color_scheme = db.Column(db.String(20), default='default')
    auto_archive_days = db.Column(db.Integer, default=30)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    creator = db.relationship('User', backref='created_boards')
    columns = db.relationship('TaskColumn', backref='board', lazy=True, cascade='all, delete-orphan', order_by='TaskColumn.position')
    members = db.relationship('TaskBoardMember', backref='board', lazy=True, cascade='all, delete-orphan')

class TaskBoardMember(db.Model):
    __tablename__ = 'task_board_members'
    
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('task_boards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # owner, admin, member, viewer
    
    # Permissions
    can_create_cards = db.Column(db.Boolean, default=True)
    can_move_cards = db.Column(db.Boolean, default=True)
    can_edit_cards = db.Column(db.Boolean, default=True)
    can_delete_cards = db.Column(db.Boolean, default=False)
    can_manage_board = db.Column(db.Boolean, default=False)
    
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = db.relationship('User', backref='board_memberships')
    
    __table_args__ = (db.UniqueConstraint('board_id', 'user_id', name='_board_user_uc'),)

class TaskColumn(db.Model):
    __tablename__ = 'task_columns'
    
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('task_boards.id'), nullable=False)
    
    # Column info
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    position = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(7), default='#6c757d')
    
    # Settings
    wip_limit = db.Column(db.Integer)  # Work in Progress limit
    is_archive = db.Column(db.Boolean, default=False)
    auto_assign_status = db.Column(db.String(20))  # pending, in_progress, completed, etc.
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    cards = db.relationship('TaskCard', backref='column', lazy=True, cascade='all, delete-orphan', order_by='TaskCard.position')

class TaskCard(db.Model):
    __tablename__ = 'task_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('task_boards.id'), nullable=False)
    column_id = db.Column(db.Integer, db.ForeignKey('task_columns.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Card info
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    position = db.Column(db.Integer, nullable=False)
    
    # Task details
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    category = db.Column(db.String(50))  # follow_up, service_reminder, general, bug, feature, etc.
    story_points = db.Column(db.Integer)  # For agile estimation
    time_estimate = db.Column(db.Integer)  # Estimated hours
    
    # References
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    parent_task_id = db.Column(db.Integer, db.ForeignKey('task_cards.id'))
    
    # Status and dates
    status = db.Column(db.String(20), default='pending')  # pending, acknowledged, in_progress, review, completed, cancelled
    due_date = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # RBAC specific fields
    acknowledged_at = db.Column(db.DateTime)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Labels and tags
    labels = db.Column(db.JSON)  # Array of label objects
    tags = db.Column(db.JSON)  # Array of tag strings
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_cards')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_cards')
    acknowledger = db.relationship('User', foreign_keys=[acknowledged_by], backref='acknowledged_cards')
    customer = db.relationship('Customer', backref='task_cards')
    quote = db.relationship('Quote', backref='task_cards')
    order = db.relationship('Order', backref='task_cards')
    parent_task = db.relationship('TaskCard', remote_side=[id], backref='subtasks')
    comments = db.relationship('TaskComment', backref='card', lazy=True, cascade='all, delete-orphan', order_by='TaskComment.created_at.desc()')
    attachments = db.relationship('TaskAttachment', backref='card', lazy=True, cascade='all, delete-orphan')
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return self.due_date < datetime.now(timezone.utc)
        return False
    
    @property
    def time_spent(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() / 3600
        elif self.started_at:
            return (datetime.now(timezone.utc) - self.started_at).total_seconds() / 3600
        return 0
    
    @property
    def progress(self):
        """Calculate task progress based on status"""
        progress_map = {
            'pending': 0,
            'acknowledged': 25,
            'in_progress': 50,
            'review': 75,
            'completed': 100,
            'cancelled': 0
        }
        return progress_map.get(self.status, 0)

class TaskComment(db.Model):
    __tablename__ = 'task_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('task_cards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Comment content
    content = db.Column(db.Text, nullable=False)
    is_system_comment = db.Column(db.Boolean, default=False)  # For automated comments
    comment_type = db.Column(db.String(20), default='user')  # user, system, mention
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = db.relationship('User', backref='task_comments')

class TaskAttachment(db.Model):
    __tablename__ = 'task_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('task_cards.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # File info
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = db.relationship('User', backref='task_attachments')

class TaskLabel(db.Model):
    __tablename__ = 'task_labels'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Label info
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#6c757d')
    description = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    creator = db.relationship('User', backref='created_labels')

class TaskTemplate(db.Model):
    __tablename__ = 'task_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Template info
    name = db.Column(db.String(100), nullable=False)
    title_template = db.Column(db.String(200), nullable=False)
    description_template = db.Column(db.Text)
    estimated_time = db.Column(db.Integer)  # in hours
    category = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='medium')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    creator = db.relationship('User', backref='created_templates')
