import os
import openai
from models.gmail_models import AIEmailLearningData, GmailMessage
from app import db
from flask_login import current_user
from flask_babel import get_locale
from datetime import datetime, timezone

openai.api_key = os.environ.get('OPENAI_API_KEY')

class AIEmailService:
    @staticmethod
    def analyze_email_content(email_text, language=None):
        """Analyze email content: extract entities, sentiment, intent, etc."""
        prompt = f"""
Analyze the following email and extract:
- Key information (dates, amounts, requirements)
- Sentiment (positive, neutral, negative)
- Intent (inquiry, complaint, order, etc.)
- Entities (customer names, product references, order numbers)

Email:
{email_text}

Respond in JSON format with fields: key_info, sentiment, intent, entities.
"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a business email analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=512
        )
        return response.choices[0].message['content']

    @staticmethod
    def suggest_response(email_text, context=None, language=None, tone="professional"):
        """Generate a smart response suggestion for an email."""
        prompt = f"""
Given the following email, draft a reply in a {tone} tone. If context is provided, use it to personalize the response. Respond in {language or 'English'}.

Email:
{email_text}

Context:
{context or ''}
"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a business email assistant that drafts professional replies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=512
        )
        return response.choices[0].message['content']

    @staticmethod
    def suggest_templates(email_text, language=None):
        """Suggest email templates based on the email content."""
        prompt = f"""
Suggest 3 email response templates for the following email. Respond in {language or 'English'}.

Email:
{email_text}

Respond in JSON array format with fields: subject, body.
"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a business email template assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=512
        )
        return response.choices[0].message['content']

    @staticmethod
    def store_learning_data(user_id, tenant_id, gmail_message_id, input_text, ai_suggestion, user_feedback, effectiveness_score=None):
        learning = AIEmailLearningData(
            user_id=user_id,
            tenant_id=tenant_id,
            gmail_message_id=gmail_message_id,
            input_text=input_text,
            ai_suggestion=ai_suggestion,
            user_feedback=user_feedback,
            effectiveness_score=effectiveness_score,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(learning)
        db.session.commit()
        return learning 