import os
import base64
import pickle
from datetime import datetime, timezone, timedelta
from flask import current_app, url_for
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from cryptography.fernet import Fernet
from models.gmail_models import GmailAccount, GmailMessage, GmailAttachment, GmailLabel
from app import db
from flask_login import current_user

# Encryption key for tokens (should be set in config)
ENCRYPTION_KEY = os.environ.get('GMAIL_TOKEN_KEY', Fernet.generate_key())
fernet = Fernet(ENCRYPTION_KEY)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.labels',
    'openid',
    'email',
    'profile'
]

class GmailService:
    @staticmethod
    def get_flow(redirect_uri):
        client_secrets_file = os.environ.get('GOOGLE_CLIENT_SECRET_FILE', 'client_secret.json')
        flow = Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        return flow

    @staticmethod
    def encrypt_token(token_bytes):
        return fernet.encrypt(token_bytes)

    @staticmethod
    def decrypt_token(token_bytes):
        return fernet.decrypt(token_bytes)

    @staticmethod
    def store_tokens(user_id, tenant_id, email, credentials):
        access_token = GmailService.encrypt_token(credentials.token.encode())
        refresh_token = GmailService.encrypt_token(credentials.refresh_token.encode())
        token_expiry = credentials.expiry
        account = GmailAccount.query.filter_by(user_id=user_id, tenant_id=tenant_id, email=email).first()
        if not account:
            account = GmailAccount(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expiry=token_expiry,
                sync_status='idle',
                is_active=True
            )
            db.session.add(account)
        else:
            account.access_token = access_token
            account.refresh_token = refresh_token
            account.token_expiry = token_expiry
            account.is_active = True
        db.session.commit()
        return account

    @staticmethod
    def get_credentials(account: GmailAccount):
        from google.oauth2.credentials import Credentials
        access_token = GmailService.decrypt_token(account.access_token).decode()
        refresh_token = GmailService.decrypt_token(account.refresh_token).decode()
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.environ.get('GOOGLE_CLIENT_ID'),
            client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
            scopes=SCOPES
        )
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            account.access_token = GmailService.encrypt_token(creds.token.encode())
            account.token_expiry = creds.expiry
            db.session.commit()
        return creds

    @staticmethod
    def build_service(account: GmailAccount):
        creds = GmailService.get_credentials(account)
        service = build('gmail', 'v1', credentials=creds)
        return service

    @staticmethod
    def fetch_messages(account: GmailAccount, query=None, page_token=None, max_results=50):
        service = GmailService.build_service(account)
        results = service.users().messages().list(
            userId='me',
            q=query,
            pageToken=page_token,
            maxResults=max_results
        ).execute()
        messages = results.get('messages', [])
        next_page_token = results.get('nextPageToken')
        for msg in messages:
            GmailService.fetch_and_store_message(account, msg['id'])
        return next_page_token

    @staticmethod
    def fetch_and_store_message(account: GmailAccount, message_id):
        service = GmailService.build_service(account)
        msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        thread_id = msg['threadId']
        payload = msg['payload']
        headers = {h['name']: h['value'] for h in payload.get('headers', [])}
        subject = headers.get('Subject', '')
        sender = headers.get('From', '')
        recipients = headers.get('To', '')
        cc = headers.get('Cc', '')
        bcc = headers.get('Bcc', '')
        snippet = msg.get('snippet', '')
        body_html, body_plain = GmailService.extract_bodies(payload)
        received_at = GmailService.parse_gmail_date(headers.get('Date'))
        is_read = 'UNREAD' not in msg.get('labelIds', [])
        is_starred = 'STARRED' in msg.get('labelIds', [])
        is_important = 'IMPORTANT' in msg.get('labelIds', [])
        labels = msg.get('labelIds', [])
        has_attachments = GmailService.has_attachments(payload)
        # Store message
        message = GmailMessage.query.filter_by(message_id=message_id).first()
        if not message:
            message = GmailMessage(
                gmail_account_id=account.id,
                thread_id=thread_id,
                message_id=message_id,
                subject=subject,
                sender=sender,
                recipients=recipients,
                cc=cc,
                bcc=bcc,
                snippet=snippet,
                body_html=body_html,
                body_plain=body_plain,
                received_at=received_at,
                is_read=is_read,
                is_starred=is_starred,
                is_important=is_important,
                labels=labels,
                has_attachments=has_attachments
            )
            db.session.add(message)
        else:
            message.subject = subject
            message.sender = sender
            message.recipients = recipients
            message.cc = cc
            message.bcc = bcc
            message.snippet = snippet
            message.body_html = body_html
            message.body_plain = body_plain
            message.received_at = received_at
            message.is_read = is_read
            message.is_starred = is_starred
            message.is_important = is_important
            message.labels = labels
            message.has_attachments = has_attachments
        db.session.commit()
        # Store attachments
        if has_attachments:
            GmailService.fetch_and_store_attachments(account, message, payload)
        return message

    @staticmethod
    def extract_bodies(payload):
        body_html = ''
        body_plain = ''
        if payload.get('mimeType') == 'text/html':
            body_html = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif payload.get('mimeType') == 'text/plain':
            body_plain = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif payload.get('parts'):
            for part in payload['parts']:
                if part.get('mimeType') == 'text/html':
                    body_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part.get('mimeType') == 'text/plain':
                    body_plain = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        return body_html, body_plain

    @staticmethod
    def has_attachments(payload):
        if payload.get('parts'):
            for part in payload['parts']:
                if part.get('filename') and part.get('body', {}).get('attachmentId'):
                    return True
        return False

    @staticmethod
    def fetch_and_store_attachments(account, message, payload):
        service = GmailService.build_service(account)
        if payload.get('parts'):
            for part in payload['parts']:
                if part.get('filename') and part.get('body', {}).get('attachmentId'):
                    attachment_id = part['body']['attachmentId']
                    att = service.users().messages().attachments().get(
                        userId='me', messageId=message.message_id, id=attachment_id).execute()
                    file_data = base64.urlsafe_b64decode(att['data'])
                    attachment = GmailAttachment(
                        gmail_message_id=message.id,
                        filename=part['filename'],
                        mime_type=part.get('mimeType'),
                        file_data=file_data,
                        file_size=len(file_data)
                    )
                    db.session.add(attachment)
            db.session.commit()

    @staticmethod
    def parse_gmail_date(date_str):
        try:
            # Gmail date format: 'Mon, 12 Jun 2023 10:00:00 +0000'
            return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        except Exception:
            return None

    # Additional methods for label sync, webhooks, bi-directional sync, etc. can be added here. 