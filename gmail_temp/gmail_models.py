from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from app import db

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
    business_links = db.relationship('GmailBusinessAssociation', backref='gmail_message', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (db.Index('ix_gmail_account_thread', 'gmail_account_id', 'thread_id'),)

class GmailAttachment(db.Model):
    __tablename__ = 'gmail_attachments'
    id = db.Column(db.Integer, primary_key=True)
    gmail_message_id = db.Column(db.Integer, db.ForeignKey('gmail_messages.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100))
    file_data = db.Column(db.LargeBinary, nullable=False)
    file_size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class GmailLabel(db.Model):
    __tablename__ = 'gmail_labels'
    id = db.Column(db.Integer, primary_key=True)
    gmail_account_id = db.Column(db.Integer, db.ForeignKey('gmail_accounts.id'), nullable=False)
    label_id = db.Column(db.String(128), nullable=False)  # Gmail label ID
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(32), default='system')  # system, user, business
    color = db.Column(db.String(7))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('gmail_account_id', 'label_id', name='_account_label_uc'),)

class GmailBusinessAssociation(db.Model):
    __tablename__ = 'gmail_business_associations'
    id = db.Column(db.Integer, primary_key=True)
    gmail_message_id = db.Column(db.Integer, db.ForeignKey('gmail_messages.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    association_type = db.Column(db.String(32))  # customer, order, quote, task
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    customer = db.relationship('Customer', backref='gmail_links')
    order = db.relationship('Order', backref='gmail_links')
    quote = db.relationship('Quote', backref='gmail_links')
    task = db.relationship('Task', backref='gmail_links')

class AIEmailLearningData(db.Model):
    __tablename__ = 'ai_email_learning_data'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gmail_message_id = db.Column(db.Integer, db.ForeignKey('gmail_messages.id'))
    input_text = db.Column(db.Text, nullable=False)
    ai_suggestion = db.Column(db.Text)
    user_feedback = db.Column(db.String(32))  # accepted, edited, rejected
    effectiveness_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='ai_email_learning')
    tenant = db.relationship('Tenant', backref='ai_email_learning')
    gmail_message = db.relationship('GmailMessage', backref='ai_learning_data') 