"""
Gmail Integration Routes
Handles all Gmail-related API endpoints and views
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from flask_babel import _, get_locale
from datetime import datetime, timezone, timedelta
from services.gmail_service import GmailService
from utils.ai_processor import AIEmailProcessor
from models import (GmailAccount, EmailMessage, EmailThread, EmailTemplate, 
                   EmailAttachment, Customer, Quote, Order)
from app import db
from utils import admin_required, manager_required
import json
import os
import logging

logger = logging.getLogger(__name__)

gmail_bp = Blueprint('gmail', __name__, url_prefix='/gmail')

@gmail_bp.route('/')
@login_required
def inbox():
    """Main Gmail inbox interface"""
    gmail_accounts = GmailAccount.query.filter_by(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        is_active=True
    ).all()
    
    if not gmail_accounts:
        return redirect(url_for('gmail.setup'))
    
    # Get primary account or first active account
    primary_account = gmail_accounts[0]
    
    return render_template('gmail/inbox.html', 
                         gmail_accounts=gmail_accounts,
                         primary_account=primary_account)

@gmail_bp.route('/setup')
@login_required
def setup():
    """Gmail account setup page"""
    gmail_accounts = GmailAccount.query.filter_by(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    ).all()
    
    return render_template('gmail/setup.html', gmail_accounts=gmail_accounts)

@gmail_bp.route('/connect')
@login_required
def connect():
    """Initiate Gmail OAuth connection"""
    gmail_service = GmailService(current_user.id, current_user.tenant_id)
    
    redirect_uri = url_for('gmail.oauth_callback', _external=True)
    auth_url = gmail_service.get_authorization_url(redirect_uri)
    
    return redirect(auth_url)

@gmail_bp.route('/oauth-callback')
@login_required
def oauth_callback():
    """Handle Gmail OAuth callback"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(_('Gmail connection failed: {}').format(error), 'error')
        return redirect(url_for('gmail.setup'))
    
    if not code:
        flash(_('No authorization code received'), 'error')
        return redirect(url_for('gmail.setup'))
    
    gmail_service = GmailService(current_user.id, current_user.tenant_id)
    redirect_uri = url_for('gmail.oauth_callback', _external=True)
    
    if gmail_service.handle_oauth_callback(code, redirect_uri):
        flash(_('Gmail account connected successfully!'), 'success')
        return redirect(url_for('gmail.inbox'))
    else:
        flash(_('Failed to connect Gmail account'), 'error')
        return redirect(url_for('gmail.setup'))

@gmail_bp.route('/disconnect/<int:account_id>')
@login_required
def disconnect(account_id):
    """Disconnect Gmail account"""
    gmail_account = GmailAccount.query.filter_by(
        id=account_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    ).first_or_404()
    
    gmail_account.is_active = False
    gmail_account.access_token = None
    gmail_account.refresh_token = None
    db.session.commit()
    
    flash(_('Gmail account disconnected'), 'info')
    return redirect(url_for('gmail.setup'))

@gmail_bp.route('/api/sync/<int:account_id>')
@login_required
def sync_emails(account_id):
    """Sync emails from Gmail API"""
    gmail_account = GmailAccount.query.filter_by(
        id=account_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    ).first_or_404()
    
    gmail_service = GmailService(current_user.id, current_user.tenant_id)
    result = gmail_service.sync_emails(account_id)
    
    if result['success']:
        gmail_account.last_sync = datetime.now(timezone.utc)
        db.session.commit()
    
    return jsonify(result)

@gmail_bp.route('/api/threads/<int:account_id>')
@login_required
def get_threads(account_id):
    """Get email threads for inbox view"""
    gmail_account = GmailAccount.query.filter_by(
        id=account_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    ).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get threads from database
    threads_query = db.session.query(EmailThread).filter_by(
        tenant_id=current_user.tenant_id,
        gmail_account_id=account_id
    ).order_by(EmailThread.last_message_date.desc())
    
    threads = threads_query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    thread_data = []
    for thread in threads.items:
        # Get latest message for preview
        latest_message = EmailMessage.query.filter_by(
            thread_id=thread.id
        ).order_by(EmailMessage.received_date.desc()).first()
        
        thread_info = {
            'id': thread.id,
            'gmail_thread_id': thread.gmail_thread_id,
            'subject': thread.subject,
            'participants': json.loads(thread.participants or '[]'),
            'message_count': thread.message_count,
            'last_message_date': thread.last_message_date.isoformat() if thread.last_message_date else None,
            'is_important': thread.is_important,
            'category': thread.thread_category,
            'sentiment': thread.thread_sentiment,
            'customer_id': thread.customer_id,
            'preview': latest_message.body_text[:100] if latest_message and latest_message.body_text else '',
            'has_unread': any(not msg.is_read for msg in thread.messages)
        }
        thread_data.append(thread_info)
    
    return jsonify({
        'success': True,
        'threads': thread_data,
        'pagination': {
            'page': threads.page,
            'pages': threads.pages,
            'per_page': threads.per_page,
            'total': threads.total,
            'has_next': threads.has_next,
            'has_prev': threads.has_prev
        }
    })

@gmail_bp.route('/api/thread/<int:thread_id>/messages')
@login_required
def get_thread_messages(thread_id):
    """Get all messages in a thread"""
    thread = EmailThread.query.filter_by(
        id=thread_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()
    
    messages = EmailMessage.query.filter_by(
        thread_id=thread_id
    ).order_by(EmailMessage.received_date.asc()).all()
    
    message_data = []
    for msg in messages:
        message_info = {
            'id': msg.id,
            'gmail_id': msg.gmail_id,
            'subject': msg.subject,
            'sender': msg.sender,
            'recipient': msg.recipient,
            'cc': msg.cc,
            'bcc': msg.bcc,
            'body_text': msg.body_text,
            'body_html': msg.body_html,
            'received_date': msg.received_date.isoformat(),
            'is_read': msg.is_read,
            'is_important': msg.is_important,
            'ai_category': msg.ai_category,
            'ai_sentiment': msg.ai_sentiment,
            'ai_summary': msg.ai_summary,
            'attachments': [{
                'id': att.id,
                'filename': att.filename,
                'mime_type': att.mime_type,
                'size': att.size
            } for att in msg.attachments]
        }
        message_data.append(message_info)
    
    # Mark messages as read
    for msg in messages:
        if not msg.is_read:
            msg.is_read = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'thread': {
            'id': thread.id,
            'subject': thread.subject,
            'participants': json.loads(thread.participants or '[]'),
            'customer_id': thread.customer_id,
            'quote_id': thread.quote_id,
            'order_id': thread.order_id
        },
        'messages': message_data
    })

@gmail_bp.route('/api/send', methods=['POST'])
@login_required
def send_email():
    """Send an email through Gmail"""
    data = request.get_json()
    
    gmail_account_id = data.get('gmail_account_id')
    to = data.get('to')
    subject = data.get('subject')
    body = data.get('body')
    cc = data.get('cc')
    bcc = data.get('bcc')
    reply_to_thread_id = data.get('reply_to_thread_id')
    
    if not all([gmail_account_id, to, subject, body]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Verify account ownership
    gmail_account = GmailAccount.query.filter_by(
        id=gmail_account_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    ).first()
    
    if not gmail_account:
        return jsonify({'success': False, 'error': 'Gmail account not found'}), 404
    
    gmail_service = GmailService(current_user.id, current_user.tenant_id)
    result = gmail_service.send_email(
        gmail_account_id=gmail_account_id,
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        reply_to_id=reply_to_thread_id
    )
    
    return jsonify(result)

@gmail_bp.route('/api/search/<int:account_id>')
@login_required
def search_emails(account_id):
    """Search emails"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'success': False, 'error': 'Search query required'}), 400
    
    gmail_account = GmailAccount.query.filter_by(
        id=account_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Search in database first
    search_results = EmailMessage.query.filter(
        EmailMessage.gmail_account_id == account_id,
        db.or_(
            EmailMessage.subject.ilike(f'%{query}%'),
            EmailMessage.body_text.ilike(f'%{query}%'),
            EmailMessage.sender.ilike(f'%{query}%')
        )
    ).order_by(EmailMessage.received_date.desc()).limit(50).all()
    
    results = []
    for msg in search_results:
        results.append({
            'id': msg.id,
            'gmail_id': msg.gmail_id,
            'subject': msg.subject,
            'sender': msg.sender,
            'received_date': msg.received_date.isoformat(),
            'preview': (msg.body_text or '')[:150],
            'thread_id': msg.thread_id
        })
    
    return jsonify({
        'success': True,
        'results': results,
        'count': len(results)
    })

@gmail_bp.route('/api/ai/suggest-response', methods=['POST'])
@login_required
def suggest_response():
    """Get AI-powered response suggestions"""
    data = request.get_json()
    message_id = data.get('message_id')
    
    if not message_id:
        return jsonify({'success': False, 'error': 'Message ID required'}), 400
    
    message = EmailMessage.query.filter_by(
        id=message_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()
    
    # Prepare email data for AI
    email_data = {
        'subject': message.subject,
        'sender': message.sender,
        'recipient': message.recipient,
        'body_text': message.body_text,
        'body_html': message.body_html,
        'received_date': message.received_date
    }
    
    # Get business context
    context = {}
    if message.customer_id:
        customer = Customer.query.get(message.customer_id)
        if customer:
            context['customer_info'] = {
                'name': customer.name,
                'email': customer.email,
                'industry': customer.industry
            }
    
    ai_processor = AIEmailProcessor()
    suggestions = ai_processor.generate_response_suggestion(email_data, context)
    
    return jsonify(suggestions)

@gmail_bp.route('/api/associate-customer', methods=['POST'])
@login_required
def associate_customer():
    """Associate email thread with a customer"""
    data = request.get_json()
    thread_id = data.get('thread_id')
    customer_id = data.get('customer_id')
    
    if not all([thread_id, customer_id]):
        return jsonify({'success': False, 'error': 'Thread ID and Customer ID required'}), 400
    
    # Verify thread ownership
    thread = EmailThread.query.filter_by(
        id=thread_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()
    
    # Verify customer ownership
    customer = Customer.query.filter_by(
        id=customer_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()
    
    thread.customer_id = customer_id
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Customer associated with email thread'})

@gmail_bp.route('/api/templates')
@login_required
def get_templates():
    """Get email templates"""
    templates = EmailTemplate.query.filter(
        db.or_(
            EmailTemplate.user_id == current_user.id,
            db.and_(
                EmailTemplate.tenant_id == current_user.tenant_id,
                EmailTemplate.is_public == True
            )
        )
    ).order_by(EmailTemplate.category, EmailTemplate.name).all()
    
    template_data = []
    for template in templates:
        template_data.append({
            'id': template.id,
            'name': template.name,
            'category': template.category,
            'subject_template': template.subject_template,
            'body_template': template.body_template,
            'language': template.language,
            'is_public': template.is_public,
            'usage_count': template.usage_count
        })
    
    return jsonify({
        'success': True,
        'templates': template_data
    })

@gmail_bp.route('/api/templates', methods=['POST'])
@login_required
def create_template():
    """Create new email template"""
    data = request.get_json()
    
    template = EmailTemplate(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        name=data.get('name'),
        category=data.get('category'),
        subject_template=data.get('subject_template'),
        body_template=data.get('body_template'),
        is_public=data.get('is_public', False),
        language=data.get('language', 'en')
    )
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'template_id': template.id,
        'message': 'Template created successfully'
    })

@gmail_bp.route('/api/analytics/<int:account_id>')
@login_required
def get_analytics(account_id):
    """Get email analytics"""
    gmail_account = GmailAccount.query.filter_by(
        id=account_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Get date range
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days)
    
    # Query email statistics
    emails_query = EmailMessage.query.filter(
        EmailMessage.gmail_account_id == account_id,
        EmailMessage.received_date >= start_date,
        EmailMessage.received_date <= end_date
    )
    
    total_emails = emails_query.count()
    
    # Category breakdown
    categories = db.session.query(
        EmailMessage.ai_category,
        db.func.count(EmailMessage.id)
    ).filter(
        EmailMessage.gmail_account_id == account_id,
        EmailMessage.received_date >= start_date,
        EmailMessage.received_date <= end_date,
        EmailMessage.ai_category.isnot(None)
    ).group_by(EmailMessage.ai_category).all()
    
    # Sentiment breakdown
    sentiments = db.session.query(
        EmailMessage.ai_sentiment,
        db.func.count(EmailMessage.id)
    ).filter(
        EmailMessage.gmail_account_id == account_id,
        EmailMessage.received_date >= start_date,
        EmailMessage.received_date <= end_date,
        EmailMessage.ai_sentiment.isnot(None)
    ).group_by(EmailMessage.ai_sentiment).all()
    
    # Daily email count
    daily_counts = db.session.query(
        db.func.date(EmailMessage.received_date).label('date'),
        db.func.count(EmailMessage.id).label('count')
    ).filter(
        EmailMessage.gmail_account_id == account_id,
        EmailMessage.received_date >= start_date,
        EmailMessage.received_date <= end_date
    ).group_by(db.func.date(EmailMessage.received_date)).all()
    
    return jsonify({
        'success': True,
        'analytics': {
            'total_emails': total_emails,
            'categories': dict(categories),
            'sentiments': dict(sentiments),
            'daily_counts': [{'date': str(d[0]), 'count': d[1]} for d in daily_counts],
            'period': f'{start_date} to {end_date}'
        }
    })

@gmail_bp.route('/compose')
@login_required
def compose():
    """Email composition interface"""
    gmail_accounts = GmailAccount.query.filter_by(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        is_active=True
    ).all()
    
    # Get customers for recipient suggestions
    customers = Customer.query.filter_by(
        tenant_id=current_user.tenant_id,
        is_active=True
    ).order_by(Customer.name).all()
    
    return render_template('gmail/compose.html', 
                         gmail_accounts=gmail_accounts,
                         customers=customers)

@gmail_bp.route('/settings')
@login_required
def settings():
    """Gmail settings page"""
    gmail_accounts = GmailAccount.query.filter_by(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    ).all()
    
    return render_template('gmail/settings.html', gmail_accounts=gmail_accounts)