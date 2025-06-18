#!/usr/bin/env python3
"""
Quick MVP Audit - Identifies critical issues immediately
"""
import sys
import os
import json
from datetime import datetime

# Add the application directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_code_structure():
    """Analyze code structure and identify issues"""
    issues = []
    
    # Check route completeness
    try:
        with open('routes.py', 'r') as f:
            routes_content = f.read()
        
        required_routes = ['orders', 'settings', 'quotes', 'customers', 'products', 'tasks']
        missing_routes = []
        
        for route in required_routes:
            if f"@main_bp.route('/{route}')" not in routes_content:
                missing_routes.append(route)
        
        if missing_routes:
            issues.append({
                'category': 'routing',
                'severity': 'high',
                'issue': f'Missing routes: {missing_routes}',
                'fixed': False
            })
        else:
            issues.append({
                'category': 'routing',
                'severity': 'high',
                'issue': 'All main routes present',
                'fixed': True
            })
    
    except Exception as e:
        issues.append({
            'category': 'routing',
            'severity': 'critical',
            'issue': f'Cannot read routes.py: {str(e)}',
            'fixed': False
        })
    
    # Check template completeness
    template_dirs = ['customers', 'products', 'quotes', 'orders', 'tasks', 'auth', 'settings']
    missing_templates = []
    
    for template_dir in template_dirs:
        dir_path = f'templates/{template_dir}'
        if not os.path.exists(dir_path):
            missing_templates.append(template_dir)
    
    if missing_templates:
        issues.append({
            'category': 'templates',
            'severity': 'high',
            'issue': f'Missing template directories: {missing_templates}',
            'fixed': False
        })
    else:
        issues.append({
            'category': 'templates',
            'severity': 'high',
            'issue': 'All template directories present',
            'fixed': True
        })
    
    # Check model imports
    try:
        with open('models.py', 'r') as f:
            models_content = f.read()
        
        required_models = ['User', 'Tenant', 'Customer', 'Product', 'Quote', 'Order', 'Task']
        missing_models = []
        
        for model in required_models:
            if f'class {model}(' not in models_content:
                missing_models.append(model)
        
        if missing_models:
            issues.append({
                'category': 'models',
                'severity': 'critical',
                'issue': f'Missing models: {missing_models}',
                'fixed': False
            })
        else:
            issues.append({
                'category': 'models',
                'severity': 'critical',
                'issue': 'All models present',
                'fixed': True
            })
    
    except Exception as e:
        issues.append({
            'category': 'models',
            'severity': 'critical',
            'issue': f'Cannot read models.py: {str(e)}',
            'fixed': False
        })
    
    # Check Flask-Babel configuration
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        babel_issues = []
        
        if 'babel.init_app(app, locale_selector=get_locale)' not in app_content:
            babel_issues.append('Babel not properly initialized')
        
        if '@app.template_global()' not in app_content:
            babel_issues.append('get_locale not available in templates')
        
        if babel_issues:
            issues.append({
                'category': 'internationalization',
                'severity': 'medium',
                'issue': f'Babel issues: {babel_issues}',
                'fixed': False
            })
        else:
            issues.append({
                'category': 'internationalization',
                'severity': 'medium',
                'issue': 'Babel properly configured',
                'fixed': True
            })
    
    except Exception as e:
        issues.append({
            'category': 'internationalization',
            'severity': 'critical',
            'issue': f'Cannot read app.py: {str(e)}',
            'fixed': False
        })
    
    return issues

def check_database_connection():
    """Check if database is accessible"""
    try:
        import psycopg2
        import os
        
        # Try to connect to database
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        conn.close()
        
        return {
            'category': 'database',
            'severity': 'critical',
            'issue': 'Database connection working',
            'fixed': True
        }
    except Exception as e:
        return {
            'category': 'database',
            'severity': 'critical',
            'issue': f'Database connection failed: {str(e)}',
            'fixed': False
        }

def check_missing_templates():
    """Check for missing critical templates"""
    critical_templates = [
        'templates/orders/create.html',
        'templates/orders/view.html',
        'templates/orders/edit.html',
        'templates/quotes/approve.html'
    ]
    
    missing = []
    for template in critical_templates:
        if not os.path.exists(template):
            missing.append(template)
    
    if missing:
        return {
            'category': 'templates',
            'severity': 'high',
            'issue': f'Missing critical templates: {missing}',
            'fixed': False
        }
    else:
        return {
            'category': 'templates',
            'severity': 'high',
            'issue': 'All critical templates present',
            'fixed': True
        }

def analyze_security():
    """Basic security analysis"""
    security_issues = []
    
    # Check for password hashing
    try:
        with open('models.py', 'r') as f:
            models_content = f.read()
        
        if 'password_hash' not in models_content:
            security_issues.append('No password hashing field found')
        
        with open('auth.py', 'r') as f:
            auth_content = f.read()
        
        if 'generate_password_hash' not in auth_content:
            security_issues.append('Password hashing not implemented')
        
        if 'check_password_hash' not in auth_content:
            security_issues.append('Password verification not implemented')
    
    except Exception as e:
        security_issues.append(f'Cannot analyze security: {str(e)}')
    
    return {
        'category': 'security',
        'severity': 'critical',
        'issue': f'Security analysis: {security_issues if security_issues else "Basic security measures in place"}',
        'fixed': len(security_issues) == 0
    }

def run_quick_audit():
    """Run quick audit and return results"""
    print("Running Quick MVP Audit...")
    
    audit_results = []
    
    # Run all checks
    audit_results.extend(analyze_code_structure())
    audit_results.append(check_database_connection())
    audit_results.append(check_missing_templates())
    audit_results.append(analyze_security())
    
    # Categorize results
    critical_issues = [r for r in audit_results if r['severity'] == 'critical' and not r['fixed']]
    high_issues = [r for r in audit_results if r['severity'] == 'high' and not r['fixed']]
    medium_issues = [r for r in audit_results if r['severity'] == 'medium' and not r['fixed']]
    
    total_issues = len(critical_issues) + len(high_issues) + len(medium_issues)
    total_tests = len(audit_results)
    passed_tests = len([r for r in audit_results if r['fixed']])
    
    # Generate summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': total_tests - passed_tests,
        'success_rate': (passed_tests / total_tests) * 100,
        'critical_issues': critical_issues,
        'high_issues': high_issues,
        'medium_issues': medium_issues,
        'all_results': audit_results
    }
    
    return summary

if __name__ == '__main__':
    try:
        results = run_quick_audit()
        
        print(f"\nQuick Audit Results:")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        
        if results['critical_issues']:
            print(f"\nCritical Issues ({len(results['critical_issues'])}):")
            for issue in results['critical_issues']:
                print(f"  - {issue['category']}: {issue['issue']}")
        
        if results['high_issues']:
            print(f"\nHigh Priority Issues ({len(results['high_issues'])}):")
            for issue in results['high_issues']:
                print(f"  - {issue['category']}: {issue['issue']}")
        
        # Save results
        with open('quick_audit_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to quick_audit_results.json")
        
        # Exit appropriately
        if results['critical_issues']:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"Audit failed: {str(e)}")
        sys.exit(1)