"""
Communication & AI Agent
=======================

Handles email integration, AI-powered composition, and communication automation.
Uses Google Gemini AI for content generation.
"""

import os
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Gmail API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("⚠️ Google API libraries not available")

# Gemini AI import
try:
    import sys
    sys.path.append('/home/runner/workspace/agents')
    from gemini_client import GeminiClient
except ImportError:
    GeminiClient = None


class CommunicationAIAgent:
    """Agent for handling email communication and AI-powered content generation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.gmail_service = None
        self.gemini_client = None
        self.setup_gmail_api()
        self.setup_gemini()
    
    def setup_gmail_api(self):
        """Initialize Gmail API connection"""
        try:
            # Gmail API scopes
            SCOPES = ['https://www.googleapis.com/auth/gmail.send',
                     'https://www.googleapis.com/auth/gmail.readonly']
            
            creds = None
            token_path = self.config.get('gmail_token_path', 'token.json')
            
            # Load existing token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # If no valid credentials, start OAuth flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    print("⚠️ Gmail credentials need setup")
                    return
            
            # Build Gmail service
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail API initialized")
            
        except Exception as e:
            print(f"❌ Gmail API setup failed: {e}")
    
    def setup_gemini(self):
        """Setup Gemini AI client"""
        try:
            api_key = self.config.get('gemini_api_key') or os.getenv('GEMINI_API_KEY')
            if GeminiClient and api_key:
                self.gemini_client = GeminiClient(api_key=api_key)
                print("✅ Gemini AI client initialized")
            else:
                print("⚠️ Gemini AI not available or API key not configured")
        except Exception as e:
            print(f"❌ Gemini AI setup failed: {e}")
    
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
            
            print("✅ Gmail authentication successful")
            return True
            
        except Exception as e:
            print(f"❌ Gmail authentication failed: {e}")
            return False
    
    def generate_ai_email_content(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate email content using AI based on context"""
        if not self.gemini_client:
            return self._generate_fallback_content(context)
        
        try:
            return self.gemini_client.generate_email_content(context)
            
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
    
    def _generate_fallback_content(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate fallback email content when AI is not available"""
        email_type = context.get('type', 'general')
        customer_name = context.get('customer_name', 'Valued Customer')
        
        if email_type == 'service_reminder':
            equipment_number = context.get('equipment_number', 'N/A')
            days_until_due = context.get('days_until_due', 30)
            return {
                'subject': f'Service Reminder - {equipment_number}',
                'body': f"""Dear {customer_name},

This is a reminder that your equipment {equipment_number} requires service in {days_until_due} days.

Please contact us to schedule your service appointment.

Best regards,
Filterdyn Team"""
            }
        
        elif email_type == 'water_quality_alert':
            equipment_number = context.get('equipment_number', 'N/A')
            parameter = context.get('parameter', 'water quality')
            alert_type = context.get('alert_type', 'warning')
            return {
                'subject': f'{alert_type.title()} Alert - {equipment_number}',
                'body': f"""Dear {customer_name},

We detected a {alert_type} level issue with your equipment {equipment_number} regarding {parameter}.

Please contact us immediately for assistance.

Best regards,
Filterdyn Team"""
            }
        
        else:
            return {
                'subject': 'Filterdyn Communication',
                'body': f"""Dear {customer_name},

Thank you for contacting Filterdyn. We will get back to you shortly.

Best regards,
Filterdyn Team"""
            }
    
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
            
            if from_email:
                message['from'] = from_email
            else:
                message['from'] = self.config.get('default_from_email', 'noreply@filterdyn.com')
            
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
        email_content = self.generate_ai_email_content(context)
        
        # Use provided subject or generated one
        subject = subject or email_content.get('subject', self._generate_subject(context))
        body = email_content.get('body', 'Email content could not be generated.')
        
        # Send email
        return self.send_email(to, subject, body)
    
    def _generate_subject(self, context: Dict[str, Any]) -> str:
        """Generate email subject based on context"""
        email_type = context.get('type', 'general')
        customer_name = context.get('customer_name', 'Customer')
        
        subjects = {
            'service_reminder': f"Service Reminder for {customer_name}",
            'water_quality_alert': f"Water Quality Alert - {customer_name}",
            'quote_followup': f"Follow-up: Your Quote from Filterdyn",
            'general': f"Message from Filterdyn"
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
            email_list = []
            
            for message in messages:
                msg = self.gmail_service.users().messages().get(
                    userId='me', id=message['id']
                ).execute()
                
                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                email_list.append({
                    'id': message['id'],
                    'subject': subject,
                    'from': sender,
                    'date': date
                })
            
            return email_list
            
        except Exception as e:
            print(f"❌ Failed to retrieve emails: {e}")
            return []
    
    def create_email_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Create and save email template"""
        template_content = self.generate_ai_email_content(context)
        
        # Save template (in production, use database)
        templates_dir = 'email_templates'
        os.makedirs(templates_dir, exist_ok=True)
        
        template_file = os.path.join(templates_dir, f"{template_name}.json")
        with open(template_file, 'w') as f:
            json.dump({
                'name': template_name,
                'subject': template_content.get('subject', ''),
                'body': template_content.get('body', ''),
                'created_at': datetime.now().isoformat(),
                'context': context
            }, f, indent=2)
        
        print(f"✅ Email template '{template_name}' created")
        return template_file
    
    def schedule_email(self, to: str, subject: str, body: str, 
                      send_time: datetime) -> bool:
        """Schedule email for later sending (basic implementation)"""
        scheduled_email = {
            'to': to,
            'subject': subject,
            'body': body,
            'send_time': send_time.isoformat(),
            'created_at': datetime.now().isoformat(),
            'status': 'scheduled'
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
    'gemini_api_key': os.getenv('GEMINI_API_KEY'),
    'default_from_email': 'noreply@filterdyn.com'
}