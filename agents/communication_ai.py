"""
Communication & AI Agent
=======================

Handles email integration, AI-powered composition, and communication automation.
"""

import os
import json
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

try:
    import openai
except ImportError:
    openai = None


class CommunicationAIAgent:
    """Agent for handling email communication and AI-powered content generation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.gmail_service = None
        self.openai_client = None
        self.setup_gmail_api()
        self.setup_openai()
    
    def setup_gmail_api(self):
        """Initialize Gmail API connection"""
        try:
            # Gmail API scopes
            SCOPES = ['https://www.googleapis.com/auth/gmail.send',
                     'https://www.googleapis.com/auth/gmail.readonly']
            
            creds = None
            token_path = self.config.get('gmail_token_path', 'token.json')
            credentials_path = self.config.get('gmail_credentials_path', 'credentials.json')
            
            # Load existing token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # Refresh token if expired
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            # Create Gmail service
            if creds:
                self.gmail_service = build('gmail', 'v1', credentials=creds)
                print("✅ Gmail API connected successfully")
            else:
                print("⚠️ Gmail credentials not found. Run authenticate_gmail() first.")
                
        except Exception as e:
            print(f"❌ Gmail API setup failed: {e}")
    
    def setup_openai(self):
        """Initialize OpenAI client for AI-powered content generation"""
        try:
            if openai and self.config.get('openai_api_key'):
                openai.api_key = self.config['openai_api_key']
                self.openai_client = openai
                print("✅ OpenAI client initialized")
            else:
                print("⚠️ OpenAI not available or API key not configured")
        except Exception as e:
            print(f"❌ OpenAI setup failed: {e}")
    
    def authenticate_gmail(self):
        """Authenticate with Gmail API"""
        try:
            SCOPES = ['https://www.googleapis.com/auth/gmail.send',
                     'https://www.googleapis.com/auth/gmail.readonly']
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.config.get('gmail_credentials_path', 'credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.config.get('gmail_token_path', 'token.json'), 'w') as token:
                token.write(creds.to_json())
            
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail authentication successful")
            return True
            
        except Exception as e:
            print(f"❌ Gmail authentication failed: {e}")
            return False
    
    def generate_ai_email_content(self, context: Dict[str, Any]) -> str:
        """Generate email content using AI based on context"""
        if not self.openai_client:
            return self._generate_fallback_content(context)
        
        try:
            # Build prompt based on context
            prompt = self._build_email_prompt(context)
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional business communication assistant for a water treatment company. Write clear, professional emails."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ AI content generation failed: {e}")
            return self._generate_fallback_content(context)
    
    def _build_email_prompt(self, context: Dict[str, Any]) -> str:
        """Build AI prompt based on email context"""
        email_type = context.get('type', 'general')
        customer_name = context.get('customer_name', 'Valued Customer')
        subject = context.get('subject', '')
        
        prompts = {
            'quote_followup': f"Write a professional follow-up email for a quote sent to {customer_name}. The quote subject is: {subject}. Be polite, professional, and encourage them to ask questions.",
            'service_reminder': f"Write a friendly service reminder email for {customer_name}. Remind them about upcoming maintenance and the importance of regular service.",
            'water_quality_alert': f"Write an urgent email to {customer_name} about water quality issues detected. Be professional but convey the importance of immediate attention.",
            'general': f"Write a professional business email to {customer_name} about: {subject}"
        }
        
        return prompts.get(email_type, prompts['general'])
    
    def _generate_fallback_content(self, context: Dict[str, Any]) -> str:
        """Generate fallback email content without AI"""
        email_type = context.get('type', 'general')
        customer_name = context.get('customer_name', 'Valued Customer')
        
        templates = {
            'quote_followup': f"""
Dear {customer_name},

Thank you for your interest in our water treatment solutions. We recently sent you a quote and wanted to follow up to ensure you received it and answer any questions you may have.

If you need any clarification or have questions about our proposal, please don't hesitate to contact us.

Best regards,
Filterdyn Operations Team
            """,
            'service_reminder': f"""
Dear {customer_name},

This is a friendly reminder that your water treatment equipment is due for routine maintenance. Regular service ensures optimal performance and extends the life of your equipment.

Please contact us to schedule your maintenance appointment.

Best regards,
Filterdyn Operations Team
            """,
            'water_quality_alert': f"""
Dear {customer_name},

Our monitoring system has detected water quality parameters outside normal ranges. We recommend immediate attention to ensure your water treatment system is operating correctly.

Please contact us urgently to schedule a service visit.

Best regards,
Filterdyn Operations Team
            """
        }
        
        return templates.get(email_type, f"Dear {customer_name},\n\nThank you for your business.\n\nBest regards,\nFilterdyn Operations Team")
    
    def send_email(self, to: str, subject: str, body: str, 
                   from_email: Optional[str] = None, 
                   attachments: Optional[List[str]] = None) -> bool:
        """Send email via Gmail API"""
        if not self.gmail_service:
            print("❌ Gmail service not available")
            return False
        
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            message['from'] = from_email or self.config.get('default_from_email', 'noreply@filterdyn.com')
            
            # Add body
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        message.attach(part)
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            self.gmail_service.users().messages().send(
                userId='me', body={'raw': raw_message}
            ).execute()
            
            print(f"✅ Email sent successfully to {to}")
            return True
            
        except HttpError as error:
            print(f"❌ Gmail API error: {error}")
            return False
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    def send_ai_generated_email(self, to: str, context: Dict[str, Any], 
                               subject: Optional[str] = None) -> bool:
        """Send AI-generated email"""
        # Generate content
        body = self.generate_ai_email_content(context)
        
        # Use provided subject or generate one
        if not subject:
            subject = self._generate_subject(context)
        
        # Send email
        return self.send_email(to, subject, body)
    
    def _generate_subject(self, context: Dict[str, Any]) -> str:
        """Generate email subject based on context"""
        email_type = context.get('type', 'general')
        
        subjects = {
            'quote_followup': 'Follow-up on Your Quote - Filterdyn Operations',
            'service_reminder': 'Service Reminder - Your Water Treatment Equipment',
            'water_quality_alert': 'URGENT: Water Quality Alert - Action Required',
            'general': 'Message from Filterdyn Operations'
        }
        
        return subjects.get(email_type, subjects['general'])
    
    def get_recent_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent emails from Gmail"""
        if not self.gmail_service:
            return []
        
        try:
            results = self.gmail_service.users().messages().list(
                userId='me', maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg = self.gmail_service.users().messages().get(
                    userId='me', id=message['id']
                ).execute()
                
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'from': from_email,
                    'date': date,
                    'snippet': msg.get('snippet', '')
                })
            
            return emails
            
        except Exception as e:
            print(f"❌ Failed to fetch emails: {e}")
            return []
    
    def create_email_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Create and save email template"""
        template = {
            'name': template_name,
            'context': context,
            'created_at': datetime.now().isoformat(),
            'body': self.generate_ai_email_content(context)
        }
        
        # Save template (in a real app, this would go to database)
        templates_dir = 'email_templates'
        os.makedirs(templates_dir, exist_ok=True)
        
        template_path = os.path.join(templates_dir, f"{template_name}.json")
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"✅ Email template '{template_name}' created")
        return template['body']
    
    def schedule_email(self, to: str, subject: str, body: str, 
                      send_time: datetime) -> bool:
        """Schedule email for later sending (basic implementation)"""
        # In a production system, this would use a task queue like Celery
        # For now, we'll just log the scheduled email
        scheduled_email = {
            'to': to,
            'subject': subject,
            'body': body,
            'send_time': send_time.isoformat(),
            'scheduled_at': datetime.now().isoformat()
        }
        
        # Save to file (in production, use database)
        scheduled_dir = 'scheduled_emails'
        os.makedirs(scheduled_dir, exist_ok=True)
        
        filename = f"scheduled_{send_time.strftime('%Y%m%d_%H%M%S')}_{hash(to)}.json"
        filepath = os.path.join(scheduled_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(scheduled_email, f, indent=2)
        
        print(f"✅ Email scheduled for {send_time}")
        return True


# Configuration example
DEFAULT_CONFIG = {
    'gmail_credentials_path': 'credentials.json',
    'gmail_token_path': 'token.json',
    'openai_api_key': os.getenv('OPENAI_API_KEY'),
    'default_from_email': 'noreply@filterdyn.com'
} 