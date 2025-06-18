#!/usr/bin/env python3
"""
Operational Suite V2 - Feature Demo
===================================

This script demonstrates all the new features implemented in the multi-agent system.
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.coordinator import get_coordinator
from agents.communication_ai import CommunicationAIAgent
from agents.operations_data import OperationsDataAgent
from agents.platform_integration import PlatformIntegrationAgent


def demo_communication_ai_features():
    """Demo Communication & AI Agent features"""
    print("\n" + "="*60)
    print("COMMUNICATION & AI AGENT DEMO")
    print("="*60)
    
    # Initialize the agent
    config = {
        'gmail_credentials_path': 'credentials.json',
        'gmail_token_path': 'token.json',
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'default_from_email': 'noreply@filterdyn.com'
    }
    
    agent = CommunicationAIAgent(config)
    
    # Demo AI email content generation
    print("\n1. AI Email Content Generation:")
    print("-" * 40)
    
    context = {
        'type': 'service_reminder',
        'customer_name': 'John Smith',
        'equipment_number': 'EQ-001',
        'service_type': 'preventive_maintenance',
        'days_until_due': 7
    }
    
    email_content = agent.generate_ai_email_content(context)
    print(f"Generated email content:\n{email_content}")
    
    # Demo email template creation
    print("\n2. Email Template Creation:")
    print("-" * 40)
    
    template_name = "service_reminder_template"
    template_content = agent.create_email_template(template_name, context)
    print(f"Template '{template_name}' created successfully")
    
    # Demo email scheduling
    print("\n3. Email Scheduling:")
    print("-" * 40)
    
    send_time = datetime.now() + timedelta(hours=2)
    scheduled = agent.schedule_email(
        to="customer@example.com",
        subject="Service Reminder",
        body="Your equipment needs service.",
        send_time=send_time
    )
    print(f"Email scheduled for {send_time}: {'Success' if scheduled else 'Failed'}")


def demo_operations_data_features():
    """Demo Operations & Data Agent features"""
    print("\n" + "="*60)
    print("OPERATIONS & DATA AGENT DEMO")
    print("="*60)
    
    # Initialize the agent
    agent = OperationsDataAgent()
    
    # Demo service reminder generation
    print("\n1. Service Reminder Generation:")
    print("-" * 40)
    
    reminders = agent.generate_service_reminders()
    print(f"Generated {len(reminders)} service reminders")
    
    if reminders:
        reminder = reminders[0]
        print(f"Sample reminder: {reminder.customer_name} - {reminder.equipment_number}")
        print(f"  Service type: {reminder.service_type}")
        print(f"  Priority: {reminder.priority}")
        print(f"  Days until due: {reminder.days_until_due}")
    
    # Demo water quality alerts
    print("\n2. Water Quality Alert Checking:")
    print("-" * 40)
    
    alerts = agent.check_water_quality_alerts()
    print(f"Found {len(alerts)} water quality alerts")
    
    if alerts:
        alert = alerts[0]
        print(f"Sample alert: {alert.customer_name} - {alert.parameter}")
        print(f"  Value: {alert.value} (Threshold: {alert.threshold})")
        print(f"  Alert type: {alert.alert_type}")
    
    # Demo service report template generation
    print("\n3. Service Report Template Generation:")
    print("-" * 40)
    
    # Note: This would need a real equipment_id from the database
    print("Service report template generation requires equipment_id from database")
    
    # Demo automated reminder schedule
    print("\n4. Automated Reminder Schedule:")
    print("-" * 40)
    
    schedule = agent.create_automated_reminder_schedule()
    print(f"Schedule generated at: {schedule['generated_at']}")
    print(f"Service reminders: {schedule['service_reminders']['total']}")
    print(f"Water quality alerts: {schedule['water_quality_alerts']['total']}")


def demo_platform_integration_features():
    """Demo Platform & Integration Agent features"""
    print("\n" + "="*60)
    print("PLATFORM & INTEGRATION AGENT DEMO")
    print("="*60)
    
    # Initialize the agent
    config = {
        'db_path': 'instance/test.db',
        'grandstream': {
            'base_url': 'https://example.com',
            'username': 'admin',
            'password': 'password'
        }
    }
    
    agent = PlatformIntegrationAgent(config)
    
    # Demo analytics dashboard creation
    print("\n1. Analytics Dashboard Creation:")
    print("-" * 40)
    
    dashboard = agent.create_analytics_dashboard()
    if 'error' not in dashboard:
        print("Analytics dashboard created successfully")
        print(f"Overview: {dashboard.get('overview', {})}")
        print(f"Equipment metrics: {dashboard.get('equipment', {})}")
    else:
        print(f"Dashboard creation failed: {dashboard['error']}")
    
    # Demo Grandstream integration setup
    print("\n2. Grandstream Integration Setup:")
    print("-" * 40)
    
    # This would fail in demo mode since we don't have real credentials
    print("Grandstream integration requires real server credentials")
    
    # Demo website contact form generation
    print("\n3. Website Contact Form Generation:")
    print("-" * 40)
    
    contact_form_html = agent.create_website_contact_form()
    print("Contact form HTML generated successfully")
    print(f"Form length: {len(contact_form_html)} characters")
    
    # Demo performance report generation
    print("\n4. Performance Report Generation:")
    print("-" * 40)
    
    # Note: This would need a real equipment_id from the database
    print("Performance report generation requires equipment_id from database")


def demo_coordinator_features():
    """Demo Agent Coordinator features"""
    print("\n" + "="*60)
    print("AGENT COORDINATOR DEMO")
    print("="*60)
    
    # Get the coordinator
    coordinator = get_coordinator()
    
    # Demo agent status checking
    print("\n1. Agent Status Check:")
    print("-" * 40)
    
    agent_statuses = coordinator.get_agent_status()
    for agent_name, status in agent_statuses.items():
        print(f"{agent_name}: {status.status} (Last activity: {status.last_activity})")
    
    # Demo automated workflows
    print("\n2. Automated Workflows:")
    print("-" * 40)
    
    workflows = coordinator.run_automated_workflows()
    print(f"Executed {len(workflows)} automated workflows")
    
    for workflow in workflows:
        print(f"  - {workflow['type']}: {workflow}")
    
    # Demo system health report
    print("\n3. System Health Report:")
    print("-" * 40)
    
    health_report = coordinator.get_system_health_report()
    print(f"System status: {health_report.get('system_status', 'unknown')}")
    print(f"Current alerts: {health_report.get('current_alerts', {})}")
    
    recommendations = health_report.get('recommendations', [])
    print(f"Recommendations ({len(recommendations)}):")
    for rec in recommendations:
        print(f"  - {rec}")


def demo_api_features():
    """Demo API features"""
    print("\n" + "="*60)
    print("API FEATURES DEMO")
    print("="*60)
    
    print("\n1. Available API Endpoints:")
    print("-" * 40)
    
    endpoints = [
        "GET /api/v1/equipment - Get equipment list",
        "GET /api/v1/equipment/{id}/status - Get equipment status",
        "POST /api/v1/water-quality - Post water quality data",
        "GET /api/v1/analytics/dashboard - Get analytics dashboard",
        "POST /api/v1/website/contact - Handle contact form"
    ]
    
    for endpoint in endpoints:
        print(f"  {endpoint}")
    
    print("\n2. API Integration Examples:")
    print("-" * 40)
    
    print("""
    # Example: Get equipment list
    curl -X GET http://localhost:5000/api/v1/equipment
    
    # Example: Post water quality data
    curl -X POST http://localhost:5000/api/v1/water-quality \\
         -H "Content-Type: application/json" \\
         -d '{
           "equipment_id": 1,
           "conductivity": 5.2,
           "ph": 7.1,
           "temperature": 25.0
         }'
    
    # Example: Get analytics dashboard
    curl -X GET http://localhost:5000/api/v1/analytics/dashboard
    """)


def main():
    """Main demo function"""
    print("Operational Suite V2 - Multi-Agent System Demo")
    print("=" * 60)
    print(f"Demo started at: {datetime.now()}")
    
    try:
        # Demo each agent's features
        demo_communication_ai_features()
        demo_operations_data_features()
        demo_platform_integration_features()
        demo_coordinator_features()
        demo_api_features()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        print("\nNext Steps:")
        print("1. Install additional dependencies: pip install -r requirements.txt")
        print("2. Set up environment variables for API keys")
        print("3. Configure Gmail API credentials")
        print("4. Set up Grandstream integration (if needed)")
        print("5. Run the Flask application: python app.py")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("This is expected if the database is not set up or dependencies are missing.")
        print("The demo shows the feature structure and capabilities.")


if __name__ == "__main__":
    main() 