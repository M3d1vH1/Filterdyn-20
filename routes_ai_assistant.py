"""
AI Assistant Integration Routes
Provides API endpoints for the AI Assistant floating button
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from flask_login import login_required, current_user
from flask_babel import _
from datetime import datetime, timezone
import logging
import os

ai_assistant_bp = Blueprint('ai_assistant', __name__, url_prefix='/ai-assistant')

@ai_assistant_bp.route('/quick-actions')
@login_required
def get_quick_actions():
    """Get quick actions for AI Assistant"""
    actions = [
        {
            'id': 'gmail_inbox',
            'title': _('Gmail Inbox'),
            'description': _('Access Gmail with AI analysis'),
            'icon': 'mail',
            'url': url_for('gmail_enhanced.complete_interface') if 'gmail_enhanced' in current_app.blueprints else url_for('gmail.inbox'),
            'category': 'email'
        },
        {
            'id': 'compose_email',
            'title': _('Compose Email'),
            'description': _('Write emails with AI assistance'),
            'icon': 'edit-3',
            'url': url_for('gmail_enhanced.enhanced_compose') if 'gmail_enhanced' in current_app.blueprints else url_for('gmail.compose'),
            'category': 'email'
        },
        {
            'id': 'create_task',
            'title': _('Create Task'),
            'description': _('Quick task creation'),
            'icon': 'plus-square',
            'url': url_for('main.create_task'),
            'category': 'productivity'
        },
        {
            'id': 'daily_kanban',
            'title': _('Daily Kanban'),
            'description': _('Today\'s task board'),
            'icon': 'columns',
            'url': url_for('main.tasks_kanban'),
            'category': 'productivity'
        },
        {
            'id': 'ai_dictation',
            'title': _('Voice Input'),
            'description': _('Speech to text with AI'),
            'icon': 'mic',
            'action': 'toggleDictation()',
            'category': 'ai'
        }
    ]
    
    return jsonify({
        'success': True,
        'actions': actions
    })

@ai_assistant_bp.route('/status')
@login_required
def get_status():
    """Get AI Assistant status and capabilities"""
    status = {
        'user': {
            'name': current_user.first_name or current_user.username,
            'role': current_user.role,
            'tenant': current_user.tenant.name if current_user.tenant else 'Unknown'
        },
        'capabilities': {
            'dictation': True,
            'gmail_ai': True,
            'task_management': True,
            'gemini_ai': bool(os.environ.get('GOOGLE_GENAI_API_KEY'))
        },
        'quick_stats': {
            'unread_emails': 0,  # Will be populated if Gmail is connected
            'pending_tasks': 0,
            'today_tasks': 0
        }
    }
    
    # Get basic stats
    try:
        from models import Task
        today = datetime.now(timezone.utc).date()
        
        status['quick_stats']['pending_tasks'] = Task.query.filter_by(
            tenant_id=current_user.tenant_id,
            status='pending'
        ).count()
        
        status['quick_stats']['today_tasks'] = Task.query.filter_by(
            tenant_id=current_user.tenant_id
        ).filter(
            Task.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
    except Exception as e:
        logging.error(f"Error getting task stats: {str(e)}")
    
    return jsonify({
        'success': True,
        'status': status
    })