#!/usr/bin/env python3
"""
Quality Guardrails Integration Test
Tests the comprehensive quality guardrails system including security, code quality, and test coverage validation.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add utilities to path
sys.path.append(str(Path(__file__).parent))

# Import our quality guardrails modules
try:
    import importlib.util
    
    # Dynamic import for hyphenated filenames
    def load_module(module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    # Load modules
    security_module = load_module("security_scanner", Path(__file__).parent / "security-scanner.py")
    quality_module = load_module("code_quality_analyzer", Path(__file__).parent / "code-quality-analyzer.py")
    coverage_module = load_module("test_coverage_validator", Path(__file__).parent / "test-coverage-validator.py")
    
    # Extract classes
    SecurityScanner = security_module.SecurityScanner
    CodeQualityAnalyzer = quality_module.CodeQualityAnalyzer
    TestCoverageValidator = coverage_module.TestCoverageValidator
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all utility modules are in the same directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualityGuardrailsTest:
    """Test suite for quality guardrails system."""
    
    def __init__(self):
        self.test_project_path = None
        self.results = {
            'security_test': {},
            'quality_test': {},
            'coverage_test': {},
            'integration_test': {}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive quality guardrails tests."""
        print("🛡️ Quality Guardrails Integration Test")
        print("=" * 50)
        
        # Create test project
        self.test_project_path = self._create_test_project()
        
        try:
            # Run individual component tests
            self.test_security_scanner()
            self.test_code_quality_analyzer()
            self.test_coverage_validator()
            self.test_integration_workflow()
            
            # Generate final report
            return self._generate_test_report()
            
        finally:
            # Cleanup
            self._cleanup_test_project()
    
    def test_security_scanner(self):
        """Test security scanner functionality."""
        print("\n🔒 Testing Security Scanner...")
        
        try:
            scanner = SecurityScanner(self.test_project_path)
            security_report = scanner.scan_all()
            
            # Validate security report structure
            required_keys = ['summary', 'details', 'recommendations']
            for key in required_keys:
                assert key in security_report, f"Missing key: {key}"
            
            # Check that it found the intentional security issues
            secrets = security_report['details']['secrets']
            owasp_issues = security_report['details']['owasp_issues']
            
            print(f"  ✅ Security scan completed")
            print(f"  📊 Found {len(secrets)} secrets")
            print(f"  📊 Found {len(owasp_issues)} OWASP issues")
            print(f"  📊 Security score: {security_report['summary']['security_score']}/100")
            
            # Verify it found our intentional issues
            assert len(secrets) > 0, "Should have found hardcoded secrets"
            assert len(owasp_issues) > 0, "Should have found OWASP issues"
            
            self.results['security_test'] = {
                'status': 'PASSED',
                'report': security_report,
                'findings': {
                    'secrets_found': len(secrets),
                    'owasp_issues_found': len(owasp_issues),
                    'security_score': security_report['summary']['security_score']
                }
            }
            
        except Exception as e:
            print(f"  ❌ Security scanner test failed: {e}")
            self.results['security_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_code_quality_analyzer(self):
        """Test code quality analyzer functionality."""
        print("\n📊 Testing Code Quality Analyzer...")
        
        try:
            analyzer = CodeQualityAnalyzer(self.test_project_path)
            quality_report = analyzer.analyze_all()
            
            # Validate quality report structure
            required_keys = ['summary', 'metrics', 'issues', 'recommendations']
            for key in required_keys:
                assert key in quality_report, f"Missing key: {key}"
            
            # Check metrics
            complexity = quality_report['metrics']['complexity']
            duplication = quality_report['metrics']['duplication']
            maintainability = quality_report['metrics']['maintainability']
            
            print(f"  ✅ Quality analysis completed")
            print(f"  📊 Overall quality score: {quality_report['summary']['overall_quality_score']}/100")
            print(f"  📊 Average complexity: {complexity.get('overall_stats', {}).get('average_complexity', 'N/A')}")
            print(f"  📊 Code duplication: {duplication.get('duplication_stats', {}).get('duplication_percentage', 'N/A')}%")
            print(f"  📊 Maintainability: {maintainability.get('overall_score', 'N/A')}/100")
            
            self.results['quality_test'] = {
                'status': 'PASSED',
                'report': quality_report,
                'findings': {
                    'overall_score': quality_report['summary']['overall_quality_score'],
                    'complexity_analyzed': len(complexity.get('functions', [])),
                    'files_analyzed': len(complexity.get('files', {})),
                    'issues_found': len(quality_report['issues']['code_smells'])
                }
            }
            
        except Exception as e:
            print(f"  ❌ Code quality analyzer test failed: {e}")
            self.results['quality_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_coverage_validator(self):
        """Test coverage validator functionality."""
        print("\n🧪 Testing Coverage Validator...")
        
        try:
            validator = TestCoverageValidator(self.test_project_path)
            coverage_report = validator.validate_all()
            
            # Validate coverage report structure
            required_keys = ['summary', 'coverage', 'quality', 'missing_tests', 'effectiveness']
            for key in required_keys:
                assert key in coverage_report, f"Missing key: {key}"
            
            # Check coverage metrics
            summary = coverage_report['summary']
            missing_tests = coverage_report['missing_tests']
            
            print(f"  ✅ Coverage validation completed")
            print(f"  📊 Overall test score: {summary['overall_test_score']}/100")
            print(f"  📊 Coverage percentage: {summary['coverage_percentage']}%")
            print(f"  📊 Total tests: {summary['total_tests']}")
            print(f"  📊 Missing tests: {summary['missing_tests_count']}")
            
            self.results['coverage_test'] = {
                'status': 'PASSED',
                'report': coverage_report,
                'findings': {
                    'test_score': summary['overall_test_score'],
                    'coverage_percentage': summary['coverage_percentage'],
                    'missing_tests': len(missing_tests)
                }
            }
            
        except Exception as e:
            print(f"  ❌ Coverage validator test failed: {e}")
            self.results['coverage_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_integration_workflow(self):
        """Test integrated quality guardrails workflow."""
        print("\n🔄 Testing Integration Workflow...")
        
        try:
            # Run all guardrails in sequence
            security_scanner = SecurityScanner(self.test_project_path)
            quality_analyzer = CodeQualityAnalyzer(self.test_project_path)
            coverage_validator = TestCoverageValidator(self.test_project_path)
            
            # Generate integrated report
            integrated_report = {
                'project_path': str(self.test_project_path),
                'analysis_timestamp': self._get_timestamp(),
                'security': security_scanner.scan_all(),
                'quality': quality_analyzer.analyze_all(),
                'coverage': coverage_validator.validate_all()
            }
            
            # Calculate overall project health score
            security_score = integrated_report['security']['summary']['security_score']
            quality_score = integrated_report['quality']['summary']['overall_quality_score']
            coverage_score = integrated_report['coverage']['summary']['overall_test_score']
            
            overall_health = (security_score + quality_score + coverage_score) / 3
            
            print(f"  ✅ Integration workflow completed")
            print(f"  📊 Overall project health: {overall_health:.2f}/100")
            print(f"  📊 Security: {security_score}/100")
            print(f"  📊 Quality: {quality_score}/100")
            print(f"  📊 Coverage: {coverage_score}/100")
            
            # Determine project readiness
            readiness = self._assess_project_readiness(security_score, quality_score, coverage_score)
            
            self.results['integration_test'] = {
                'status': 'PASSED',
                'overall_health': overall_health,
                'component_scores': {
                    'security': security_score,
                    'quality': quality_score,
                    'coverage': coverage_score
                },
                'readiness_assessment': readiness,
                'integrated_report': integrated_report
            }
            
        except Exception as e:
            print(f"  ❌ Integration workflow test failed: {e}")
            self.results['integration_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def _create_test_project(self) -> Path:
        """Create a test project with various code quality issues."""
        print("📁 Creating test project...")
        
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix='quality_test_'))
        
        # Create main application file with various issues
        main_py = temp_dir / 'main.py'
        main_py.write_text('''#!/usr/bin/env python3
"""
Test application with intentional quality issues for testing guardrails.
"""

import os
import sys

# Hardcoded secret (security issue)
API_KEY = "sk-1234567890abcdef1234567890abcdef"
PASSWORD = "super_secret_password"

class DataProcessor:
    """Data processor with various quality issues."""
    
    def __init__(self, data_source, api_key, password, timeout, retries, debug_mode, log_level):
        """Constructor with too many parameters."""
        self.data_source = data_source
        self.api_key = api_key
        self.password = password
        self.timeout = timeout
        self.retries = retries
        self.debug_mode = debug_mode
        self.log_level = log_level
    
    def process_data(self, data):
        """Long method with high complexity and deep nesting."""
        if data is not None:
            if len(data) > 0:
                if isinstance(data, list):
                    if all(isinstance(item, dict) for item in data):
                        if 'id' in data[0]:
                            if data[0]['id'] > 0:
                                processed_data = []
                                for item in data:
                                    if item.get('status') == 'active':
                                        if item.get('priority') > 5:
                                            if item.get('category') in ['urgent', 'critical']:
                                                processed_item = {
                                                    'id': item['id'],
                                                    'processed_at': 1234567890,  # Magic number
                                                    'status': 'processed',
                                                    'priority': item['priority'] * 2,
                                                    'score': item.get('score', 0) + 100  # Magic number
                                                }
                                                processed_data.append(processed_item)
                                return processed_data
        return []
    
    def validate_input(self, input_data):
        """Method with SQL injection vulnerability."""
        query = f"SELECT * FROM users WHERE id = {input_data['user_id']}"  # SQL injection
        return query
    
    def render_html(self, user_input):
        """Method with XSS vulnerability."""
        html = f"<div>Welcome {user_input}</div>"  # XSS vulnerability
        return html

# Duplicated code block 1
def calculate_score(value, multiplier, bonus):
    """Calculate score with bonus."""
    base_score = value * multiplier
    if base_score > 100:
        base_score = base_score + bonus
    return base_score

# Duplicated code block 2 (same as above)
def calculate_rating(value, multiplier, bonus):
    """Calculate rating with bonus."""
    base_score = value * multiplier
    if base_score > 100:
        base_score = base_score + bonus
    return base_score

def main():
    """Main function."""
    processor = DataProcessor("database", API_KEY, PASSWORD, 30, 3, True, "DEBUG")
    
    # Test data
    test_data = [
        {'id': 1, 'status': 'active', 'priority': 8, 'category': 'urgent', 'score': 50},
        {'id': 2, 'status': 'active', 'priority': 6, 'category': 'critical', 'score': 75}
    ]
    
    result = processor.process_data(test_data)
    print(f"Processed {len(result)} items")

if __name__ == "__main__":
    main()
''')
        
        # Create a utility file with more issues
        utils_py = temp_dir / 'utils.py'
        utils_py.write_text('''"""
Utility functions with quality issues.
"""

import hashlib

# Weak cryptographic algorithm
def hash_password(password):
    """Hash password using weak algorithm."""
    return hashlib.md5(password.encode()).hexdigest()  # Weak crypto

# Another duplicated code block
def calculate_score(value, multiplier, bonus):
    """Calculate score with bonus."""
    base_score = value * multiplier
    if base_score > 100:
        base_score = base_score + bonus
    return base_score

def process_file(filename):
    """Process file with path traversal vulnerability."""
    file_path = f"../data/{filename}"  # Path traversal
    with open(file_path, 'r') as f:
        return f.read()

class ComplexClass:
    """Class with high complexity."""
    
    def complex_method(self, a, b, c, d, e, f, g, h):
        """Method with high complexity and many parameters."""
        result = 0
        
        if a > 0:
            if b > 0:
                if c > 0:
                    if d > 0:
                        if e > 0:
                            if f > 0:
                                if g > 0:
                                    if h > 0:
                                        for i in range(a):
                                            for j in range(b):
                                                for k in range(c):
                                                    if i * j * k > 1000:  # Magic number
                                                        result += i + j + k
                                                    elif i * j * k > 500:  # Magic number
                                                        result += (i + j + k) * 2
                                                    else:
                                                        result += (i + j + k) * 3
        return result
''')
        
        # Create a minimal test file
        test_dir = temp_dir / 'tests'
        test_dir.mkdir()
        
        test_main_py = test_dir / 'test_main.py'
        test_main_py.write_text('''"""
Minimal test file for testing coverage validation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import DataProcessor, calculate_score

def test_data_processor_init():
    """Test DataProcessor initialization."""
    processor = DataProcessor("test", "key", "pass", 30, 3, True, "INFO")
    assert processor.data_source == "test"

def test_calculate_score():
    """Test calculate_score function."""
    result = calculate_score(10, 2, 5)
    assert result == 25  # 10 * 2 + 5

# Missing tests for:
# - process_data method
# - validate_input method  
# - render_html method
# - utils.py functions
# - ComplexClass methods
''')
        
        # Create requirements.txt with vulnerable dependencies
        requirements_txt = temp_dir / 'requirements.txt'
        requirements_txt.write_text('''# Intentionally vulnerable dependencies for testing
django==2.0.0
flask==1.0.0
requests==2.19.0
pyyaml==3.13
pillow==5.0.0
''')
        
        # Create package.json with vulnerable dependencies
        package_json = temp_dir / 'package.json'
        package_json.write_text('''{
  "name": "test-project",
  "version": "1.0.0",
  "dependencies": {
    "lodash": "4.17.0",
    "minimist": "1.2.0",
    "express": "4.16.0",
    "axios": "0.18.0"
  }
}''')
        
        print(f"  ✅ Test project created at: {temp_dir}")
        return temp_dir
    
    def _cleanup_test_project(self):
        """Clean up test project."""
        if self.test_project_path and self.test_project_path.exists():
            import shutil
            shutil.rmtree(self.test_project_path)
            print(f"  🧹 Cleaned up test project")
    
    def _assess_project_readiness(self, security_score: float, quality_score: float, coverage_score: float) -> Dict[str, Any]:
        """Assess project readiness based on scores."""
        overall_score = (security_score + quality_score + coverage_score) / 3
        
        if overall_score >= 90:
            readiness = "PRODUCTION_READY"
            recommendation = "Project meets high quality standards and is ready for production deployment."
        elif overall_score >= 80:
            readiness = "STAGING_READY"
            recommendation = "Project is ready for staging with minor improvements recommended."
        elif overall_score >= 70:
            readiness = "DEVELOPMENT_READY"
            recommendation = "Project needs quality improvements before staging deployment."
        else:
            readiness = "NOT_READY"
            recommendation = "Project requires significant quality improvements before deployment."
        
        return {
            'readiness_level': readiness,
            'overall_score': overall_score,
            'recommendation': recommendation,
            'blocking_issues': self._identify_blocking_issues(security_score, quality_score, coverage_score)
        }
    
    def _identify_blocking_issues(self, security_score: float, quality_score: float, coverage_score: float) -> List[str]:
        """Identify blocking issues preventing deployment."""
        blocking_issues = []
        
        if security_score < 70:
            blocking_issues.append("Critical security vulnerabilities must be addressed")
        
        if quality_score < 60:
            blocking_issues.append("Code quality issues must be resolved")
        
        if coverage_score < 70:
            blocking_issues.append("Test coverage must be improved")
        
        return blocking_issues
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        passed_tests = sum(1 for result in self.results.values() if result.get('status') == 'PASSED')
        total_tests = len(self.results)
        
        report = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': (passed_tests / total_tests) * 100,
                'test_timestamp': self._get_timestamp()
            },
            'component_results': self.results,
            'overall_assessment': self._get_overall_assessment()
        }
        
        return report
    
    def _get_overall_assessment(self) -> str:
        """Get overall assessment of quality guardrails system."""
        if all(result.get('status') == 'PASSED' for result in self.results.values()):
            return "✅ ALL TESTS PASSED - Quality guardrails system is fully functional"
        else:
            failed_components = [name for name, result in self.results.items() if result.get('status') == 'FAILED']
            return f"❌ SOME TESTS FAILED - Issues in: {', '.join(failed_components)}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """Run quality guardrails integration test."""
    tester = QualityGuardrailsTest()
    
    try:
        report = tester.run_all_tests()
        
        # Print final results
        print("\n" + "=" * 50)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 50)
        
        summary = report['test_summary']
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        print(f"\n{report['overall_assessment']}")
        
        # Print component details
        for component, result in report['component_results'].items():
            status = result.get('status', 'UNKNOWN')
            print(f"\n{component.upper()}: {status}")
            
            if status == 'PASSED' and 'findings' in result:
                findings = result['findings']
                for key, value in findings.items():
                    print(f"  {key}: {value}")
            elif status == 'FAILED':
                print(f"  Error: {result.get('error', 'Unknown error')}")
        
        # Show integration results if available
        if 'integration_test' in report['component_results']:
            integration = report['component_results']['integration_test']
            if integration.get('status') == 'PASSED':
                print(f"\n🏥 PROJECT HEALTH ASSESSMENT:")
                health = integration['overall_health']
                scores = integration['component_scores']
                readiness = integration['readiness_assessment']
                
                print(f"  Overall Health: {health:.1f}/100")
                print(f"  Security Score: {scores['security']}/100")
                print(f"  Quality Score: {scores['quality']}/100")
                print(f"  Coverage Score: {scores['coverage']}/100")
                print(f"  Readiness: {readiness['readiness_level']}")
                print(f"  Recommendation: {readiness['recommendation']}")
                
                if readiness['blocking_issues']:
                    print(f"  Blocking Issues:")
                    for issue in readiness['blocking_issues']:
                        print(f"    - {issue}")
        
        return report
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return {'error': str(e)}


if __name__ == "__main__":
    main()
