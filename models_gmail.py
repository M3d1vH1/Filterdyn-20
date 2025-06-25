"""
Gmail and AI Email Models for Filterdyn
Extends the existing model structure with Gmail integration
"""
from datetime import datetime, timezone
from app import db
from models import Tenant, User

class GmailAccount(db.Model):
    __tablename__ = 'gmail_accounts'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    access_token = db.Column(db.LargeBinary, nullable=False)  # Encrypted
    refresh_token = db.Column(db.LargeBinary, nullable=False)  # Encrypted
    token_expiry = db.Column(db.DateTime, nullable=False)
    sync_status = db.Column(db.String(20), default='idle')  # idle, syncing, error
    last_synced = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='gmail_accounts')
    tenant = db.relationship('Tenant', backref='gmail_accounts')
    messages = db.relationship('GmailMessage', backref='gmail_account', lazy=True)

    __table_args__ = (db.UniqueConstraint('tenant_id', 'user_id', 'email', name='_tenant_user_email_uc'),)

class GmailMessage(db.Model):
    __tablename__ = 'gmail_messages'
    id = db.Column(db.Integer, primary_key=True)
    gmail_account_id = db.Column(db.Integer, db.ForeignKey('gmail_accounts.id'), nullable=False)
    thread_id = db.Column(db.String(128), nullable=False)
    message_id = db.Column(db.String(128), nullable=False, unique=True)
    subject = db.Column(db.String(512))
    sender = db.Column(db.String(256))
    recipients = db.Column(db.Text)  # Comma-separated
    cc = db.Column(db.Text)
    bcc = db.Column(db.Text)
    snippet = db.Column(db.Text)
    body_html = db.Column(db.Text)
    body_plain = db.Column(db.Text)
    received_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)
    is_starred = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    labels = db.Column(db.JSON)  # List of label IDs
    has_attachments = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    attachments = db.relationship('GmailAttachment', backref='gmail_message', lazy=True, cascade='all, delete-orphan')
    ai_analysis = db.relationship('AIEmailAnalysis', backref='gmail_message', uselist=False)

    # Business entity links
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)

    customer = db.relationship('Customer', backref='gmail_messages')
    order = db.relationship('Order', backref='gmail_messages')
    quote = db.relationship('Quote', backref='gmail_messages')
    task = db.relationship('Task', backref='gmail_messages')

class GmailAttachment(db.Model):
    __tablename__ = 'gmail_attachments'
    id = db.Column(db.Integer, primary_key=True)
    gmail_message_id = db.Column(db.Integer, db.ForeignKey('gmail_messages.id'), nullable=False)
    attachment_id = db.Column(db.String(128), nullable=False)  # Gmail attachment ID
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(128))
    size = db.Column(db.Integer)
    content = db.Column(db.LargeBinary)  # Actual file content
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class AIEmailAnalysis(db.Model):
    __tablename__ = 'ai_email_analysis'
    id = db.Column(db.Integer, primary_key=True)
    gmail_message_id = db.Column(db.Integer, db.ForeignKey('gmail_messages.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # sentiment, intent, entities, etc.
    
    # Analysis results
    sentiment = db.Column(db.String(20))  # positive, neutral, negative
    intent = db.Column(db.String(50))     # inquiry, complaint, order, support, etc.
    entities = db.Column(db.JSON)         # Extracted entities (names, dates, amounts)
    key_info = db.Column(db.JSON)         # Key information extracted
    confidence_score = db.Column(db.Float) # AI confidence (0-1)
    
    # Response suggestions
    suggested_response = db.Column(db.Text)
    response_tone = db.Column(db.String(20))  # professional, friendly, formal
    template_suggestions = db.Column(db.JSON)  # Array of template suggestions
    
    # Learning data
    user_feedback = db.Column(db.String(20))  # helpful, not_helpful, partially_helpful
    effectiveness_score = db.Column(db.Integer)  # 1-5 rating
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tenant = db.relationship('Tenant', backref='ai_email_analyses')

class AIEmailLearningData(db.Model):
    __tablename__ = 'ai_email_learning_data'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Interaction details
    interaction_type = db.Column(db.String(50), nullable=False)  # analysis, suggestion, template
    input_data = db.Column(db.JSON)  # Original email content/context
    ai_response = db.Column(db.JSON)  # AI's response
    user_action = db.Column(db.String(50))  # accepted, modified, rejected
    
    # Performance metrics
    processing_time_ms = db.Column(db.Integer)
    tokens_used = db.Column(db.Integer)
    model_version = db.Column(db.String(20))
    
    # User feedback
    feedback_rating = db.Column(db.Integer)  # 1-5 stars
    feedback_comment = db.Column(db.Text)
    was_helpful = db.Column(db.Boolean)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    tenant = db.relationship('Tenant', backref='ai_learning_data')
    user = db.relationship('User', backref='ai_learning_data')

class GmailSync(db.Model):
    __tablename__ = 'gmail_syncs'
    id = db.Column(db.Integer, primary_key=True)
    gmail_account_id = db.Column(db.Integer, db.ForeignKey('gmail_accounts.id'), nullable=False)
    sync_type = db.Column(db.String(20), nullable=False)  # full, incremental, manual
    status = db.Column(db.String(20), nullable=False)     # running, completed, failed
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime)
    
    # Sync statistics
    messages_processed = db.Column(db.Integer, default=0)
    messages_new = db.Column(db.Integer, default=0)
    messages_updated = db.Column(db.Integer, default=0)
    attachments_downloaded = db.Column(db.Integer, default=0)
    
    # Error handling
    error_message = db.Column(db.Text)
    error_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    gmail_account = db.relationship('GmailAccount', backref='sync_history')