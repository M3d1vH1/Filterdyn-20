"""
Agent Routes for Filterdyn Operations Suite
==========================================

Flask routes for integrating the multi-agent system with the main application.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_babel import _
from datetime import datetime
import json
import os

from agents.coordinator import AgentCoordinator
from agents.communication_ai import CommunicationAIAgent
from agents.operations_data import OperationsDataAgent
from agents.platform_integration import PlatformIntegrationAgent
from utils import admin_required

agent_bp = Blueprint('agents', __name__, url_prefix='/agents')

# Global coordinator instance
coordinator = None

def get_coordinator():
    """Get or create the agent coordinator"""
    global coordinator
    if coordinator is None:
        config = {
            'db_path': os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/filterdyn'),
            'gmail_credentials_path': 'credentials.json',
            'gmail_token_path': 'token.json',
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'gemini_model': os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'),
            'gemini_max_tokens': int(os.getenv('GEMINI_MAX_TOKENS', '1000')),
            'gemini_temperature': float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
            'gemini_top_p': float(os.getenv('GEMINI_TOP_P', '0.8')),
            'gemini_top_k': int(os.getenv('GEMINI_TOP_K', '40')),
            'default_from_email': 'noreply@filterdyn.com'
        }
        coordinator = AgentCoordinator(config)
    return coordinator

@agent_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Agent system dashboard"""
    try:
        coord = get_coordinator()
        agent_status = coord.get_agent_status()
        system_health = coord.get_system_health_report()
        
        return render_template('agents/dashboard.html',
                             agent_status=agent_status,
                             system_health=system_health)
    except Exception as e:
        flash(_('Error loading agent dashboard: %(error)s', error=str(e)), 'error')
        return redirect(url_for('main.dashboard'))

@agent_bp.route('/communication')
@login_required
@admin_required
def communicationai():
    """Communication & AI Agent interface"""
    try:
        coord = get_coordinator()
        comm_agent = coord.agents.get('communication_ai')
        
        if comm_agent:
            status = coord.agent_status.get('communication_ai')
            return render_template('agents/communication.html',
                                 agent=comm_agent,
                                 status=status)
        else:
            flash(_('Communication agent not available'), 'error')
            return redirect(url_for('agents.dashboard'))
    except Exception as e:
        flash(_('Error loading communication agent: %(error)s', error=str(e)), 'error')
        return redirect(url_for('agents.dashboard'))

@agent_bp.route('/operations')
@login_required
@admin_required
def operations_agent():
    """Operations & Data Agent interface"""
    try:
        coord = get_coordinator()
        ops_agent = coord.agents.get('operations_data')
        
        if ops_agent:
            # Get service reminders
            reminders = ops_agent.get_upcoming_service_reminders()
            alerts = ops_agent.get_water_quality_alerts()
            
            return render_template('agents/operations.html',
                                 reminders=reminders,
                                 alerts=alerts)
        else:
            flash(_('Operations agent not available'), 'error')
            return redirect(url_for('agents.dashboard'))
    except Exception as e:
        flash(_('Error loading operations agent: %(error)s', error=str(e)), 'error')
        return redirect(url_for('agents.dashboard'))

@agent_bp.route('/analytics')
@login_required
@admin_required
def analytics_dashboard():
    """Analytics dashboard from Platform Integration Agent"""
    try:
        coord = get_coordinator()
        platform_agent = coord.agents.get('platform_integration')
        
        if platform_agent:
            dashboard_data = platform_agent.create_analytics_dashboard()
            return render_template('agents/analytics.html',
                                 dashboard_data=dashboard_data)
        else:
            flash(_('Platform integration agent not available'), 'error')
            return redirect(url_for('agents.dashboard'))
    except Exception as e:
        flash(_('Error loading analytics dashboard: %(error)s', error=str(e)), 'error')
        return redirect(url_for('agents.dashboard'))

@agent_bp.route('/send-email', methods=['POST'])
@login_required
@admin_required
def send_email():
    """Send email via Communication Agent"""
    try:
        data = request.get_json()
        
        coord = get_coordinator()
        comm_agent = coord.agents.get('communication_ai')
        
        if not comm_agent:
            return jsonify({'success': False, 'error': 'Communication agent not available'})
        
        # Send email
        result = comm_agent.send_email(
            to_email=data.get('to_email'),
            subject=data.get('subject'),
            content=data.get('content'),
            email_type=data.get('email_type', 'general')
        )
        
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@agent_bp.route('/generate-service-reports', methods=['POST'])
@login_required
@admin_required
def generate_service_reports():
    """Generate service reports via Operations Agent"""
    try:
        coord = get_coordinator()
        ops_agent = coord.agents.get('operations_data')
        
        if not ops_agent:
            return jsonify({'success': False, 'error': 'Operations agent not available'})
        
        # Generate reports
        reports = ops_agent.generate_service_reports()
        
        return jsonify({'success': True, 'reports': reports})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@agent_bp.route('/api/health')
def api_health():
    """API health check endpoint"""
    try:
        coord = get_coordinator()
        health_report = coord.get_system_health_report()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'agents': health_report
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@agent_bp.route('/api/analytics/dashboard')
@login_required
def api_analytics_dashboard():
    """API endpoint for analytics dashboard data"""
    try:
        coord = get_coordinator()
        platform_agent = coord.agents.get('platform_integration')
        
        if platform_agent:
            dashboard_data = platform_agent.create_analytics_dashboard()
            return jsonify(dashboard_data)
        else:
            return jsonify({'error': 'Platform integration agent not available'}), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500