"""
Test Analysis Module
====================

Analyzes test results and provides insights.
"""

from typing import Dict, List, Any
from datetime import datetime

def analyze_results(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze test results and provide insights"""
    
    if test_results.get('status') != 'completed':
        return {
            'status': 'analysis_failed',
            'message': f"Cannot analyze results: {test_results.get('message', 'Unknown error')}",
            'timestamp': datetime.now().isoformat()
        }
    
    results = test_results.get('results', {})
    summary = results.get('summary', {})
    
    # Calculate metrics
    total_tests = summary.get('total', 0)
    passed_tests = summary.get('passed', 0)
    failed_tests = summary.get('failed', 0)
    skipped_tests = summary.get('skipped', 0)
    error_tests = summary.get('error', 0)
    
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    failure_rate = (failed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Quality assessment
    quality_score = calculate_quality_score(pass_rate, total_tests)
    quality_level = get_quality_level(quality_score)
    
    # Identify issues
    issues = identify_issues(test_results)
    recommendations = generate_recommendations(pass_rate, total_tests, issues)
    
    return {
        'status': 'completed',
        'timestamp': datetime.now().isoformat(),
        'metrics': {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'error_tests': error_tests,
            'pass_rate': round(pass_rate, 2),
            'failure_rate': round(failure_rate, 2)
        },
        'quality': {
            'score': quality_score,
            'level': quality_level,
            'description': get_quality_description(quality_level)
        },
        'issues': issues,
        'recommendations': recommendations,
        'test_details': results.get('tests', [])
    }

def calculate_quality_score(pass_rate: float, total_tests: int) -> int:
    """Calculate overall quality score (0-100)"""
    if total_tests == 0:
        return 0
    
    # Base score from pass rate
    score = pass_rate
    
    # Adjust for test coverage (more tests = higher confidence)
    if total_tests >= 10:
        score += 10
    elif total_tests >= 5:
        score += 5
    
    # Cap at 100
    return min(int(score), 100)

def get_quality_level(score: int) -> str:
    """Get quality level based on score"""
    if score >= 90:
        return 'excellent'
    elif score >= 80:
        return 'good'
    elif score >= 70:
        return 'fair'
    elif score >= 60:
        return 'poor'
    else:
        return 'critical'

def get_quality_description(level: str) -> str:
    """Get description for quality level"""
    descriptions = {
        'excellent': 'Code quality is excellent with comprehensive test coverage',
        'good': 'Code quality is good with adequate test coverage',
        'fair': 'Code quality is fair but could benefit from more tests',
        'poor': 'Code quality is poor and needs improvement',
        'critical': 'Code quality is critical and requires immediate attention'
    }
    return descriptions.get(level, 'Unknown quality level')

def identify_issues(test_results: Dict[str, Any]) -> List[Dict[str, str]]:
    """Identify issues from test results"""
    issues = []
    
    results = test_results.get('results', {})
    summary = results.get('summary', {})
    
    # Check for failed tests
    if summary.get('failed', 0) > 0:
        issues.append({
            'type': 'test_failures',
            'severity': 'high',
            'message': f"{summary['failed']} test(s) are failing"
        })
    
    # Check for errors
    if summary.get('error', 0) > 0:
        issues.append({
            'type': 'test_errors',
            'severity': 'high',
            'message': f"{summary['error']} test(s) have errors"
        })
    
    # Check for low test coverage
    total_tests = summary.get('total', 0)
    if total_tests < 5:
        issues.append({
            'type': 'low_coverage',
            'severity': 'medium',
            'message': 'Low test coverage - consider adding more tests'
        })
    
    # Check for skipped tests
    if summary.get('skipped', 0) > 0:
        issues.append({
            'type': 'skipped_tests',
            'severity': 'low',
            'message': f"{summary['skipped']} test(s) are being skipped"
        })
    
    return issues

def generate_recommendations(pass_rate: float, total_tests: int, issues: List[Dict[str, str]]) -> List[str]:
    """Generate recommendations based on analysis"""
    recommendations = []
    
    # Address test failures
    if any(issue['type'] == 'test_failures' for issue in issues):
        recommendations.append('Fix failing tests to improve code reliability')
    
    # Address test errors
    if any(issue['type'] == 'test_errors' for issue in issues):
        recommendations.append('Resolve test errors to ensure proper test execution')
    
    # Improve test coverage
    if total_tests < 10:
        recommendations.append('Add more test cases to improve code coverage')
    
    # Address skipped tests
    if any(issue['type'] == 'skipped_tests' for issue in issues):
        recommendations.append('Review and enable skipped tests if possible')
    
    # General recommendations based on pass rate
    if pass_rate < 80:
        recommendations.append('Focus on improving test pass rate above 80%')
    elif pass_rate < 95:
        recommendations.append('Work towards achieving 95%+ test pass rate')
    
    if not recommendations:
        recommendations.append('Test quality is good - maintain current standards')
    
    return recommendations