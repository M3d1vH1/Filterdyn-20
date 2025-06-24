from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from models.gmail_models import GmailAccount, GmailMessage, GmailAttachment, GmailLabel
from services.gmail_service import GmailService
from services.ai_email_service import AIEmailService
from app import db
from utils.email_parser import extract_entities
from utils.ai_processor import clean_email_text
import os

gmail_bp = Blueprint('gmail', __name__, url_prefix='/gmail')

# 1. OAuth2 Connect
@gmail_bp.route('/connect')
@login_required
def connect_gmail():
    redirect_uri = url_for('gmail.oauth2_callback', _external=True)
    flow = GmailService.get_flow(redirect_uri)
    auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
    session['oauth2_state'] = state
    return redirect(auth_url)

# 2. OAuth2 Callback
@gmail_bp.route('/oauth2callback')
@login_required
def oauth2_callback():
    state = session.get('oauth2_state')
    redirect_uri = url_for('gmail.oauth2_callback', _external=True)
    flow = GmailService.get_flow(redirect_uri)
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    # Get user email from credentials
    service = GmailService.build_service_from_credentials(credentials)
    profile = service.users().getProfile(userId='me').execute()
    email = profile['emailAddress']
    GmailService.store_tokens(current_user.id, current_user.tenant_id, email, credentials)
    flash('Gmail account connected successfully!', 'success')
    return redirect(url_for('gmail.inbox'))

# 3. Inbox View
@gmail_bp.route('/inbox')
@login_required
def inbox():
    account = GmailAccount.query.filter_by(user_id=current_user.id, tenant_id=current_user.tenant_id, is_active=True).first()
    if not account:
        flash('No Gmail account connected.', 'warning')
        return redirect(url_for('gmail.connect_gmail'))
    # Optionally trigger sync here
    messages = GmailMessage.query.filter_by(gmail_account_id=account.id).order_by(GmailMessage.received_at.desc()).limit(50).all()
    return render_template('gmail/inbox.html', messages=messages)

# 4. Read Message
@gmail_bp.route('/message/<string:message_id>')
@login_required
def read_message(message_id):
    message = GmailMessage.query.filter_by(message_id=message_id).first_or_404()
    attachments = GmailAttachment.query.filter_by(gmail_message_id=message.id).all()
    return render_template('gmail/message.html', message=message, attachments=attachments)

# 5. Compose/Send Email
@gmail_bp.route('/compose', methods=['GET', 'POST'])
@login_required
def compose_email():
    if request.method == 'POST':
        # TODO: Implement sending via Gmail API
        flash('Email sending not yet implemented.', 'warning')
        return redirect(url_for('gmail.inbox'))
    return render_template('gmail/compose.html')

# 6. Search Emails (API)
@gmail_bp.route('/api/search')
@login_required
def api_search():
    query = request.args.get('q', '')
    account = GmailAccount.query.filter_by(user_id=current_user.id, tenant_id=current_user.tenant_id, is_active=True).first()
    if not account:
        return jsonify({'error': 'No Gmail account connected.'}), 400
    # Optionally trigger GmailService.fetch_messages with query
    messages = GmailMessage.query.filter_by(gmail_account_id=account.id).filter(GmailMessage.subject.ilike(f'%{query}%')).limit(20).all()
    return jsonify([{'id': m.message_id, 'subject': m.subject, 'from': m.sender, 'date': m.received_at.isoformat() if m.received_at else None} for m in messages])

# 7. AI Analysis (API)
@gmail_bp.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    data = request.json
    email_text = data.get('email_text', '')
    cleaned = clean_email_text(email_text)
    analysis = AIEmailService.analyze_email_content(cleaned)
    entities = extract_entities(cleaned)
    return jsonify({'analysis': analysis, 'entities': entities})

# 8. AI Suggestion (API)
@gmail_bp.route('/api/suggest', methods=['POST'])
@login_required
def api_suggest():
    data = request.json
    email_text = data.get('email_text', '')
    context = data.get('context')
    language = data.get('language')
    tone = data.get('tone', 'professional')
    suggestion = AIEmailService.suggest_response(email_text, context=context, language=language, tone=tone)
    return jsonify({'suggestion': suggestion}) 