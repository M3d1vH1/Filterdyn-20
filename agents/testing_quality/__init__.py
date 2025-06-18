"""
Testing & Quality Assurance Agent
=================================

Provides automated testing, quality analysis, and test reporting functionality.
"""

from .test_runner import run_tests
from .test_analysis import analyze_results
from .test_reporter import generate_report

__all__ = ['run_tests', 'analyze_results', 'generate_report', 'TestingQualityAgent']

class TestingQualityAgent:
    """Agent for testing and quality assurance"""
    
    def __init__(self):
        self.run_tests = run_tests
        self.analyze_results = analyze_results
        self.generate_report = generate_report
        
    def execute_test_suite(self, test_path='.'):
        """Execute complete test suite"""
        results = self.run_tests(test_path)
        analysis = self.analyze_results(results)
        report = self.generate_report(analysis)
        return {
            'results': results,
            'analysis': analysis,
            'report': report
        }