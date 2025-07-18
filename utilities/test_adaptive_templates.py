#!/usr/bin/env python3
"""
Adaptive Template System Integration Test
Tests the project type detection and adaptive template selection system.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
import logging

# Add utilities to path
sys.path.append(str(Path(__file__).parent))

# Import modules with dynamic loading for hyphenated filenames
try:
    import importlib.util
    
    def load_module(module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    # Load modules
    detector_module = load_module("project_type_detector", Path(__file__).parent / "project-type-detector.py")
    template_module = load_module("adaptive_template_engine", Path(__file__).parent / "adaptive-template-engine.py")
    
    # Extract classes
    ProjectTypeDetector = detector_module.ProjectTypeDetector
    AdaptiveTemplateEngine = template_module.AdaptiveTemplateEngine
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AdaptiveTemplateTest:
    """Test suite for adaptive template system."""
    
    def __init__(self):
        self.test_results = {
            'project_detection_test': {},
            'template_selection_test': {},
            'template_generation_test': {},
            'integration_test': {}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive adaptive template tests."""
        print("🎯 Adaptive Template System Integration Test")
        print("=" * 60)
        
        try:
            # Run individual tests
            self.test_project_detection()
            self.test_template_selection()
            self.test_template_generation()
            self.test_full_integration()
            
            # Generate final report
            return self._generate_test_report()
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return {'error': str(e)}
    
    def test_project_detection(self):
        """Test project type detection functionality."""
        print("\n🔍 Testing Project Type Detection...")
        
        try:
            # Test cases with different project prompts
            test_cases = [
                {
                    'name': 'Web Application',
                    'prompt': 'Build a web application for task management with user authentication, dashboard, and real-time notifications using Flask and PostgreSQL',
                    'expected_type': 'web_application',
                    'expected_complexity': 'medium'
                },
                {
                    'name': 'REST API',
                    'prompt': 'Create a REST API for a blog platform with CRUD operations, authentication, and rate limiting using FastAPI',
                    'expected_type': 'api_service',
                    'expected_complexity': 'medium'
                },
                {
                    'name': 'ML Project',
                    'prompt': 'Develop a machine learning model for sentiment analysis using scikit-learn and pandas with data preprocessing and model evaluation',
                    'expected_type': 'ml_ai_project',
                    'expected_complexity': 'medium'
                },
                {
                    'name': 'CLI Tool',
                    'prompt': 'Build a command-line tool for file processing and automation with argument parsing and logging',
                    'expected_type': 'cli_tool',
                    'expected_complexity': 'simple'
                }
            ]
            
            detector = ProjectTypeDetector()
            test_results = []
            
            for test_case in test_cases:
                print(f"  Testing: {test_case['name']}")
                
                # Analyze project
                analysis = detector.analyze_project(test_case['prompt'])
                
                # Check results
                detected_type = analysis.get('project_type', {}).get('primary', 'unknown')
                detected_complexity = analysis.get('complexity_assessment', {}).get('level', 'unknown')
                
                result = {
                    'name': test_case['name'],
                    'prompt': test_case['prompt'],
                    'expected_type': test_case['expected_type'],
                    'detected_type': detected_type,
                    'expected_complexity': test_case['expected_complexity'],
                    'detected_complexity': detected_complexity,
                    'type_match': detected_type == test_case['expected_type'],
                    'complexity_reasonable': detected_complexity in ['simple', 'medium', 'complex'],
                    'analysis': analysis
                }
                
                test_results.append(result)
                
                # Print result
                type_status = "✅" if result['type_match'] else "⚠️"
                complexity_status = "✅" if result['complexity_reasonable'] else "⚠️"
                print(f"    {type_status} Type: {detected_type} (expected: {test_case['expected_type']})")
                print(f"    {complexity_status} Complexity: {detected_complexity}")
            
            # Calculate success rate
            type_matches = sum(1 for r in test_results if r['type_match'])
            success_rate = (type_matches / len(test_results)) * 100
            
            print(f"  📊 Detection Success Rate: {success_rate:.1f}% ({type_matches}/{len(test_results)})")
            
            self.test_results['project_detection_test'] = {
                'status': 'PASSED' if success_rate >= 75 else 'PARTIAL',
                'success_rate': success_rate,
                'test_cases': test_results,
                'summary': f"Detected {type_matches}/{len(test_results)} project types correctly"
            }
            
        except Exception as e:
            print(f"  ❌ Project detection test failed: {e}")
            self.test_results['project_detection_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_template_selection(self):
        """Test template selection logic."""
        print("\n🎯 Testing Template Selection...")
        
        try:
            engine = AdaptiveTemplateEngine()
            
            # Test template selection with different analyses
            test_analyses = [
                {
                    'name': 'Simple Web App',
                    'analysis': {
                        'project_type': {'primary': 'web_application', 'confidence': 0.8},
                        'complexity_assessment': {'level': 'simple', 'score': 1.5},
                        'technology_stack': {
                            'detected_technologies': {
                                'python': {'confidence': 0.9, 'frameworks': [{'name': 'flask', 'confidence': 0.8}]}
                            }
                        },
                        'template_recommendations': [
                            {'template': 'web_application_simple', 'priority': 'primary', 'reason': 'Best match'}
                        ]
                    },
                    'expected_template': 'web_application_simple'
                },
                {
                    'name': 'REST API',
                    'analysis': {
                        'project_type': {'primary': 'api_service', 'confidence': 0.9},
                        'complexity_assessment': {'level': 'medium', 'score': 2.0},
                        'technology_stack': {
                            'detected_technologies': {
                                'python': {'confidence': 0.9, 'frameworks': [{'name': 'fastapi', 'confidence': 0.9}]}
                            }
                        },
                        'template_recommendations': [
                            {'template': 'rest_api_simple', 'priority': 'primary', 'reason': 'API service match'}
                        ]
                    },
                    'expected_template': 'rest_api_simple'
                },
                {
                    'name': 'ML Project',
                    'analysis': {
                        'project_type': {'primary': 'ml_ai_project', 'confidence': 0.8},
                        'complexity_assessment': {'level': 'medium', 'score': 2.5},
                        'technology_stack': {
                            'detected_technologies': {
                                'python': {'confidence': 0.9, 'frameworks': [{'name': 'scikit-learn', 'confidence': 0.8}]}
                            }
                        },
                        'template_recommendations': [
                            {'template': 'ml_project_simple', 'priority': 'primary', 'reason': 'ML project match'}
                        ]
                    },
                    'expected_template': 'ml_project_simple'
                }
            ]
            
            selection_results = []
            
            for test_case in test_analyses:
                print(f"  Testing: {test_case['name']}")
                
                # Select template
                selection = engine.select_template(test_case['analysis'])
                
                selected_template = selection['selected_template']
                confidence = selection['confidence']
                
                result = {
                    'name': test_case['name'],
                    'expected_template': test_case['expected_template'],
                    'selected_template': selected_template,
                    'confidence': confidence,
                    'template_match': selected_template == test_case['expected_template'],
                    'high_confidence': confidence >= 0.7,
                    'selection': selection
                }
                
                selection_results.append(result)
                
                # Print result
                template_status = "✅" if result['template_match'] else "⚠️"
                confidence_status = "✅" if result['high_confidence'] else "⚠️"
                print(f"    {template_status} Template: {selected_template} (expected: {test_case['expected_template']})")
                print(f"    {confidence_status} Confidence: {confidence:.2f}")
            
            # Calculate success rate
            template_matches = sum(1 for r in selection_results if r['template_match'])
            success_rate = (template_matches / len(selection_results)) * 100
            
            print(f"  📊 Selection Success Rate: {success_rate:.1f}% ({template_matches}/{len(selection_results)})")
            
            self.test_results['template_selection_test'] = {
                'status': 'PASSED' if success_rate >= 75 else 'PARTIAL',
                'success_rate': success_rate,
                'test_cases': selection_results,
                'summary': f"Selected {template_matches}/{len(selection_results)} templates correctly"
            }
            
        except Exception as e:
            print(f"  ❌ Template selection test failed: {e}")
            self.test_results['template_selection_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_template_generation(self):
        """Test template content generation."""
        print("\n📝 Testing Template Generation...")
        
        try:
            engine = AdaptiveTemplateEngine()
            
            # Test template generation
            test_selection = {
                'selected_template': 'web_application_simple',
                'confidence': 0.8,
                'customizations': {
                    'variables': {
                        'project_name': 'task_manager',
                        'project_type': 'web_application',
                        'complexity_level': 'simple',
                        'primary_language': 'Python'
                    },
                    'features': ['user_authentication', 'task_management', 'dashboard'],
                    'dependencies': ['python', 'flask'],
                    'structure_modifications': []
                }
            }
            
            # Generate template content
            templates = engine.generate_template_content(
                test_selection, 
                "A web application for task management with user authentication"
            )
            
            # Validate generated templates
            expected_files = ['README.md', 'project_structure.md', 'implementation_plan.md', 'requirements.txt', 'main.py']
            generated_files = list(templates.keys())
            
            file_results = []
            for expected_file in expected_files:
                exists = expected_file in generated_files
                content_length = len(templates.get(expected_file, '')) if exists else 0
                has_content = content_length > 100  # Minimum content check
                
                file_results.append({
                    'file': expected_file,
                    'exists': exists,
                    'content_length': content_length,
                    'has_content': has_content
                })
                
                status = "✅" if exists and has_content else "❌"
                print(f"    {status} {expected_file}: {content_length} characters")
            
            # Check for customization integration
            readme_content = templates.get('README.md', '')
            customization_checks = [
                ('project_name' in readme_content, 'Project name in README'),
                ('task_manager' in readme_content, 'Specific project name'),
                ('authentication' in readme_content.lower(), 'Feature mentioned'),
                ('flask' in readme_content.lower(), 'Technology mentioned')
            ]
            
            customization_score = sum(1 for check, _ in customization_checks if check)
            print(f"    📊 Customization Integration: {customization_score}/{len(customization_checks)} checks passed")
            
            # Overall generation success
            files_generated = sum(1 for r in file_results if r['exists'] and r['has_content'])
            generation_success = (files_generated / len(expected_files)) * 100
            
            self.test_results['template_generation_test'] = {
                'status': 'PASSED' if generation_success >= 80 else 'PARTIAL',
                'generation_success': generation_success,
                'files_generated': files_generated,
                'total_files': len(expected_files),
                'customization_score': customization_score,
                'file_results': file_results,
                'templates': templates
            }
            
        except Exception as e:
            print(f"  ❌ Template generation test failed: {e}")
            self.test_results['template_generation_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_full_integration(self):
        """Test full end-to-end integration."""
        print("\n🔄 Testing Full Integration...")
        
        try:
            # Test full workflow: prompt -> analysis -> template -> generation
            test_prompt = "Build a REST API for a book library management system with user authentication, book catalog, borrowing system, and search functionality using FastAPI and PostgreSQL"
            
            print(f"  Input Prompt: {test_prompt[:100]}...")
            
            # Step 1: Project Analysis
            detector = ProjectTypeDetector()
            analysis = detector.analyze_project(test_prompt)
            
            detected_type = analysis.get('project_type', {}).get('primary', 'unknown')
            detected_complexity = analysis.get('complexity_assessment', {}).get('level', 'unknown')
            
            print(f"  📊 Analysis: {detected_type} ({detected_complexity})")
            
            # Step 2: Template Selection
            engine = AdaptiveTemplateEngine()
            selection = engine.select_template(analysis)
            
            selected_template = selection['selected_template']
            confidence = selection['confidence']
            
            print(f"  🎯 Selected: {selected_template} (confidence: {confidence:.2f})")
            
            # Step 3: Template Generation
            templates = engine.generate_template_content(selection, test_prompt)
            
            generated_count = len(templates)
            total_content = sum(len(content) for content in templates.values())
            
            print(f"  📝 Generated: {generated_count} files ({total_content} characters)")
            
            # Validation checks
            integration_checks = [
                (detected_type != 'unknown', 'Project type detected'),
                (detected_complexity in ['simple', 'medium', 'complex'], 'Complexity assessed'),
                (confidence >= 0.5, 'Template selection confidence'),
                (generated_count >= 4, 'Minimum files generated'),
                (total_content >= 1000, 'Sufficient content generated'),
                ('api' in selected_template.lower(), 'API template selected for API project')
            ]
            
            passed_checks = sum(1 for check, _ in integration_checks if check)
            integration_score = (passed_checks / len(integration_checks)) * 100
            
            print(f"  ✅ Integration Score: {integration_score:.1f}% ({passed_checks}/{len(integration_checks)})")
            
            # Print check details
            for check, description in integration_checks:
                status = "✅" if check else "❌"
                print(f"    {status} {description}")
            
            self.test_results['integration_test'] = {
                'status': 'PASSED' if integration_score >= 80 else 'PARTIAL',
                'integration_score': integration_score,
                'checks_passed': passed_checks,
                'total_checks': len(integration_checks),
                'workflow_results': {
                    'detected_type': detected_type,
                    'detected_complexity': detected_complexity,
                    'selected_template': selected_template,
                    'selection_confidence': confidence,
                    'generated_files': generated_count,
                    'total_content': total_content
                }
            }
            
        except Exception as e:
            print(f"  ❌ Integration test failed: {e}")
            self.test_results['integration_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        passed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'PASSED')
        total_tests = len(self.test_results)
        
        report = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'partial_tests': sum(1 for result in self.test_results.values() if result.get('status') == 'PARTIAL'),
                'failed_tests': sum(1 for result in self.test_results.values() if result.get('status') == 'FAILED'),
                'success_rate': (passed_tests / total_tests) * 100,
                'test_timestamp': self._get_timestamp()
            },
            'test_results': self.test_results,
            'overall_assessment': self._get_overall_assessment()
        }
        
        return report
    
    def _get_overall_assessment(self) -> str:
        """Get overall assessment of adaptive template system."""
        passed_count = sum(1 for result in self.test_results.values() if result.get('status') == 'PASSED')
        total_count = len(self.test_results)
        
        if passed_count == total_count:
            return "✅ ALL TESTS PASSED - Adaptive template system is fully functional"
        elif passed_count >= total_count * 0.75:
            return "✅ MOSTLY PASSED - Adaptive template system is largely functional with minor issues"
        elif passed_count >= total_count * 0.5:
            return "⚠️ PARTIALLY PASSED - Adaptive template system has some functionality but needs improvements"
        else:
            return "❌ MOSTLY FAILED - Adaptive template system needs significant work"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """Run adaptive template system integration test."""
    tester = AdaptiveTemplateTest()
    
    try:
        report = tester.run_all_tests()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🎯 ADAPTIVE TEMPLATE SYSTEM TEST RESULTS")
        print("=" * 60)
        
        if 'error' in report:
            print(f"❌ Test execution failed: {report['error']}")
            return
        
        summary = report['test_summary']
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Partial: {summary['partial_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        print(f"\n{report['overall_assessment']}")
        
        # Print detailed results
        for test_name, result in report['test_results'].items():
            status = result.get('status', 'UNKNOWN')
            print(f"\n{test_name.upper().replace('_', ' ')}: {status}")
            
            if status == 'PASSED':
                if 'success_rate' in result:
                    print(f"  Success Rate: {result['success_rate']:.1f}%")
                if 'summary' in result:
                    print(f"  Summary: {result['summary']}")
            elif status == 'FAILED':
                print(f"  Error: {result.get('error', 'Unknown error')}")
        
        return report
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return {'error': str(e)}


if __name__ == "__main__":
    main()
