"""
Enhanced Gmail Routes with AI Integration
Integrates with existing Filterdyn Gmail functionality
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user
from flask_babel import _, get_locale
from datetime import datetime, timezone
import os
import logging
# Use existing Gmail models from existing codebase
try:
    from models import GmailAccount, GmailMessage, GmailAttachment, AIEmailAnalysis
except ImportError:
    # Create placeholder classes if models don't exist
    GmailAccount = GmailMessage = GmailAttachment = AIEmailAnalysis = None
from gmail_ai_enhanced_service import GmailAIEnhancedService
from gmail_service import GmailService
from app import db

gmail_enhanced_bp = Blueprint('gmail_enhanced', __name__, url_prefix='/gmail')

@gmail_enhanced_bp.route('/ai/analyze', methods=['POST'])
@login_required
def ai_analyze_email():
    """Analyze email content with enhanced Gemini AI"""
    try:
        data = request.get_json()
        email_text = data.get('email_text', '')
        language = data.get('language', str(get_locale()))
        
        if not email_text.strip():
            return jsonify({'error': _('Email content is required')}), 400
        
        # Analyze with enhanced AI service
        analysis = GmailAIEnhancedService.analyze_email_content(email_text, language)
        
        if 'error' in analysis:
            return jsonify(analysis), 500
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logging.error(f"AI analysis error: {str(e)}")
        return jsonify({'error': _('Analysis failed')}), 500

@gmail_enhanced_bp.route('/ai/suggest', methods=['POST'])
@login_required
def ai_suggest_response():
    """Generate AI response suggestions with enhanced context"""
    try:
        data = request.get_json()
        email_text = data.get('email_text', '')
        context = data.get('context', '')
        language = data.get('language', str(get_locale()))
        tone = data.get('tone', 'professional')
        
        if not email_text.strip():
            return jsonify({'error': _('Email content is required')}), 400
        
        # Generate suggestions with enhanced AI service
        suggestion = GmailAIEnhancedService.suggest_response(email_text, context, language, tone)
        
        if 'error' in suggestion:
            return jsonify(suggestion), 500
        
        return jsonify({
            'success': True,
            'suggestion': suggestion,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logging.error(f"AI suggestion error: {str(e)}")
        return jsonify({'error': _('Suggestion failed')}), 500

@gmail_enhanced_bp.route('/ai/templates', methods=['POST'])
@login_required
def ai_suggest_templates():
    """Get AI-powered email template suggestions"""
    try:
        data = request.get_json()
        email_text = data.get('email_text', '')
        language = data.get('language', str(get_locale()))
        
        if not email_text.strip():
            return jsonify({'error': _('Email content is required')}), 400
        
        templates = GmailAIEnhancedService.suggest_templates(email_text, language)
        
        if 'error' in templates:
            return jsonify(templates), 500
        
        return jsonify({
            'success': True,
            'templates': templates,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logging.error(f"Template suggestion error: {str(e)}")
        return jsonify({'error': _('Template suggestion failed')}), 500

@gmail_enhanced_bp.route('/ai/extract-entities', methods=['POST'])
@login_required
def ai_extract_entities():
    """Extract business entities and suggest database links"""
    try:
        data = request.get_json()
        email_text = data.get('email_text', '')
        
        if not email_text.strip():
            return jsonify({'error': _('Email content is required')}), 400
        
        entities = GmailAIEnhancedService.extract_business_entities(email_text)
        
        if 'error' in entities:
            return jsonify(entities), 500
        
        return jsonify({
            'success': True,
            'entities': entities,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logging.error(f"Entity extraction error: {str(e)}")
        return jsonify({'error': _('Entity extraction failed')}), 500

@gmail_enhanced_bp.route('/ai/feedback', methods=['POST'])
@login_required
def ai_provide_feedback():
    """Store user feedback on AI suggestions"""
    try:
        data = request.get_json()
        interaction_id = data.get('interaction_id')
        feedback = data.get('feedback', '')
        rating = data.get('rating')
        
        if not interaction_id:
            return jsonify({'error': _('Interaction ID is required')}), 400
        
        success = GmailAIEnhancedService.provide_feedback(interaction_id, feedback, rating)
        
        if success:
            return jsonify({
                'success': True,
                'message': _('Feedback stored successfully')
            })
        else:
            return jsonify({'error': _('Failed to store feedback')}), 500
        
    except Exception as e:
        logging.error(f"Feedback storage error: {str(e)}")
        return jsonify({'error': _('Feedback storage failed')}), 500

@gmail_enhanced_bp.route('/ai/stats')
@login_required
def ai_learning_stats():
    """Get AI learning and usage statistics"""
    try:
        user_id = request.args.get('user_id', current_user.id, type=int)
        
        # Only allow users to see their own stats or admins to see all
        if user_id != current_user.id and current_user.role not in ['admin', 'superadmin']:
            return jsonify({'error': _('Access denied')}), 403
        
        stats = GmailAIEnhancedService.get_learning_stats(current_user.tenant_id, user_id)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logging.error(f"Stats retrieval error: {str(e)}")
        return jsonify({'error': _('Failed to retrieve stats')}), 500

@gmail_enhanced_bp.route('/message/<message_id>/link', methods=['POST'])
@login_required
def link_message_to_entity():
    """Link Gmail message to business entity (customer, order, quote, task)"""
    try:
        data = request.get_json()
        entity_type = data.get('entity_type')  # customer, order, quote, task
        entity_id = data.get('entity_id')
        
        if not entity_type or not entity_id:
            return jsonify({'error': _('Entity type and ID are required')}), 400
        
        # Get the message
        message = GmailMessage.query.filter_by(
            message_id=message_id
        ).join(GmailAccount).filter(
            GmailAccount.tenant_id == current_user.tenant_id
        ).first()
        
        if not message:
            return jsonify({'error': _('Message not found')}), 404
        
        # Link to entity
        if entity_type == 'customer':
            message.customer_id = entity_id
        elif entity_type == 'order':
            message.order_id = entity_id
        elif entity_type == 'quote':
            message.quote_id = entity_id
        elif entity_type == 'task':
            message.task_id = entity_id
        else:
            return jsonify({'error': _('Invalid entity type')}), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': _('Message linked successfully')
        })
        
    except Exception as e:
        logging.error(f"Message linking error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': _('Failed to link message')}), 500

@gmail_enhanced_bp.route('/enhanced-compose')
@login_required
def enhanced_compose():
    """Enhanced compose page with AI features"""
    # Check permissions
    if current_user.role not in ['admin', 'superadmin', 'manager']:
        flash(_('Access denied. Gmail integration requires admin or manager permissions.'), 'error')
        return redirect(url_for('main.dashboard'))
    
    # Check if user has connected Gmail account
    account = GmailService.get_user_account(current_user.id, current_user.tenant_id)
    if not account:
        flash(_('No Gmail account connected. Please connect your account first.'), 'warning')
        return redirect(url_for('gmail.connect'))
    
    return render_template('gmail/enhanced_compose.html',
                         account=account,
                         current_locale=str(get_locale()))

@gmail_enhanced_bp.route('/complete-interface')
@login_required
def complete_interface():
    """Complete Gmail interface with full functionality"""
    # Check permissions
    if current_user.role not in ['admin', 'superadmin', 'manager']:
        flash(_('Access denied. Gmail integration requires admin or manager permissions.'), 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get Gmail account if it exists, otherwise show connection interface
    try:
        account = GmailService.get_user_account(current_user.id, current_user.tenant_id) if GmailService else None
    except Exception as e:
        current_app.logger.error(f"Gmail service error: {e}")
        account = None
    
    return render_template('gmail/complete_interface.html',
                         account=account,
                         current_locale=str(get_locale()))

@gmail_enhanced_bp.route('/enhanced-inbox')
@login_required
def enhanced_inbox():
    """Enhanced inbox with AI analysis features"""
    # Check permissions
    if current_user.role not in ['admin', 'superadmin', 'manager']:
        flash(_('Access denied. Gmail integration requires admin or manager permissions.'), 'error')
        return redirect(url_for('main.dashboard'))
    
    account = GmailService.get_user_account(current_user.id, current_user.tenant_id)
    if not account:
        flash(_('No Gmail account connected. Please connect your account first.'), 'warning')
        return redirect(url_for('gmail.connect'))
    
    try:
        # Get messages with AI analysis data
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        messages = GmailMessage.query.filter_by(
            gmail_account_id=account.id
        ).outerjoin(AIEmailAnalysis).order_by(
            GmailMessage.received_at.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('gmail/enhanced_inbox.html',
                             messages=messages,
                             account=account,
                             current_locale=str(get_locale()))
        
    except Exception as e:
        logging.error(f"Enhanced inbox error: {str(e)}")
        flash(_('Error loading inbox'), 'error')
        return redirect(url_for('main.dashboard'))

@gmail_enhanced_bp.route('/message/<message_id>/enhanced')
@login_required
def enhanced_message_view():
    """Enhanced message view with AI analysis and business entity linking"""
    # Check permissions
    if current_user.role not in ['admin', 'superadmin', 'manager']:
        flash(_('Access denied'), 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Get message with analysis
        message = GmailMessage.query.filter_by(
            message_id=message_id
        ).join(GmailAccount).filter(
            GmailAccount.tenant_id == current_user.tenant_id
        ).first()
        
        if not message:
            flash(_('Message not found'), 'error')
            return redirect(url_for('gmail_enhanced.enhanced_inbox'))
        
        # Get or create AI analysis
        analysis = AIEmailAnalysis.query.filter_by(
            gmail_message_id=message.id
        ).first()
        
        # Auto-analyze if not done yet
        if not analysis and message.body_plain:
            try:
                analysis_data = GmailAIEnhancedService.analyze_email_content(
                    message.body_plain or message.snippet
                )
                if 'error' not in analysis_data:
                    analysis = AIEmailAnalysis(
                        gmail_message_id=message.id,
                        tenant_id=current_user.tenant_id,
                        analysis_type='auto',
                        sentiment=analysis_data.get('sentiment'),
                        intent=analysis_data.get('intent'),
                        entities=analysis_data.get('entities'),
                        key_info=analysis_data.get('key_info'),
                        confidence_score=analysis_data.get('confidence_score', 0.5)
                    )
                    db.session.add(analysis)
                    db.session.commit()
            except Exception as e:
                logging.error(f"Auto-analysis error: {str(e)}")
        
        return render_template('gmail/enhanced_message.html',
                             message=message,
                             analysis=analysis,
                             current_locale=str(get_locale()))
        
    except Exception as e:
        logging.error(f"Enhanced message view error: {str(e)}")
        flash(_('Error loading message'), 'error')
        return redirect(url_for('gmail_enhanced.enhanced_inbox'))