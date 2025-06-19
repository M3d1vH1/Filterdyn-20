import os
import json
import google.generativeai as genai
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_babel import _, get_locale
from models import Customer, Product, ProductCategory, Task, User
from app import db
from datetime import datetime, timezone
import logging

# Configure Gemini AI
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

ai_bp = Blueprint('ai_assistant', __name__, url_prefix='/ai')

class GeminiVoiceProcessor:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        
    def process_voice_command(self, text, language='el'):
        """Process voice command and extract structured data"""
        try:
            # Create language-specific prompts
            if language == 'el':
                system_prompt = """
Είσαι ένας έξυπνος βοηθός για την εφαρμογή Filterdyn που διαχειρίζεται πελάτες, προϊόντα και εργασίες για εταιρείες επεξεργασίας νερού.

Αναλύει τις φωνητικές εντολές και εξάγει δομημένα δεδομένα. Απάντησε ΜΟΝΟ με έγκυρο JSON.

Τύποι εντολών:
1. CUSTOMER: Δημιουργία πελάτη
2. PRODUCT: Δημιουργία προϊόντος  
3. TASK: Δημιουργία εργασίας
4. QUOTE: Δημιουργία προσφοράς

Για CUSTOMER, εξάγει:
- name: όνομα εταιρείας
- contact_person: υπεύθυνος επικοινωνίας
- email: διεύθυνση email
- phone: τηλέφωνο
- mobile: κινητό
- address: διεύθυνση
- city: πόλη
- tax_number: ΑΦΜ
- industry: κλάδος

Για PRODUCT, εξάγει:
- name_el: όνομα στα ελληνικά
- name_en: όνομα στα αγγλικά
- category: κατηγορία
- code: κωδικός προϊόντος
- unit_price: τιμή
- description_el: περιγραφή ελληνικά

Για TASK, εξάγει:
- title: τίτλος
- description: περιγραφή
- priority: προτεραιότητα (low, medium, high, urgent)
- due_date: ημερομηνία παράδοσης
- category: κατηγορία (follow_up, service_reminder, general)
"""
            else:
                system_prompt = """
You are a smart assistant for the Filterdyn application that manages customers, products and tasks for water treatment companies.

Analyze voice commands and extract structured data. Respond ONLY with valid JSON.

Command types:
1. CUSTOMER: Create customer
2. PRODUCT: Create product
3. TASK: Create task
4. QUOTE: Create quote

For CUSTOMER, extract:
- name: company name
- contact_person: contact person
- email: email address
- phone: phone number
- mobile: mobile number
- address: address
- city: city
- tax_number: tax number
- industry: industry

For PRODUCT, extract:
- name_en: name in English
- name_el: name in Greek
- category: category
- code: product code
- unit_price: price
- description_en: description in English

For TASK, extract:
- title: title
- description: description
- priority: priority (low, medium, high, urgent)
- due_date: due date
- category: category (follow_up, service_reminder, general)
"""

            prompt = f"""
{system_prompt}

Ανάλυσε αυτή τη φωνητική εντολή: "{text}"

Απάντησε με JSON στη μορφή:
{{
    "type": "CUSTOMER|PRODUCT|TASK|QUOTE",
    "data": {{...extracted fields...}},
    "confidence": 0.8,
    "language": "{language}"
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            logging.error(f"Gemini processing error: {str(e)}")
            return {"error": str(e), "confidence": 0.0}

    def create_entity_from_voice(self, voice_data, tenant_id):
        """Create database entity from voice command data"""
        try:
            entity_type = voice_data.get('type')
            data = voice_data.get('data', {})
            
            if entity_type == 'CUSTOMER':
                return self._create_customer(data, tenant_id)
            elif entity_type == 'PRODUCT':
                return self._create_product(data, tenant_id)
            elif entity_type == 'TASK':
                return self._create_task(data, tenant_id)
            else:
                return {"error": "Unsupported entity type"}
                
        except Exception as e:
            logging.error(f"Entity creation error: {str(e)}")
            return {"error": str(e)}

    def _create_customer(self, data, tenant_id):
        """Create customer from voice data"""
        customer = Customer(
            tenant_id=tenant_id,
            name=data.get('name', ''),
            contact_person=data.get('contact_person'),
            email=data.get('email'),
            phone=data.get('phone'),
            mobile=data.get('mobile'),
            address=data.get('address'),
            city=data.get('city'),
            tax_number=data.get('tax_number'),
            industry=data.get('industry')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return {
            "success": True,
            "entity": "customer",
            "id": customer.id,
            "name": customer.name
        }

    def _create_product(self, data, tenant_id):
        """Create product from voice data"""
        # Get or create default category
        category = ProductCategory.query.filter_by(
            tenant_id=tenant_id,
            name_el="Γενικά"
        ).first()
        
        if not category:
            category = ProductCategory(
                tenant_id=tenant_id,
                name_el="Γενικά",
                name_en="General"
            )
            db.session.add(category)
            db.session.flush()

        product = Product(
            tenant_id=tenant_id,
            category_id=category.id,
            code=data.get('code', f'PROD-{datetime.now().strftime("%Y%m%d%H%M%S")}'),
            name_el=data.get('name_el', data.get('name', '')),
            name_en=data.get('name_en', data.get('name', '')),
            description_el=data.get('description_el'),
            description_en=data.get('description_en'),
            unit_price=data.get('unit_price', 0),
            unit='piece'
        )
        
        db.session.add(product)
        db.session.commit()
        
        return {
            "success": True,
            "entity": "product",
            "id": product.id,
            "name": product.name_el or product.name_en
        }

    def _create_task(self, data, tenant_id):
        """Create task from voice data"""
        # Get a default assignee (current user or first admin)
        assignee = current_user
        if not assignee:
            assignee = User.query.filter_by(
                tenant_id=tenant_id,
                role='admin'
            ).first()
        
        if not assignee:
            return {"error": "No available user to assign task"}

        task = Task(
            tenant_id=tenant_id,
            title=data.get('title', ''),
            description=data.get('description'),
            priority=data.get('priority', 'medium'),
            category=data.get('category', 'general'),
            assigned_to=assignee.id,
            created_by=current_user.id if current_user else assignee.id,
            status='pending'
        )
        
        # Parse due date if provided
        due_date_str = data.get('due_date')
        if due_date_str:
            try:
                # Simple date parsing - could be enhanced
                task.due_date = datetime.now(timezone.utc) + timedelta(days=7)
            except:
                pass
        
        db.session.add(task)
        db.session.commit()
        
        return {
            "success": True,
            "entity": "task",
            "id": task.id,
            "title": task.title
        }

# Initialize processor
voice_processor = GeminiVoiceProcessor()

@ai_bp.route('/')
@login_required
def assistant_home():
    """AI Assistant main interface"""
    return render_template('ai_assistant/assistant.html')

@ai_bp.route('/process_voice', methods=['POST'])
@login_required
def process_voice():
    """Process voice command via Gemini AI"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'el')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Process voice command
        result = voice_processor.process_voice_command(text, language)
        
        if 'error' in result:
            return jsonify(result), 500
            
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Voice processing error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/create_entity', methods=['POST'])
@login_required
def create_entity():
    """Create database entity from processed voice data"""
    try:
        data = request.get_json()
        
        if not data or 'type' not in data:
            return jsonify({"error": "Invalid data provided"}), 400
        
        # Create entity
        result = voice_processor.create_entity_from_voice(data, current_user.tenant_id)
        
        if 'error' in result:
            return jsonify(result), 500
            
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Entity creation error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/get_suggestions', methods=['POST'])
@login_required  
def get_suggestions():
    """Get AI suggestions for completing data entry"""
    try:
        data = request.get_json()
        entity_type = data.get('type')
        partial_data = data.get('data', {})
        
        # Generate suggestions based on existing data
        suggestions = {}
        
        if entity_type == 'CUSTOMER':
            # Suggest similar customers or common fields
            existing_customers = Customer.query.filter_by(
                tenant_id=current_user.tenant_id
            ).limit(5).all()
            
            suggestions['similar_customers'] = [
                {"name": c.name, "industry": c.industry} 
                for c in existing_customers
            ]
            
        elif entity_type == 'PRODUCT':
            # Suggest product categories
            categories = ProductCategory.query.filter_by(
                tenant_id=current_user.tenant_id
            ).all()
            
            suggestions['categories'] = [
                {"id": c.id, "name": c.name_el, "name_en": c.name_en}
                for c in categories
            ]
        
        return jsonify({"suggestions": suggestions})
        
    except Exception as e:
        logging.error(f"Suggestions error: {str(e)}")
        return jsonify({"error": str(e)}), 500