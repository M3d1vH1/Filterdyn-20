from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import login_required, current_user
from flask_babel import _, get_locale
from models import GmailAccount, EmailBusinessAssociation, AIEmailInteraction
from gmail_service import GmailService
from gmail_ai_service import GmailAIService
from app import db
from werkzeug.utils import secure_filename
import os
import io
import json

gmail_bp = Blueprint('gmail', __name__, url_prefix='/gmail')

@gmail_bp.route('/connect')
@login_required
def connect():
    """Initiate Gmail OAuth connection"""
    try:
        # Use actual deployment domain
        if 'replit.app' in request.host or 'repl.co' in request.host:
            redirect_uri = f"https://filterdyn.replit.app/gmail/oauth-callback"
        else:
            # Fallback for development
            redirect_uri = url_for('gmail.oauth_callback', _external=True)
            
        flow = GmailService.get_flow(redirect_uri)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        session['gmail_oauth_state'] = state
        return redirect(authorization_url)
        
    except Exception as e:
        flash(f'Error connecting to Gmail: {str(e)}', 'error')
        return redirect(url_for('main.ai_assistant'))

@gmail_bp.route('/oauth-callback')
def oauth_callback():
    """Handle Gmail OAuth callback"""
    try:
        # Check if user is authenticated
        if not current_user.is_authenticated:
            flash(_('Please log in first'), 'error')
            return redirect(url_for('auth.login'))
            
        state = session.get('gmail_oauth_state')
        error = request.args.get('error')
        
        if error:
            flash(f'Gmail authentication failed: {error}', 'error')
            return redirect(url_for('main.ai_assistant'))
            
        if not state:
            flash(_('Invalid OAuth state'), 'error')
            return redirect(url_for('main.ai_assistant'))
        
        # Use actual deployment domain (same as connect())
        if 'replit.app' in request.host or 'repl.co' in request.host:
            redirect_uri = f"https://filterdyn.replit.app/gmail/oauth-callback"
        else:
            redirect_uri = url_for('gmail.oauth_callback', _external=True)
            
        flow = GmailService.get_flow(redirect_uri)
        flow.fetch_token(authorization_response=request.url)
        
        credentials = flow.credentials
        account = GmailService.store_credentials(
            current_user.id,
            current_user.tenant_id,
            credentials
        )
        
        # Store session info - remove session-based tracking, use database only
        # Session cleared - using database-only approach for Phase 3
        
        flash(_('Gmail connected successfully!'), 'success')
        
        # Initial sync
        try:
            GmailService.sync_messages(account, max_results=20)
            flash(_('Initial email sync completed'), 'info')
        except Exception as sync_error:
            flash(f'Connected but sync failed: {str(sync_error)}', 'warning')
        
        return redirect(url_for('gmail.inbox'))
        
    except Exception as e:
        flash(f'OAuth callback error: {str(e)}', 'error')
        return redirect(url_for('main.ai_assistant'))

@gmail_bp.route('/disconnect')
@login_required
def disconnect():
    """Disconnect Gmail account"""
    try:
        account = GmailService.get_user_account(current_user.id, current_user.tenant_id)
        if account:
            account.sync_enabled = False
            db.session.commit()
        
        # Clear any legacy session data
        session.pop('google_connected', None)
        session.pop('google_email', None)
        session.pop('google_access_token', None)
        session.pop('google_refresh_token', None)
        
        flash(_('Gmail account disconnected'), 'info')
        return redirect(url_for('main.ai_assistant'))
        
    except Exception as e:
        flash(f'Error disconnecting: {str(e)}', 'error')
        return redirect(url_for('gmail.inbox'))

@gmail_bp.route('/inbox')
@login_required
def inbox():
    """Gmail inbox view"""
    if current_user.role not in ['admin', 'superadmin', 'manager']:
        flash(_('Access denied. Gmail integration requires admin or manager permissions.'), 'error')
        return redirect(url_for('main.dashboard'))
    
    account = GmailService.get_user_account(current_user.id, current_user.tenant_id)
    if not account:
        flash(_('No Gmail account connected. Please connect your account first.'), 'warning')
        return redirect(url_for('main.gmail_inbox'))
    
    try:
        # Get email messages grouped by thread
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '')
        
        # Use existing Gmail structure - get messages from Gmail API on demand
        messages = []
        try:
            # Fetch recent messages from Gmail API
            message_count = GmailService.sync_messages(account, max_results=20)
            flash(f'Synced {message_count} messages from Gmail', 'info')
        except Exception as sync_error:
            flash(f'Gmail sync error: {str(sync_error)}', 'warning')
        
        # For now, create a simple pagination-like object
        class SimplePagination:
            def __init__(self, items):
                self.items = items
                self.total = len(items)
                self.pages = 1
                self.page = 1
                self.has_prev = False
                self.has_next = False
                self.prev_num = None
                self.next_num = None
                
            def iter_pages(self):
                return [1]
        
        messages = SimplePagination([])
        
        return render_template('gmail/inbox.html', 
                             messages=messages, 
                             account=account,
                             search_query=search_query)
    
    except Exception as e:
        flash(f'Error loading inbox: {str(e)}', 'error')
        return redirect(url_for('main.ai_assistant'))

@gmail_bp.route('/thread/<string:thread_id>')
@login_required
def view_thread(thread_id):
    """View email thread (simplified)"""
    account = GmailService.get_user_account(current_user.id, current_user.tenant_id)
    if not account:
        flash(_('No Gmail account connected'), 'error')
        return redirect(url_for('gmail.inbox'))
    
    # Simplified thread view - redirect to message view for now
    flash(_('Thread view coming soon - redirected to inbox'), 'info')
    return redirect(url_for('gmail.inbox'))

@gmail_bp.route('/message/<int:message_id>')
@login_required
def view_message(message_id):
    """View single message"""
    account = GmailService.get_user_account(current_user.id, current_user.tenant_id)
    if not account:
        flash(_('No Gmail account connected'), 'error')
        return redirect(url_for('gmail.inbox'))
    
    # Simplified message view for now
    flash(_('Individual message view coming soon - please use Gmail interface'), 'info')
    return redirect(url_for('gmail.inbox'))

@gmail_bp.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    """Compose new email"""
    account = GmailService.get_user_account(current_user.id, current_user.tenant_id)
    if not account:
        flash(_('No Gmail account connected'), 'error')
        return redirect(url_for('gmail.inbox'))
    
    if request.method == 'POST':
        try:
            to_email = request.form.get('to')
            cc_email = request.form.get('cc')
            bcc_email = request.form.get('bcc')
            subject = request.form.get('subject')
            body = request.form.get('body')
            
            # Handle attachments
            attachments = []
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file.filename:
                        filename = secure_filename(file.filename)
                        attachments.append({
                            'filename': filename,
                            'data': file.read()
                        })
            
            # Send email
            result = GmailService.send_email(
                account=account,
                to_email=to_email,
                subject=subject,
                body=body,
                cc=cc_email,
                bcc=bcc_email,
                attachments=attachments
            )
            
            flash(_('Email sent successfully!'), 'success')
            return redirect(url_for('gmail.inbox'))
            
        except Exception as e:
            flash(f'Error sending email: {str(e)}', 'error')
    
    # Handle reply-to
    reply_to_id = request.args.get('reply_to')
    original_message = None
    if reply_to_id:
        original_message = EmailMessage.query.join(EmailThread).filter(
            EmailMessage.id == reply_to_id,
            EmailThread.gmail_account_id == account.id
        ).first()
    
    return render_template('gmail/compose.html', 
                         original_message=original_message,
                         account=account)

@gmail_bp.route('/sync')
@login_required
def sync():
    """Manual email sync"""
    account = GmailService.get_user_account(current_user.id, current_user.tenant_id)
    if not account:
        return jsonify({'error': 'No Gmail account connected'}), 400
    
    try:
        message_count = GmailService.sync_messages(account, max_results=50)
        return jsonify({'success': True, 'messages_synced': message_count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gmail_bp.route('/attachment/<int:attachment_id>')
@login_required
def download_attachment(attachment_id):
    """Download attachment"""
    account = GmailService.get_user_account(current_user.id, current_user.tenant_id)
    if not account:
        flash(_('No Gmail account connected'), 'error')
        return redirect(url_for('gmail.inbox'))
    
    attachment = EmailAttachment.query.join(EmailMessage, EmailThread).filter(
        EmailAttachment.id == attachment_id,
        EmailThread.gmail_account_id == account.id
    ).first_or_404()
    
    return send_file(
        io.BytesIO(attachment.file_data),
        as_attachment=True,
        download_name=attachment.filename,
        mimetype=attachment.mime_type
    )

# AI API Routes
@gmail_bp.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    """Analyze email content with AI"""
    try:
        data = request.get_json()
        email_text = data.get('email_text', '')
        language = data.get('language') or str(get_locale())
        
        if not email_text.strip():
            return jsonify({'error': 'No email content provided'}), 400
        
        analysis = GmailAIService.analyze_email_content(email_text, language)
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gmail_bp.route('/api/suggest', methods=['POST'])
@login_required
def api_suggest():
    """Get AI response suggestion"""
    try:
        data = request.get_json()
        email_text = data.get('email_text', '')
        context = data.get('context')
        language = data.get('language') or str(get_locale())
        tone = data.get('tone', 'professional')
        
        if not email_text.strip():
            return jsonify({'error': 'No email content provided'}), 400
        
        suggestion = GmailAIService.suggest_response(email_text, context, language, tone)
        return jsonify({'suggestion': suggestion})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gmail_bp.route('/api/templates', methods=['POST'])
@login_required
def api_templates():
    """Get email template suggestions"""
    try:
        data = request.get_json()
        email_text = data.get('email_text', '')
        language = data.get('language') or str(get_locale())
        
        templates = GmailAIService.suggest_templates(email_text, language)
        return jsonify(templates)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gmail_bp.route('/api/entities', methods=['POST'])
@login_required
def api_extract_entities():
    """Extract business entities from email"""
    try:
        data = request.get_json()
        email_text = data.get('email_text', '')
        
        entities = GmailAIService.extract_business_entities(email_text)
        return jsonify(entities)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gmail_bp.route('/api/feedback', methods=['POST'])
@login_required
def api_feedback():
    """Provide feedback on AI suggestions"""
    try:
        data = request.get_json()
        interaction_id = data.get('interaction_id')
        feedback = data.get('feedback')  # accepted, edited, rejected
        effectiveness_score = data.get('effectiveness_score')
        
        success = GmailAIService.provide_feedback(interaction_id, feedback, effectiveness_score)
        return jsonify({'success': success})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gmail_bp.route('/api/search')
@login_required
def api_search():
    """Search emails API"""
    try:
        query = request.args.get('q', '')
        account = GmailService.get_user_account(current_user.id, current_user.tenant_id)
        
        if not account:
            return jsonify({'error': 'No Gmail account connected'}), 400
        
        # Simplified search - return empty for now
        return jsonify([{
            'message_id': 'demo1',
            'subject': 'Demo Gmail Integration',
            'sender': 'demo@example.com',
            'snippet': 'Gmail integration is being configured...',
            'date': '2025-06-24T18:30:00Z',
            'is_read': False
        }])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gmail_bp.route('/api/stats')
@login_required  
def api_stats():
    """Get Gmail and AI statistics"""
    try:
        account = GmailService.get_user_account(current_user.id, current_user.tenant_id)
        if not account:
            return jsonify({'error': 'No Gmail account connected'}), 400
        
        # Simplified email stats
        total_threads = 0
        unread_threads = 0
        total_messages = 0
        
        # AI stats
        ai_stats = GmailAIService.get_learning_stats(current_user.tenant_id, current_user.id)
        
        return jsonify({
            'email_stats': {
                'total_threads': total_threads,
                'unread_threads': unread_threads,
                'total_messages': total_messages,
                'last_sync': account.last_sync_at.isoformat() if account.last_sync_at else None
            },
            'ai_stats': ai_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500