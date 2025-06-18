"""
Gemini AI Client for Filterdyn Operations Suite
==============================================

Unified client for Google Gemini AI integration.
"""

import os
import google.generativeai as genai
from typing import Dict, Any, Optional, List
import json
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for Google Gemini AI API"""
    
    def __init__(self, api_key: str = None):
        """Initialize Gemini client"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using Gemini"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini content generation failed: {e}")
            raise
    
    def generate_email_content(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate email content based on context"""
        email_type = context.get('type', 'general')
        
        if email_type == 'service_reminder':
            return self._generate_service_reminder_email(context)
        elif email_type == 'water_quality_alert':
            return self._generate_water_quality_alert_email(context)
        elif email_type == 'quote_follow_up':
            return self._generate_quote_follow_up_email(context)
        elif email_type == 'maintenance_completion':
            return self._generate_maintenance_completion_email(context)
        else:
            return self._generate_general_email(context)
    
    def _generate_service_reminder_email(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate service reminder email"""
        customer_name = context.get('customer_name', 'Valued Customer')
        equipment_number = context.get('equipment_number', 'N/A')
        service_type = context.get('service_type', 'maintenance')
        days_until_due = context.get('days_until_due', 30)
        
        prompt = f"""
        Write a professional service reminder email for a water treatment equipment customer.
        
        Details:
        - Customer: {customer_name}
        - Equipment: {equipment_number}
        - Service Type: {service_type}
        - Days until due: {days_until_due}
        
        Requirements:
        - Professional but friendly tone
        - Emphasize the importance of regular maintenance
        - Include benefits of timely service
        - Provide contact information placeholder
        - Keep it concise (under 200 words)
        - Include subject line
        
        Format as JSON with 'subject' and 'body' keys.
        """
        
        try:
            response = self.generate_content(prompt)
            # Parse JSON response
            content = json.loads(response)
            return {
                'subject': content.get('subject', f'Service Reminder - {equipment_number}'),
                'body': content.get('body', 'Service reminder email content')
            }
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse Gemini email response: {e}")
            return {
                'subject': f'Service Reminder - {equipment_number}',
                'body': f'Dear {customer_name},\n\nThis is a reminder that your equipment {equipment_number} requires {service_type} in {days_until_due} days.\n\nPlease contact us to schedule your service appointment.\n\nBest regards,\nFilterdyn Team'
            }
    
    def _generate_water_quality_alert_email(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate water quality alert email"""
        customer_name = context.get('customer_name', 'Valued Customer')
        equipment_number = context.get('equipment_number', 'N/A')
        parameter = context.get('parameter', 'water quality')
        value = context.get('value', 'N/A')
        threshold = context.get('threshold', 'N/A')
        alert_type = context.get('alert_type', 'warning')
        
        prompt = f"""
        Write a professional water quality alert email for a water treatment equipment customer.
        
        Details:
        - Customer: {customer_name}
        - Equipment: {equipment_number}
        - Parameter: {parameter}
        - Current Value: {value}
        - Threshold: {threshold}
        - Alert Level: {alert_type}
        
        Requirements:
        - Professional and urgent tone for critical alerts
        - Explain the issue and potential consequences
        - Recommend immediate action
        - Include contact information placeholder
        - Keep it concise but informative
        - Include subject line
        
        Format as JSON with 'subject' and 'body' keys.
        """
        
        try:
            response = self.generate_content(prompt)
            content = json.loads(response)
            return {
                'subject': content.get('subject', f'{alert_type.title()} Alert - {equipment_number}'),
                'body': content.get('body', 'Water quality alert email content')
            }
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse Gemini alert email response: {e}")
            return {
                'subject': f'{alert_type.title()} Alert - {equipment_number}',
                'body': f'Dear {customer_name},\n\nWe detected a {alert_type} level alert for your equipment {equipment_number}.\n\nParameter: {parameter}\nCurrent Value: {value}\nThreshold: {threshold}\n\nPlease contact us immediately for assistance.\n\nBest regards,\nFilterdyn Team'
            }
    
    def _generate_quote_follow_up_email(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate quote follow-up email"""
        customer_name = context.get('customer_name', 'Valued Customer')
        quote_number = context.get('quote_number', 'N/A')
        quote_date = context.get('quote_date', 'recently')
        days_since_quote = context.get('days_since_quote', 7)
        
        prompt = f"""
        Write a professional quote follow-up email for a water treatment solutions customer.
        
        Details:
        - Customer: {customer_name}
        - Quote Number: {quote_number}
        - Quote Date: {quote_date}
        - Days since quote: {days_since_quote}
        
        Requirements:
        - Professional and helpful tone
        - Not pushy but encouraging
        - Offer to answer questions
        - Provide value proposition
        - Include contact information placeholder
        - Keep it concise (under 150 words)
        - Include subject line
        
        Format as JSON with 'subject' and 'body' keys.
        """
        
        try:
            response = self.generate_content(prompt)
            content = json.loads(response)
            return {
                'subject': content.get('subject', f'Follow-up on Quote {quote_number}'),
                'body': content.get('body', 'Quote follow-up email content')
            }
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse Gemini quote email response: {e}")
            return {
                'subject': f'Follow-up on Quote {quote_number}',
                'body': f'Dear {customer_name},\n\nI wanted to follow up on the quote {quote_number} we sent {days_since_quote} days ago.\n\nDo you have any questions about our proposal? We\'re here to help with any clarifications.\n\nBest regards,\nFilterdyn Team'
            }
    
    def _generate_maintenance_completion_email(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate maintenance completion email"""
        customer_name = context.get('customer_name', 'Valued Customer')
        equipment_number = context.get('equipment_number', 'N/A')
        service_date = context.get('service_date', 'today')
        technician = context.get('technician', 'our technician')
        next_service_date = context.get('next_service_date', 'TBD')
        
        prompt = f"""
        Write a professional maintenance completion email for a water treatment equipment customer.
        
        Details:
        - Customer: {customer_name}
        - Equipment: {equipment_number}
        - Service Date: {service_date}
        - Technician: {technician}
        - Next Service Date: {next_service_date}
        
        Requirements:
        - Professional and reassuring tone
        - Confirm work completion
        - Mention next service date
        - Invite feedback
        - Include contact information placeholder
        - Keep it concise (under 150 words)
        - Include subject line
        
        Format as JSON with 'subject' and 'body' keys.
        """
        
        try:
            response = self.generate_content(prompt)
            content = json.loads(response)
            return {
                'subject': content.get('subject', f'Service Completed - {equipment_number}'),
                'body': content.get('body', 'Maintenance completion email content')
            }
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse Gemini maintenance email response: {e}")
            return {
                'subject': f'Service Completed - {equipment_number}',
                'body': f'Dear {customer_name},\n\nWe completed the maintenance service for your equipment {equipment_number} on {service_date}.\n\nTechnician: {technician}\nNext Service Date: {next_service_date}\n\nPlease contact us if you have any questions.\n\nBest regards,\nFilterdyn Team'
            }
    
    def _generate_general_email(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate general email content"""
        customer_name = context.get('customer_name', 'Valued Customer')
        topic = context.get('topic', 'general inquiry')
        
        return {
            'subject': f'Regarding {topic}',
            'body': f'Dear {customer_name},\n\nThank you for contacting Filterdyn regarding {topic}.\n\nWe will get back to you shortly with more information.\n\nBest regards,\nFilterdyn Team'
        }
    
    def analyze_water_quality_data(self, measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze water quality data and provide insights"""
        if not measurements:
            return {'analysis': 'No data available for analysis'}
        
        # Prepare data summary for Gemini
        data_summary = []
        for measurement in measurements[-10:]:  # Last 10 measurements
            data_summary.append({
                'date': measurement.get('date', 'N/A'),
                'ph': measurement.get('ph', 'N/A'),
                'conductivity': measurement.get('conductivity', 'N/A'),
                'temperature': measurement.get('temperature', 'N/A'),
                'turbidity': measurement.get('turbidity', 'N/A')
            })
        
        prompt = f"""
        Analyze the following water quality measurements and provide insights:
        
        Data: {json.dumps(data_summary, indent=2)}
        
        Please provide:
        1. Overall water quality assessment
        2. Trend analysis (improving/declining/stable)
        3. Any parameters of concern
        4. Recommendations for action
        
        Format as JSON with keys: 'assessment', 'trends', 'concerns', 'recommendations'
        """
        
        try:
            response = self.generate_content(prompt)
            analysis = json.loads(response)
            return analysis
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to analyze water quality data: {e}")
            return {
                'assessment': 'Unable to analyze data',
                'trends': 'Analysis unavailable',
                'concerns': 'None identified',
                'recommendations': 'Please review data manually'
            }