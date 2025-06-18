"""
Agent Coordinator
================

Main coordinator for all agents in the Operational Suite V2.
Provides unified interface and manages agent interactions.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .communication_ai import CommunicationAIAgent
from .operations_data import OperationsDataAgent
from .platform_integration import PlatformIntegrationAgent
from .testing_quality import TestingQualityAgent


@dataclass
class AgentStatus:
    """Agent status information"""
    name: str
    status: str  # active, inactive, error
    last_activity: datetime
    error_message: Optional[str] = None


class AgentCoordinator:
    """Main coordinator for all agents"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.agents = {}
        self.agent_status = {}
        self.initialize_agents()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            'db_path': 'instance/test.db',
            'gmail_credentials_path': 'credentials.json',
            'gmail_token_path': 'token.json',
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'default_from_email': 'noreply@filterdyn.com',
            'grandstream': {
                'base_url': os.getenv('GRANDSTREAM_URL', ''),
                'username': os.getenv('GRANDSTREAM_USERNAME', ''),
                'password': os.getenv('GRANDSTREAM_PASSWORD', '')
            },
            'api_keys': {
                'external_service_1': os.getenv('EXTERNAL_API_KEY_1', ''),
                'external_service_2': os.getenv('EXTERNAL_API_KEY_2', '')
            }
        }
    
    def initialize_agents(self):
        """Initialize all agents"""
        try:
            # Initialize Communication & AI Agent
            self.agents['communication_ai'] = CommunicationAIAgent(self.config)
            self.agent_status['communication_ai'] = AgentStatus(
                name='Communication & AI Agent',
                status='active',
                last_activity=datetime.now()
            )
            print("✅ Communication & AI Agent initialized")
            
            # Initialize Operations & Data Agent
            self.agents['operations_data'] = OperationsDataAgent(self.config.get('db_path'))
            self.agent_status['operations_data'] = AgentStatus(
                name='Operations & Data Agent',
                status='active',
                last_activity=datetime.now()
            )
            print("✅ Operations & Data Agent initialized")
            
            # Initialize Platform & Integration Agent
            self.agents['platform_integration'] = PlatformIntegrationAgent(self.config)
            self.agent_status['platform_integration'] = AgentStatus(
                name='Platform & Integration Agent',
                status='active',
                last_activity=datetime.now()
            )
            print("✅ Platform & Integration Agent initialized")
            
            # Initialize Testing & Quality Agent
            self.agents['testing_quality'] = TestingQualityAgent()
            self.agent_status['testing_quality'] = AgentStatus(
                name='Testing & Quality Agent',
                status='active',
                last_activity=datetime.now()
            )
            print("✅ Testing & Quality Agent initialized")
            
        except Exception as e:
            print(f"❌ Error initializing agents: {e}")
    
    def get_agent_status(self) -> Dict[str, AgentStatus]:
        """Get status of all agents"""
        return self.agent_status
    
    def get_agent(self, agent_name: str):
        """Get a specific agent by name"""
        return self.agents.get(agent_name)
    
    def run_automated_workflows(self):
        """Run automated workflows across all agents"""
        workflows = []
        
        try:
            # 1. Check for service reminders
            operations_agent = self.get_agent('operations_data')
            if operations_agent:
                reminders = operations_agent.generate_service_reminders()
                alerts = operations_agent.check_water_quality_alerts()
                
                workflows.append({
                    'type': 'service_reminders',
                    'count': len(reminders),
                    'urgent': len([r for r in reminders if r.priority == 'urgent']),
                    'timestamp': datetime.now().isoformat()
                })
                
                workflows.append({
                    'type': 'water_quality_alerts',
                    'count': len(alerts),
                    'critical': len([a for a in alerts if a.alert_type == 'critical']),
                    'timestamp': datetime.now().isoformat()
                })
                
                # Update agent status
                self.agent_status['operations_data'].last_activity = datetime.now()
            
            # 2. Send automated emails for urgent reminders
            communication_agent = self.get_agent('communication_ai')
            if communication_agent and reminders:
                urgent_reminders = [r for r in reminders if r.priority == 'urgent']
                
                for reminder in urgent_reminders[:5]:  # Limit to 5 emails per run
                    context = {
                        'type': 'service_reminder',
                        'customer_name': reminder.customer_name,
                        'equipment_number': reminder.equipment_number,
                        'service_type': reminder.service_type,
                        'days_until_due': reminder.days_until_due
                    }
                    
                    success = communication_agent.send_ai_generated_email(
                        to=reminder.customer_email,
                        context=context
                    )
                    
                    if success:
                        workflows.append({
                            'type': 'email_sent',
                            'recipient': reminder.customer_email,
                            'subject': 'Service Reminder',
                            'timestamp': datetime.now().isoformat()
                        })
                
                # Update agent status
                self.agent_status['communication_ai'].last_activity = datetime.now()
            
            # 3. Generate analytics dashboard
            platform_agent = self.get_agent('platform_integration')
            if platform_agent:
                dashboard = platform_agent.create_analytics_dashboard()
                
                workflows.append({
                    'type': 'analytics_dashboard',
                    'generated': True,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Update agent status
                self.agent_status['platform_integration'].last_activity = datetime.now()
            
            return workflows
            
        except Exception as e:
            print(f"❌ Error running automated workflows: {e}")
            return []
    
    def send_service_reminder_email(self, customer_email: str, customer_name: str, 
                                   equipment_number: str, service_type: str, 
                                   days_until_due: int) -> bool:
        """Send a service reminder email"""
        try:
            communication_agent = self.get_agent('communication_ai')
            if not communication_agent:
                return False
            
            context = {
                'type': 'service_reminder',
                'customer_name': customer_name,
                'equipment_number': equipment_number,
                'service_type': service_type,
                'days_until_due': days_until_due
            }
            
            success = communication_agent.send_ai_generated_email(
                to=customer_email,
                context=context
            )
            
            if success:
                self.agent_status['communication_ai'].last_activity = datetime.now()
            
            return success
            
        except Exception as e:
            print(f"❌ Error sending service reminder email: {e}")
            return False
    
    def send_water_quality_alert_email(self, customer_email: str, customer_name: str,
                                      equipment_number: str, parameter: str, 
                                      value: float, threshold: float) -> bool:
        """Send a water quality alert email"""
        try:
            communication_agent = self.get_agent('communication_ai')
            if not communication_agent:
                return False
            
            context = {
                'type': 'water_quality_alert',
                'customer_name': customer_name,
                'equipment_number': equipment_number,
                'parameter': parameter,
                'value': value,
                'threshold': threshold
            }
            
            success = communication_agent.send_ai_generated_email(
                to=customer_email,
                context=context
            )
            
            if success:
                self.agent_status['communication_ai'].last_activity = datetime.now()
            
            return success
            
        except Exception as e:
            print(f"❌ Error sending water quality alert email: {e}")
            return False
    
    def generate_service_report(self, equipment_id: int, service_type: str) -> Dict[str, Any]:
        """Generate a service report template"""
        try:
            operations_agent = self.get_agent('operations_data')
            if not operations_agent:
                return {'error': 'Operations agent not available'}
            
            template = operations_agent.generate_service_report_template(equipment_id, service_type)
            
            self.agent_status['operations_data'].last_activity = datetime.now()
            
            return template
            
        except Exception as e:
            print(f"❌ Error generating service report: {e}")
            return {'error': str(e)}
    
    def get_analytics_dashboard(self) -> Dict[str, Any]:
        """Get analytics dashboard data"""
        try:
            platform_agent = self.get_agent('platform_integration')
            if not platform_agent:
                return {'error': 'Platform agent not available'}
            
            dashboard = platform_agent.create_analytics_dashboard()
            
            self.agent_status['platform_integration'].last_activity = datetime.now()
            
            return dashboard
            
        except Exception as e:
            print(f"❌ Error getting analytics dashboard: {e}")
            return {'error': str(e)}
    
    def run_performance_analysis(self, equipment_id: int, days: int = 30) -> Dict[str, Any]:
        """Run performance analysis for equipment"""
        try:
            operations_agent = self.get_agent('operations_data')
            if not operations_agent:
                return {'error': 'Operations agent not available'}
            
            analysis = operations_agent.analyze_equipment_performance(equipment_id, days)
            
            self.agent_status['operations_data'].last_activity = datetime.now()
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error running performance analysis: {e}")
            return {'error': str(e)}
    
    def setup_api_endpoints(self, app):
        """Setup API endpoints for all agents"""
        try:
            platform_agent = self.get_agent('platform_integration')
            if platform_agent:
                platform_agent.create_api_endpoints(app)
                print("✅ API endpoints setup complete")
            
        except Exception as e:
            print(f"❌ Error setting up API endpoints: {e}")
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Get comprehensive system health report"""
        try:
            # Get agent statuses
            agent_statuses = {}
            for name, status in self.agent_status.items():
                agent_statuses[name] = {
                    'status': status.status,
                    'last_activity': status.last_activity.isoformat(),
                    'error_message': status.error_message
                }
            
            # Get recent workflows
            recent_workflows = self.run_automated_workflows()
            
            # Get basic system metrics
            operations_agent = self.get_agent('operations_data')
            total_reminders = 0
            total_alerts = 0
            
            if operations_agent:
                reminders = operations_agent.generate_service_reminders()
                alerts = operations_agent.check_water_quality_alerts()
                total_reminders = len(reminders)
                total_alerts = len(alerts)
            
            health_report = {
                'timestamp': datetime.now().isoformat(),
                'system_status': 'healthy',
                'agents': agent_statuses,
                'recent_workflows': recent_workflows,
                'current_alerts': {
                    'service_reminders': total_reminders,
                    'water_quality_alerts': total_alerts
                },
                'recommendations': self._generate_health_recommendations(
                    agent_statuses, total_reminders, total_alerts
                )
            }
            
            return health_report
            
        except Exception as e:
            print(f"❌ Error generating system health report: {e}")
            return {'error': str(e)}
    
    def _generate_health_recommendations(self, agent_statuses: Dict, 
                                       total_reminders: int, 
                                       total_alerts: int) -> List[str]:
        """Generate health recommendations based on system state"""
        recommendations = []
        
        # Check agent statuses
        for name, status in agent_statuses.items():
            if status['status'] != 'active':
                recommendations.append(f"Agent {name} is not active. Check configuration.")
        
        # Check for urgent reminders
        if total_reminders > 10:
            recommendations.append("High number of service reminders. Consider batch processing.")
        
        # Check for critical alerts
        if total_alerts > 5:
            recommendations.append("Multiple water quality alerts detected. Immediate attention required.")
        
        # Check agent activity
        for name, status in agent_statuses.items():
            last_activity = datetime.fromisoformat(status['last_activity'])
            if (datetime.now() - last_activity).days > 1:
                recommendations.append(f"Agent {name} has been inactive for over 24 hours.")
        
        if not recommendations:
            recommendations.append("System is operating normally. No immediate action required.")
        
        return recommendations
    
    def export_agent_data(self, agent_name: str, data_type: str) -> str:
        """Export data from a specific agent"""
        try:
            if agent_name == 'operations_data':
                operations_agent = self.get_agent('operations_data')
                if operations_agent and data_type == 'reminder_schedule':
                    schedule = operations_agent.create_automated_reminder_schedule()
                    return json.dumps(schedule, indent=2, default=str)
                elif operations_agent and data_type == 'performance_report':
                    # This would need equipment_id parameter
                    return "Performance report export requires equipment_id parameter"
            
            elif agent_name == 'platform_integration':
                platform_agent = self.get_agent('platform_integration')
                if platform_agent and data_type == 'analytics_dashboard':
                    dashboard = platform_agent.create_analytics_dashboard()
                    return json.dumps(dashboard, indent=2, default=str)
            
            return f"Export not available for {agent_name} - {data_type}"
            
        except Exception as e:
            print(f"❌ Error exporting agent data: {e}")
            return f"Export failed: {str(e)}"


# Global coordinator instance
coordinator = None

def get_coordinator() -> AgentCoordinator:
    """Get the global coordinator instance"""
    global coordinator
    if coordinator is None:
        coordinator = AgentCoordinator()
    return coordinator 