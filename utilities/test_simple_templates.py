#!/usr/bin/env python3
"""
Simple Adaptive Template System Test
Quick validation of core functionality.
"""

import os
import sys
from pathlib import Path
import importlib.util

# Add utilities to path
sys.path.append(str(Path(__file__).parent))

def load_module(module_name, file_path):
    """Load module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_project_detection():
    """Test project type detection."""
    print("🔍 Testing Project Detection...")
    
    try:
        # Load detector
        detector_module = load_module("project_type_detector", Path(__file__).parent / "project-type-detector.py")
        detector = detector_module.ProjectTypeDetector()
        
        # Test simple case
        prompt = "Build a REST API for user management with FastAPI"
        analysis = detector.analyze_project(prompt)
        
        project_type = analysis.get('project_type', {}).get('primary', 'unknown')
        complexity = analysis.get('complexity_assessment', {}).get('level', 'unknown')
        
        print(f"  ✅ Detected: {project_type} ({complexity})")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def test_template_selection():
    """Test template selection."""
    print("🎯 Testing Template Selection...")
    
    try:
        # Load engine
        template_module = load_module("adaptive_template_engine", Path(__file__).parent / "adaptive-template-engine.py")
        engine = template_module.AdaptiveTemplateEngine()
        
        # Test template selection
        analysis = {
            'project_type': {'primary': 'api_service', 'confidence': 0.8},
            'complexity_assessment': {'level': 'medium', 'score': 2.0},
            'template_recommendations': [
                {'template': 'rest_api_simple', 'priority': 'primary', 'reason': 'API match'}
            ]
        }
        
        selection = engine.select_template(analysis)
        template = selection['selected_template']
        confidence = selection['confidence']
        
        print(f"  ✅ Selected: {template} (confidence: {confidence:.2f})")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def test_template_generation():
    """Test template generation."""
    print("📝 Testing Template Generation...")
    
    try:
        # Load engine
        template_module = load_module("adaptive_template_engine", Path(__file__).parent / "adaptive-template-engine.py")
        engine = template_module.AdaptiveTemplateEngine()
        
        # Test generation
        selection = {
            'selected_template': 'rest_api_simple',
            'confidence': 0.8,
            'customizations': {
                'variables': {
                    'project_name': 'test_api',
                    'project_type': 'api_service'
                }
            }
        }
        
        templates = engine.generate_template_content(selection, "Test API project")
        
        files_count = len(templates)
        total_content = sum(len(content) for content in templates.values())
        
        print(f"  ✅ Generated: {files_count} files ({total_content} chars)")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def main():
    """Run simple tests."""
    print("🎯 Simple Adaptive Template Test")
    print("=" * 40)
    
    tests = [
        test_project_detection,
        test_template_selection,
        test_template_generation
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - System is functional!")
    elif passed >= total * 0.5:
        print("⚠️ PARTIAL SUCCESS - Some issues need attention")
    else:
        print("❌ TESTS FAILED - System needs work")

if __name__ == "__main__":
    main()
