
#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Tenant, Customer, Product, ProductCategory, Quote, Order, Task
from forms import (
    LoginForm, UserForm, CustomerForm, ProductCategoryForm, 
    ProductForm, QuoteForm, OrderForm, TaskForm
)

def test_forms_audit():
    """Comprehensive audit of all forms"""
    app = create_app()
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_forms': 0,
        'working_forms': 0,
        'broken_forms': 0,
        'form_details': [],
        'critical_issues': []
    }
    
    with app.app_context():
        # Create test tenant and user
        try:
            db.create_all()
            
            # Create test tenant
            test_tenant = Tenant(
                name="Test Company",
                subdomain="test",
                is_active=True
            )
            db.session.add(test_tenant)
            db.session.commit()
            
            # Create test user
            test_user = User(
                tenant_id=test_tenant.id,
                username="testuser",
                email="test@example.com",
                password_hash="dummy_hash",
                role="admin",
                first_name="Test",
                last_name="User"
            )
            db.session.add(test_user)
            db.session.commit()
            
            # Create test customer
            test_customer = Customer(
                tenant_id=test_tenant.id,
                name="Test Customer",
                contact_person="John Doe",
                email="customer@example.com",
                phone="1234567890"
            )
            db.session.add(test_customer)
            db.session.commit()
            
            # Create test product category
            test_category = ProductCategory(
                tenant_id=test_tenant.id,
                name_en="Test Category",
                name_el="Κατηγορία Δοκιμής"
            )
            db.session.add(test_category)
            db.session.commit()
            
        except Exception as e:
            results['critical_issues'].append(f"Database setup failed: {str(e)}")
            return results
        
        # Test 1: LoginForm
        results['total_forms'] += 1
        try:
            form = LoginForm()
            form.username.data = "testuser"
            form.password.data = "testpass"
            
            # Check required fields
            has_username = hasattr(form, 'username')
            has_password = hasattr(form, 'password')
            has_remember_me = hasattr(form, 'remember_me')
            
            login_working = has_username and has_password and has_remember_me
            
            if login_working:
                results['working_forms'] += 1
                results['form_details'].append({
                    'form': 'LoginForm',
                    'status': 'WORKING',
                    'issues': []
                })
            else:
                results['broken_forms'] += 1
                issues = []
                if not has_username: issues.append("Missing username field")
                if not has_password: issues.append("Missing password field")
                if not has_remember_me: issues.append("Missing remember_me field")
                
                results['form_details'].append({
                    'form': 'LoginForm',
                    'status': 'BROKEN',
                    'issues': issues
                })
                
        except Exception as e:
            results['broken_forms'] += 1
            results['form_details'].append({
                'form': 'LoginForm',
                'status': 'ERROR',
                'issues': [f"Exception: {str(e)}"]
            })
        
        # Test 2: UserForm
        results['total_forms'] += 1
        try:
            form = UserForm()
            form.username.data = "newuser"
            form.email.data = "new@example.com"
            form.role.data = "user"
            form.first_name.data = "New"
            form.last_name.data = "User"
            
            required_fields = ['username', 'email', 'role', 'first_name', 'last_name', 'phone', 'is_active']
            missing_fields = []
            
            for field in required_fields:
                if not hasattr(form, field):
                    missing_fields.append(field)
            
            if not missing_fields:
                results['working_forms'] += 1
                results['form_details'].append({
                    'form': 'UserForm',
                    'status': 'WORKING',
                    'issues': []
                })
            else:
                results['broken_forms'] += 1
                results['form_details'].append({
                    'form': 'UserForm',
                    'status': 'BROKEN',
                    'issues': [f"Missing fields: {missing_fields}"]
                })
                
        except Exception as e:
            results['broken_forms'] += 1
            results['form_details'].append({
                'form': 'UserForm',
                'status': 'ERROR',
                'issues': [f"Exception: {str(e)}"]
            })
        
        # Test 3: CustomerForm
        results['total_forms'] += 1
        try:
            form = CustomerForm()
            form.name.data = "Test Company"
            form.contact_person.data = "Jane Doe"
            form.email.data = "jane@company.com"
            form.phone.data = "1234567890"
            
            required_fields = ['name', 'contact_person', 'email', 'phone', 'mobile', 'address', 
                             'city', 'postal_code', 'country', 'tax_number', 'industry', 'notes']
            missing_fields = []
            
            for field in required_fields:
                if not hasattr(form, field):
                    missing_fields.append(field)
            
            if not missing_fields:
                results['working_forms'] += 1
                results['form_details'].append({
                    'form': 'CustomerForm',
                    'status': 'WORKING',
                    'issues': []
                })
            else:
                results['broken_forms'] += 1
                results['form_details'].append({
                    'form': 'CustomerForm',
                    'status': 'BROKEN',
                    'issues': [f"Missing fields: {missing_fields}"]
                })
                
        except Exception as e:
            results['broken_forms'] += 1
            results['form_details'].append({
                'form': 'CustomerForm',
                'status': 'ERROR',
                'issues': [f"Exception: {str(e)}"]
            })
        
        # Test 4: ProductCategoryForm
        results['total_forms'] += 1
        try:
            form = ProductCategoryForm()
            form.name_en.data = "New Category"
            form.name_el.data = "Νέα Κατηγορία"
            
            required_fields = ['name_en', 'name_el', 'description_en', 'description_el']
            missing_fields = []
            
            for field in required_fields:
                if not hasattr(form, field):
                    missing_fields.append(field)
            
            if not missing_fields:
                results['working_forms'] += 1
                results['form_details'].append({
                    'form': 'ProductCategoryForm',
                    'status': 'WORKING',
                    'issues': []
                })
            else:
                results['broken_forms'] += 1
                results['form_details'].append({
                    'form': 'ProductCategoryForm',
                    'status': 'BROKEN',
                    'issues': [f"Missing fields: {missing_fields}"]
                })
                
        except Exception as e:
            results['broken_forms'] += 1
            results['form_details'].append({
                'form': 'ProductCategoryForm',
                'status': 'ERROR',
                'issues': [f"Exception: {str(e)}"]
            })
        
        # Test 5: ProductForm
        results['total_forms'] += 1
        try:
            form = ProductForm()
            form.category_id.choices = [(test_category.id, test_category.name_en)]
            form.category_id.data = test_category.id
            form.code.data = "TEST001"
            form.name_en.data = "Test Product"
            form.name_el.data = "Προϊόν Δοκιμής"
            form.unit_price.data = Decimal('100.00')
            
            required_fields = ['category_id', 'code', 'name_en', 'name_el', 'description_en', 
                             'description_el', 'unit_price', 'cost_price', 'unit', 'specifications']
            missing_fields = []
            
            for field in required_fields:
                if not hasattr(form, field):
                    missing_fields.append(field)
            
            if not missing_fields:
                results['working_forms'] += 1
                results['form_details'].append({
                    'form': 'ProductForm',
                    'status': 'WORKING',
                    'issues': []
                })
            else:
                results['broken_forms'] += 1
                results['form_details'].append({
                    'form': 'ProductForm',
                    'status': 'BROKEN',
                    'issues': [f"Missing fields: {missing_fields}"]
                })
                
        except Exception as e:
            results['broken_forms'] += 1
            results['form_details'].append({
                'form': 'ProductForm',
                'status': 'ERROR',
                'issues': [f"Exception: {str(e)}"]
            })
        
        # Test 6: QuoteForm
        results['total_forms'] += 1
        try:
            form = QuoteForm()
            form.customer_id.choices = [(test_customer.id, test_customer.name)]
            form.customer_id.data = test_customer.id
            form.quote_type.data = "new_columns"
            form.title.data = "Test Quote"
            form.validity_days.data = 30
            form.delivery_days.data = 15
            form.payment_terms.data = "30 days"
            form.tax_rate.data = Decimal('24.00')
            
            required_fields = ['customer_id', 'quote_type', 'title', 'description', 'validity_days',
                             'delivery_days', 'payment_terms', 'tax_rate']
            missing_fields = []
            
            for field in required_fields:
                if not hasattr(form, field):
                    missing_fields.append(field)
            
            if not missing_fields:
                results['working_forms'] += 1
                results['form_details'].append({
                    'form': 'QuoteForm',
                    'status': 'WORKING',
                    'issues': []
                })
            else:
                results['broken_forms'] += 1
                results['form_details'].append({
                    'form': 'QuoteForm',
                    'status': 'BROKEN',
                    'issues': [f"Missing fields: {missing_fields}"]
                })
                
        except Exception as e:
            results['broken_forms'] += 1
            results['form_details'].append({
                'form': 'QuoteForm',
                'status': 'ERROR',
                'issues': [f"Exception: {str(e)}"]
            })
        
        # Test 7: OrderForm
        results['total_forms'] += 1
        try:
            form = OrderForm()
            form.customer_id.choices = [(test_customer.id, test_customer.name)]
            form.quote_id.choices = [(0, 'None')]
            form.customer_id.data = test_customer.id
            form.order_type.data = "phone_order"
            form.title.data = "Test Order"
            
            required_fields = ['customer_id', 'quote_id', 'order_type', 'title', 'description',
                             'delivery_address', 'delivery_date', 'delivery_notes']
            missing_fields = []
            
            for field in required_fields:
                if not hasattr(form, field):
                    missing_fields.append(field)
            
            if not missing_fields:
                results['working_forms'] += 1
                results['form_details'].append({
                    'form': 'OrderForm',
                    'status': 'WORKING',
                    'issues': []
                })
            else:
                results['broken_forms'] += 1
                results['form_details'].append({
                    'form': 'OrderForm',
                    'status': 'BROKEN',
                    'issues': [f"Missing fields: {missing_fields}"]
                })
                
        except Exception as e:
            results['broken_forms'] += 1
            results['form_details'].append({
                'form': 'OrderForm',
                'status': 'ERROR',
                'issues': [f"Exception: {str(e)}"]
            })
        
        # Test 8: TaskForm (the problematic one)
        results['total_forms'] += 1
        try:
            form = TaskForm()
            
            # Set up choices - this is likely where the issue is
            form.assigned_to.choices = [(test_user.id, test_user.full_name)]
            form.customer_id.choices = [(0, 'Select Customer'), (test_customer.id, test_customer.name)]
            
            # Set form data
            form.title.data = "Test Task"
            form.description.data = "Test task description"
            form.status.data = "pending"
            form.priority.data = "medium"
            form.category.data = "general"
            form.assigned_to.data = test_user.id
            form.customer_id.data = test_customer.id
            form.due_date.data = datetime.now()
            form.notes.data = "Test notes"
            
            required_fields = ['title', 'description', 'status', 'priority', 'category',
                             'assigned_to', 'customer_id', 'due_date', 'notes']
            missing_fields = []
            issues = []
            
            for field in required_fields:
                if not hasattr(form, field):
                    missing_fields.append(field)
            
            # Check if form validates
            try:
                is_valid = form.validate()
                if not is_valid:
                    for field, errors in form.errors.items():
                        issues.append(f"Field '{field}': {', '.join(errors)}")
            except Exception as validation_error:
                issues.append(f"Validation error: {str(validation_error)}")
            
            all_issues = []
            if missing_fields:
                all_issues.append(f"Missing fields: {missing_fields}")
            if issues:
                all_issues.extend(issues)
            
            if not missing_fields and not issues:
                results['working_forms'] += 1
                results['form_details'].append({
                    'form': 'TaskForm',
                    'status': 'WORKING',
                    'issues': []
                })
            else:
                results['broken_forms'] += 1
                results['form_details'].append({
                    'form': 'TaskForm',
                    'status': 'BROKEN',
                    'issues': all_issues
                })
                
        except Exception as e:
            results['broken_forms'] += 1
            results['form_details'].append({
                'form': 'TaskForm',
                'status': 'ERROR',
                'issues': [f"Exception: {str(e)}"]
            })
        
        # Clean up test data
        try:
            db.session.rollback()
            db.session.close()
        except:
            pass
    
    return results

if __name__ == "__main__":
    results = test_forms_audit()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"FORMS AUDIT RESULTS")
    print(f"{'='*60}")
    print(f"Total Forms Tested: {results['total_forms']}")
    print(f"Working Forms: {results['working_forms']}")
    print(f"Broken Forms: {results['broken_forms']}")
    print(f"Success Rate: {(results['working_forms']/results['total_forms']*100):.1f}%")
    
    print(f"\n{'='*60}")
    print(f"DETAILED RESULTS")
    print(f"{'='*60}")
    
    for form_result in results['form_details']:
        status_icon = "✅" if form_result['status'] == 'WORKING' else "❌"
        print(f"{status_icon} {form_result['form']}: {form_result['status']}")
        
        if form_result['issues']:
            for issue in form_result['issues']:
                print(f"   - {issue}")
    
    if results['critical_issues']:
        print(f"\n{'='*60}")
        print(f"CRITICAL ISSUES")
        print(f"{'='*60}")
        for issue in results['critical_issues']:
            print(f"❌ {issue}")
    
    # Save detailed results
    with open('forms_audit_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: forms_audit_results.json")
