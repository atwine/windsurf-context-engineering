#!/usr/bin/env python3
"""
Test Coverage Validator
Provides comprehensive test coverage analysis and validation.
"""

import os
import re
import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCoverageValidator:
    """Comprehensive test coverage validator."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results = {
            'coverage_analysis': {},
            'test_quality': {},
            'missing_tests': [],
            'test_effectiveness': {}
        }
    
    def validate_all(self) -> Dict[str, any]:
        """Run comprehensive test coverage validation."""
        logger.info(f"Starting test coverage validation for {self.project_path}")
        
        # Run all validation checks
        self.analyze_coverage()
        self.assess_test_quality()
        self.identify_missing_tests()
        self.evaluate_test_effectiveness()
        
        # Generate coverage report
        return self.generate_coverage_report()
    
    def analyze_coverage(self) -> Dict[str, any]:
        """Analyze test coverage using coverage.py if available."""
        logger.info("Analyzing test coverage...")
        
        coverage_results = {
            'overall_coverage': 0,
            'file_coverage': {},
            'uncovered_lines': {},
            'coverage_by_type': {}
        }
        
        # Try to run coverage analysis
        try:
            # Check if coverage.py is available
            result = subprocess.run(['coverage', '--version'], 
                                  capture_output=True, text=True, cwd=self.project_path)
            
            if result.returncode == 0:
                # Run coverage analysis
                logger.info("Running coverage analysis...")
                
                # Run tests with coverage
                test_result = subprocess.run(['coverage', 'run', '-m', 'pytest'], 
                                           capture_output=True, text=True, cwd=self.project_path)
                
                # Generate coverage report
                report_result = subprocess.run(['coverage', 'report', '--format=json'], 
                                             capture_output=True, text=True, cwd=self.project_path)
                
                if report_result.returncode == 0:
                    coverage_data = json.loads(report_result.stdout)
                    coverage_results = self._parse_coverage_data(coverage_data)
                else:
                    logger.warning("Could not generate coverage report")
            else:
                logger.info("Coverage.py not available, performing manual analysis")
                coverage_results = self._manual_coverage_analysis()
                
        except Exception as e:
            logger.warning(f"Coverage analysis failed: {e}")
            coverage_results = self._manual_coverage_analysis()
        
        self.results['coverage_analysis'] = coverage_results
        return coverage_results
    
    def assess_test_quality(self) -> Dict[str, any]:
        """Assess the quality of existing tests."""
        logger.info("Assessing test quality...")
        
        test_quality = {
            'test_files': [],
            'test_patterns': {},
            'assertion_analysis': {},
            'test_structure': {}
        }
        
        # Find test files
        test_files = []
        for pattern in ['test_*.py', '*_test.py', 'tests/*.py', 'test/**/*.py']:
            test_files.extend(self.project_path.rglob(pattern))
        
        total_tests = 0
        total_assertions = 0
        test_patterns = {'unit': 0, 'integration': 0, 'functional': 0}
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse test file
                tree = ast.parse(content)
                file_analysis = self._analyze_test_file(tree, content, test_file)
                
                test_quality['test_files'].append(file_analysis)
                total_tests += file_analysis['test_count']
                total_assertions += file_analysis['assertion_count']
                
                # Categorize tests
                for category in file_analysis['test_categories']:
                    test_patterns[category] = test_patterns.get(category, 0) + 1
                    
            except Exception as e:
                logger.warning(f"Could not analyze test file {test_file}: {e}")
        
        # Calculate test quality metrics
        avg_assertions_per_test = total_assertions / max(total_tests, 1)
        
        test_quality['test_patterns'] = test_patterns
        test_quality['assertion_analysis'] = {
            'total_tests': total_tests,
            'total_assertions': total_assertions,
            'avg_assertions_per_test': round(avg_assertions_per_test, 2),
            'quality_score': self._calculate_test_quality_score(total_tests, total_assertions, test_patterns)
        }
        
        self.results['test_quality'] = test_quality
        return test_quality
    
    def identify_missing_tests(self) -> List[Dict[str, any]]:
        """Identify functions and classes that lack tests."""
        logger.info("Identifying missing tests...")
        
        missing_tests = []
        
        # Get all Python source files (excluding tests)
        source_files = []
        for py_file in self.project_path.rglob('*.py'):
            if not self._is_test_file(py_file):
                source_files.append(py_file)
        
        # Get all test files and extract tested functions
        tested_functions = set()
        test_files = []
        for pattern in ['test_*.py', '*_test.py', 'tests/*.py', 'test/**/*.py']:
            test_files.extend(self.project_path.rglob(pattern))
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract function calls in tests (simplified)
                function_calls = re.findall(r'(\w+)\s*\(', content)
                tested_functions.update(function_calls)
                
            except Exception as e:
                logger.warning(f"Could not analyze test file {test_file}: {e}")
        
        # Analyze source files for untested functions
        for source_file in source_files:
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                file_functions = self._extract_functions_and_classes(tree)
                
                for func_info in file_functions:
                    if func_info['name'] not in tested_functions and not func_info['name'].startswith('_'):
                        missing_tests.append({
                            'type': func_info['type'],
                            'name': func_info['name'],
                            'file': str(source_file.relative_to(self.project_path)),
                            'line': func_info['line'],
                            'complexity': func_info.get('complexity', 1),
                            'priority': self._get_test_priority(func_info),
                            'suggested_tests': self._suggest_test_cases(func_info)
                        })
                        
            except Exception as e:
                logger.warning(f"Could not analyze source file {source_file}: {e}")
        
        # Sort by priority
        missing_tests.sort(key=lambda x: x['priority'], reverse=True)
        
        self.results['missing_tests'] = missing_tests
        return missing_tests
    
    def evaluate_test_effectiveness(self) -> Dict[str, any]:
        """Evaluate the effectiveness of existing tests."""
        logger.info("Evaluating test effectiveness...")
        
        effectiveness = {
            'edge_case_coverage': 0,
            'error_handling_tests': 0,
            'integration_coverage': 0,
            'performance_tests': 0,
            'effectiveness_score': 0
        }
        
        # Find test files
        test_files = []
        for pattern in ['test_*.py', '*_test.py', 'tests/*.py', 'test/**/*.py']:
            test_files.extend(self.project_path.rglob(pattern))
        
        edge_case_patterns = [
            r'test.*empty', r'test.*null', r'test.*none', r'test.*zero',
            r'test.*negative', r'test.*boundary', r'test.*limit', r'test.*edge'
        ]
        
        error_patterns = [
            r'test.*error', r'test.*exception', r'test.*fail', r'test.*invalid',
            r'pytest\.raises', r'assertRaises', r'with.*raises'
        ]
        
        integration_patterns = [
            r'test.*integration', r'test.*end.*to.*end', r'test.*e2e',
            r'test.*workflow', r'test.*scenario'
        ]
        
        performance_patterns = [
            r'test.*performance', r'test.*speed', r'test.*time', r'test.*benchmark',
            r'@pytest\.mark\.benchmark', r'timeit'
        ]
        
        total_tests = 0
        edge_case_tests = 0
        error_handling_tests = 0
        integration_tests = 0
        performance_tests = 0
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Count different types of tests
                test_functions = re.findall(r'def\s+(test_\w+)', content)
                total_tests += len(test_functions)
                
                # Count edge case tests
                for pattern in edge_case_patterns:
                    edge_case_tests += len(re.findall(pattern, content, re.IGNORECASE))
                
                # Count error handling tests
                for pattern in error_patterns:
                    error_handling_tests += len(re.findall(pattern, content, re.IGNORECASE))
                
                # Count integration tests
                for pattern in integration_patterns:
                    integration_tests += len(re.findall(pattern, content, re.IGNORECASE))
                
                # Count performance tests
                for pattern in performance_patterns:
                    performance_tests += len(re.findall(pattern, content, re.IGNORECASE))
                    
            except Exception as e:
                logger.warning(f"Could not analyze test effectiveness for {test_file}: {e}")
        
        # Calculate effectiveness percentages
        if total_tests > 0:
            effectiveness['edge_case_coverage'] = round((edge_case_tests / total_tests) * 100, 2)
            effectiveness['error_handling_tests'] = round((error_handling_tests / total_tests) * 100, 2)
            effectiveness['integration_coverage'] = round((integration_tests / total_tests) * 100, 2)
            effectiveness['performance_tests'] = round((performance_tests / total_tests) * 100, 2)
        
        # Calculate overall effectiveness score
        effectiveness_score = (
            min(effectiveness['edge_case_coverage'], 30) +
            min(effectiveness['error_handling_tests'], 25) +
            min(effectiveness['integration_coverage'], 25) +
            min(effectiveness['performance_tests'], 20)
        )
        
        effectiveness['effectiveness_score'] = round(effectiveness_score, 2)
        effectiveness['total_tests'] = total_tests
        
        self.results['test_effectiveness'] = effectiveness
        return effectiveness
    
    def generate_coverage_report(self) -> Dict[str, any]:
        """Generate comprehensive coverage report."""
        coverage_analysis = self.results.get('coverage_analysis', {})
        test_quality = self.results.get('test_quality', {})
        missing_tests = self.results.get('missing_tests', [])
        effectiveness = self.results.get('test_effectiveness', {})
        
        # Calculate overall test score
        coverage_score = coverage_analysis.get('overall_coverage', 0)
        quality_score = test_quality.get('assertion_analysis', {}).get('quality_score', 0)
        effectiveness_score = effectiveness.get('effectiveness_score', 0)
        missing_penalty = min(50, len(missing_tests) * 2)
        
        overall_test_score = max(0, (coverage_score + quality_score + effectiveness_score - missing_penalty) / 3)
        
        report = {
            'summary': {
                'overall_test_score': round(overall_test_score, 2),
                'test_grade': self._get_test_grade(overall_test_score),
                'coverage_percentage': coverage_analysis.get('overall_coverage', 0),
                'total_tests': test_quality.get('assertion_analysis', {}).get('total_tests', 0),
                'missing_tests_count': len(missing_tests),
                'validation_timestamp': self._get_timestamp()
            },
            'coverage': coverage_analysis,
            'quality': test_quality,
            'missing_tests': missing_tests[:10],  # Top 10 priority missing tests
            'effectiveness': effectiveness,
            'recommendations': self._generate_test_recommendations()
        }
        
        return report
    
    # Helper methods
    def _parse_coverage_data(self, coverage_data: Dict) -> Dict[str, any]:
        """Parse coverage.py JSON output."""
        return {
            'overall_coverage': round(coverage_data.get('totals', {}).get('percent_covered', 0), 2),
            'file_coverage': {
                filename: {
                    'coverage': round(file_data.get('summary', {}).get('percent_covered', 0), 2),
                    'missing_lines': file_data.get('missing_lines', []),
                    'covered_lines': file_data.get('executed_lines', [])
                }
                for filename, file_data in coverage_data.get('files', {}).items()
            },
            'lines_covered': coverage_data.get('totals', {}).get('covered_lines', 0),
            'lines_total': coverage_data.get('totals', {}).get('num_statements', 0)
        }
    
    def _manual_coverage_analysis(self) -> Dict[str, any]:
        """Perform manual coverage analysis when coverage.py is not available."""
        logger.info("Performing manual coverage analysis...")
        
        # Get all source files
        source_files = []
        for py_file in self.project_path.rglob('*.py'):
            if not self._is_test_file(py_file) and not self._should_skip_file(py_file):
                source_files.append(py_file)
        
        # Get all test files
        test_files = []
        for pattern in ['test_*.py', '*_test.py', 'tests/*.py', 'test/**/*.py']:
            test_files.extend(self.project_path.rglob(pattern))
        
        # Extract tested modules/functions (simplified)
        tested_modules = set()
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for imports
                imports = re.findall(r'from\s+(\w+(?:\.\w+)*)\s+import', content)
                imports.extend(re.findall(r'import\s+(\w+(?:\.\w+)*)', content))
                tested_modules.update(imports)
                
            except Exception as e:
                logger.warning(f"Could not analyze test file {test_file}: {e}")
        
        # Calculate rough coverage estimate
        total_files = len(source_files)
        covered_files = 0
        
        for source_file in source_files:
            module_name = source_file.stem
            if any(module_name in tested_module for tested_module in tested_modules):
                covered_files += 1
        
        estimated_coverage = (covered_files / max(total_files, 1)) * 100
        
        return {
            'overall_coverage': round(estimated_coverage, 2),
            'file_coverage': {},
            'estimation_method': 'manual',
            'total_source_files': total_files,
            'estimated_covered_files': covered_files
        }
    
    def _analyze_test_file(self, tree: ast.AST, content: str, file_path: Path) -> Dict[str, any]:
        """Analyze a single test file."""
        test_visitor = TestVisitor()
        test_visitor.visit(tree)
        
        # Count assertions
        assertion_patterns = [
            r'assert\s+', r'assertEqual', r'assertTrue', r'assertFalse',
            r'assertIn', r'assertNotIn', r'assertRaises', r'assertIsNone'
        ]
        
        total_assertions = 0
        for pattern in assertion_patterns:
            total_assertions += len(re.findall(pattern, content))
        
        # Categorize tests
        test_categories = []
        if 'integration' in str(file_path).lower():
            test_categories.append('integration')
        elif 'unit' in str(file_path).lower():
            test_categories.append('unit')
        elif 'functional' in str(file_path).lower():
            test_categories.append('functional')
        else:
            test_categories.append('unit')  # Default
        
        return {
            'file_path': str(file_path.relative_to(self.project_path)),
            'test_count': len(test_visitor.test_functions),
            'assertion_count': total_assertions,
            'test_categories': test_categories,
            'test_functions': test_visitor.test_functions
        }
    
    def _extract_functions_and_classes(self, tree: ast.AST) -> List[Dict[str, any]]:
        """Extract functions and classes from AST."""
        extractor = FunctionExtractor()
        extractor.visit(tree)
        return extractor.items
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        test_patterns = ['test_', '_test.py', '/tests/', '/test/']
        return any(pattern in str(file_path) for pattern in test_patterns)
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            '__pycache__', '.git', '.svn', 'node_modules', '.venv', 'venv',
            'setup.py', '__init__.py', 'conftest.py'
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _get_test_priority(self, func_info: Dict[str, any]) -> int:
        """Calculate test priority for a function."""
        priority = 1
        
        # Higher priority for public functions
        if not func_info['name'].startswith('_'):
            priority += 2
        
        # Higher priority for complex functions
        complexity = func_info.get('complexity', 1)
        if complexity > 5:
            priority += 3
        elif complexity > 2:
            priority += 1
        
        # Higher priority for classes
        if func_info['type'] == 'class':
            priority += 2
        
        return priority
    
    def _suggest_test_cases(self, func_info: Dict[str, any]) -> List[str]:
        """Suggest test cases for a function."""
        suggestions = []
        
        if func_info['type'] == 'function':
            suggestions.extend([
                f"test_{func_info['name']}_normal_case",
                f"test_{func_info['name']}_edge_cases",
                f"test_{func_info['name']}_error_handling"
            ])
        elif func_info['type'] == 'class':
            suggestions.extend([
                f"test_{func_info['name']}_initialization",
                f"test_{func_info['name']}_methods",
                f"test_{func_info['name']}_edge_cases"
            ])
        
        return suggestions
    
    def _calculate_test_quality_score(self, total_tests: int, total_assertions: int, test_patterns: Dict[str, int]) -> float:
        """Calculate test quality score."""
        if total_tests == 0:
            return 0
        
        # Base score from assertions per test
        assertions_per_test = total_assertions / total_tests
        assertion_score = min(50, assertions_per_test * 10)
        
        # Bonus for test variety
        variety_score = min(30, len([v for v in test_patterns.values() if v > 0]) * 10)
        
        # Bonus for having enough tests
        volume_score = min(20, total_tests * 2)
        
        return round(assertion_score + variety_score + volume_score, 2)
    
    def _get_test_grade(self, score: float) -> str:
        """Get test grade from score."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_test_recommendations(self) -> List[str]:
        """Generate test improvement recommendations."""
        recommendations = []
        
        coverage = self.results.get('coverage_analysis', {}).get('overall_coverage', 0)
        if coverage < 80:
            recommendations.append(f"Increase test coverage from {coverage}% to at least 80%")
        
        missing_tests = len(self.results.get('missing_tests', []))
        if missing_tests > 0:
            recommendations.append(f"Add tests for {missing_tests} untested functions/classes")
        
        effectiveness = self.results.get('test_effectiveness', {})
        if effectiveness.get('edge_case_coverage', 0) < 20:
            recommendations.append("Add more edge case and boundary condition tests")
        
        if effectiveness.get('error_handling_tests', 0) < 15:
            recommendations.append("Add more error handling and exception tests")
        
        # General recommendations
        recommendations.extend([
            "Use parameterized tests for testing multiple scenarios",
            "Add integration tests for component interactions",
            "Implement test fixtures for consistent test data",
            "Add performance/benchmark tests for critical functions",
            "Use mocking for external dependencies in unit tests"
        ])
        
        return recommendations
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


class TestVisitor(ast.NodeVisitor):
    """AST visitor to extract test functions."""
    
    def __init__(self):
        self.test_functions = []
    
    def visit_FunctionDef(self, node):
        if node.name.startswith('test_'):
            self.test_functions.append({
                'name': node.name,
                'line': node.lineno,
                'docstring': ast.get_docstring(node)
            })
        self.generic_visit(node)


class FunctionExtractor(ast.NodeVisitor):
    """AST visitor to extract functions and classes."""
    
    def __init__(self):
        self.items = []
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        complexity = self._calculate_complexity(node)
        
        self.items.append({
            'type': 'function',
            'name': node.name,
            'line': node.lineno,
            'class': self.current_class,
            'complexity': complexity,
            'docstring': ast.get_docstring(node)
        })
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.items.append({
            'type': 'class',
            'name': node.name,
            'line': node.lineno,
            'class': None,
            'docstring': ast.get_docstring(node)
        })
        
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def _calculate_complexity(self, node):
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        return complexity


# Utility functions
def validate_project_coverage(project_path: str) -> Dict[str, any]:
    """Validate project test coverage."""
    validator = TestCoverageValidator(project_path)
    return validator.validate_all()

def generate_coverage_report(project_path: str, output_file: str = None) -> Dict[str, any]:
    """Generate and optionally save coverage report."""
    report = validate_project_coverage(project_path)
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Coverage report saved to {output_file}")
    
    return report

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test-coverage-validator.py <project_path> [output_file]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🧪 Test Coverage Validator")
    print(f"Validating project: {project_path}")
    print("=" * 50)
    
    try:
        report = generate_coverage_report(project_path, output_file)
        
        # Print summary
        summary = report['summary']
        print(f"\n📊 Test Coverage Results:")
        print(f"  Overall Test Score: {summary['overall_test_score']}/100")
        print(f"  Test Grade: {summary['test_grade']}")
        print(f"  Coverage Percentage: {summary['coverage_percentage']}%")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Missing Tests: {summary['missing_tests_count']}")
        
        # Print effectiveness metrics
        effectiveness = report['effectiveness']
        print(f"\n🎯 Test Effectiveness:")
        print(f"  Edge Case Coverage: {effectiveness.get('edge_case_coverage', 0)}%")
        print(f"  Error Handling Tests: {effectiveness.get('error_handling_tests', 0)}%")
        print(f"  Integration Coverage: {effectiveness.get('integration_coverage', 0)}%")
        print(f"  Performance Tests: {effectiveness.get('performance_tests', 0)}%")
        
        # Test assessment
        score = summary['overall_test_score']
        if score >= 90:
            print("  ✅ EXCELLENT - Comprehensive test coverage")
        elif score >= 80:
            print("  ✅ GOOD - Good test coverage with minor gaps")
        elif score >= 70:
            print("  ⚠️ FAIR - Adequate testing but improvements needed")
        else:
            print("  ❌ NEEDS WORK - Significant testing gaps")
            
    except Exception as e:
        print(f"❌ Coverage validation failed: {e}")
        sys.exit(1)
