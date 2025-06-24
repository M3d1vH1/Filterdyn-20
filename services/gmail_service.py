"""
Gmail API Service Module
Handles all Gmail API interactions, email processing, and synchronization
"""

import os
import json
import base64
import email
import quopri
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from flask import current_app
from models_gmail import GmailAccount, EmailMessage, EmailAttachment, EmailThread
from app import db
from utils.ai_processor import AIEmailProcessor
import logging

logger = logging.getLogger(__name__)

class GmailService:
    """Gmail API service for email management"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    def __init__(self, user_id: int, tenant_id: int):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.ai_processor = AIEmailProcessor()
        
    def get_authorization_url(self, redirect_uri: str) -> str:
        """Generate OAuth authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
                    "client_secret": os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES
        )
        flow.redirect_uri = redirect_uri
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return auth_url
    
    def handle_oauth_callback(self, code: str, redirect_uri: str) -> bool:
        """Handle OAuth callback and store credentials"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
                        "client_secret": os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                scopes=self.SCOPES
            )
            flow.redirect_uri = redirect_uri
            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            
            # Get user info
            service = build('gmail', 'v1', credentials=credentials)
            profile = service.users().getProfile(userId='me').execute()
            
            # Store or update Gmail account
            gmail_account = GmailAccount.query.filter_by(
                user_id=self.user_id,
                email_address=profile['emailAddress']
            ).first()
            
            if not gmail_account:
                gmail_account = GmailAccount(
                    tenant_id=self.tenant_id,
                    user_id=self.user_id,
                    email_address=profile['emailAddress'],
                    display_name=profile.get('messagesTotal', ''),
                )
                db.session.add(gmail_account)
            
            # Update credentials
            gmail_account.access_token = credentials.token
            gmail_account.refresh_token = credentials.refresh_token
            gmail_account.token_expiry = credentials.expiry
            gmail_account.is_active = True
            gmail_account.last_sync = datetime.now(timezone.utc)
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"OAuth callback error: {str(e)}")
            return False
    
    def get_gmail_service(self, gmail_account_id: int):
        """Get authenticated Gmail service"""
        gmail_account = GmailAccount.query.get(gmail_account_id)
        if not gmail_account or not gmail_account.is_active:
            return None
            
        credentials = Credentials(
            token=gmail_account.access_token,
            refresh_token=gmail_account.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
            client_secret=os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
        )
        
        if credentials.expired:
            credentials.refresh(Request())
            gmail_account.access_token = credentials.token
            gmail_account.token_expiry = credentials.expiry
            db.session.commit()
        
        return build('gmail', 'v1', credentials=credentials)
    
    def sync_emails(self, gmail_account_id: int, page_token: str = None, max_results: int = 100) -> Dict[str, Any]:
        """Synchronize emails from Gmail"""
        service = self.get_gmail_service(gmail_account_id)
        if not service:
            return {'success': False, 'error': 'Unable to authenticate with Gmail'}
        
        gmail_account = GmailAccount.query.get(gmail_account_id)
        
        try:
            # Get message list
            query_params = {
                'userId': 'me',
                'maxResults': max_results,
                'includeSpamTrash': False
            }
            
            if page_token:
                query_params['pageToken'] = page_token
            
            if gmail_account.last_sync:
                # Only get emails since last sync
                query_params['q'] = f'after:{int(gmail_account.last_sync.timestamp())}'
            
            result = service.users().messages().list(**query_params).execute()
            messages = result.get('messages', [])
            
            synced_count = 0
            for message in messages:
                if self._sync_single_email(service, gmail_account_id, message['id']):
                    synced_count += 1
            
            # Update last sync time
            gmail_account.last_sync = datetime.now(timezone.utc)
            db.session.commit()
            
            return {
                'success': True,
                'synced_count': synced_count,
                'next_page_token': result.get('nextPageToken'),
                'total_messages': len(messages)
            }
            
        except Exception as e:
            logger.error(f"Email sync error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _sync_single_email(self, service, gmail_account_id: int, message_id: str) -> bool:
        """Sync a single email message"""
        try:
            # Check if email already exists
            existing = EmailMessage.query.filter_by(
                gmail_account_id=gmail_account_id,
                gmail_id=message_id
            ).first()
            
            if existing:
                return False  # Already synced
            
            # Get full message
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Parse message
            email_data = self._parse_email_message(message)
            
            # Create database record
            email_msg = EmailMessage(
                tenant_id=self.tenant_id,
                gmail_account_id=gmail_account_id,
                gmail_id=message_id,
                thread_id=message['threadId'],
                subject=email_data['subject'],
                sender=email_data['sender'],
                recipient=email_data['recipient'],
                cc=email_data.get('cc'),
                bcc=email_data.get('bcc'),
                body_text=email_data.get('body_text'),
                body_html=email_data.get('body_html'),
                received_date=email_data['date'],
                is_read=not ('UNREAD' in message.get('labelIds', [])),
                is_important='IMPORTANT' in message.get('labelIds', []),
                labels=json.dumps(message.get('labelIds', [])),
            )
            
            db.session.add(email_msg)
            db.session.flush()  # Get the ID
            
            # Process attachments
            if 'parts' in message['payload']:
                self._process_attachments(service, message, email_msg.id)
            
            # AI Processing
            try:
                ai_data = self.ai_processor.process_email(email_data)
                email_msg.ai_category = ai_data.get('category')
                email_msg.ai_sentiment = ai_data.get('sentiment')
                email_msg.ai_intent = ai_data.get('intent')
                email_msg.ai_entities = json.dumps(ai_data.get('entities', {}))
                email_msg.ai_summary = ai_data.get('summary')
            except Exception as e:
                logger.warning(f"AI processing failed for email {message_id}: {str(e)}")
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync email {message_id}: {str(e)}")
            db.session.rollback()
            return False
    
    def _parse_email_message(self, message: Dict) -> Dict[str, Any]:
        """Parse Gmail message into structured data"""
        payload = message['payload']
        headers = {h['name'].lower(): h['value'] for h in payload.get('headers', [])}
        
        # Extract basic info
        data = {
            'subject': headers.get('subject', ''),
            'sender': headers.get('from', ''),
            'recipient': headers.get('to', ''),
            'cc': headers.get('cc'),
            'bcc': headers.get('bcc'),
            'date': datetime.fromtimestamp(
                int(message['internalDate']) / 1000,
                tz=timezone.utc
            )
        }
        
        # Extract body
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data['body_text'] = self._decode_body(part['body'])
                elif part['mimeType'] == 'text/html':
                    data['body_html'] = self._decode_body(part['body'])
        else:
            # Single part message
            if payload['mimeType'] == 'text/plain':
                data['body_text'] = self._decode_body(payload['body'])
            elif payload['mimeType'] == 'text/html':
                data['body_html'] = self._decode_body(payload['body'])
        
        return data
    
    def _decode_body(self, body_data: Dict) -> str:
        """Decode email body content"""
        if 'data' in body_data:
            # Base64 decode
            decoded = base64.urlsafe_b64decode(body_data['data']).decode('utf-8')
            return decoded
        return ''
    
    def _process_attachments(self, service, message: Dict, email_id: int):
        """Process and store email attachments"""
        payload = message['payload']
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename'):
                    attachment_id = part['body'].get('attachmentId')
                    if attachment_id:
                        # Get attachment data
                        attachment = service.users().messages().attachments().get(
                            userId='me',
                            messageId=message['id'],
                            id=attachment_id
                        ).execute()
                        
                        # Store attachment
                        email_attachment = EmailAttachment(
                            email_message_id=email_id,
                            filename=part['filename'],
                            mime_type=part['mimeType'],
                            size=part['body'].get('size', 0),
                            attachment_data=base64.urlsafe_b64decode(attachment['data'])
                        )
                        db.session.add(email_attachment)
    
    def send_email(self, gmail_account_id: int, to: str, subject: str, body: str, 
                   cc: str = None, bcc: str = None, reply_to_id: str = None) -> Dict[str, Any]:
        """Send an email through Gmail"""
        service = self.get_gmail_service(gmail_account_id)
        if not service:
            return {'success': False, 'error': 'Unable to authenticate with Gmail'}
        
        try:
            # Create message
            message = email.message.EmailMessage()
            message['To'] = to
            message['Subject'] = subject
            if cc:
                message['Cc'] = cc
            if bcc:
                message['Bcc'] = bcc
            
            message.set_content(body)
            
            # Convert to Gmail format
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_params = {
                'userId': 'me',
                'body': {'raw': raw_message}
            }
            
            if reply_to_id:
                send_params['body']['threadId'] = reply_to_id
            
            result = service.users().messages().send(**send_params).execute()
            
            return {'success': True, 'message_id': result['id']}
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def search_emails(self, gmail_account_id: int, query: str, max_results: int = 50) -> List[Dict]:
        """Search emails with Gmail query syntax"""
        service = self.get_gmail_service(gmail_account_id)
        if not service:
            return []
        
        try:
            result = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = []
            for msg in result.get('messages', []):
                # Get basic message info
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata'
                ).execute()
                
                headers = {h['name'].lower(): h['value'] for h in message['payload'].get('headers', [])}
                
                messages.append({
                    'id': msg['id'],
                    'thread_id': msg['threadId'],
                    'subject': headers.get('subject', ''),
                    'sender': headers.get('from', ''),
                    'date': datetime.fromtimestamp(
                        int(message['internalDate']) / 1000,
                        tz=timezone.utc
                    ),
                    'is_read': not ('UNREAD' in message.get('labelIds', [])),
                    'labels': message.get('labelIds', [])
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Email search error: {str(e)}")
            return []
    
    def get_email_threads(self, gmail_account_id: int, page_token: str = None) -> Dict[str, Any]:
        """Get email threads for inbox view"""
        try:
            # Get from database first
            query = EmailMessage.query.filter_by(
                gmail_account_id=gmail_account_id
            ).order_by(EmailMessage.received_date.desc())
            
            if page_token:
                # Implement pagination logic
                pass
            
            emails = query.limit(50).all()
            
            # Group by thread
            threads = {}
            for email in emails:
                if email.thread_id not in threads:
                    threads[email.thread_id] = {
                        'thread_id': email.thread_id,
                        'subject': email.subject,
                        'participants': set(),
                        'latest_date': email.received_date,
                        'is_read': True,
                        'message_count': 0,
                        'labels': [],
                        'messages': []
                    }
                
                thread = threads[email.thread_id]
                thread['participants'].add(email.sender)
                thread['participants'].add(email.recipient)
                thread['message_count'] += 1
                thread['is_read'] = thread['is_read'] and email.is_read
                thread['messages'].append({
                    'id': email.id,
                    'gmail_id': email.gmail_id,
                    'subject': email.subject,
                    'sender': email.sender,
                    'recipient': email.recipient,
                    'received_date': email.received_date,
                    'body_text': email.body_text,
                    'body_html': email.body_html,
                    'is_read': email.is_read,
                    'ai_category': email.ai_category,
                    'ai_sentiment': email.ai_sentiment
                })
                
                if email.received_date > thread['latest_date']:
                    thread['latest_date'] = email.received_date
            
            # Convert to list and sort
            thread_list = list(threads.values())
            thread_list.sort(key=lambda x: x['latest_date'], reverse=True)
            
            # Convert participants set to list
            for thread in thread_list:
                thread['participants'] = list(thread['participants'])
            
            return {
                'success': True,
                'threads': thread_list,
                'total_count': len(thread_list)
            }
            
        except Exception as e:
            logger.error(f"Failed to get email threads: {str(e)}")
            return {'success': False, 'error': str(e)}