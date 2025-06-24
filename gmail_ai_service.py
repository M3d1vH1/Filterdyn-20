import os
import json
import google.generativeai as genai
from models import AIEmailInteraction, GmailMessage
from app import db
from flask_login import current_user
from flask_babel import get_locale
from datetime import datetime, timezone
import logging

# Configure Gemini
genai.configure(api_key=os.environ.get('GOOGLE_GENAI_API_KEY'))

class GmailAIService:
    @staticmethod
    def get_model():
        """Get Gemini model instance"""
        return genai.GenerativeModel('gemini-1.5-flash')
    
    @staticmethod
    def analyze_email_content(email_text, language=None):
        """Analyze email content using Gemini AI"""
        try:
            model = GmailAIService.get_model()
            
            if not language:
                language = str(get_locale()) if get_locale() else 'en'
            
            prompt = f"""
            Analyze the following email and extract information in {language}:
            
            1. Key Information: Important dates, amounts, requirements, deadlines
            2. Sentiment: positive, neutral, negative, or urgent
            3. Intent: inquiry, complaint, order, support, follow-up, etc.
            4. Entities: Customer names, product references, order numbers, contact info
            5. Priority: low, medium, high, urgent
            6. Summary: Brief summary in 1-2 sentences
            
            Email content:
            {email_text}
            
            Please respond in JSON format with these exact fields:
            {{
                "key_info": ["list of key information"],
                "sentiment": "sentiment_value",
                "intent": "intent_value", 
                "entities": {{"names": [], "products": [], "orders": [], "amounts": [], "dates": []}},
                "priority": "priority_level",
                "summary": "brief summary"
            }}
            """
            
            start_time = datetime.now()
            response = model.generate_content(prompt)
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Try to parse JSON response
            try:
                result = json.loads(response.text.strip())
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                result = {
                    "key_info": [],
                    "sentiment": "neutral",
                    "intent": "general",
                    "entities": {"names": [], "products": [], "orders": [], "amounts": [], "dates": []},
                    "priority": "medium",
                    "summary": response.text[:200] + "..." if len(response.text) > 200 else response.text
                }
            
            # Store interaction for learning
            if current_user:
                GmailAIService.store_interaction(
                    tenant_id=current_user.tenant_id,
                    user_id=current_user.id,
                    interaction_type='analysis',
                    input_data={'email_text': email_text[:500], 'language': language},
                    ai_response=json.dumps(result),
                    processing_time_ms=processing_time
                )
            
            return result
            
        except Exception as e:
            logging.error(f"Email analysis error: {str(e)}")
            return {
                "key_info": [],
                "sentiment": "neutral", 
                "intent": "unknown",
                "entities": {"names": [], "products": [], "orders": [], "amounts": [], "dates": []},
                "priority": "medium",
                "summary": "Analysis failed",
                "error": str(e)
            }

    @staticmethod
    def suggest_response(email_text, context=None, language=None, tone="professional"):
        """Generate response suggestion using Gemini AI"""
        try:
            model = GmailAIService.get_model()
            
            if not language:
                language = str(get_locale()) if get_locale() else 'en'
            
            context_info = ""
            if context:
                context_info = f"\nAdditional context: {context}"
            
            prompt = f"""
            You are a professional business email assistant for a water treatment solutions company (Filterdyn).
            
            Generate a {tone} email response in {language} for the following email:
            
            Email to respond to:
            {email_text}
            {context_info}
            
            Guidelines:
            - Be professional and helpful
            - Address the main points from the original email
            - Keep it concise but complete
            - Use appropriate business language
            - Include a proper greeting and closing
            - If technical water treatment topics are mentioned, provide knowledgeable responses
            
            Generate only the email response content (no subject line needed):
            """
            
            start_time = datetime.now()
            response = model.generate_content(prompt)
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            suggested_response = response.text.strip()
            
            # Store interaction for learning
            if current_user:
                GmailAIService.store_interaction(
                    tenant_id=current_user.tenant_id,
                    user_id=current_user.id,
                    interaction_type='suggestion',
                    input_data={'email_text': email_text[:500], 'context': context, 'language': language, 'tone': tone},
                    ai_response=suggested_response,
                    processing_time_ms=processing_time
                )
            
            return suggested_response
            
        except Exception as e:
            logging.error(f"Response suggestion error: {str(e)}")
            return f"I apologize, but I'm unable to generate a response suggestion at this time. Please try again later. (Error: {str(e)})"

    @staticmethod
    def suggest_templates(email_text, language=None):
        """Suggest email templates based on content"""
        try:
            model = GmailAIService.get_model()
            
            if not language:
                language = str(get_locale()) if get_locale() else 'en'
            
            prompt = f"""
            Based on the following email content, suggest 3 different response templates in {language}.
            Each template should have a different tone: professional, friendly, and brief.
            
            Email content:
            {email_text}
            
            Respond in JSON format:
            {{
                "templates": [
                    {{"tone": "professional", "subject": "subject line", "body": "email body"}},
                    {{"tone": "friendly", "subject": "subject line", "body": "email body"}},
                    {{"tone": "brief", "subject": "subject line", "body": "email body"}}
                ]
            }}
            """
            
            start_time = datetime.now()
            response = model.generate_content(prompt)
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            try:
                result = json.loads(response.text.strip())
            except json.JSONDecodeError:
                # Fallback templates
                result = {
                    "templates": [
                        {"tone": "professional", "subject": "Re: Your inquiry", "body": "Thank you for your email. We will review your request and get back to you soon."},
                        {"tone": "friendly", "subject": "Re: Your message", "body": "Hi! Thanks for reaching out. I'll look into this and get back to you shortly."},
                        {"tone": "brief", "subject": "Re: Your email", "body": "Received. Will respond soon."}
                    ]
                }
            
            # Store interaction
            if current_user:
                GmailAIService.store_interaction(
                    tenant_id=current_user.tenant_id,
                    user_id=current_user.id,
                    interaction_type='templates',
                    input_data={'email_text': email_text[:500], 'language': language},
                    ai_response=json.dumps(result),
                    processing_time_ms=processing_time
                )
            
            return result
            
        except Exception as e:
            logging.error(f"Template suggestion error: {str(e)}")
            return {
                "templates": [
                    {"tone": "professional", "subject": "Re: Your inquiry", "body": "Thank you for your email. We appreciate your interest and will respond soon."},
                    {"tone": "friendly", "subject": "Re: Your message", "body": "Hello! Thanks for getting in touch. We'll get back to you as soon as possible."},
                    {"tone": "brief", "subject": "Re: Your email", "body": "Thank you for your email. We will respond shortly."}
                ],
                "error": str(e)
            }

    @staticmethod
    def extract_business_entities(email_text):
        """Extract business-relevant entities from email"""
        try:
            model = GmailAIService.get_model()
            
            prompt = f"""
            Extract business entities from this email that might relate to:
            - Customer information (names, companies, contact details)
            - Order references (order numbers, product codes)
            - Financial information (amounts, prices, invoices)
            - Dates and deadlines
            - Product or service references
            
            Email:
            {email_text}
            
            Return in JSON format:
            {{
                "customers": [{{"name": "", "company": "", "email": "", "phone": ""}}],
                "orders": ["order numbers or references"],
                "products": ["product names or codes"],
                "amounts": [{{"value": "", "currency": ""}}],
                "dates": [{{"date": "", "context": ""}}],
                "actions_required": ["list of actions"]
            }}
            """
            
            response = model.generate_content(prompt)
            
            try:
                result = json.loads(response.text.strip())
            except json.JSONDecodeError:
                result = {
                    "customers": [],
                    "orders": [],
                    "products": [],
                    "amounts": [],
                    "dates": [],
                    "actions_required": []
                }
            
            return result
            
        except Exception as e:
            logging.error(f"Entity extraction error: {str(e)}")
            return {
                "customers": [],
                "orders": [],
                "products": [],
                "amounts": [],
                "dates": [],
                "actions_required": [],
                "error": str(e)
            }

    @staticmethod
    def store_interaction(tenant_id, user_id, interaction_type, input_data, ai_response, 
                         message_id=None, processing_time_ms=None, tokens_used=None):
        """Store AI interaction for learning and analytics"""
        try:
            interaction = AIEmailInteraction(
                tenant_id=tenant_id,
                user_id=user_id,
                message_id=message_id,
                interaction_type=interaction_type,
                input_data=input_data,
                ai_response=ai_response,
                processing_time_ms=processing_time_ms,
                tokens_used=tokens_used
            )
            
            db.session.add(interaction)
            db.session.commit()
            
            return interaction
            
        except Exception as e:
            logging.error(f"Error storing AI interaction: {str(e)}")
            return None

    @staticmethod
    def provide_feedback(interaction_id, feedback, effectiveness_score=None):
        """Store user feedback on AI suggestions"""
        try:
            interaction = AIEmailInteraction.query.get(interaction_id)
            if interaction:
                interaction.user_feedback = feedback
                interaction.effectiveness_score = effectiveness_score
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            logging.error(f"Error storing feedback: {str(e)}")
            return False

    @staticmethod
    def get_learning_stats(tenant_id, user_id=None):
        """Get AI learning statistics"""
        try:
            query = AIEmailInteraction.query.filter_by(tenant_id=tenant_id)
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            interactions = query.all()
            
            total_interactions = len(interactions)
            feedback_given = len([i for i in interactions if i.user_feedback])
            avg_effectiveness = sum([i.effectiveness_score or 0 for i in interactions if i.effectiveness_score]) / max(1, len([i for i in interactions if i.effectiveness_score]))
            avg_processing_time = sum([i.processing_time_ms or 0 for i in interactions]) / max(1, total_interactions)
            
            by_type = {}
            for interaction in interactions:
                by_type[interaction.interaction_type] = by_type.get(interaction.interaction_type, 0) + 1
            
            return {
                "total_interactions": total_interactions,
                "feedback_given": feedback_given,
                "avg_effectiveness": round(avg_effectiveness, 2),
                "avg_processing_time_ms": round(avg_processing_time, 2),
                "by_type": by_type,
                "recent_interactions": len([i for i in interactions if (datetime.now(timezone.utc) - i.created_at).days <= 7])
            }
            
        except Exception as e:
            logging.error(f"Error getting learning stats: {str(e)}")
            return {
                "total_interactions": 0,
                "feedback_given": 0,
                "avg_effectiveness": 0,
                "avg_processing_time_ms": 0,
                "by_type": {},
                "recent_interactions": 0
            }