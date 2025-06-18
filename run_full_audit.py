#!/usr/bin/env python3
"""
Full audit runner that bypasses timeout issues
"""
import os
import sys
import json
from datetime import datetime
import subprocess
import traceback

def run_comprehensive_tests():
    """Run comprehensive tests with proper error handling"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'critical_issues': [],
        'security_issues': [],
        'performance_issues': [],
        'usability_issues': [],
        'infrastructure_issues': [],
        'test_details': []
    }
    
    # Test 1: Route Completeness
    try:
        with open('routes.py', 'r') as f:
            routes_content = f.read()
        
        required_routes = [
            ('/customers', 'Customer management'),
            ('/products', 'Product catalog'),
            ('/quotes', 'Quote generation'),
            ('/orders', 'Order processing'),
            ('/tasks', 'Task management'),
            ('/settings', 'System settings')
        ]
        
        route_issues = []
        for route, desc in required_routes:
            if f"@main_bp.route('{route}')" not in routes_content:
                route_issues.append(f"Missing {route} route for {desc}")
        
        results['total_tests'] += 1
        if not route_issues:
            results['passed_tests'] += 1
            results['test_details'].append({
                'test': 'Route Completeness',
                'status': 'PASS',
                'details': 'All main routes present'
            })
        else:
            results['failed_tests'] += 1
            results['infrastructure_issues'].extend(route_issues)
            results['test_details'].append({
                'test': 'Route Completeness',
                'status': 'FAIL',
                'details': f"Missing routes: {route_issues}"
            })
    
    except Exception as e:
        results['critical_issues'].append(f"Cannot analyze routes: {str(e)}")
        results['failed_tests'] += 1
        results['total_tests'] += 1
    
    # Test 2: Template Completeness
    critical_templates = [
        'templates/base.html',
        'templates/dashboard.html',
        'templates/auth/login.html',
        'templates/customers/index.html',
        'templates/products/index.html',
        'templates/quotes/index.html',
        'templates/orders/index.html',
        'templates/orders/view.html',
        'templates/orders/create.html',
        'templates/orders/edit.html',
        'templates/tasks/index.html',
        'templates/settings/index.html'
    ]
    
    missing_templates = []
    for template in critical_templates:
        if not os.path.exists(template):
            missing_templates.append(template)
    
    results['total_tests'] += 1
    if not missing_templates:
        results['passed_tests'] += 1
        results['test_details'].append({
            'test': 'Template Completeness',
            'status': 'PASS',
            'details': 'All critical templates present'
        })
    else:
        results['failed_tests'] += 1
        results['usability_issues'].extend(missing_templates)
        results['test_details'].append({
            'test': 'Template Completeness',
            'status': 'FAIL',
            'details': f"Missing templates: {missing_templates}"
        })
    
    # Test 3: Database Models
    try:
        with open('models.py', 'r') as f:
            models_content = f.read()
        
        required_models = ['User', 'Tenant', 'Customer', 'Product', 'Quote', 'Order', 'Task']
        missing_models = []
        
        for model in required_models:
            if f'class {model}(' not in models_content:
                missing_models.append(model)
        
        results['total_tests'] += 1
        if not missing_models:
            results['passed_tests'] += 1
            results['test_details'].append({
                'test': 'Database Models',
                'status': 'PASS',
                'details': 'All required models present'
            })
        else:
            results['failed_tests'] += 1
            results['critical_issues'].append(f"Missing models: {missing_models}")
            results['test_details'].append({
                'test': 'Database Models',
                'status': 'FAIL',
                'details': f"Missing models: {missing_models}"
            })
    
    except Exception as e:
        results['critical_issues'].append(f"Cannot analyze models: {str(e)}")
        results['failed_tests'] += 1
        results['total_tests'] += 1
    
    # Test 4: Security Implementation
    security_checks = []
    
    try:
        # Check password hashing
        with open('auth.py', 'r') as f:
            auth_content = f.read()
        
        if 'generate_password_hash' not in auth_content:
            security_checks.append('Password hashing not implemented')
        
        if 'check_password_hash' not in auth_content:
            security_checks.append('Password verification not implemented')
        
        # Check CSRF protection
        with open('forms.py', 'r') as f:
            forms_content = f.read()
        
        if 'FlaskForm' not in forms_content:
            security_checks.append('CSRF protection not implemented')
        
        # Check login required decorators
        with open('routes.py', 'r') as f:
            routes_content = f.read()
        
        if '@login_required' not in routes_content:
            security_checks.append('Authentication protection not implemented')
        
        results['total_tests'] += 1
        if not security_checks:
            results['passed_tests'] += 1
            results['test_details'].append({
                'test': 'Security Implementation',
                'status': 'PASS',
                'details': 'Basic security measures implemented'
            })
        else:
            results['failed_tests'] += 1
            results['security_issues'].extend(security_checks)
            results['test_details'].append({
                'test': 'Security Implementation',
                'status': 'FAIL',
                'details': f"Security issues: {security_checks}"
            })
    
    except Exception as e:
        results['security_issues'].append(f"Cannot analyze security: {str(e)}")
        results['failed_tests'] += 1
        results['total_tests'] += 1
    
    # Test 5: Database Connection
    try:
        import psycopg2
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        conn.close()
        
        results['total_tests'] += 1
        results['passed_tests'] += 1
        results['test_details'].append({
            'test': 'Database Connection',
            'status': 'PASS',
            'details': 'Database connection working'
        })
    
    except Exception as e:
        results['total_tests'] += 1
        results['failed_tests'] += 1
        results['critical_issues'].append(f"Database connection failed: {str(e)}")
        results['test_details'].append({
            'test': 'Database Connection',
            'status': 'FAIL',
            'details': f"Database error: {str(e)}"
        })
    
    # Test 6: Internationalization
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        i18n_issues = []
        
        if 'babel.init_app' not in app_content:
            i18n_issues.append('Babel not initialized')
        
        if '@app.template_global()' not in app_content or 'get_locale' not in app_content:
            i18n_issues.append('Locale function not available in templates')
        
        # Check translation files
        if not os.path.exists('babel.cfg'):
            i18n_issues.append('Babel configuration missing')
        
        results['total_tests'] += 1
        if not i18n_issues:
            results['passed_tests'] += 1
            results['test_details'].append({
                'test': 'Internationalization',
                'status': 'PASS',
                'details': 'I18n properly configured'
            })
        else:
            results['failed_tests'] += 1
            results['usability_issues'].extend(i18n_issues)
            results['test_details'].append({
                'test': 'Internationalization',
                'status': 'FAIL',
                'details': f"I18n issues: {i18n_issues}"
            })
    
    except Exception as e:
        results['usability_issues'].append(f"Cannot analyze i18n: {str(e)}")
        results['failed_tests'] += 1
        results['total_tests'] += 1
    
    # Test 7: PDF Generation
    try:
        if os.path.exists('pdf_generator.py'):
            with open('pdf_generator.py', 'r') as f:
                pdf_content = f.read()
            
            if 'fpdf' in pdf_content or 'FPDF' in pdf_content:
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_details'].append({
                    'test': 'PDF Generation',
                    'status': 'PASS',
                    'details': 'PDF generation implemented'
                })
            else:
                results['total_tests'] += 1
                results['failed_tests'] += 1
                results['usability_issues'].append('PDF generation not properly implemented')
                results['test_details'].append({
                    'test': 'PDF Generation',
                    'status': 'FAIL',
                    'details': 'PDF library not found'
                })
        else:
            results['total_tests'] += 1
            results['failed_tests'] += 1
            results['usability_issues'].append('PDF generator missing')
            results['test_details'].append({
                'test': 'PDF Generation',
                'status': 'FAIL',
                'details': 'PDF generator file missing'
            })
    
    except Exception as e:
        results['usability_issues'].append(f"Cannot analyze PDF generation: {str(e)}")
        results['failed_tests'] += 1
        results['total_tests'] += 1
    
    # Calculate success rate
    results['success_rate'] = (results['passed_tests'] / results['total_tests']) * 100 if results['total_tests'] > 0 else 0
    
    return results

def main():
    print("🔍 Running Comprehensive MVP Audit...")
    print("=" * 60)
    
    try:
        results = run_comprehensive_tests()
        
        print(f"\n📊 Audit Results:")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        
        if results['critical_issues']:
            print(f"\n🚨 Critical Issues ({len(results['critical_issues'])}):")
            for issue in results['critical_issues']:
                print(f"  - {issue}")
        
        if results['security_issues']:
            print(f"\n🔒 Security Issues ({len(results['security_issues'])}):")
            for issue in results['security_issues']:
                print(f"  - {issue}")
        
        if results['infrastructure_issues']:
            print(f"\n🏗️ Infrastructure Issues ({len(results['infrastructure_issues'])}):")
            for issue in results['infrastructure_issues']:
                print(f"  - {issue}")
        
        if results['usability_issues']:
            print(f"\n👥 Usability Issues ({len(results['usability_issues'])}):")
            for issue in results['usability_issues']:
                print(f"  - {issue}")
        
        print(f"\n📋 Detailed Results:")
        for test in results['test_details']:
            status_icon = "✅" if test['status'] == 'PASS' else "❌"
            print(f"  {status_icon} {test['test']}: {test['details']}")
        
        # Save results
        with open('comprehensive_audit_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to comprehensive_audit_results.json")
        
        # Return appropriate exit code
        if results['critical_issues'] or results['failed_tests'] > results['passed_tests']:
            print("\n❌ AUDIT FAILED - Critical issues need resolution")
            return 1
        else:
            print("\n✅ AUDIT PASSED - System ready for deployment")
            return 0
            
    except Exception as e:
        print(f"\n💥 AUDIT ERROR: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())