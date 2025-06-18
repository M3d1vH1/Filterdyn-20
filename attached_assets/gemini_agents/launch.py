#!/usr/bin/env python3
"""
Operational Suite V2 - Feature Launcher
=======================================

Main launcher script for the multi-agent system features.
This script provides a unified interface to start and manage all features.
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.coordinator import get_coordinator
from agents.communication_ai import CommunicationAIAgent
from agents.operations_data import OperationsDataAgent
from agents.platform_integration import PlatformIntegrationAgent


def setup_logging(level: str = 'INFO', log_file: str = None):
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if log_file:
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    else:
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format=log_format
        )


def launch_demo():
    """Launch the feature demonstration"""
    print("🚀 Launching Operational Suite V2 Feature Demo...")
    
    try:
        # Import and run demo
        from examples.demo_features import main as demo_main
        demo_main()
    except ImportError as e:
        print(f"❌ Error importing demo: {e}")
        print("Make sure demo_features.py is in the examples directory")
    except Exception as e:
        print(f"❌ Demo failed: {e}")


def launch_coordinator():
    """Launch the agent coordinator"""
    print("🤖 Launching Agent Coordinator...")
    
    try:
        coordinator = get_coordinator()
        
        # Get agent status
        agent_statuses = coordinator.get_agent_status()
        print(f"✅ Coordinator launched with {len(agent_statuses)} agents:")
        
        for agent_name, status in agent_statuses.items():
            print(f"  - {agent_name}: {status.status}")
        
        # Run automated workflows
        print("\n🔄 Running automated workflows...")
        workflows = coordinator.run_automated_workflows()
        print(f"✅ Executed {len(workflows)} workflows")
        
        # Get system health
        print("\n📊 System Health Report:")
        health_report = coordinator.get_system_health_report()
        print(f"  Status: {health_report.get('system_status', 'unknown')}")
        print(f"  Alerts: {health_report.get('current_alerts', {})}")
        
        return coordinator
        
    except Exception as e:
        print(f"❌ Coordinator launch failed: {e}")
        return None


def launch_communication_agent():
    """Launch the Communication & AI Agent"""
    print("📧 Launching Communication & AI Agent...")
    
    try:
        config = {
            'gmail_credentials_path': 'credentials.json',
            'gmail_token_path': 'token.json',
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'default_from_email': 'noreply@filterdyn.com'
        }
        
        agent = CommunicationAIAgent(config)
        
        # Test AI email generation
        context = {
            'type': 'service_reminder',
            'customer_name': 'Test Customer',
            'equipment_number': 'EQ-001',
            'service_type': 'preventive_maintenance',
            'days_until_due': 7
        }
        
        email_content = agent.generate_ai_email_content(context)
        print("✅ AI email generation test successful")
        print(f"Generated content length: {len(email_content)} characters")
        
        return agent
        
    except Exception as e:
        print(f"❌ Communication agent launch failed: {e}")
        return None


def launch_operations_agent():
    """Launch the Operations & Data Agent"""
    print("⚙️ Launching Operations & Data Agent...")
    
    try:
        agent = OperationsDataAgent()
        
        # Test service reminder generation
        reminders = agent.generate_service_reminders()
        print(f"✅ Service reminder generation: {len(reminders)} reminders found")
        
        # Test water quality alerts
        alerts = agent.check_water_quality_alerts()
        print(f"✅ Water quality monitoring: {len(alerts)} alerts found")
        
        # Test automated schedule
        schedule = agent.create_automated_reminder_schedule()
        print(f"✅ Automated schedule generated at: {schedule['generated_at']}")
        
        return agent
        
    except Exception as e:
        print(f"❌ Operations agent launch failed: {e}")
        return None


def launch_platform_agent():
    """Launch the Platform & Integration Agent"""
    print("🌐 Launching Platform & Integration Agent...")
    
    try:
        config = {
            'db_path': 'instance/test.db',
            'grandstream': {
                'base_url': os.getenv('GRANDSTREAM_URL', ''),
                'username': os.getenv('GRANDSTREAM_USERNAME', ''),
                'password': os.getenv('GRANDSTREAM_PASSWORD', '')
            }
        }
        
        agent = PlatformIntegrationAgent(config)
        
        # Test analytics dashboard
        dashboard = agent.create_analytics_dashboard()
        if 'error' not in dashboard:
            print("✅ Analytics dashboard creation successful")
        else:
            print(f"⚠️ Dashboard creation failed: {dashboard['error']}")
        
        # Test contact form generation
        contact_form = agent.create_website_contact_form()
        print(f"✅ Contact form generation: {len(contact_form)} characters")
        
        return agent
        
    except Exception as e:
        print(f"❌ Platform agent launch failed: {e}")
        return None


def launch_all_agents():
    """Launch all agents"""
    print("🎯 Launching All Agents...")
    print("=" * 50)
    
    agents = {}
    
    # Launch each agent
    agents['communication'] = launch_communication_agent()
    agents['operations'] = launch_operations_agent()
    agents['platform'] = launch_platform_agent()
    agents['coordinator'] = launch_coordinator()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 AGENT LAUNCH SUMMARY")
    print("=" * 50)
    
    successful_agents = sum(1 for agent in agents.values() if agent is not None)
    total_agents = len(agents)
    
    for name, agent in agents.items():
        status = "✅ SUCCESS" if agent is not None else "❌ FAILED"
        print(f"  {name.capitalize()} Agent: {status}")
    
    print(f"\nOverall: {successful_agents}/{total_agents} agents launched successfully")
    
    if successful_agents == total_agents:
        print("🎉 All agents launched successfully!")
    else:
        print("⚠️ Some agents failed to launch. Check configuration and dependencies.")
    
    return agents


def launch_api_server():
    """Launch the API server"""
    print("🌐 Launching API Server...")
    
    try:
        from flask import Flask
        from agents.platform_integration import PlatformIntegrationAgent
        
        app = Flask(__name__)
        
        # Setup API endpoints
        config = {
            'db_path': 'instance/test.db',
            'grandstream': {
                'base_url': os.getenv('GRANDSTREAM_URL', ''),
                'username': os.getenv('GRANDSTREAM_USERNAME', ''),
                'password': os.getenv('GRANDSTREAM_PASSWORD', '')
            }
        }
        
        platform_agent = PlatformIntegrationAgent(config)
        platform_agent.create_api_endpoints(app)
        
        # Add health check endpoint
        @app.route('/health')
        def health_check():
            return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
        
        print("✅ API server configured successfully")
        print("📡 Available endpoints:")
        print("  - GET /health - Health check")
        print("  - GET /api/v1/equipment - Equipment list")
        print("  - GET /api/v1/analytics/dashboard - Analytics dashboard")
        print("  - POST /api/v1/water-quality - Water quality data")
        print("  - POST /api/v1/website/contact - Contact form")
        
        return app
        
    except Exception as e:
        print(f"❌ API server launch failed: {e}")
        return None


def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description='Operational Suite V2 Feature Launcher')
    parser.add_argument('--mode', choices=['demo', 'coordinator', 'communication', 'operations', 'platform', 'all', 'api'], 
                       default='all', help='Launch mode')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    parser.add_argument('--log-file', help='Log file path')
    parser.add_argument('--port', type=int, default=5000, help='API server port')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    print("🚀 Operational Suite V2 - Feature Launcher")
    print("=" * 50)
    print(f"Mode: {args.mode}")
    print(f"Log Level: {args.log_level}")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 50)
    
    try:
        if args.mode == 'demo':
            launch_demo()
        elif args.mode == 'coordinator':
            launch_coordinator()
        elif args.mode == 'communication':
            launch_communication_agent()
        elif args.mode == 'operations':
            launch_operations_agent()
        elif args.mode == 'platform':
            launch_platform_agent()
        elif args.mode == 'all':
            launch_all_agents()
        elif args.mode == 'api':
            app = launch_api_server()
            if app:
                print(f"\n🌐 Starting API server on port {args.port}...")
                print("Press Ctrl+C to stop the server")
                app.run(host='0.0.0.0', port=args.port, debug=True)
        
        print("\n✅ Launch completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Launch interrupted by user")
    except Exception as e:
        print(f"\n❌ Launch failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 