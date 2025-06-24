"""
Settings Manager for Filterdyn Operations Suite
Centralized management of application settings and RBAC permissions
"""

import json
from typing import Any, Dict, List, Optional
from flask import current_app, session
from flask_login import current_user
from models import db, ApplicationSetting, RolePermission
from sqlalchemy.exc import IntegrityError


class SettingsManager:
    """Centralized settings management with caching and type safety"""
    
    def __init__(self, tenant_id: int = None):
        self.tenant_id = tenant_id or self._get_current_tenant_id()
        self._cache = {}
    
    def _get_current_tenant_id(self) -> int:
        """Get current tenant ID from user session or current_user"""
        if current_user and current_user.is_authenticated:
            return current_user.tenant_id
        return session.get('tenant_id', 1)  # Default to tenant 1
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get a setting value with proper type conversion"""
        cache_key = f"{category}.{key}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        setting = ApplicationSetting.query.filter_by(
            tenant_id=self.tenant_id,
            category=category,
            key=key
        ).first()
        
        if setting:
            value = setting.get_typed_value()
            self._cache[cache_key] = value
            return value
        
        return default
    
    def set_setting(self, category: str, key: str, value: Any, 
                   value_type: str = 'string', description: str = '',
                   is_sensitive: bool = False) -> bool:
        """Set a setting value with proper type conversion"""
        try:
            setting = ApplicationSetting.query.filter_by(
                tenant_id=self.tenant_id,
                category=category,
                key=key
            ).first()
            
            if setting:
                setting.set_typed_value(value)
                setting.value_type = value_type
                setting.description = description
                setting.is_sensitive = is_sensitive
            else:
                setting = ApplicationSetting(
                    tenant_id=self.tenant_id,
                    category=category,
                    key=key,
                    value_type=value_type,
                    description=description,
                    is_sensitive=is_sensitive
                )
                setting.set_typed_value(value)
                db.session.add(setting)
            
            db.session.commit()
            
            # Update cache
            cache_key = f"{category}.{key}"
            self._cache[cache_key] = value
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error setting {category}.{key}: {e}")
            return False
    
    def get_category_settings(self, category: str) -> Dict[str, Any]:
        """Get all settings for a category"""
        settings = ApplicationSetting.query.filter_by(
            tenant_id=self.tenant_id,
            category=category
        ).all()
        
        result = {}
        for setting in settings:
            result[setting.key] = {
                'value': setting.get_typed_value(),
                'type': setting.value_type,
                'description': setting.description,
                'is_sensitive': setting.is_sensitive
            }
        
        return result
    
    def delete_setting(self, category: str, key: str) -> bool:
        """Delete a setting"""
        try:
            setting = ApplicationSetting.query.filter_by(
                tenant_id=self.tenant_id,
                category=category,
                key=key
            ).first()
            
            if setting:
                db.session.delete(setting)
                db.session.commit()
                
                # Clear from cache
                cache_key = f"{category}.{key}"
                self._cache.pop(cache_key, None)
                
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting {category}.{key}: {e}")
            return False
    
    def clear_cache(self):
        """Clear the settings cache"""
        self._cache.clear()


class RBACManager:
    """Role-Based Access Control management"""
    
    def __init__(self, tenant_id: int = None):
        self.tenant_id = tenant_id or self._get_current_tenant_id()
    
    def _get_current_tenant_id(self) -> int:
        """Get current tenant ID from user session or current_user"""
        if current_user and current_user.is_authenticated:
            return current_user.tenant_id
        return session.get('tenant_id', 1)
    
    def set_permission(self, role: str, resource: str, permission: str, granted: bool = True) -> bool:
        """Set a role permission"""
        try:
            perm = RolePermission.query.filter_by(
                tenant_id=self.tenant_id,
                role=role,
                resource=resource,
                permission=permission
            ).first()
            
            if perm:
                perm.granted = granted
            else:
                perm = RolePermission(
                    tenant_id=self.tenant_id,
                    role=role,
                    resource=resource,
                    permission=permission,
                    granted=granted
                )
                db.session.add(perm)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error setting permission {role}.{resource}.{permission}: {e}")
            return False
    
    def has_permission(self, role: str, resource: str, permission: str) -> bool:
        """Check if role has permission for resource"""
        # Superadmin always has all permissions
        if role == 'superadmin':
            return True
        
        perm = RolePermission.query.filter_by(
            tenant_id=self.tenant_id,
            role=role,
            resource=resource,
            permission=permission,
            granted=True
        ).first()
        
        return perm is not None
    
    def get_role_permissions(self, role: str) -> Dict[str, List[str]]:
        """Get all permissions for a role grouped by resource"""
        permissions = RolePermission.query.filter_by(
            tenant_id=self.tenant_id,
            role=role,
            granted=True
        ).all()
        
        result = {}
        for perm in permissions:
            if perm.resource not in result:
                result[perm.resource] = []
            result[perm.resource].append(perm.permission)
        
        return result
    
    def get_all_permissions(self) -> Dict[str, Dict[str, List[str]]]:
        """Get all permissions organized by role and resource"""
        permissions = RolePermission.query.filter_by(
            tenant_id=self.tenant_id,
            granted=True
        ).all()
        
        result = {}
        for perm in permissions:
            if perm.role not in result:
                result[perm.role] = {}
            if perm.resource not in result[perm.role]:
                result[perm.role][perm.resource] = []
            result[perm.role][perm.resource].append(perm.permission)
        
        return result
    
    def initialize_default_permissions(self):
        """Initialize default RBAC permissions for a tenant"""
        default_permissions = {
            'user': {
                'customers': ['read'],
                'products': ['read'],
                'quotes': ['read'],
                'orders': ['read'],
                'tasks': ['read', 'update']
            },
            'manager': {
                'customers': ['create', 'read', 'update'],
                'products': ['create', 'read', 'update'],
                'quotes': ['create', 'read', 'update', 'approve'],
                'orders': ['create', 'read', 'update'],
                'tasks': ['create', 'read', 'update', 'delete']
            },
            'admin': {
                'customers': ['create', 'read', 'update', 'delete'],
                'products': ['create', 'read', 'update', 'delete'],
                'quotes': ['create', 'read', 'update', 'delete', 'approve'],
                'orders': ['create', 'read', 'update', 'delete'],
                'tasks': ['create', 'read', 'update', 'delete'],
                'users': ['create', 'read', 'update'],
                'settings': ['read', 'update']
            },
            'superadmin': {
                'customers': ['create', 'read', 'update', 'delete', 'export'],
                'products': ['create', 'read', 'update', 'delete', 'export'],
                'quotes': ['create', 'read', 'update', 'delete', 'approve', 'export'],
                'orders': ['create', 'read', 'update', 'delete', 'export'],
                'tasks': ['create', 'read', 'update', 'delete', 'export'],
                'users': ['create', 'read', 'update', 'delete'],
                'settings': ['create', 'read', 'update', 'delete'],
                'system': ['read', 'update', 'delete']
            }
        }
        
        for role, resources in default_permissions.items():
            for resource, permissions in resources.items():
                for permission in permissions:
                    self.set_permission(role, resource, permission, True)


def initialize_default_settings(tenant_id: int = 1):
    """Initialize default application settings"""
    settings_manager = SettingsManager(tenant_id)
    rbac_manager = RBACManager(tenant_id)
    
    # Business settings
    settings_manager.set_setting('business', 'company_name', 'Filterdyn', 'string', 'Company name displayed throughout the application')
    settings_manager.set_setting('business', 'default_currency', 'EUR', 'string', 'Default currency for quotes and orders')
    settings_manager.set_setting('business', 'default_tax_rate', 24.0, 'integer', 'Default tax rate percentage')
    settings_manager.set_setting('business', 'quote_validity_days', 30, 'integer', 'Default quote validity in days')
    settings_manager.set_setting('business', 'order_delivery_days', 15, 'integer', 'Default delivery time in days')
    
    # UI settings
    settings_manager.set_setting('ui', 'items_per_page', 20, 'integer', 'Number of items to display per page')
    settings_manager.set_setting('ui', 'default_language', 'en', 'string', 'Default application language')
    settings_manager.set_setting('ui', 'theme_primary_color', '#1ba3a3', 'string', 'Primary theme color')
    settings_manager.set_setting('ui', 'theme_secondary_color', '#ffffff', 'string', 'Secondary theme color')
    settings_manager.set_setting('ui', 'enable_dark_mode', False, 'boolean', 'Enable dark mode interface')
    
    # Email settings
    settings_manager.set_setting('email', 'smtp_enabled', False, 'boolean', 'Enable email notifications')
    settings_manager.set_setting('email', 'smtp_server', '', 'string', 'SMTP server hostname', True)
    settings_manager.set_setting('email', 'smtp_port', 587, 'integer', 'SMTP server port')
    settings_manager.set_setting('email', 'smtp_username', '', 'string', 'SMTP username', True)
    settings_manager.set_setting('email', 'smtp_password', '', 'string', 'SMTP password', True)
    settings_manager.set_setting('email', 'from_email', '', 'string', 'Default from email address')
    
    # Security settings
    settings_manager.set_setting('security', 'session_timeout', 30, 'integer', 'Session timeout in minutes')
    settings_manager.set_setting('security', 'password_min_length', 6, 'integer', 'Minimum password length')
    settings_manager.set_setting('security', 'require_password_change', False, 'boolean', 'Require users to change password on first login')
    settings_manager.set_setting('security', 'max_login_attempts', 5, 'integer', 'Maximum failed login attempts before lockout')
    
    # System settings
    settings_manager.set_setting('system', 'backup_enabled', True, 'boolean', 'Enable automatic database backups')
    settings_manager.set_setting('system', 'backup_frequency', 'daily', 'string', 'Backup frequency (daily, weekly, monthly)')
    settings_manager.set_setting('system', 'debug_mode', False, 'boolean', 'Enable debug mode')
    settings_manager.set_setting('system', 'maintenance_mode', False, 'boolean', 'Enable maintenance mode')
    
    # Initialize RBAC permissions
    rbac_manager.initialize_default_permissions()
    
    return True