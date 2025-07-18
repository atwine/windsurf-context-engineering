#!/usr/bin/env python3
"""
Code Quality Analyzer
Provides comprehensive code quality analysis including complexity, duplication, and maintainability metrics.
"""

import os
import re
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeQualityAnalyzer:
    """Comprehensive code quality analyzer."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results = {
            'complexity': {},
            'duplication': {},
            'maintainability': {},
            'code_smells': [],
            'technical_debt': {}
        }
    
    def analyze_all(self) -> Dict[str, any]:
        """Run comprehensive code quality analysis."""
        logger.info(f"Starting code quality analysis for {self.project_path}")
        
        # Run all quality checks
        self.analyze_complexity()
        self.analyze_duplication()
        self.analyze_maintainability()
        self.detect_code_smells()
        self.calculate_technical_debt()
        
        # Generate quality report
        return self.generate_quality_report()
    
    def analyze_complexity(self) -> Dict[str, any]:
        """Analyze cyclomatic complexity of code."""
        logger.info("Analyzing code complexity...")
        
        complexity_results = {
            'files': {},
            'functions': [],
            'classes': [],
            'overall_stats': {}
        }
        
        python_files = list(self.project_path.rglob('*.py'))
        total_complexity = 0
        total_functions = 0
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                file_complexity = self._calculate_file_complexity(tree, file_path)
                
                complexity_results['files'][str(file_path.relative_to(self.project_path))] = file_complexity
                
                # Aggregate stats
                for func in file_complexity['functions']:
                    total_complexity += func['complexity']
                    total_functions += 1
                    complexity_results['functions'].append(func)
                
                for cls in file_complexity['classes']:
                    complexity_results['classes'].append(cls)
                    
            except Exception as e:
                logger.warning(f"Could not analyze complexity for {file_path}: {e}")
        
        # Calculate overall statistics
        avg_complexity = total_complexity / max(total_functions, 1)
        complexity_results['overall_stats'] = {
            'total_files': len(complexity_results['files']),
            'total_functions': total_functions,
            'average_complexity': round(avg_complexity, 2),
            'high_complexity_functions': len([f for f in complexity_results['functions'] if f['complexity'] > 10]),
            'complexity_distribution': self._get_complexity_distribution(complexity_results['functions'])
        }
        
        self.results['complexity'] = complexity_results
        return complexity_results
    
    def analyze_duplication(self) -> Dict[str, any]:
        """Analyze code duplication."""
        logger.info("Analyzing code duplication...")
        
        duplication_results = {
            'duplicated_blocks': [],
            'duplication_stats': {}
        }
        
        # Get all code files
        code_files = []
        for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c']:
            code_files.extend(self.project_path.rglob(f'*{ext}'))
        
        # Analyze duplication
        file_hashes = {}
        line_hashes = defaultdict(list)
        
        for file_path in code_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # Hash each line for duplication detection
                for i, line in enumerate(lines):
                    normalized_line = self._normalize_line(line)
                    if len(normalized_line.strip()) > 10:  # Skip short lines
                        line_hash = hashlib.md5(normalized_line.encode()).hexdigest()
                        line_hashes[line_hash].append({
                            'file': str(file_path.relative_to(self.project_path)),
                            'line_number': i + 1,
                            'content': line.strip()
                        })
                
                # Hash blocks of code
                for i in range(len(lines) - 5):  # Minimum 6 lines for a block
                    block = ''.join(lines[i:i+6])
                    normalized_block = self._normalize_code_block(block)
                    if len(normalized_block.strip()) > 100:  # Skip short blocks
                        block_hash = hashlib.md5(normalized_block.encode()).hexdigest()
                        if block_hash not in file_hashes:
                            file_hashes[block_hash] = []
                        file_hashes[block_hash].append({
                            'file': str(file_path.relative_to(self.project_path)),
                            'start_line': i + 1,
                            'end_line': i + 6,
                            'content': block.strip()
                        })
                        
            except Exception as e:
                logger.warning(f"Could not analyze duplication for {file_path}: {e}")
        
        # Find duplicated blocks
        duplicated_blocks = []
        for block_hash, locations in file_hashes.items():
            if len(locations) > 1:
                duplicated_blocks.append({
                    'hash': block_hash,
                    'occurrences': len(locations),
                    'locations': locations,
                    'severity': 'HIGH' if len(locations) > 3 else 'MEDIUM'
                })
        
        # Calculate duplication statistics
        total_lines = sum(len(list(fp.open().readlines())) for fp in code_files if not self._should_skip_file(fp))
        duplicated_lines = sum(
            (block['occurrences'] - 1) * (block['locations'][0]['end_line'] - block['locations'][0]['start_line'] + 1)
            for block in duplicated_blocks
        )
        
        duplication_percentage = (duplicated_lines / max(total_lines, 1)) * 100
        
        duplication_results['duplicated_blocks'] = duplicated_blocks
        duplication_results['duplication_stats'] = {
            'total_duplicated_blocks': len(duplicated_blocks),
            'duplication_percentage': round(duplication_percentage, 2),
            'total_lines': total_lines,
            'duplicated_lines': duplicated_lines
        }
        
        self.results['duplication'] = duplication_results
        return duplication_results
    
    def analyze_maintainability(self) -> Dict[str, any]:
        """Calculate maintainability index for code files."""
        logger.info("Analyzing code maintainability...")
        
        maintainability_results = {
            'files': {},
            'overall_score': 0
        }
        
        python_files = list(self.project_path.rglob('*.py'))
        total_score = 0
        file_count = 0
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Calculate maintainability metrics
                lines_of_code = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
                comment_lines = len([line for line in content.split('\n') if line.strip().startswith('#')])
                
                # Parse AST for complexity
                tree = ast.parse(content)
                complexity = self._calculate_average_complexity(tree)
                
                # Calculate maintainability index (simplified version)
                # MI = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
                # Where HV = Halstead Volume, CC = Cyclomatic Complexity, LOC = Lines of Code
                
                # Simplified calculation
                halstead_volume = max(lines_of_code * 0.5, 1)  # Simplified
                maintainability_index = max(0, 171 - 5.2 * (halstead_volume ** 0.5) - 0.23 * complexity - 16.2 * (lines_of_code ** 0.5))
                
                # Normalize to 0-100 scale
                maintainability_score = min(100, max(0, maintainability_index))
                
                file_result = {
                    'lines_of_code': lines_of_code,
                    'comment_lines': comment_lines,
                    'comment_ratio': comment_lines / max(lines_of_code, 1),
                    'complexity': complexity,
                    'maintainability_score': round(maintainability_score, 2),
                    'maintainability_grade': self._get_maintainability_grade(maintainability_score)
                }
                
                maintainability_results['files'][str(file_path.relative_to(self.project_path))] = file_result
                total_score += maintainability_score
                file_count += 1
                
            except Exception as e:
                logger.warning(f"Could not analyze maintainability for {file_path}: {e}")
        
        # Calculate overall score
        overall_score = total_score / max(file_count, 1)
        maintainability_results['overall_score'] = round(overall_score, 2)
        maintainability_results['overall_grade'] = self._get_maintainability_grade(overall_score)
        
        self.results['maintainability'] = maintainability_results
        return maintainability_results
    
    def detect_code_smells(self) -> List[Dict[str, any]]:
        """Detect code smells and anti-patterns."""
        logger.info("Detecting code smells...")
        
        code_smells = []
        
        # Code smell patterns
        smell_patterns = {
            'long_method': {
                'pattern': r'def\s+\w+\([^)]*\):',
                'check': lambda content, match: len(self._get_method_body(content, match.start())) > 50,
                'severity': 'MEDIUM',
                'description': 'Method is too long (>50 lines)'
            },
            'too_many_parameters': {
                'pattern': r'def\s+\w+\(([^)]*)\):',
                'check': lambda content, match: len([p for p in match.group(1).split(',') if p.strip()]) > 5,
                'severity': 'MEDIUM',
                'description': 'Method has too many parameters (>5)'
            },
            'deep_nesting': {
                'pattern': r'(\s{12,})(if|for|while|try)',
                'check': lambda content, match: True,
                'severity': 'MEDIUM',
                'description': 'Deep nesting detected (>3 levels)'
            },
            'magic_numbers': {
                'pattern': r'(?<![a-zA-Z0-9_])[0-9]{2,}(?![a-zA-Z0-9_])',
                'check': lambda content, match: not self._is_acceptable_number(match.group(0)),
                'severity': 'LOW',
                'description': 'Magic number found - consider using named constants'
            },
            'long_line': {
                'pattern': r'.{120,}',
                'check': lambda content, match: True,
                'severity': 'LOW',
                'description': 'Line is too long (>120 characters)'
            }
        }
        
        # Scan all Python files
        python_files = list(self.project_path.rglob('*.py'))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for smell_type, smell_info in smell_patterns.items():
                    matches = re.finditer(smell_info['pattern'], content, re.MULTILINE)
                    
                    for match in matches:
                        if smell_info['check'](content, match):
                            line_num = content[:match.start()].count('\n') + 1
                            
                            smell = {
                                'type': smell_type,
                                'file': str(file_path.relative_to(self.project_path)),
                                'line': line_num,
                                'severity': smell_info['severity'],
                                'description': smell_info['description'],
                                'context': self._get_line_context(content, match.start()),
                                'recommendation': self._get_smell_recommendation(smell_type)
                            }
                            
                            code_smells.append(smell)
                            
            except Exception as e:
                logger.warning(f"Could not detect code smells in {file_path}: {e}")
        
        self.results['code_smells'] = code_smells
        return code_smells
    
    def calculate_technical_debt(self) -> Dict[str, any]:
        """Calculate technical debt metrics."""
        logger.info("Calculating technical debt...")
        
        # Technical debt factors
        debt_factors = {
            'high_complexity': len([f for f in self.results.get('complexity', {}).get('functions', []) if f['complexity'] > 10]),
            'code_duplication': len(self.results.get('duplication', {}).get('duplicated_blocks', [])),
            'code_smells': len(self.results.get('code_smells', [])),
            'low_maintainability': len([f for f in self.results.get('maintainability', {}).get('files', {}).values() if f['maintainability_score'] < 50])
        }
        
        # Calculate debt score (0-100, lower is better)
        total_issues = sum(debt_factors.values())
        total_files = len(list(self.project_path.rglob('*.py')))
        
        debt_ratio = total_issues / max(total_files, 1)
        debt_score = min(100, debt_ratio * 20)  # Scale to 0-100
        
        # Estimate remediation effort (in hours)
        remediation_hours = (
            debt_factors['high_complexity'] * 2 +
            debt_factors['code_duplication'] * 1.5 +
            debt_factors['code_smells'] * 0.5 +
            debt_factors['low_maintainability'] * 3
        )
        
        technical_debt = {
            'debt_score': round(debt_score, 2),
            'debt_grade': self._get_debt_grade(debt_score),
            'debt_factors': debt_factors,
            'estimated_remediation_hours': round(remediation_hours, 1),
            'priority_actions': self._get_priority_actions(debt_factors)
        }
        
        self.results['technical_debt'] = technical_debt
        return technical_debt
    
    def generate_quality_report(self) -> Dict[str, any]:
        """Generate comprehensive quality report."""
        # Calculate overall quality score
        complexity_score = 100 - min(100, self.results.get('complexity', {}).get('overall_stats', {}).get('average_complexity', 0) * 10)
        duplication_score = 100 - self.results.get('duplication', {}).get('duplication_stats', {}).get('duplication_percentage', 0)
        maintainability_score = self.results.get('maintainability', {}).get('overall_score', 0)
        smell_penalty = min(50, len(self.results.get('code_smells', [])) * 2)
        
        overall_quality_score = max(0, (complexity_score + duplication_score + maintainability_score - smell_penalty) / 3)
        
        report = {
            'summary': {
                'overall_quality_score': round(overall_quality_score, 2),
                'quality_grade': self._get_quality_grade(overall_quality_score),
                'total_issues': len(self.results.get('code_smells', [])),
                'analysis_timestamp': self._get_timestamp()
            },
            'metrics': {
                'complexity': self.results.get('complexity', {}),
                'duplication': self.results.get('duplication', {}),
                'maintainability': self.results.get('maintainability', {}),
                'technical_debt': self.results.get('technical_debt', {})
            },
            'issues': {
                'code_smells': self.results.get('code_smells', [])
            },
            'recommendations': self._generate_quality_recommendations()
        }
        
        return report
    
    # Helper methods
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during analysis."""
        skip_patterns = [
            '__pycache__', '.git', '.svn', 'node_modules', '.venv', 'venv',
            'test_', '_test.py', 'tests/', '.pytest_cache', '.mypy_cache'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _calculate_file_complexity(self, tree: ast.AST, file_path: Path) -> Dict[str, any]:
        """Calculate complexity metrics for a file."""
        complexity_visitor = ComplexityVisitor()
        complexity_visitor.visit(tree)
        
        return {
            'file_path': str(file_path.relative_to(self.project_path)),
            'functions': complexity_visitor.functions,
            'classes': complexity_visitor.classes,
            'total_complexity': sum(f['complexity'] for f in complexity_visitor.functions)
        }
    
    def _calculate_average_complexity(self, tree: ast.AST) -> float:
        """Calculate average complexity for a file."""
        complexity_visitor = ComplexityVisitor()
        complexity_visitor.visit(tree)
        
        if not complexity_visitor.functions:
            return 1.0
        
        return sum(f['complexity'] for f in complexity_visitor.functions) / len(complexity_visitor.functions)
    
    def _get_complexity_distribution(self, functions: List[Dict]) -> Dict[str, int]:
        """Get distribution of complexity levels."""
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'very_high': 0}
        
        for func in functions:
            complexity = func['complexity']
            if complexity <= 5:
                distribution['low'] += 1
            elif complexity <= 10:
                distribution['medium'] += 1
            elif complexity <= 20:
                distribution['high'] += 1
            else:
                distribution['very_high'] += 1
        
        return distribution
    
    def _normalize_line(self, line: str) -> str:
        """Normalize line for duplication detection."""
        # Remove leading/trailing whitespace and comments
        normalized = re.sub(r'#.*$', '', line).strip()
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    def _normalize_code_block(self, block: str) -> str:
        """Normalize code block for duplication detection."""
        lines = block.split('\n')
        normalized_lines = [self._normalize_line(line) for line in lines]
        return '\n'.join(line for line in normalized_lines if line)
    
    def _get_method_body(self, content: str, start_pos: int) -> List[str]:
        """Get method body lines."""
        lines = content[start_pos:].split('\n')
        method_lines = []
        indent_level = None
        
        for line in lines[1:]:  # Skip method definition line
            if line.strip() == '':
                continue
            
            current_indent = len(line) - len(line.lstrip())
            
            if indent_level is None:
                indent_level = current_indent
            elif current_indent <= indent_level and line.strip():
                break
            
            method_lines.append(line)
        
        return method_lines
    
    def _is_acceptable_number(self, number_str: str) -> bool:
        """Check if number is acceptable (not a magic number)."""
        acceptable_numbers = {'0', '1', '2', '10', '100', '1000'}
        return number_str in acceptable_numbers
    
    def _get_line_context(self, content: str, position: int) -> str:
        """Get context around a specific position."""
        lines = content.split('\n')
        line_num = content[:position].count('\n')
        
        start_line = max(0, line_num - 1)
        end_line = min(len(lines), line_num + 2)
        
        context_lines = []
        for i in range(start_line, end_line):
            prefix = '>>> ' if i == line_num else '    '
            context_lines.append(f"{prefix}{lines[i]}")
        
        return '\n'.join(context_lines)
    
    def _get_maintainability_grade(self, score: float) -> str:
        """Get maintainability grade from score."""
        if score >= 85:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 55:
            return 'C'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
    
    def _get_debt_grade(self, score: float) -> str:
        """Get technical debt grade from score."""
        if score <= 10:
            return 'A'
        elif score <= 20:
            return 'B'
        elif score <= 35:
            return 'C'
        elif score <= 50:
            return 'D'
        else:
            return 'F'
    
    def _get_quality_grade(self, score: float) -> str:
        """Get overall quality grade from score."""
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
    
    def _get_smell_recommendation(self, smell_type: str) -> str:
        """Get recommendation for code smell."""
        recommendations = {
            'long_method': 'Break method into smaller, focused methods',
            'too_many_parameters': 'Use parameter objects or reduce parameter count',
            'deep_nesting': 'Extract nested logic into separate methods',
            'magic_numbers': 'Replace with named constants',
            'long_line': 'Break line into multiple lines for readability'
        }
        
        return recommendations.get(smell_type, 'Follow clean code principles')
    
    def _get_priority_actions(self, debt_factors: Dict[str, int]) -> List[str]:
        """Get priority actions based on debt factors."""
        actions = []
        
        if debt_factors['high_complexity'] > 0:
            actions.append(f"Refactor {debt_factors['high_complexity']} high-complexity functions")
        
        if debt_factors['code_duplication'] > 0:
            actions.append(f"Eliminate {debt_factors['code_duplication']} duplicated code blocks")
        
        if debt_factors['low_maintainability'] > 0:
            actions.append(f"Improve maintainability of {debt_factors['low_maintainability']} files")
        
        if debt_factors['code_smells'] > 5:
            actions.append(f"Address {debt_factors['code_smells']} code smells")
        
        return actions
    
    def _generate_quality_recommendations(self) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        # Complexity recommendations
        complexity_stats = self.results.get('complexity', {}).get('overall_stats', {})
        if complexity_stats.get('average_complexity', 0) > 5:
            recommendations.append("Reduce cyclomatic complexity by breaking down complex functions")
        
        # Duplication recommendations
        duplication_stats = self.results.get('duplication', {}).get('duplication_stats', {})
        if duplication_stats.get('duplication_percentage', 0) > 5:
            recommendations.append("Eliminate code duplication by extracting common functionality")
        
        # Maintainability recommendations
        maintainability = self.results.get('maintainability', {})
        if maintainability.get('overall_score', 100) < 70:
            recommendations.append("Improve code maintainability through better documentation and structure")
        
        # General recommendations
        recommendations.extend([
            "Add comprehensive unit tests for better coverage",
            "Implement consistent code formatting and style",
            "Add meaningful comments and documentation",
            "Regular code reviews and refactoring sessions",
            "Use static analysis tools in CI/CD pipeline"
        ])
        
        return recommendations
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity."""
    
    def __init__(self):
        self.functions = []
        self.classes = []
        self.current_function = None
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        complexity = self._calculate_complexity(node)
        
        func_info = {
            'name': node.name,
            'line': node.lineno,
            'complexity': complexity,
            'class': self.current_class['name'] if self.current_class else None
        }
        
        self.functions.append(func_info)
        
        # Visit child nodes
        old_function = self.current_function
        self.current_function = func_info
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_ClassDef(self, node):
        class_info = {
            'name': node.name,
            'line': node.lineno,
            'methods': []
        }
        
        self.classes.append(class_info)
        
        # Visit child nodes
        old_class = self.current_class
        self.current_class = class_info
        self.generic_visit(node)
        self.current_class = old_class
    
    def _calculate_complexity(self, node):
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity


# Utility functions
def analyze_project_quality(project_path: str) -> Dict[str, any]:
    """Analyze project code quality."""
    analyzer = CodeQualityAnalyzer(project_path)
    return analyzer.analyze_all()

def generate_quality_report(project_path: str, output_file: str = None) -> Dict[str, any]:
    """Generate and optionally save quality report."""
    report = analyze_project_quality(project_path)
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Quality report saved to {output_file}")
    
    return report

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python code-quality-analyzer.py <project_path> [output_file]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"📊 Code Quality Analyzer")
    print(f"Analyzing project: {project_path}")
    print("=" * 50)
    
    try:
        report = generate_quality_report(project_path, output_file)
        
        # Print summary
        summary = report['summary']
        print(f"\n📈 Code Quality Results:")
        print(f"  Overall Quality Score: {summary['overall_quality_score']}/100")
        print(f"  Quality Grade: {summary['quality_grade']}")
        print(f"  Total Issues: {summary['total_issues']}")
        
        # Print key metrics
        metrics = report['metrics']
        if 'complexity' in metrics:
            complexity = metrics['complexity'].get('overall_stats', {})
            print(f"  Average Complexity: {complexity.get('average_complexity', 'N/A')}")
        
        if 'duplication' in metrics:
            duplication = metrics['duplication'].get('duplication_stats', {})
            print(f"  Code Duplication: {duplication.get('duplication_percentage', 'N/A')}%")
        
        if 'maintainability' in metrics:
            maintainability = metrics['maintainability']
            print(f"  Maintainability Score: {maintainability.get('overall_score', 'N/A')}/100")
        
        if 'technical_debt' in metrics:
            debt = metrics['technical_debt']
            print(f"  Technical Debt: {debt.get('debt_grade', 'N/A')} ({debt.get('estimated_remediation_hours', 'N/A')} hours)")
        
        # Quality assessment
        score = summary['overall_quality_score']
        if score >= 90:
            print("  ✅ EXCELLENT - High quality code")
        elif score >= 80:
            print("  ✅ GOOD - Good quality with minor improvements needed")
        elif score >= 70:
            print("  ⚠️ FAIR - Some quality issues to address")
        else:
            print("  ❌ NEEDS WORK - Significant quality improvements needed")
            
    except Exception as e:
        print(f"❌ Quality analysis failed: {e}")
        sys.exit(1)
