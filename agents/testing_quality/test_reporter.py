"""
Test Reporter Module
====================

Generates test reports in various formats.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

def generate_report(analysis: Dict[str, Any], format: str = 'json') -> Dict[str, Any]:
    """Generate test report in specified format"""
    
    if analysis.get('status') != 'completed':
        return {
            'status': 'report_failed',
            'message': 'Cannot generate report from incomplete analysis',
            'timestamp': datetime.now().isoformat()
        }
    
    report_data = {
        'report_info': {
            'generated_at': datetime.now().isoformat(),
            'format': format,
            'version': '1.0'
        },
        'summary': create_summary(analysis),
        'details': analysis,
        'charts': generate_chart_data(analysis)
    }
    
    if format == 'json':
        return generate_json_report(report_data)
    elif format == 'html':
        return generate_html_report(report_data)
    else:
        return generate_json_report(report_data)

def create_summary(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Create executive summary of test results"""
    metrics = analysis.get('metrics', {})
    quality = analysis.get('quality', {})
    issues = analysis.get('issues', [])
    
    return {
        'test_execution': {
            'total_tests': metrics.get('total_tests', 0),
            'pass_rate': f"{metrics.get('pass_rate', 0):.1f}%",
            'status': 'passing' if metrics.get('pass_rate', 0) >= 80 else 'failing'
        },
        'quality_assessment': {
            'score': quality.get('score', 0),
            'level': quality.get('level', 'unknown'),
            'description': quality.get('description', '')
        },
        'issues_found': len(issues),
        'critical_issues': len([i for i in issues if i.get('severity') == 'high']),
        'recommendations_count': len(analysis.get('recommendations', []))
    }

def generate_chart_data(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate data for charts and visualizations"""
    metrics = analysis.get('metrics', {})
    
    return {
        'test_results_pie': {
            'passed': metrics.get('passed_tests', 0),
            'failed': metrics.get('failed_tests', 0),
            'skipped': metrics.get('skipped_tests', 0),
            'error': metrics.get('error_tests', 0)
        },
        'quality_gauge': {
            'score': analysis.get('quality', {}).get('score', 0),
            'max_score': 100
        },
        'issues_severity': {
            'high': len([i for i in analysis.get('issues', []) if i.get('severity') == 'high']),
            'medium': len([i for i in analysis.get('issues', []) if i.get('severity') == 'medium']),
            'low': len([i for i in analysis.get('issues', []) if i.get('severity') == 'low'])
        }
    }

def generate_json_report(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate JSON format report"""
    return {
        'status': 'completed',
        'format': 'json',
        'timestamp': datetime.now().isoformat(),
        'report': report_data
    }

def generate_html_report(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate HTML format report"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Report - {timestamp}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .summary {{ margin: 20px 0; }}
            .metrics {{ display: flex; gap: 20px; }}
            .metric {{ background: #e8f4f8; padding: 15px; border-radius: 5px; flex: 1; }}
            .issues {{ margin: 20px 0; }}
            .issue {{ padding: 10px; margin: 5px 0; border-left: 4px solid #ff6b6b; background: #fff5f5; }}
            .recommendations {{ margin: 20px 0; }}
            .recommendation {{ padding: 10px; margin: 5px 0; border-left: 4px solid #51cf66; background: #f3fff3; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Test Quality Report</h1>
            <p>Generated: {timestamp}</p>
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <div class="metrics">
                <div class="metric">
                    <h3>Test Execution</h3>
                    <p>Total Tests: {total_tests}</p>
                    <p>Pass Rate: {pass_rate}</p>
                    <p>Status: {status}</p>
                </div>
                <div class="metric">
                    <h3>Quality Score</h3>
                    <p>Score: {quality_score}/100</p>
                    <p>Level: {quality_level}</p>
                </div>
                <div class="metric">
                    <h3>Issues</h3>
                    <p>Total: {total_issues}</p>
                    <p>Critical: {critical_issues}</p>
                </div>
            </div>
        </div>
        
        <div class="issues">
            <h2>Issues Found</h2>
            {issues_html}
        </div>
        
        <div class="recommendations">
            <h2>Recommendations</h2>
            {recommendations_html}
        </div>
    </body>
    </html>
    """
    
    summary = report_data['summary']
    issues_html = ''.join([f'<div class="issue">{issue.get("message", "")}</div>' 
                          for issue in report_data['details'].get('issues', [])])
    recommendations_html = ''.join([f'<div class="recommendation">{rec}</div>' 
                                   for rec in report_data['details'].get('recommendations', [])])
    
    html_content = html_template.format(
        timestamp=report_data['report_info']['generated_at'],
        total_tests=summary['test_execution']['total_tests'],
        pass_rate=summary['test_execution']['pass_rate'],
        status=summary['test_execution']['status'],
        quality_score=summary['quality_assessment']['score'],
        quality_level=summary['quality_assessment']['level'],
        total_issues=summary['issues_found'],
        critical_issues=summary['critical_issues'],
        issues_html=issues_html,
        recommendations_html=recommendations_html
    )
    
    return {
        'status': 'completed',
        'format': 'html',
        'timestamp': datetime.now().isoformat(),
        'content': html_content
    }

def save_report(report: Dict[str, Any], filename: str = None) -> str:
    """Save report to file"""
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        format_ext = 'json' if report.get('format') == 'json' else 'html'
        filename = f'test_report_{timestamp}.{format_ext}'
    
    os.makedirs('reports', exist_ok=True)
    filepath = os.path.join('reports', filename)
    
    if report.get('format') == 'html':
        with open(filepath, 'w') as f:
            f.write(report.get('content', ''))
    else:
        with open(filepath, 'w') as f:
            json.dump(report.get('report', {}), f, indent=2)
    
    return filepath