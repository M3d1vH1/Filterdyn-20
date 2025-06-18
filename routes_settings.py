"""
Settings Management Routes
=========================

Flask routes for managing application settings and API integrations.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app import db
from models_settings import AgentConfiguration, APIKeyConfiguration
import os
from agents.gemini_client import GeminiClient
import json

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
@login_required
def index():
    """Settings dashboard"""
    # Get current API configurations
    gemini_config = APIKeyConfiguration.get_config(current_user.tenant_id, 'gemini')
    gmail_config = APIKeyConfiguration.get_config(current_user.tenant_id, 'gmail')
    
    # Get agent configurations
    agents_config = {}
    agent_names = ['communication_ai', 'operations_data', 'platform_integration', 'testing_quality']
    
    for agent_name in agent_names:
        config = AgentConfiguration.get_agent_config(current_user.tenant_id, agent_name)
        agents_config[agent_name] = {
            'enabled': config.is_enabled if config else False,
            'auto_run': config.auto_run_enabled if config else False,
            'interval': config.run_interval_minutes if config else 60,
            'last_run': config.last_run.isoformat() if config and config.last_run else None
        }
    
    return render_template('settings/index.html',
                         gemini_config=gemini_config,
                         gmail_config=gmail_config,
                         agents_config=agents_config)

@settings_bp.route('/api-keys', methods=['POST'])
@login_required
def save_api_keys():
    """Save API key configurations"""
    try:
        # Get form data
        gemini_api_key = request.form.get('gemini_api_key', '').strip()
        gmail_credentials = request.form.get('gmail_credentials', '').strip()
        
        # Validate Gemini API key
        if gemini_api_key:
            try:
                # Test Gemini API key
                test_client = GeminiClient(api_key=gemini_api_key)
                test_response = test_client.generate_content("Hello, respond with 'API key is working'")
                
                # Save Gemini configuration
                gemini_config = APIKeyConfiguration.get_config(current_user.tenant_id, 'gemini')
                if not gemini_config:
                    gemini_config = APIKeyConfiguration(
                        tenant_id=current_user.tenant_id,
                        service_name='gemini'
                    )
                
                gemini_config.is_configured = True
                gemini_config.configuration = {
                    'api_key_set': True,
                    'model': 'gemini-pro',
                    'max_tokens': int(request.form.get('gemini_max_tokens', 1000)),
                    'temperature': float(request.form.get('gemini_temperature', 0.7))
                }
                
                db.session.merge(gemini_config)
                
                # Set environment variable for current session
                os.environ['GEMINI_API_KEY'] = gemini_api_key
                
                flash(_('Gemini API key saved and verified successfully'), 'success')
                
            except Exception as e:
                flash(_('Invalid Gemini API key: %(error)s', error=str(e)), 'error')
                return redirect(url_for('settings.index'))
        
        # Save Gmail configuration
        if gmail_credentials:
            try:
                # Validate JSON format
                json.loads(gmail_credentials)
                
                gmail_config = APIKeyConfiguration.get_config(current_user.tenant_id, 'gmail')
                if not gmail_config:
                    gmail_config = APIKeyConfiguration(
                        tenant_id=current_user.tenant_id,
                        service_name='gmail'
                    )
                
                gmail_config.is_configured = True
                gmail_config.configuration = {
                    'credentials_set': True,
                    'rate_limit': int(request.form.get('gmail_rate_limit', 10)),
                    'batch_size': int(request.form.get('gmail_batch_size', 5))
                }
                
                db.session.merge(gmail_config)
                
                flash(_('Gmail credentials saved successfully'), 'success')
                
            except json.JSONDecodeError:
                flash(_('Invalid Gmail credentials JSON format'), 'error')
                return redirect(url_for('settings.index'))
        
        db.session.commit()
        return redirect(url_for('settings.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(_('Error saving API keys: %(error)s', error=str(e)), 'error')
        return redirect(url_for('settings.index'))

@settings_bp.route('/agents', methods=['POST'])
@login_required
def save_agents_config():
    """Save agent configurations"""
    try:
        # Get form data for each agent
        agent_configs = {
            'communication_ai': {
                'enabled': request.form.get('comm_ai_enabled') == 'on',
                'auto_run': request.form.get('comm_ai_auto_run') == 'on',
                'interval': int(request.form.get('comm_ai_interval', 60)),
                'email_rate_limit': int(request.form.get('comm_ai_rate_limit', 10)),
                'batch_size': int(request.form.get('comm_ai_batch_size', 5))
            },
            'operations_data': {
                'enabled': request.form.get('ops_data_enabled') == 'on',
                'auto_run': request.form.get('ops_data_auto_run') == 'on',
                'interval': int(request.form.get('ops_data_interval', 120)),
                'reminder_days_ahead': int(request.form.get('ops_reminder_days', 30)),
                'alert_threshold': request.form.get('ops_alert_threshold', 'critical')
            },
            'platform_integration': {
                'enabled': request.form.get('platform_enabled') == 'on',
                'auto_run': request.form.get('platform_auto_run') == 'on',
                'interval': int(request.form.get('platform_interval', 300)),
                'cache_duration': int(request.form.get('platform_cache_duration', 300)),
                'max_data_points': int(request.form.get('platform_max_data_points', 1000))
            },
            'testing_quality': {
                'enabled': request.form.get('testing_enabled') == 'on',
                'auto_run': request.form.get('testing_auto_run') == 'on',
                'interval': int(request.form.get('testing_interval', 1440)),
                'test_coverage_threshold': int(request.form.get('testing_coverage_threshold', 80)),
                'performance_threshold': int(request.form.get('testing_performance_threshold', 2000))
            }
        }
        
        # Save configurations
        for agent_name, config_data in agent_configs.items():
            agent_config = AgentConfiguration.get_agent_config(current_user.tenant_id, agent_name)
            
            if not agent_config:
                agent_config = AgentConfiguration(
                    tenant_id=current_user.tenant_id,
                    agent_name=agent_name
                )
            
            agent_config.is_enabled = config_data['enabled']
            agent_config.auto_run_enabled = config_data['auto_run']
            agent_config.run_interval_minutes = config_data['interval']
            
            # Remove enabled, auto_run, and interval from config_data for storage
            storage_config = {k: v for k, v in config_data.items() 
                            if k not in ['enabled', 'auto_run', 'interval']}
            agent_config.configuration = storage_config
            
            db.session.merge(agent_config)
        
        db.session.commit()
        flash(_('Agent configurations saved successfully'), 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(_('Error saving agent configurations: %(error)s', error=str(e)), 'error')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/test-gemini', methods=['POST'])
@login_required
def test_gemini():
    """Test Gemini API connection"""
    try:
        api_key = request.json.get('api_key')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key is required'})
        
        # Test the API key
        client = GeminiClient(api_key=api_key)
        response = client.generate_content("Hello, please respond with 'Gemini API is working correctly'")
        
        return jsonify({
            'success': True,
            'message': 'Gemini API is working correctly',
            'response': response[:100] + '...' if len(response) > 100 else response
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@settings_bp.route('/api/agent-status')
@login_required
def api_agent_status():
    """API endpoint to get agent status"""
    try:
        # Get agent configurations
        agents_status = {}
        agent_names = ['communication_ai', 'operations_data', 'platform_integration', 'testing_quality']
        
        for agent_name in agent_names:
            config = AgentConfiguration.get_agent_config(current_user.tenant_id, agent_name)
            if config:
                agents_status[agent_name] = {
                    'enabled': config.is_enabled,
                    'auto_run': config.auto_run_enabled,
                    'last_run': config.last_run.isoformat() if config.last_run else None,
                    'next_run': config.next_run.isoformat() if config.next_run else None,
                    'status': 'active' if config.is_enabled else 'inactive'
                }
            else:
                agents_status[agent_name] = {
                    'enabled': False,
                    'auto_run': False,
                    'last_run': None,
                    'next_run': None,
                    'status': 'not_configured'
                }
        
        return jsonify(agents_status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500