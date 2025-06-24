from datetime import datetime, timezone
from app import db

class GmailAccount(db.Model):
    __tablename__ = 'gmail_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    email_address = db.Column(db.String(255), nullable=False)
    google_user_id = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.LargeBinary, nullable=False)  # Encrypted
    refresh_token = db.Column(db.LargeBinary, nullable=False)  # Encrypted
    token_expires_at = db.Column(db.DateTime)
    
    # Account settings
    is_primary = db.Column(db.Boolean, default=False)
    sync_enabled = db.Column(db.Boolean, default=True)
    last_sync_at = db.Column(db.DateTime)
    sync_history_token = db.Column(db.String(255))
    
    # Filters and preferences
    auto_categorize = db.Column(db.Boolean, default=True)
    ai_suggestions_enabled = db.Column(db.Boolean, default=True)
    smart_replies_enabled = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = db.relationship('User', backref='gmail_accounts')
    tenant = db.relationship('Tenant', backref='gmail_accounts')
    email_threads = db.relationship('EmailThread', backref='gmail_account', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'user_id', 'email_address', name='_tenant_user_email_uc'),
    )

class EmailThread(db.Model):
    __tablename__ = 'email_threads'
    
    id = db.Column(db.Integer, primary_key=True)
    gmail_account_id = db.Column(db.Integer, db.ForeignKey('gmail_accounts.id'), nullable=False)
    thread_id = db.Column(db.String(128), nullable=False)
    subject = db.Column(db.String(512))
    participants = db.Column(db.Text)  # JSON array of participants
    message_count = db.Column(db.Integer, default=0)
    has_attachments = db.Column(db.Boolean, default=False)
    last_message_at = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)
    is_starred = db.Column(db.Boolean, default=False)
    labels = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    messages = db.relationship('EmailMessage', backref='thread', lazy=True, cascade='all, delete-orphan')
    business_links = db.relationship('EmailBusinessAssociation', backref='thread', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('gmail_account_id', 'thread_id', name='_account_thread_uc'),
        db.Index('ix_thread_account_updated', 'gmail_account_id', 'updated_at'),
    )

class EmailMessage(db.Model):
    __tablename__ = 'email_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('email_threads.id'), nullable=False)
    message_id = db.Column(db.String(128), nullable=False, unique=True)
    
    subject = db.Column(db.String(512))
    sender_name = db.Column(db.String(255))
    sender_email = db.Column(db.String(255))
    recipients = db.Column(db.Text)  # JSON array
    cc_recipients = db.Column(db.Text)  # JSON array
    bcc_recipients = db.Column(db.Text)  # JSON array
    
    snippet = db.Column(db.Text)
    body_html = db.Column(db.Text)
    body_plain = db.Column(db.Text)
    
    sent_at = db.Column(db.DateTime)
    received_at = db.Column(db.DateTime)
    
    is_read = db.Column(db.Boolean, default=False)
    is_starred = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    is_draft = db.Column(db.Boolean, default=False)
    
    labels = db.Column(db.JSON)
    has_attachments = db.Column(db.Boolean, default=False)
    
    # AI Analysis fields
    ai_analyzed = db.Column(db.Boolean, default=False)
    ai_sentiment = db.Column(db.String(50))
    ai_intent = db.Column(db.String(100))
    ai_entities = db.Column(db.JSON)
    ai_summary = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    attachments = db.relationship('EmailAttachment', backref='message', lazy=True, cascade='all, delete-orphan')
    ai_interactions = db.relationship('AIEmailInteraction', backref='message', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('ix_message_thread_sent', 'thread_id', 'sent_at'),
        db.Index('ix_message_sender', 'sender_email'),
    )

class EmailAttachment(db.Model):
    __tablename__ = 'email_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('email_messages.id'), nullable=False)
    
    attachment_id = db.Column(db.String(128))  # Gmail attachment ID
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)
    file_data = db.Column(db.LargeBinary)  # Stored locally for offline access
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class EmailBusinessAssociation(db.Model):
    __tablename__ = 'email_business_associations'
    
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('email_threads.id'), nullable=False)
    
    # Link to business entities
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    
    association_type = db.Column(db.String(32))  # customer, order, quote, task
    confidence_score = db.Column(db.Float)  # AI confidence in association
    manual_override = db.Column(db.Boolean, default=False)  # User manually set
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    customer = db.relationship('Customer', backref='email_links')
    order = db.relationship('Order', backref='email_links')
    quote = db.relationship('Quote', backref='email_links')
    task = db.relationship('Task', backref='email_links')
    creator = db.relationship('User', backref='email_associations_created')

class AIEmailInteraction(db.Model):
    __tablename__ = 'ai_email_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('email_messages.id'))
    
    interaction_type = db.Column(db.String(50), nullable=False)  # analysis, suggestion, template
    input_data = db.Column(db.JSON)
    ai_response = db.Column(db.Text)
    user_feedback = db.Column(db.String(32))  # accepted, edited, rejected
    effectiveness_score = db.Column(db.Float)
    
    processing_time_ms = db.Column(db.Integer)
    tokens_used = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = db.relationship('User', backref='ai_email_interactions')
    tenant = db.relationship('Tenant', backref='ai_email_interactions')

class EmailLabel(db.Model):
    __tablename__ = 'email_labels'
    
    id = db.Column(db.Integer, primary_key=True)
    gmail_account_id = db.Column(db.Integer, db.ForeignKey('gmail_accounts.id'), nullable=False)
    
    label_id = db.Column(db.String(128), nullable=False)  # Gmail label ID
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(32), default='system')  # system, user, business
    color = db.Column(db.String(7))
    messages_total = db.Column(db.Integer, default=0)
    messages_unread = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.UniqueConstraint('gmail_account_id', 'label_id', name='_account_label_uc'),
    )