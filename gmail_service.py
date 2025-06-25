import os
import base64
import json
from datetime import datetime, timezone, timedelta
from flask import current_app, url_for, session
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from cryptography.fernet import Fernet
from models import GmailAccount
from app import db
from flask_login import current_user
import logging

# Encryption for tokens
def get_encryption_key():
    key = os.environ.get('GMAIL_TOKEN_KEY')
    if not key:
        # Generate and save a key (in production, this should be persistent)
        key = Fernet.generate_key()
        current_app.logger.warning("Generated temporary encryption key for Gmail tokens")
    elif isinstance(key, str):
        key = key.encode()
    return key

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify', 
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/userinfo.email'
]

class GmailService:
    @staticmethod
    def get_flow(redirect_uri):
        """Create OAuth2 flow"""
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("Google OAuth credentials not configured")
        
        # Debug OAuth configuration
        current_app.logger.info(f"OAuth Debug - Client ID: {client_id[:20]}...")
        current_app.logger.info(f"OAuth Debug - Redirect URI: {redirect_uri}")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        return flow

    @staticmethod
    def encrypt_token(token_str):
        """Encrypt token for storage"""
        fernet = Fernet(get_encryption_key())
        return fernet.encrypt(token_str.encode())

    @staticmethod
    def decrypt_token(token_bytes):
        """Decrypt token from storage"""
        fernet = Fernet(get_encryption_key())
        return fernet.decrypt(token_bytes).decode()

    @staticmethod
    def store_credentials(user_id, tenant_id, credentials):
        """Store OAuth2 credentials"""
        # Get user email from credentials
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        email = user_info['email']
        google_user_id = user_info['id']
        
        # Encrypt tokens
        access_token = GmailService.encrypt_token(credentials.token)
        refresh_token = GmailService.encrypt_token(credentials.refresh_token) if credentials.refresh_token else None
        
        # Store or update account
        account = GmailAccount.query.filter_by(
            user_id=user_id, 
            tenant_id=tenant_id, 
            email_address=email
        ).first()
        
        if not account:
            account = GmailAccount(
                user_id=user_id,
                tenant_id=tenant_id,
                email_address=email,
                google_user_id=google_user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=credentials.expiry,
                is_primary=True,  # First account is primary
                sync_enabled=True
            )
            db.session.add(account)
        else:
            account.access_token = access_token
            account.refresh_token = refresh_token
            account.token_expires_at = credentials.expiry
            account.sync_enabled = True
        
        db.session.commit()
        return account

    @staticmethod
    def get_credentials(account: GmailAccount):
        """Get valid credentials from account"""
        access_token = GmailService.decrypt_token(account.access_token)
        refresh_token = GmailService.decrypt_token(account.refresh_token) if account.refresh_token else None
        
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.environ.get('GOOGLE_CLIENT_ID'),
            client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
            scopes=SCOPES
        )
        
        # Refresh if expired
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # Update stored tokens
            account.access_token = GmailService.encrypt_token(credentials.token)
            account.token_expires_at = credentials.expiry
            db.session.commit()
        
        return credentials

    @staticmethod
    def build_service(account: GmailAccount):
        """Build Gmail service"""
        credentials = GmailService.get_credentials(account)
        return build('gmail', 'v1', credentials=credentials)

    @staticmethod
    def sync_messages(account: GmailAccount, max_results=50):
        """Sync messages from Gmail"""
        try:
            service = GmailService.build_service(account)
            
            # Get message list
            results = service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # For now, just log the message count
            current_app.logger.info(f"Found {len(messages)} messages in Gmail")
            
            account.last_sync_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return len(messages)
            
        except Exception as e:
            current_app.logger.error(f"Gmail sync error: {str(e)}")
            return 0

    @staticmethod
    def fetch_and_store_message(account: GmailAccount, service, message_id):
        """Fetch and store a single message"""
        try:
            # Get full message
            msg = service.users().messages().get(
                userId='me', 
                id=message_id, 
                format='full'
            ).execute()
            
            # Check if message already exists
            existing = EmailMessage.query.filter_by(message_id=message_id).first()
            if existing:
                return existing
            
            # Extract message data
            payload = msg['payload']
            headers = {h['name']: h['value'] for h in payload.get('headers', [])}
            
            # Get or create thread
            thread = GmailService.get_or_create_thread(account, msg['threadId'], headers.get('Subject', ''))
            
            # Parse message details
            subject = headers.get('Subject', '')
            sender_email = GmailService.extract_email(headers.get('From', ''))
            sender_name = GmailService.extract_name(headers.get('From', ''))
            
            # Parse body
            body_html, body_plain = GmailService.extract_message_body(payload)
            
            # Parse date
            date_str = headers.get('Date', '')
            sent_at = GmailService.parse_date(date_str)
            
            # Create message
            message = EmailMessage(
                thread_id=thread.id,
                message_id=message_id,
                subject=subject,
                sender_name=sender_name,
                sender_email=sender_email,
                recipients=json.dumps([headers.get('To', '')]),
                cc_recipients=json.dumps([headers.get('Cc', '')]) if headers.get('Cc') else None,
                snippet=msg.get('snippet', ''),
                body_html=body_html,
                body_plain=body_plain,
                sent_at=sent_at,
                received_at=datetime.now(timezone.utc),
                is_read='UNREAD' not in msg.get('labelIds', []),
                is_starred='STARRED' in msg.get('labelIds', []),
                is_important='IMPORTANT' in msg.get('labelIds', []),
                labels=msg.get('labelIds', []),
                has_attachments=GmailService.has_attachments(payload)
            )
            
            db.session.add(message)
            db.session.commit()
            
            # Handle attachments
            if message.has_attachments:
                GmailService.store_attachments(service, message, payload)
            
            # Update thread
            thread.message_count = EmailMessage.query.filter_by(thread_id=thread.id).count()
            thread.last_message_at = sent_at or datetime.now(timezone.utc)
            db.session.commit()
            
            return message
            
        except Exception as e:
            current_app.logger.error(f"Error fetching message {message_id}: {str(e)}")
            return None

    # Thread management simplified - using existing message grouping

    @staticmethod
    def extract_message_body(payload):
        """Extract HTML and plain text from message payload"""
        body_html = ''
        body_plain = ''
        
        def extract_from_part(part):
            nonlocal body_html, body_plain
            
            mime_type = part.get('mimeType', '')
            
            if mime_type == 'text/plain' and part.get('body', {}).get('data'):
                body_plain = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            elif mime_type == 'text/html' and part.get('body', {}).get('data'):
                body_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            elif part.get('parts'):
                for subpart in part['parts']:
                    extract_from_part(subpart)
        
        if payload.get('parts'):
            for part in payload['parts']:
                extract_from_part(part)
        elif payload.get('body', {}).get('data'):
            # Single part message
            mime_type = payload.get('mimeType', '')
            data = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            if mime_type == 'text/html':
                body_html = data
            else:
                body_plain = data
        
        return body_html, body_plain

    @staticmethod
    def has_attachments(payload):
        """Check if message has attachments"""
        def check_parts(parts):
            for part in parts:
                if part.get('filename') and part.get('body', {}).get('attachmentId'):
                    return True
                if part.get('parts'):
                    if check_parts(part['parts']):
                        return True
            return False
        
        if payload.get('parts'):
            return check_parts(payload['parts'])
        return False

    @staticmethod
    def store_attachments(service, message, payload):
        """Store message attachments using existing structure"""
        def process_parts(parts):
            for part in parts:
                if part.get('filename') and part.get('body', {}).get('attachmentId'):
                    try:
                        attachment = service.users().messages().attachments().get(
                            userId='me',
                            messageId=message.message_id,
                            id=part['body']['attachmentId']
                        ).execute()
                        
                        file_data = base64.urlsafe_b64decode(attachment['data'])
                        
                        # Log attachment info for now
                        current_app.logger.info(f"Found attachment: {part['filename']}")
                        
                    except Exception as e:
                        current_app.logger.error(f"Error storing attachment: {str(e)}")
                
                if part.get('parts'):
                    process_parts(part['parts'])
        
        if payload.get('parts'):
            process_parts(payload['parts'])
            db.session.commit()

    @staticmethod
    def extract_email(from_header):
        """Extract email address from From header"""
        import re
        email_match = re.search(r'<(.+?)>', from_header)
        if email_match:
            return email_match.group(1)
        elif '@' in from_header:
            return from_header.strip()
        return ''

    @staticmethod
    def extract_name(from_header):
        """Extract name from From header"""
        import re
        if '<' in from_header:
            name = from_header.split('<')[0].strip().strip('"')
            return name if name else from_header
        return from_header

    @staticmethod
    def parse_date(date_str):
        """Parse Gmail date string"""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.now(timezone.utc)

    @staticmethod
    def get_user_account(user_id, tenant_id):
        """Get user's primary Gmail account"""
        return GmailAccount.query.filter_by(
            user_id=user_id,
            tenant_id=tenant_id,
            is_active=True
        ).first()

    @staticmethod
    def send_email(account: GmailAccount, to_email, subject, body, cc=None, bcc=None, attachments=None):
        """Send email via Gmail API"""
        try:
            service = GmailService.build_service(account)
            
            # Create message
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders
            
            message = MIMEMultipart()
            message['to'] = to_email
            message['subject'] = subject
            message['from'] = account.email_address
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            # Add body
            message.attach(MIMEText(body, 'html' if '<' in body else 'plain'))
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['data'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    message.attach(part)
            
            # Send message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return send_message
            
        except Exception as e:
            current_app.logger.error(f"Error sending email: {str(e)}")
            raise e