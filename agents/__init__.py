"""
Operational Suite V2 - Multi-Agent System
=========================================

This package contains specialized agents for different aspects of the business:

1. Communication & AI Agent - Email integration, AI composition
2. Operations & Data Agent - Asset tracking, water quality, service reports
3. Platform & Integration Agent - APIs, analytics, integrations
4. Testing & Quality Agent - Test automation and quality assurance
"""

from .communication_ai import CommunicationAIAgent
from .operations_data import OperationsDataAgent
from .platform_integration import PlatformIntegrationAgent
from .testing_quality import TestingQualityAgent

__all__ = [
    'CommunicationAIAgent',
    'OperationsDataAgent', 
    'PlatformIntegrationAgent',
    'TestingQualityAgent'
] 