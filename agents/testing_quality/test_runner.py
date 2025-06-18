"""
Test Runner Module
==================

Handles test discovery and execution.
"""

import os
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Any

def run_tests(test_path: str = '.') -> Dict[str, Any]:
    """Run tests and return results"""
    try:
        # Discover test files
        test_files = discover_tests(test_path)
        
        if not test_files:
            return {
                'status': 'no_tests',
                'message': 'No test files found',
                'timestamp': datetime.now().isoformat(),
                'test_files': [],
                'results': {}
            }
        
        # Run pytest with JSON output
        result = subprocess.run([
            'python', '-m', 'pytest', 
            '--json-report', '--json-report-file=/tmp/test_results.json',
            '-v', test_path
        ], capture_output=True, text=True, timeout=300)
        
        # Parse results
        if os.path.exists('/tmp/test_results.json'):
            with open('/tmp/test_results.json', 'r') as f:
                test_results = json.load(f)
        else:
            test_results = parse_pytest_output(result.stdout, result.stderr)
        
        return {
            'status': 'completed',
            'exit_code': result.returncode,
            'timestamp': datetime.now().isoformat(),
            'test_files': test_files,
            'results': test_results,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            'status': 'timeout',
            'message': 'Test execution timed out',
            'timestamp': datetime.now().isoformat(),
            'test_files': test_files if 'test_files' in locals() else [],
            'results': {}
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat(),
            'test_files': [],
            'results': {}
        }

def discover_tests(path: str) -> List[str]:
    """Discover test files in the given path"""
    test_files = []
    patterns = ['test_*.py', '*_test.py']
    
    for root, dirs, files in os.walk(path):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if any(file.startswith('test_') or file.endswith('_test.py') for pattern in patterns):
                if file.endswith('.py'):
                    test_files.append(os.path.join(root, file))
    
    return test_files

def parse_pytest_output(stdout: str, stderr: str) -> Dict[str, Any]:
    """Parse pytest output when JSON report is not available"""
    lines = stdout.split('\n') + stderr.split('\n')
    
    results = {
        'summary': {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'error': 0
        },
        'tests': []
    }
    
    for line in lines:
        if '::' in line and any(status in line for status in ['PASSED', 'FAILED', 'SKIPPED', 'ERROR']):
            parts = line.split()
            if len(parts) >= 2:
                test_name = parts[0]
                status = parts[-1].lower()
                
                results['tests'].append({
                    'name': test_name,
                    'outcome': status,
                    'duration': 0.0
                })
                
                if status in results['summary']:
                    results['summary'][status] += 1
                results['summary']['total'] += 1
    
    return results