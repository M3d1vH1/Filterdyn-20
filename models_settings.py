"""
Settings Models for API Keys and System Configuration
====================================================
"""

from app import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import json


class SystemSetting(db.Model):
    """System-wide settings and API keys"""
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Setting identification
    setting_key = db.Column(db.String(100), nullable=False)
    setting_category = db.Column(db.String(50), nullable=False)  # api_keys, general, integrations
    
    # Setting value (encrypted for sensitive data)
    setting_value = db.Column(db.Text)
    is_encrypted = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadata
    description = db.Column(db.Text)
    default_value = db.Column(db.Text)
    validation_pattern = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'setting_key', name='unique_tenant_setting'),
    )

    def set_encrypted_value(self, value):
        """Set encrypted value for sensitive settings like API keys"""
        if value:
            self.setting_value = generate_password_hash(value)
            self.is_encrypted = True
        else:
            self.setting_value = None
            self.is_encrypted = False

    def check_value(self, value):
        """Check if provided value matches encrypted value"""
        if self.is_encrypted and self.setting_value:
            return check_password_hash(self.setting_value, value)
        return self.setting_value == value

    @classmethod
    def get_setting(cls, tenant_id, key, default=None):
        """Get setting value for tenant"""
        setting = cls.query.filter_by(tenant_id=tenant_id, setting_key=key, is_active=True).first()
        if setting:
            return setting.setting_value if not setting.is_encrypted else None
        return default

    @classmethod
    def set_setting(cls, tenant_id, key, value, category='general', description=None, user_id=None, encrypt=False):
        """Set setting value for tenant"""
        setting = cls.query.filter_by(tenant_id=tenant_id, setting_key=key).first()
        
        if not setting:
            setting = cls(
                tenant_id=tenant_id,
                setting_key=key,
                setting_category=category,
                description=description
            )
            db.session.add(setting)
        
        if encrypt:
            setting.set_encrypted_value(value)
        else:
            setting.setting_value = value
            setting.is_encrypted = False
        
        setting.updated_by = user_id
        setting.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        return setting


class AgentConfiguration(db.Model):
    """Configuration for AI agents"""
    __tablename__ = 'agent_configurations'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    agent_name = db.Column(db.String(100), nullable=False)  # communication_ai, operations_data, etc.
    is_enabled = db.Column(db.Boolean, default=True)
    
    # Configuration as JSON
    configuration = db.Column(db.JSON)
    
    # Scheduling
    auto_run_enabled = db.Column(db.Boolean, default=False)
    run_interval_minutes = db.Column(db.Integer, default=60)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'agent_name', name='unique_tenant_agent'),
    )

    @classmethod
    def get_agent_config(cls, tenant_id, agent_name):
        """Get agent configuration"""
        return cls.query.filter_by(tenant_id=tenant_id, agent_name=agent_name).first()

    def get_config_value(self, key, default=None):
        """Get specific configuration value"""
        if self.configuration and isinstance(self.configuration, dict):
            return self.configuration.get(key, default)
        return default


class APIKeyConfiguration(db.Model):
    """Configuration for API keys and external services"""
    __tablename__ = 'api_key_configurations'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    service_name = db.Column(db.String(100), nullable=False)  # gemini, gmail, twilio, etc.
    is_configured = db.Column(db.Boolean, default=False)
    
    # Configuration as JSON (without actual API keys)
    configuration = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'service_name', name='unique_tenant_service'),
    )

    @classmethod
    def get_config(cls, tenant_id, service_name):
        """Get API key configuration"""
        return cls.query.filter_by(tenant_id=tenant_id, service_name=service_name).first()

    def get_config_value(self, key, default=None):
        """Get specific configuration value"""
        if self.configuration and isinstance(self.configuration, dict):
            return self.configuration.get(key, default)
        return default

    def set_config_value(self, key, value):
        """Set specific configuration value"""
        if not self.configuration:
            self.configuration = {}
        self.configuration[key] = value
        db.session.commit()