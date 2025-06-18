"""
Operational Suite V2 - Configuration Template
============================================

This file contains configuration templates for all agents and features.
Copy this file and customize it for your specific environment.
"""

import os
from typing import Dict, Any

# =============================================================================
# CORE CONFIGURATION
# =============================================================================

class Config:
    """Base configuration class"""
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///instance/test.db')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Multi-Agent System Configuration
    AGENT_LOG_LEVEL = os.getenv('AGENT_LOG_LEVEL', 'INFO')
    AGENT_AUTO_START = os.getenv('AGENT_AUTO_START', 'True').lower() == 'true'

# =============================================================================
# COMMUNICATION & AI AGENT CONFIGURATION
# =============================================================================

class CommunicationAIConfig:
    """Configuration for Communication & AI Agent"""
    
    # Gmail API Configuration
    GMAIL_CREDENTIALS_PATH = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
    GMAIL_TOKEN_PATH = os.getenv('GMAIL_TOKEN_PATH', 'token.json')
    GMAIL_SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '500'))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    
    # Email Configuration
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@filterdyn.com')
    EMAIL_RATE_LIMIT = int(os.getenv('EMAIL_RATE_LIMIT', '10'))  # emails per minute
    EMAIL_BATCH_SIZE = int(os.getenv('EMAIL_BATCH_SIZE', '5'))
    
    # Email Templates
    EMAIL_TEMPLATES_DIR = os.getenv('EMAIL_TEMPLATES_DIR', 'email_templates')
    SCHEDULED_EMAILS_DIR = os.getenv('SCHEDULED_EMAILS_DIR', 'scheduled_emails')

# =============================================================================
# OPERATIONS & DATA AGENT CONFIGURATION
# =============================================================================

class OperationsDataConfig:
    """Configuration for Operations & Data Agent"""
    
    # Database Configuration
    DB_PATH = os.getenv('DB_PATH', 'instance/test.db')
    
    # Service Reminder Configuration
    REMINDER_DAYS_BEFORE_DUE = int(os.getenv('REMINDER_DAYS_BEFORE_DUE', '30'))
    URGENT_REMINDER_DAYS = int(os.getenv('URGENT_REMINDER_DAYS', '7'))
    
    # Equipment Maintenance Schedules
    EQUIPMENT_MAINTENANCE_SCHEDULES = {
        'deionization_column': {
            'preventive_maintenance_days': 90,
            'resin_replacement_days': 365,
            'regeneration_reminder_days': 30
        },
        'ro_system': {
            'preventive_maintenance_days': 180,
            'membrane_replacement_days': 730,
            'filter_replacement_days': 90
        },
        'filter': {
            'preventive_maintenance_days': 60,
            'filter_replacement_days': 180
        },
        'general': {
            'preventive_maintenance_days': 90
        }
    }
    
    # Water Quality Thresholds
    WATER_QUALITY_THRESHOLDS = {
        'conductivity': {
            'warning': 10.0,  # μS/cm
            'critical': 50.0
        },
        'resistivity': {
            'warning': 0.1,  # MΩ·cm
            'critical': 0.05
        },
        'ph': {
            'warning_low': 6.5,
            'warning_high': 8.5,
            'critical_low': 6.0,
            'critical_high': 9.0
        },
        'tds': {
            'warning': 10.0,  # mg/L
            'critical': 50.0
        },
        'turbidity': {
            'warning': 1.0,  # NTU
            'critical': 5.0
        }
    }
    
    # Performance Analysis Configuration
    DEFAULT_ANALYSIS_DAYS = int(os.getenv('DEFAULT_ANALYSIS_DAYS', '30'))
    MAX_ANALYSIS_DAYS = int(os.getenv('MAX_ANALYSIS_DAYS', '365'))
    
    # Data Export Configuration
    EXPORT_DIR = os.getenv('EXPORT_DIR', 'exports')
    EXPORT_FORMATS = ['json', 'csv', 'xlsx']

# =============================================================================
# PLATFORM & INTEGRATION AGENT CONFIGURATION
# =============================================================================

class PlatformIntegrationConfig:
    """Configuration for Platform & Integration Agent"""
    
    # Grandstream Integration
    GRANDSTREAM_CONFIG = {
        'base_url': os.getenv('GRANDSTREAM_URL', ''),
        'username': os.getenv('GRANDSTREAM_USERNAME', ''),
        'password': os.getenv('GRANDSTREAM_PASSWORD', ''),
        'timeout': int(os.getenv('GRANDSTREAM_TIMEOUT', '10')),
        'retry_attempts': int(os.getenv('GRANDSTREAM_RETRY_ATTEMPTS', '3'))
    }
    
    # API Configuration
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '100'))  # requests per minute
    API_CORS_ORIGINS = os.getenv('API_CORS_ORIGINS', '*').split(',')
    
    # Analytics Configuration
    ANALYTICS_CACHE_DURATION = int(os.getenv('ANALYTICS_CACHE_DURATION', '300'))  # seconds
    ANALYTICS_MAX_DATA_POINTS = int(os.getenv('ANALYTICS_MAX_DATA_POINTS', '1000'))
    
    # Dashboard Configuration
    DASHBOARD_REFRESH_INTERVAL = int(os.getenv('DASHBOARD_REFRESH_INTERVAL', '60'))  # seconds
    DASHBOARD_MAX_CHARTS = int(os.getenv('DASHBOARD_MAX_CHARTS', '10'))
    
    # External API Keys
    EXTERNAL_API_KEYS = {
        'service_1': os.getenv('EXTERNAL_API_KEY_1', ''),
        'service_2': os.getenv('EXTERNAL_API_KEY_2', ''),
        'service_3': os.getenv('EXTERNAL_API_KEY_3', '')
    }

# =============================================================================
# TESTING & QUALITY AGENT CONFIGURATION
# =============================================================================

class TestingQualityConfig:
    """Configuration for Testing & Quality Agent"""
    
    # Test Configuration
    TEST_DISCOVERY_PATTERNS = [
        'test_*.py',
        '*_test.py',
        'tests/*.py'
    ]
    
    TEST_TIMEOUT = int(os.getenv('TEST_TIMEOUT', '300'))  # seconds
    TEST_PARALLEL = os.getenv('TEST_PARALLEL', 'False').lower() == 'true'
    TEST_COVERAGE = os.getenv('TEST_COVERAGE', 'True').lower() == 'true'
    
    # Quality Configuration
    QUALITY_THRESHOLDS = {
        'test_coverage': float(os.getenv('QUALITY_TEST_COVERAGE', '80.0')),
        'test_pass_rate': float(os.getenv('QUALITY_TEST_PASS_RATE', '90.0')),
        'code_complexity': int(os.getenv('QUALITY_CODE_COMPLEXITY', '10'))
    }
    
    # Reporting Configuration
    REPORT_DIR = os.getenv('REPORT_DIR', 'reports')
    REPORT_FORMATS = ['json', 'html', 'xml']

# =============================================================================
# COORDINATOR CONFIGURATION
# =============================================================================

class CoordinatorConfig:
    """Configuration for Agent Coordinator"""
    
    # Workflow Configuration
    WORKFLOW_INTERVAL = int(os.getenv('WORKFLOW_INTERVAL', '300'))  # seconds
    MAX_WORKFLOW_DURATION = int(os.getenv('MAX_WORKFLOW_DURATION', '60'))  # seconds
    
    # Health Monitoring
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '60'))  # seconds
    AGENT_TIMEOUT = int(os.getenv('AGENT_TIMEOUT', '30'))  # seconds
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'operational_suite.log')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# =============================================================================
# ENVIRONMENT-SPECIFIC CONFIGURATIONS
# =============================================================================

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    AGENT_LOG_LEVEL = 'DEBUG'
    DATABASE_URL = 'sqlite:///instance/dev.db'

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    AGENT_LOG_LEVEL = 'WARNING'
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/db')

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///instance/test.db'
    WTF_CSRF_ENABLED = False

# =============================================================================
# CONFIGURATION FACTORY
# =============================================================================

def get_config(environment: str = None) -> Dict[str, Any]:
    """Get configuration based on environment"""
    if environment is None:
        environment = os.getenv('FLASK_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    base_config = configs.get(environment, DevelopmentConfig)
    
    # Combine all configurations
    config = {
        'base': base_config,
        'communication_ai': CommunicationAIConfig,
        'operations_data': OperationsDataConfig,
        'platform_integration': PlatformIntegrationConfig,
        'testing_quality': TestingQualityConfig,
        'coordinator': CoordinatorConfig
    }
    
    return config

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Example usage
    config = get_config('development')
    
    print("Configuration loaded successfully!")
    print(f"Database URL: {config['base'].DATABASE_URL}")
    print(f"Debug mode: {config['base'].DEBUG}")
    print(f"OpenAI API Key configured: {'Yes' if config['communication_ai'].OPENAI_API_KEY else 'No'}") 