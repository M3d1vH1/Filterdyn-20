
import os
import json
import base64
from datetime import datetime, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import openai

class EmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
              'https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.service = None
        self.openai_client = None
        
    def authenticate_gmail(self, credentials_json):
        """Authenticate with Gmail API using OAuth2"""
        try:
            creds = None
            token_path = f'tokens/gmail_token_{self.user_id}.json'
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_config(
                        json.loads(credentials_json), self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                os.makedirs('tokens', exist_ok=True)
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=creds)
            return True
        except Exception as e:
            print(f"Gmail authentication error: {e}")
            return False
    
    def setup_openai(self, api_key):
        """Setup OpenAI client for email composition"""
        self.openai_client = openai.OpenAI(api_key=api_key)
    
    def compose_email_with_ai(self, context, recipient_name, subject_hint=""):
        """Generate email content using OpenAI"""
        if not self.openai_client:
            return None
            
        prompt = f"""
        Compose a professional email for a water treatment company.
        
        Context: {context}
        Recipient: {recipient_name}
        Subject hint: {subject_hint}
        
        Please provide:
        1. A professional subject line
        2. Email body with proper greeting and closing
        3. Keep it concise and professional
        
        Company: Filterdyn Water Solutions
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            # Parse subject and body from response
            lines = content.split('\n')
            subject = lines[0].replace('Subject:', '').strip()
            body = '\n'.join(lines[2:]).strip()
            
            return {
                'subject': subject,
                'body': body
            }
        except Exception as e:
            print(f"OpenAI email generation error: {e}")
            return None
    
    def send_email(self, to_email, subject, body, attachments=None):
        """Send email through Gmail API"""
        if not self.service:
            return False
            
        try:
            message = self._create_message(to_email, subject, body, attachments)
            sent_message = self.service.users().messages().send(
                userId='me', body=message).execute()
            return sent_message['id']
        except Exception as e:
            print(f"Email sending error: {e}")
            return False
    
    def _create_message(self, to, subject, body, attachments=None):
        """Create email message"""
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders
        
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        message.attach(MIMEText(body, 'plain'))
        
        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment['content'])
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment["filename"]}'
                )
                message.attach(part)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}
