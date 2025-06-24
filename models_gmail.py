"""
Gmail Integration Models
Separate file to avoid conflicts with existing models
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from app import db

# Gmail Integration Models
class GmailAccount(db.Model):
    __tablename__ = 'gmail_accounts'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Account info
    email_address = db.Column(db.String(120), nullable=False)
    display_name = db.Column(db.String(100))
    
    # OAuth credentials
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expiry = db.Column(db.DateTime)
    
    # Sync status
    is_active = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime)
    sync_status = db.Column(db.String(50), default='active')  # active, error, disabled
    
    # Settings
    auto_sync = db.Column(db.Boolean, default=True)
    sync_frequency = db.Column(db.Integer, default=15)  # minutes
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class EmailThread(db.Model):
    __tablename__ = 'email_threads'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    gmail_account_id = db.Column(db.Integer, db.ForeignKey('gmail_accounts.id'), nullable=False)
    
    # Thread info
    gmail_thread_id = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(500))
    participants = db.Column(db.Text)  # JSON array of email addresses
    
    # Business associations
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    
    # Thread status
    is_archived = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    last_message_date = db.Column(db.DateTime)
    message_count = db.Column(db.Integer, default=0)
    
    # AI analysis
    thread_category = db.Column(db.String(50))
    thread_sentiment = db.Column(db.String(30))
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class EmailMessage(db.Model):
    __tablename__ = 'email_messages'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    gmail_account_id = db.Column(db.Integer, db.ForeignKey('gmail_accounts.id'), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('email_threads.id'))
    
    # Gmail info
    gmail_id = db.Column(db.String(100), nullable=False)
    gmail_thread_id = db.Column(db.String(100), nullable=False)
    
    # Message content
    subject = db.Column(db.String(500))
    sender = db.Column(db.String(150))
    recipient = db.Column(db.String(500))  # Can be multiple recipients
    cc = db.Column(db.Text)
    bcc = db.Column(db.Text)
    body_text = db.Column(db.Text)
    body_html = db.Column(db.Text)
    
    # Message metadata
    received_date = db.Column(db.DateTime, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    is_draft = db.Column(db.Boolean, default=False)
    labels = db.Column(db.Text)  # JSON array of Gmail labels
    
    # AI analysis
    ai_category = db.Column(db.String(50))
    ai_intent = db.Column(db.String(50))
    ai_sentiment = db.Column(db.String(30))
    ai_priority = db.Column(db.String(20))
    ai_entities = db.Column(db.Text)  # JSON of extracted entities
    ai_summary = db.Column(db.Text)
    ai_confidence = db.Column(db.Float)
    requires_response = db.Column(db.Boolean, default=False)
    urgency_level = db.Column(db.Integer, default=1)
    
    # Business associations
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class EmailAttachment(db.Model):
    __tablename__ = 'email_attachments'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    email_message_id = db.Column(db.Integer, db.ForeignKey('email_messages.id'), nullable=False)
    
    # Attachment info
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100))
    size = db.Column(db.Integer)
    gmail_attachment_id = db.Column(db.String(100))
    
    # File storage
    attachment_data = db.Column(db.LargeBinary)  # For small files
    file_path = db.Column(db.String(500))  # For large files stored on disk
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class EmailTemplate(db.Model):
    __tablename__ = 'email_templates'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Template info
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # quote_follow_up, support_response, etc.
    subject_template = db.Column(db.String(200))
    body_template = db.Column(db.Text, nullable=False)
    
    # Template settings
    is_public = db.Column(db.Boolean, default=False)  # Available to all users in tenant
    language = db.Column(db.String(10), default='en')
    
    # Usage tracking
    usage_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class EmailAnalytics(db.Model):
    __tablename__ = 'email_analytics'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    gmail_account_id = db.Column(db.Integer, db.ForeignKey('gmail_accounts.id'), nullable=False)
    
    # Analytics period
    date = db.Column(db.Date, nullable=False)
    period_type = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    
    # Email metrics
    emails_received = db.Column(db.Integer, default=0)
    emails_sent = db.Column(db.Integer, default=0)
    response_time_avg = db.Column(db.Float)  # Average response time in hours
    
    # Category breakdown
    customer_inquiries = db.Column(db.Integer, default=0)
    quote_requests = db.Column(db.Integer, default=0)
    support_tickets = db.Column(db.Integer, default=0)
    complaints = db.Column(db.Integer, default=0)
    
    # Sentiment breakdown
    positive_emails = db.Column(db.Integer, default=0)
    neutral_emails = db.Column(db.Integer, default=0)
    negative_emails = db.Column(db.Integer, default=0)
    
    # AI performance
    ai_suggestions_made = db.Column(db.Integer, default=0)
    ai_suggestions_accepted = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class EmailAutoResponse(db.Model):
    __tablename__ = 'email_auto_responses'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Trigger conditions
    trigger_type = db.Column(db.String(50), nullable=False)  # keyword, category, sender
    trigger_value = db.Column(db.String(200), nullable=False)
    
    # Response settings
    response_template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id'))
    response_delay = db.Column(db.Integer, default=0)  # Minutes to delay response
    
    # Conditions
    is_active = db.Column(db.Boolean, default=True)
    business_hours_only = db.Column(db.Boolean, default=False)
    max_responses_per_day = db.Column(db.Integer, default=10)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))