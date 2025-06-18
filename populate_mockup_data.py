
#!/usr/bin/env python3
"""
Populate the database with comprehensive mockup data for testing
"""
import os
import sys
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import random

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import (
    Tenant, User, Customer, ProductCategory, Product, 
    Quote, QuoteItem, Order, OrderItem, Task
)
from werkzeug.security import generate_password_hash

def create_mockup_data():
    app = create_app()
    
    with app.app_context():
        print("🚀 Starting mockup data creation...")
        
        # Get the default tenant (should already exist)
        tenant = Tenant.query.filter_by(subdomain='filterdyn').first()
        if not tenant:
            print("❌ Default tenant not found. Run the app first to create it.")
            return
        
        print(f"✅ Using tenant: {tenant.name}")
        
        # Create additional users
        users_data = [
            {
                'username': 'john_manager',
                'email': 'john@filterdyn.com',
                'password': 'manager123',
                'role': 'manager',
                'first_name': 'John',
                'last_name': 'Smith',
                'phone': '+30210123456'
            },
            {
                'username': 'maria_sales',
                'email': 'maria@filterdyn.com',
                'password': 'sales123',
                'role': 'user',
                'first_name': 'Maria',
                'last_name': 'Konstantinou',
                'phone': '+30210234567'
            },
            {
                'username': 'dimitris_tech',
                'email': 'dimitris@filterdyn.com',
                'password': 'tech123',
                'role': 'user',
                'first_name': 'Dimitris',
                'last_name': 'Papadopoulos',
                'phone': '+30210345678'
            }
        ]
        
        created_users = []
        for user_data in users_data:
            existing_user = User.query.filter_by(
                tenant_id=tenant.id, 
                username=user_data['username']
            ).first()
            
            if not existing_user:
                user = User(
                    tenant_id=tenant.id,
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    role=user_data['role'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone=user_data['phone'],
                    is_active=True
                )
                db.session.add(user)
                created_users.append(user)
                print(f"👤 Created user: {user_data['username']} ({user_data['role']})")
        
        db.session.commit()
        
        # Get all users for assignments
        all_users = User.query.filter_by(tenant_id=tenant.id).all()
        
        # Create customers
        customers_data = [
            {
                'name': 'COCA-COLA HBC ΕΛΛΑΣ ΑΕ',
                'contact_person': 'Γιάννης Μαρινόπουλος',
                'email': 'procurement@coca-cola.gr',
                'phone': '+302108001000',
                'mobile': '+306971234567',
                'address': 'Λ. Κηφισίας 280, Χαλάνδρι',
                'city': 'Αθήνα',
                'postal_code': '15232',
                'tax_number': '123456789',
                'industry': 'Beverages',
                'notes': 'Major client with regular filtration needs'
            },
            {
                'name': 'ΒΙΟΧΑΛΚΟ ΑΕ',
                'contact_person': 'Ελένη Κωνσταντίνου',
                'email': 'purchasing@viohalco.com',
                'phone': '+302106868000',
                'mobile': '+306987654321',
                'address': 'Λ. Μεσογείων 2-8',
                'city': 'Αθήνα',
                'postal_code': '11527',
                'tax_number': '987654321',
                'industry': 'Mining & Metallurgy',
                'notes': 'Industrial client requiring high-capacity systems'
            },
            {
                'name': 'ΕΛΛΗΝΙΚΑ ΠΕΤΡΕΛΑΙΑ ΑΕ',
                'contact_person': 'Νίκος Παπαδάκης',
                'email': 'supply@hellenic-petroleum.gr',
                'phone': '+302106302000',
                'mobile': '+306912345678',
                'address': 'Χιμάρρας 8Α, Μαρούσι',
                'city': 'Αθήνα',
                'postal_code': '15125',
                'tax_number': '123789456',
                'industry': 'Oil & Gas',
                'notes': 'Petrochemical filtration requirements'
            },
            {
                'name': 'ΤΙΤΑΝ CEMENT INTERNATIONAL ΑΕ',
                'contact_person': 'Σοφία Αλεξάνδρου',
                'email': 'info@titan.gr',
                'phone': '+302106502200',
                'mobile': '+306945678912',
                'address': 'Χ.Κ. 22.5 Λ. Λαυρίου, Αγία Παρασκευή',
                'city': 'Αθήνα',
                'postal_code': '15343',
                'tax_number': '456123789',
                'industry': 'Construction Materials',
                'notes': 'Cement production dust collection systems'
            },
            {
                'name': 'ΘΕΡΜΟΚΗΠΙΑ ΚΡΗΤΗΣ ΑΕ',
                'contact_person': 'Μανόλης Κρητικός',
                'email': 'orders@greenhouse-crete.gr',
                'phone': '+302810234567',
                'mobile': '+306978123456',
                'address': 'Αγροκήπιο Ηρακλείου',
                'city': 'Ηράκλειο',
                'postal_code': '71601',
                'tax_number': '789456123',
                'industry': 'Agriculture',
                'notes': 'Greenhouse water filtration systems'
            }
        ]
        
        created_customers = []
        for customer_data in customers_data:
            customer = Customer(
                tenant_id=tenant.id,
                **customer_data
            )
            db.session.add(customer)
            created_customers.append(customer)
            print(f"🏢 Created customer: {customer_data['name']}")
        
        db.session.commit()
        
        # Create product categories
        categories_data = [
            {
                'name_en': 'Filter Columns',
                'name_el': 'Κολώνες Φίλτρων',
                'description_en': 'Industrial filtration columns and towers',
                'description_el': 'Βιομηχανικές κολώνες και πύργοι φιλτραρίσματος'
            },
            {
                'name_en': 'Filtration Equipment',
                'name_el': 'Εξοπλισμός Φιλτραρίσματος',
                'description_en': 'Complete filtration systems and equipment',
                'description_el': 'Πλήρη συστήματα και εξοπλισμός φιλτραρίσματος'
            },
            {
                'name_en': 'Filter Media',
                'name_el': 'Υλικά Φίλτρων',
                'description_en': 'Filter cartridges, media and consumables',
                'description_el': 'Φυσίγγια φίλτρων, υλικά και αναλώσιμα'
            },
            {
                'name_en': 'Pumps & Valves',
                'name_el': 'Αντλίες & Βάνες',
                'description_en': 'Pumping systems and control valves',
                'description_el': 'Συστήματα άντλησης και βάνες ελέγχου'
            }
        ]
        
        created_categories = []
        for category_data in categories_data:
            category = ProductCategory(
                tenant_id=tenant.id,
                **category_data
            )
            db.session.add(category)
            created_categories.append(category)
            print(f"📂 Created category: {category_data['name_en']}")
        
        db.session.commit()
        
        # Create products
        products_data = [
            # Filter Columns
            {
                'category_idx': 0,
                'code': 'FC-2000-SS',
                'name_en': 'Stainless Steel Filter Column 2000L',
                'name_el': 'Κολώνα Φίλτρου Ανοξείδωτου Χάλυβα 2000L',
                'description_en': 'High-capacity stainless steel filtration column for industrial applications',
                'description_el': 'Κολώνα φιλτραρίσματος υψηλής χωρητικότητας από ανοξείδωτο χάλυβα',
                'unit_price': Decimal('12500.00'),
                'cost_price': Decimal('8500.00'),
                'unit': 'piece'
            },
            {
                'category_idx': 0,
                'code': 'FC-1000-CS',
                'name_en': 'Carbon Steel Filter Column 1000L',
                'name_el': 'Κολώνα Φίλτρου Χαλυβδίνη 1000L',
                'description_en': 'Medium-capacity carbon steel filtration column',
                'description_el': 'Κολώνα φιλτραρίσματος μεσαίας χωρητικότητας από χάλυβα',
                'unit_price': Decimal('8750.00'),
                'cost_price': Decimal('5950.00'),
                'unit': 'piece'
            },
            # Filtration Equipment
            {
                'category_idx': 1,
                'code': 'FE-AUTO-500',
                'name_en': 'Automatic Backwash Filter System 500 m³/h',
                'name_el': 'Αυτόματο Σύστημα Φίλτρου με Αντίστροφη Πλύση 500 m³/h',
                'description_en': 'Fully automated filtration system with backwash capability',
                'description_el': 'Πλήρως αυτοματοποιημένο σύστημα φιλτραρίσματος με δυνατότητα αντίστροφης πλύσης',
                'unit_price': Decimal('25000.00'),
                'cost_price': Decimal('17500.00'),
                'unit': 'set'
            },
            {
                'category_idx': 1,
                'code': 'FE-SAND-250',
                'name_en': 'Sand Filter System 250 m³/h',
                'name_el': 'Σύστημα Φίλτρου Άμμου 250 m³/h',
                'description_en': 'High-efficiency sand filtration system',
                'description_el': 'Σύστημα φιλτραρίσματος άμμου υψηλής απόδοσης',
                'unit_price': Decimal('15500.00'),
                'cost_price': Decimal('10850.00'),
                'unit': 'set'
            },
            # Filter Media
            {
                'category_idx': 2,
                'code': 'FM-CART-10',
                'name_en': '10" Pleated Filter Cartridge (50 micron)',
                'name_el': 'Φυσίγγιο Φίλτρου 10" Πλισέ (50 micron)',
                'description_en': 'High-quality pleated filter cartridge for fine filtration',
                'description_el': 'Υψηλής ποιότητας φυσίγγιο φίλτρου πλισέ για λεπτό φιλτράρισμα',
                'unit_price': Decimal('45.50'),
                'cost_price': Decimal('28.30'),
                'unit': 'piece'
            },
            {
                'category_idx': 2,
                'code': 'FM-ACT-CARBON',
                'name_en': 'Activated Carbon Media (25kg bag)',
                'name_el': 'Ενεργός Άνθρακας (σάκος 25kg)',
                'description_en': 'Premium activated carbon for water treatment',
                'description_el': 'Ενεργός άνθρακας premium για επεξεργασία νερού',
                'unit_price': Decimal('125.00'),
                'cost_price': Decimal('87.50'),
                'unit': 'bag'
            },
            # Pumps & Valves
            {
                'category_idx': 3,
                'code': 'PV-PUMP-5HP',
                'name_en': 'Centrifugal Pump 5HP 3-Phase',
                'name_el': 'Φυγόκεντρη Αντλία 5HP Τριφασική',
                'description_en': 'Industrial centrifugal pump for filtration systems',
                'description_el': 'Βιομηχανική φυγόκεντρη αντλία για συστήματα φιλτραρίσματος',
                'unit_price': Decimal('2750.00'),
                'cost_price': Decimal('1925.00'),
                'unit': 'piece'
            },
            {
                'category_idx': 3,
                'code': 'PV-VALVE-DN50',
                'name_en': 'Motorized Ball Valve DN50',
                'name_el': 'Μηχανοκίνητη Σφαιρική Βάνα DN50',
                'description_en': 'Automated ball valve with electric actuator',
                'description_el': 'Αυτοματοποιημένη σφαιρική βάνα με ηλεκτρικό ενεργοποιητή',
                'unit_price': Decimal('850.00'),
                'cost_price': Decimal('595.00'),
                'unit': 'piece'
            }
        ]
        
        created_products = []
        for product_data in products_data:
            category_idx = product_data.pop('category_idx')
            product = Product(
                tenant_id=tenant.id,
                category_id=created_categories[category_idx].id,
                **product_data
            )
            db.session.add(product)
            created_products.append(product)
            print(f"📦 Created product: {product_data['code']}")
        
        db.session.commit()
        
        # Create quotes with items
        quotes_data = [
            {
                'customer_idx': 0,  # COCA-COLA
                'user_idx': 1,  # maria_sales
                'quote_type': 'filtration_equipment',
                'title': 'Bottling Line Water Treatment System',
                'description': 'Complete water filtration system for new bottling line in Thessaloniki plant',
                'status': 'approved',
                'validity_days': 45,
                'delivery_days': 30,
                'items': [
                    {'product_idx': 2, 'quantity': 1, 'unit_price': 25000.00},  # Auto backwash system
                    {'product_idx': 4, 'quantity': 24, 'unit_price': 45.50},    # Filter cartridges
                    {'product_idx': 6, 'quantity': 1, 'unit_price': 2750.00}    # Pump
                ]
            },
            {
                'customer_idx': 1,  # ΒΙΟΧΑΛΚΟ
                'user_idx': 2,  # dimitris_tech
                'quote_type': 'new_columns',
                'title': 'Mining Process Water Filtration Columns',
                'description': 'Large capacity filtration columns for mining wastewater treatment',
                'status': 'sent',
                'validity_days': 60,
                'delivery_days': 45,
                'items': [
                    {'product_idx': 0, 'quantity': 3, 'unit_price': 12500.00},  # SS columns
                    {'product_idx': 1, 'quantity': 2, 'unit_price': 8750.00},   # CS columns
                    {'product_idx': 5, 'quantity': 10, 'unit_price': 125.00}    # Activated carbon
                ]
            },
            {
                'customer_idx': 2,  # ΕΛΛΗΝΙΚΑ ΠΕΤΡΕΛΑΙΑ
                'user_idx': 1,  # maria_sales
                'quote_type': 'emergency_repair',
                'title': 'Emergency Filter Column Replacement',
                'description': 'Urgent replacement of damaged filtration column at Aspropyrgos refinery',
                'status': 'approved',
                'validity_days': 15,
                'delivery_days': 7,
                'items': [
                    {'product_idx': 0, 'quantity': 1, 'unit_price': 12500.00},  # SS column
                    {'product_idx': 7, 'quantity': 4, 'unit_price': 850.00}     # Valves
                ]
            }
        ]
        
        created_quotes = []
        for i, quote_data in enumerate(quotes_data):
            customer_idx = quote_data.pop('customer_idx')
            user_idx = quote_data.pop('user_idx')
            items_data = quote_data.pop('items')
            
            # Generate quote number
            quote_number = f"Q2024{1000 + i + 1}"
            
            quote = Quote(
                tenant_id=tenant.id,
                customer_id=created_customers[customer_idx].id,
                created_by=all_users[user_idx].id,
                quote_number=quote_number,
                **quote_data
            )
            
            if quote.status == 'approved':
                quote.approved_by = all_users[0].id  # superadmin
                quote.approved_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 5))
            
            db.session.add(quote)
            db.session.flush()  # Get the quote ID
            
            # Add quote items
            subtotal = Decimal('0')
            for item_data in items_data:
                product_idx = item_data['product_idx']
                quantity = Decimal(str(item_data['quantity']))
                unit_price = Decimal(str(item_data['unit_price']))
                line_total = quantity * unit_price
                
                quote_item = QuoteItem(
                    quote_id=quote.id,
                    product_id=created_products[product_idx].id,
                    description=created_products[product_idx].name_en,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total
                )
                db.session.add(quote_item)
                subtotal += line_total
            
            # Update quote totals
            quote.subtotal = subtotal
            quote.tax_amount = subtotal * (quote.tax_rate / 100)
            quote.total_amount = quote.subtotal + quote.tax_amount
            
            created_quotes.append(quote)
            print(f"💰 Created quote: {quote_number} for {created_customers[customer_idx].name}")
        
        db.session.commit()
        
        # Create orders from some quotes
        order_from_quote = created_quotes[0]  # COCA-COLA approved quote
        
        order = Order(
            tenant_id=tenant.id,
            customer_id=order_from_quote.customer_id,
            quote_id=order_from_quote.id,
            created_by=order_from_quote.created_by,
            order_number=f"ORD-{datetime.now().strftime('%Y%m%d')}-0001",
            order_type='quote_conversion',
            title=order_from_quote.title,
            description=order_from_quote.description,
            delivery_address='COCA-COLA Plant, Thessaloniki Industrial Area',
            delivery_date=datetime.now(timezone.utc) + timedelta(days=30),
            status='confirmed',
            subtotal=order_from_quote.subtotal,
            tax_rate=order_from_quote.tax_rate,
            tax_amount=order_from_quote.tax_amount,
            total_amount=order_from_quote.total_amount
        )
        
        db.session.add(order)
        db.session.flush()
        
        # Add order items from quote items
        for quote_item in order_from_quote.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=quote_item.product_id,
                description=quote_item.description,
                quantity=quote_item.quantity,
                unit_price=quote_item.unit_price,
                line_total=quote_item.line_total
            )
            db.session.add(order_item)
        
        print(f"📋 Created order: {order.order_number}")
        
        # Create tasks
        tasks_data = [
            {
                'title': 'Follow up on COCA-COLA delivery schedule',
                'description': 'Contact customer to confirm delivery timeline and site preparation requirements',
                'priority': 'high',
                'category': 'follow_up',
                'customer_idx': 0,
                'order_id': order.id,
                'assigned_to_idx': 1,  # maria_sales
                'due_date': datetime.now(timezone.utc) + timedelta(days=3)
            },
            {
                'title': 'Prepare technical documentation for ΒΙΟΧΑΛΚΟ quote',
                'description': 'Create detailed technical specifications and installation guidelines',
                'priority': 'medium',
                'category': 'general',
                'customer_idx': 1,
                'quote_id': created_quotes[1].id,
                'assigned_to_idx': 2,  # dimitris_tech
                'due_date': datetime.now(timezone.utc) + timedelta(days=7)
            },
            {
                'title': 'Schedule installation team for ΕΛΛΗΝΙΚΑ ΠΕΤΡΕΛΑΙΑ',
                'description': 'Coordinate with technical team for emergency installation at refinery',
                'priority': 'urgent',
                'category': 'service_reminder',
                'customer_idx': 2,
                'quote_id': created_quotes[2].id,
                'assigned_to_idx': 0,  # superadmin
                'due_date': datetime.now(timezone.utc) + timedelta(days=1),
                'status': 'in_progress'
            },
            {
                'title': 'Monthly maintenance check - ΤΙΤΑΝ CEMENT',
                'description': 'Scheduled monthly maintenance and filter replacement check',
                'priority': 'medium',
                'category': 'service_reminder',
                'customer_idx': 3,
                'assigned_to_idx': 2,  # dimitris_tech
                'due_date': datetime.now(timezone.utc) + timedelta(days=14)
            },
            {
                'title': 'Quote preparation for greenhouse irrigation system',
                'description': 'Prepare comprehensive quote for water filtration system for greenhouse complex',
                'priority': 'low',
                'category': 'general',
                'customer_idx': 4,
                'assigned_to_idx': 1,  # maria_sales
                'due_date': datetime.now(timezone.utc) + timedelta(days=10)
            }
        ]
        
        for task_data in tasks_data:
            customer_idx = task_data.pop('customer_idx')
            assigned_to_idx = task_data.pop('assigned_to_idx')
            
            task = Task(
                tenant_id=tenant.id,
                created_by=all_users[0].id,  # superadmin created all tasks
                assigned_to=all_users[assigned_to_idx].id,
                customer_id=created_customers[customer_idx].id,
                **task_data
            )
            db.session.add(task)
            print(f"✅ Created task: {task_data['title']}")
        
        db.session.commit()
        
        print("\n🎉 Mockup data creation completed successfully!")
        print("\n📊 Summary:")
        print(f"   👤 Users: {len(created_users)} created (+ existing superadmin)")
        print(f"   🏢 Customers: {len(created_customers)} created")
        print(f"   📂 Categories: {len(created_categories)} created")
        print(f"   📦 Products: {len(created_products)} created")
        print(f"   💰 Quotes: {len(created_quotes)} created")
        print(f"   📋 Orders: 1 created")
        print(f"   ✅ Tasks: {len(tasks_data)} created")
        
        print("\n🔐 Test Users:")
        print("   superadmin / admin123 (superadmin)")
        print("   john_manager / manager123 (manager)")
        print("   maria_sales / sales123 (user)")
        print("   dimitris_tech / tech123 (user)")
        
        print("\n🚀 You can now test the system with realistic data!")

if __name__ == "__main__":
    create_mockup_data()
