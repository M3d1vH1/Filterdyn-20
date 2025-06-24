"""
AI Email Processing Module
Uses Gemini AI to analyze emails for business intelligence
"""

import os
import json
import logging
from typing import Dict, Any, List
from google import genai
from google.genai import types
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailAnalysis(BaseModel):
    """Structured email analysis result"""
    category: str
    intent: str
    sentiment: str
    priority: str
    entities: Dict[str, Any]
    summary: str
    suggested_actions: List[str]
    customer_satisfaction: str
    requires_response: bool
    urgency_level: int

class AIEmailProcessor:
    """AI-powered email processing and analysis"""
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
    
    def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email with AI analysis"""
        try:
            # Prepare email content for analysis
            content = self._prepare_email_content(email_data)
            
            # Analyze with Gemini
            analysis = self._analyze_with_gemini(content, email_data)
            
            return {
                'category': analysis.category,
                'intent': analysis.intent,
                'sentiment': analysis.sentiment,
                'priority': analysis.priority,
                'entities': analysis.entities,
                'summary': analysis.summary,
                'suggested_actions': analysis.suggested_actions,
                'customer_satisfaction': analysis.customer_satisfaction,
                'requires_response': analysis.requires_response,
                'urgency_level': analysis.urgency_level
            }
            
        except Exception as e:
            logger.error(f"AI email processing failed: {str(e)}")
            return self._fallback_analysis(email_data)
    
    def _prepare_email_content(self, email_data: Dict[str, Any]) -> str:
        """Prepare email content for AI analysis"""
        content_parts = []
        
        content_parts.append(f"Subject: {email_data.get('subject', '')}")
        content_parts.append(f"From: {email_data.get('sender', '')}")
        content_parts.append(f"To: {email_data.get('recipient', '')}")
        
        if email_data.get('cc'):
            content_parts.append(f"CC: {email_data['cc']}")
        
        content_parts.append("Body:")
        body = email_data.get('body_text') or email_data.get('body_html', '')
        content_parts.append(body[:2000])  # Limit content length
        
        return "\n".join(content_parts)
    
    def _analyze_with_gemini(self, content: str, email_data: Dict[str, Any]) -> EmailAnalysis:
        """Analyze email content with Gemini AI"""
        
        system_prompt = """
        You are an AI assistant specialized in analyzing business emails for a water treatment solutions company called Filterdyn. 
        
        Analyze the email and provide structured information about:
        1. Category: customer_inquiry, quote_request, order_update, complaint, technical_support, general, spam
        2. Intent: information_request, quote_request, order_placement, complaint, support_request, follow_up, other
        3. Sentiment: positive, neutral, negative, frustrated, satisfied
        4. Priority: low, medium, high, urgent
        5. Entities: Extract customer names, product references, order numbers, dates, amounts, phone numbers
        6. Summary: Brief 2-3 sentence summary of the email
        7. Suggested actions: List of 2-3 specific actions to take
        8. Customer satisfaction: satisfied, neutral, dissatisfied, unknown
        9. Requires response: true/false
        10. Urgency level: 1-5 (1=low, 5=critical)
        
        Focus on water treatment industry context, filtration equipment, maintenance services, and customer relations.
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=content)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=EmailAnalysis,
                    temperature=0.3
                ),
            )
            
            if response.text:
                data = json.loads(response.text)
                return EmailAnalysis(**data)
            else:
                raise ValueError("Empty response from AI")
                
        except Exception as e:
            logger.error(f"Gemini analysis failed: {str(e)}")
            raise
    
    def _fallback_analysis(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI fails"""
        subject = email_data.get('subject', '').lower()
        body = (email_data.get('body_text') or email_data.get('body_html', '')).lower()
        
        # Simple keyword-based analysis
        category = 'general'
        if any(word in subject + body for word in ['quote', 'quotation', 'price', 'cost']):
            category = 'quote_request'
        elif any(word in subject + body for word in ['order', 'purchase', 'buy']):
            category = 'order_update'
        elif any(word in subject + body for word in ['problem', 'issue', 'broken', 'not working']):
            category = 'technical_support'
        elif any(word in subject + body for word in ['complaint', 'unhappy', 'disappointed']):
            category = 'complaint'
        
        return {
            'category': category,
            'intent': 'information_request',
            'sentiment': 'neutral',
            'priority': 'medium',
            'entities': {},
            'summary': f"Email from {email_data.get('sender', 'unknown')} regarding {email_data.get('subject', 'general inquiry')}",
            'suggested_actions': ['Review email content', 'Respond within 24 hours'],
            'customer_satisfaction': 'unknown',
            'requires_response': True,
            'urgency_level': 2
        }
    
    def generate_response_suggestion(self, email_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate AI-powered response suggestions"""
        try:
            # Prepare context
            content = self._prepare_email_content(email_data)
            
            context_info = ""
            if context:
                if context.get('customer_info'):
                    context_info += f"Customer: {context['customer_info']}\n"
                if context.get('previous_orders'):
                    context_info += f"Previous orders: {context['previous_orders']}\n"
                if context.get('quote_history'):
                    context_info += f"Quote history: {context['quote_history']}\n"
            
            system_prompt = f"""
            You are a customer service representative for Filterdyn, a water treatment solutions company.
            Generate a professional, helpful response to the customer email.
            
            Context about the customer:
            {context_info}
            
            Guidelines:
            - Be professional and friendly
            - Address their specific concerns
            - Provide helpful information about water treatment solutions
            - Include next steps if applicable
            - Keep response concise but complete
            - Use proper business email format
            - Sign as "Filterdyn Support Team"
            
            Generate 3 different response options: formal, friendly, and technical.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Original email:\n{content}\n\nGenerate response suggestions."
            )
            
            suggestions = response.text if response.text else "I'll review your inquiry and respond shortly."
            
            return {
                'success': True,
                'suggestions': [
                    {'type': 'formal', 'content': suggestions},
                    {'type': 'friendly', 'content': suggestions.replace('Dear', 'Hi')},
                    {'type': 'technical', 'content': suggestions}
                ]
            }
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback': "Thank you for your inquiry. I'll review your message and respond within 24 hours."
            }
    
    def extract_business_entities(self, text: str) -> Dict[str, Any]:
        """Extract business-relevant entities from text"""
        try:
            system_prompt = """
            Extract business entities from the text:
            - Customer names and companies
            - Product names and models
            - Order numbers and reference IDs
            - Dates and deadlines
            - Monetary amounts and prices
            - Phone numbers and email addresses
            - Technical specifications
            - Location information
            
            Return as JSON with entity types as keys and lists of found entities as values.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Text to analyze: {text[:1500]}",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            
            if response.text:
                return json.loads(response.text)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return {}
    
    def categorize_customer_satisfaction(self, email_content: str) -> str:
        """Determine customer satisfaction level from email"""
        try:
            system_prompt = """
            Analyze the customer satisfaction level from this email content.
            Return one of: very_satisfied, satisfied, neutral, dissatisfied, very_dissatisfied
            
            Consider:
            - Tone and language used
            - Explicit satisfaction statements
            - Complaints or praise
            - Urgency and frustration indicators
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Email content: {email_content[:1000]}",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.1
                )
            )
            
            result = response.text.strip().lower() if response.text else 'neutral'
            
            valid_levels = ['very_satisfied', 'satisfied', 'neutral', 'dissatisfied', 'very_dissatisfied']
            return result if result in valid_levels else 'neutral'
            
        except Exception as e:
            logger.error(f"Satisfaction analysis failed: {str(e)}")
            return 'neutral'
    
    def suggest_follow_up_actions(self, email_analysis: Dict[str, Any], business_context: Dict[str, Any] = None) -> List[str]:
        """Suggest follow-up actions based on email analysis"""
        actions = []
        
        category = email_analysis.get('category', '')
        urgency = email_analysis.get('urgency_level', 1)
        intent = email_analysis.get('intent', '')
        
        # Urgency-based actions
        if urgency >= 4:
            actions.append("Respond immediately - high urgency")
        elif urgency >= 3:
            actions.append("Respond within 2 hours")
        else:
            actions.append("Respond within 24 hours")
        
        # Category-specific actions
        if category == 'quote_request':
            actions.extend([
                "Prepare detailed quote",
                "Schedule site visit if needed",
                "Send product specifications"
            ])
        elif category == 'technical_support':
            actions.extend([
                "Escalate to technical team",
                "Schedule maintenance visit",
                "Provide troubleshooting guide"
            ])
        elif category == 'complaint':
            actions.extend([
                "Acknowledge complaint promptly",
                "Investigate issue thoroughly",
                "Propose resolution plan"
            ])
        elif category == 'order_update':
            actions.extend([
                "Check order status",
                "Update delivery timeline",
                "Coordinate with logistics"
            ])
        
        # Intent-specific actions
        if intent == 'information_request':
            actions.append("Provide comprehensive information")
        elif intent == 'follow_up':
            actions.append("Check on previous communication")
        
        return actions[:5]  # Limit to 5 actions