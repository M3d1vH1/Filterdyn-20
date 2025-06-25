"""
Enhanced Gmail AI Service with Gemini Integration
Replaces OpenAI with Google's Gemini for better Gmail integration
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import google.generativeai as genai
from models_gmail import GmailMessage, AIEmailAnalysis, AIEmailLearningData
from models import Customer, Order, Quote, Task
from app import db
from flask_login import current_user
from flask_babel import get_locale

# Configure Gemini AI
genai.configure(api_key=os.environ.get('GOOGLE_GENAI_API_KEY'))

class GmailAIEnhancedService:
    """Enhanced Gmail AI Service using Google Gemini"""
    
    @staticmethod
    def get_model():
        """Get Gemini model instance"""
        return genai.GenerativeModel('gemini-1.5-flash')
    
    @staticmethod
    def analyze_email_content(email_text: str, language: str = None) -> Dict[str, Any]:
        """Analyze email content using Gemini AI with enhanced business context"""
        if not email_text.strip():
            return {"error": "Empty email content"}
        
        # Get current locale if language not specified
        if not language:
            language = str(get_locale())
        
        # Enhanced prompt for business email analysis
        prompt = f"""
        Analyze this business email and extract the following information in JSON format:
        
        Email Content:
        {email_text}
        
        Please provide analysis in {language} and return JSON with these fields:
        
        {{
            "sentiment": "positive|neutral|negative",
            "intent": "inquiry|complaint|order|support|quote_request|follow_up|other",
            "urgency": "low|medium|high|urgent",
            "key_info": {{
                "dates": ["list of mentioned dates"],
                "amounts": ["list of monetary amounts or quantities"],
                "products": ["list of mentioned products or services"],
                "requirements": ["list of specific requirements or requests"]
            }},
            "entities": {{
                "person_names": ["list of person names"],
                "company_names": ["list of company names"],
                "locations": ["list of locations"],
                "contact_info": ["phone numbers, emails"]
            }},
            "action_items": ["list of actions requested or implied"],
            "business_category": "sales|support|technical|administrative|other",
            "confidence_score": 0.85
        }}
        
        Focus on extracting business-relevant information for a water treatment/filtration company.
        """
        
        try:
            model = GmailAIEnhancedService.get_model()
            response = model.generate_content(prompt)
            
            # Parse JSON response
            analysis_data = json.loads(response.text)
            
            # Store analysis if we have a current user context
            if current_user.is_authenticated:
                GmailAIEnhancedService.store_interaction(
                    current_user.tenant_id,
                    current_user.id,
                    'email_analysis',
                    {'email_text': email_text[:500]},  # Store first 500 chars
                    analysis_data
                )
            
            return analysis_data
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "sentiment": "neutral",
                "intent": "other",
                "urgency": "medium",
                "key_info": {"summary": response.text[:200]},
                "entities": {},
                "action_items": [],
                "business_category": "other",
                "confidence_score": 0.5
            }
        except Exception as e:
            logging.error(f"Email analysis error: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    @staticmethod
    def suggest_response(email_text: str, context: str = None, language: str = None, tone: str = "professional") -> Dict[str, Any]:
        """Generate response suggestion using Gemini AI"""
        if not language:
            language = str(get_locale())
        
        # Enhanced context-aware prompt
        prompt = f"""
        You are an AI assistant helping to compose professional email responses for a water treatment and filtration company (Filterdyn).
        
        Original Email:
        {email_text}
        
        Additional Context:
        {context or 'No additional context provided'}
        
        Please generate a {tone} email response in {language} that:
        1. Acknowledges the sender's message appropriately
        2. Addresses their main concerns or requests
        3. Maintains a {tone} tone throughout
        4. Includes relevant company expertise (water treatment, filtration systems)
        5. Provides clear next steps or call to action when appropriate
        
        Return JSON with:
        {{
            "subject": "Suggested email subject line",
            "response": "Full email response text",
            "key_points": ["main points addressed"],
            "tone_used": "{tone}",
            "suggestions": {{
                "alternative_openings": ["2-3 alternative opening sentences"],
                "alternative_closings": ["2-3 alternative closing sentences"],
                "follow_up_actions": ["suggested follow-up actions"]
            }}
        }}
        """
        
        try:
            model = GmailAIEnhancedService.get_model()
            response = model.generate_content(prompt)
            
            suggestion_data = json.loads(response.text)
            
            # Store interaction
            if current_user.is_authenticated:
                GmailAIEnhancedService.store_interaction(
                    current_user.tenant_id,
                    current_user.id,
                    'response_suggestion',
                    {'email_text': email_text[:500], 'context': context, 'tone': tone},
                    suggestion_data
                )
            
            return suggestion_data
            
        except json.JSONDecodeError:
            # Fallback response
            return {
                "subject": "Re: Your Inquiry",
                "response": f"Thank you for your email. We have received your message and will respond shortly.\n\nBest regards,\n{current_user.first_name if current_user.is_authenticated else 'Filterdyn Team'}",
                "key_points": ["Acknowledgment"],
                "tone_used": tone,
                "suggestions": {}
            }
        except Exception as e:
            logging.error(f"Response suggestion error: {str(e)}")
            return {"error": f"Suggestion failed: {str(e)}"}
    
    @staticmethod
    def suggest_templates(email_text: str, language: str = None) -> Dict[str, Any]:
        """Suggest email templates based on content analysis"""
        if not language:
            language = str(get_locale())
        
        prompt = f"""
        Based on this email content, suggest 3-5 appropriate email templates for a water treatment company:
        
        Email: {email_text}
        
        Return JSON with template suggestions in {language}:
        {{
            "templates": [
                {{
                    "name": "Template name",
                    "category": "sales|support|technical|follow_up",
                    "subject": "Email subject template",
                    "body": "Email body template with [PLACEHOLDER] for customization",
                    "use_case": "When to use this template",
                    "tone": "professional|friendly|formal"
                }}
            ]
        }}
        
        Focus on templates relevant to water treatment, filtration systems, and customer service.
        """
        
        try:
            model = GmailAIEnhancedService.get_model()
            response = model.generate_content(prompt)
            
            templates_data = json.loads(response.text)
            
            # Store interaction
            if current_user.is_authenticated:
                GmailAIEnhancedService.store_interaction(
                    current_user.tenant_id,
                    current_user.id,
                    'template_suggestions',
                    {'email_text': email_text[:500]},
                    templates_data
                )
            
            return templates_data
            
        except Exception as e:
            logging.error(f"Template suggestion error: {str(e)}")
            return {"error": f"Template suggestion failed: {str(e)}"}
    
    @staticmethod
    def extract_business_entities(email_text: str) -> Dict[str, Any]:
        """Extract business entities and suggest database links"""
        prompt = f"""
        Analyze this email for business entities that could be linked to database records:
        
        Email: {email_text}
        
        Extract and return JSON:
        {{
            "potential_customers": [
                {{
                    "name": "Company or person name",
                    "confidence": 0.85,
                    "context": "How they were mentioned",
                    "contact_info": "email/phone if mentioned"
                }}
            ],
            "potential_orders": [
                {{
                    "description": "Order or product reference",
                    "confidence": 0.75,
                    "context": "How it was mentioned"
                }}
            ],
            "potential_quotes": [
                {{
                    "description": "Quote or pricing reference",
                    "confidence": 0.80,
                    "context": "Context of mention"
                }}
            ],
            "suggested_actions": [
                "Link to existing customer John Smith",
                "Create new quote for filtration system",
                "Follow up on pending order #123"
            ]
        }}
        """
        
        try:
            model = GmailAIEnhancedService.get_model()
            response = model.generate_content(prompt)
            
            entities_data = json.loads(response.text)
            
            # Enhance with actual database matches
            entities_data = GmailAIEnhancedService._enhance_with_db_matches(entities_data)
            
            return entities_data
            
        except Exception as e:
            logging.error(f"Entity extraction error: {str(e)}")
            return {"error": f"Entity extraction failed: {str(e)}"}
    
    @staticmethod
    def _enhance_with_db_matches(entities_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance extracted entities with actual database matches"""
        if not current_user.is_authenticated:
            return entities_data
        
        try:
            # Search for matching customers
            if 'potential_customers' in entities_data:
                for customer_entity in entities_data['potential_customers']:
                    name = customer_entity.get('name', '')
                    if name:
                        # Search for similar customer names
                        matches = Customer.query.filter(
                            Customer.tenant_id == current_user.tenant_id,
                            Customer.name.ilike(f'%{name}%')
                        ).limit(3).all()
                        
                        customer_entity['database_matches'] = [
                            {
                                'id': c.id,
                                'name': c.name,
                                'email': c.email,
                                'similarity': 'high' if name.lower() in c.name.lower() else 'medium'
                            } for c in matches
                        ]
            
            # Add database match indicators
            entities_data['has_database_matches'] = any(
                'database_matches' in entity and entity['database_matches']
                for entity in entities_data.get('potential_customers', [])
            )
            
        except Exception as e:
            logging.error(f"Database matching error: {str(e)}")
        
        return entities_data
    
    @staticmethod
    def store_interaction(tenant_id: int, user_id: int, interaction_type: str, 
                         input_data: Dict, ai_response: Dict, 
                         message_id: str = None, processing_time_ms: int = None, 
                         tokens_used: int = None) -> int:
        """Store AI interaction for learning and analytics"""
        try:
            learning_data = AIEmailLearningData(
                tenant_id=tenant_id,
                user_id=user_id,
                interaction_type=interaction_type,
                input_data=input_data,
                ai_response=ai_response,
                processing_time_ms=processing_time_ms,
                tokens_used=tokens_used,
                model_version='gemini-1.5-flash'
            )
            
            db.session.add(learning_data)
            db.session.commit()
            
            return learning_data.id
            
        except Exception as e:
            logging.error(f"Failed to store AI interaction: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def provide_feedback(interaction_id: int, feedback: str, effectiveness_score: int = None) -> bool:
        """Store user feedback on AI suggestions"""
        try:
            learning_data = AIEmailLearningData.query.get(interaction_id)
            if learning_data:
                learning_data.feedback_comment = feedback
                learning_data.feedback_rating = effectiveness_score
                learning_data.was_helpful = effectiveness_score and effectiveness_score >= 3
                
                db.session.commit()
                return True
                
        except Exception as e:
            logging.error(f"Failed to store feedback: {str(e)}")
            db.session.rollback()
            
        return False
    
    @staticmethod
    def get_learning_stats(tenant_id: int, user_id: int = None) -> Dict[str, Any]:
        """Get AI learning statistics"""
        try:
            query = AIEmailLearningData.query.filter_by(tenant_id=tenant_id)
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            total_interactions = query.count()
            helpful_interactions = query.filter_by(was_helpful=True).count()
            
            # Interaction type breakdown
            interaction_types = db.session.query(
                AIEmailLearningData.interaction_type,
                db.func.count(AIEmailLearningData.id)
            ).filter_by(tenant_id=tenant_id).group_by(
                AIEmailLearningData.interaction_type
            ).all()
            
            # Average ratings
            avg_rating = db.session.query(
                db.func.avg(AIEmailLearningData.feedback_rating)
            ).filter(
                AIEmailLearningData.tenant_id == tenant_id,
                AIEmailLearningData.feedback_rating.isnot(None)
            ).scalar() or 0
            
            return {
                'total_interactions': total_interactions,
                'helpful_interactions': helpful_interactions,
                'helpfulness_rate': helpful_interactions / total_interactions if total_interactions > 0 else 0,
                'average_rating': round(float(avg_rating), 2),
                'interaction_breakdown': {itype: count for itype, count in interaction_types},
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logging.error(f"Failed to get learning stats: {str(e)}")
            return {'error': str(e)}