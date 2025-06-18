"""
Testing & Quality Agent
======================

Handles automated testing, quality assurance, and test reporting.
"""

import os
import json
import unittest
import sys
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    status: str  # passed, failed, skipped
    duration: float
    error_message: Optional[str] = None


class TestingQualityAgent:
    """Agent for handling testing and quality assurance"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.test_results = []
    
    def discover_tests(self, test_directory: str = 'tests') -> List[str]:
        """Discover test files in the specified directory"""
        test_files = []
        if os.path.exists(test_directory):
            for root, dirs, files in os.walk(test_directory):
                for file in files:
                    if file.startswith('test_') and file.endswith('.py'):
                        test_files.append(os.path.join(root, file))
        return test_files
    
    def run_tests(self, test_directory: str = 'tests') -> Dict[str, Any]:
        """Run all discovered tests"""
        test_files = self.discover_tests(test_directory)
        
        results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_results': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for test_file in test_files:
            try:
                # Load and run test
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromName(test_file.replace('/', '.').replace('.py', ''))
                runner = unittest.TextTestRunner(verbosity=0)
                result = runner.run(suite)
                
                results['total_tests'] += result.testsRun
                results['failed_tests'] += len(result.failures) + len(result.errors)
                results['skipped_tests'] += len(result.skipped)
                results['passed_tests'] += result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
                
            except Exception as e:
                print(f"Error running test {test_file}: {e}")
        
        return results
    
    def get_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        return {
            'agent_name': 'Testing & Quality Agent',
            'status': 'active',
            'last_run': datetime.now().isoformat(),
            'features': [
                'Automated test discovery',
                'Test execution and reporting',
                'Quality assurance checks'
            ]
        }