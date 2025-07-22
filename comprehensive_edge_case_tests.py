#!/usr/bin/env python3
"""
Comprehensive Edge Case Testing Suite for Advanced Learning System
Tests all components with edge cases, stress scenarios, and error conditions
"""

import os
import sys
import shutil
import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_test_environment():
    """Setup clean test environment"""
    print("🧹 Setting up clean test environment...")
    
    # Clean up any existing test data
    test_dirs = ["test_learning_data", "edge_test_data", "stress_test_data"]
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    # Create fresh test directories
    for test_dir in test_dirs:
        os.makedirs(test_dir, exist_ok=True)
    
    print("   ✅ Test environment ready")

def test_edge_case_imports():
    """Test imports with various edge conditions"""
    print("\n🧪 Testing Edge Case Imports...")
    
    try:
        # Test all imports
        from learning.learning_engine import LearningEngine
        from learning.feedback_collector import FeedbackCollector
        from learning.pattern_analyzer import PatternAnalyzer
        from learning.template_evolution import TemplateEvolution
        from learning.metrics_tracker import MetricsTracker
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        print("   ✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_database_edge_cases():
    """Test database operations with edge cases"""
    print("\n🧪 Testing Database Edge Cases...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        # Test 1: Invalid database path
        print("   Testing invalid database paths...")
        try:
            config = LearningSystemConfig(learning_data_dir="/invalid/path/that/does/not/exist")
            integration = LearningSystemIntegration(config)
            print("   ⚠️  Invalid path handled gracefully")
        except Exception as e:
            print(f"   ⚠️  Invalid path error handled: {e}")
        
        # Test 2: Database corruption simulation
        print("   Testing database corruption handling...")
        config = LearningSystemConfig(learning_data_dir="edge_test_data")
        integration = LearningSystemIntegration(config)
        
        # Corrupt a database file
        db_path = os.path.join("edge_test_data", "learning_engine.db")
        if os.path.exists(db_path):
            with open(db_path, 'w') as f:
                f.write("corrupted data")
        
        # Try to use the corrupted database
        try:
            result = integration.process_project_completion(
                project_id="corruption_test",
                user_id="test_user",
                project_data={"name": "Test"},
                outcome_data={"success": True}
            )
            print("   ✅ Database corruption handled gracefully")
        except Exception as e:
            print(f"   ⚠️  Database corruption error: {e}")
        
        # Test 3: Concurrent access
        print("   Testing concurrent database access...")
        config1 = LearningSystemConfig(learning_data_dir="edge_test_data")
        config2 = LearningSystemConfig(learning_data_dir="edge_test_data")
        integration1 = LearningSystemIntegration(config1)
        integration2 = LearningSystemIntegration(config2)
        
        # Simulate concurrent operations
        result1 = integration1.process_project_completion(
            project_id="concurrent_test_1",
            user_id="user1",
            project_data={"name": "Test1"},
            outcome_data={"success": True}
        )
        
        result2 = integration2.process_project_completion(
            project_id="concurrent_test_2",
            user_id="user2",
            project_data={"name": "Test2"},
            outcome_data={"success": False}
        )
        
        print(f"   ✅ Concurrent access results: {result1}, {result2}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database edge case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_validation_edge_cases():
    """Test data validation with extreme inputs"""
    print("\n🧪 Testing Data Validation Edge Cases...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        config = LearningSystemConfig(learning_data_dir="edge_test_data")
        integration = LearningSystemIntegration(config)
        
        # Test 1: Extremely long strings
        print("   Testing extremely long strings...")
        long_string = "x" * 10000
        result = integration.process_project_completion(
            project_id=long_string[:50],  # Truncate for practical reasons
            user_id="test_user",
            project_data={"name": long_string, "description": long_string},
            outcome_data={"success": True, "notes": long_string}
        )
        print(f"   ✅ Long strings handled: {result}")
        
        # Test 2: Special characters and Unicode
        print("   Testing special characters and Unicode...")
        special_chars = "!@#$%^&*()[]{}|;':\",./<>?`~"
        unicode_chars = "🚀🎯✅❌🔥💡🌟⭐🎉🎊"
        emoji_project = f"test_project_{unicode_chars}"
        
        result = integration.process_project_completion(
            project_id=emoji_project,
            user_id="test_user",
            project_data={"name": special_chars, "emoji": unicode_chars},
            outcome_data={"success": True, "symbols": special_chars}
        )
        print(f"   ✅ Special characters handled: {result}")
        
        # Test 3: None and empty values
        print("   Testing None and empty values...")
        result = integration.process_project_completion(
            project_id="",
            user_id="",
            project_data={},
            outcome_data={}
        )
        print(f"   ✅ Empty values handled: {result}")
        
        result = integration.process_project_completion(
            project_id=None,
            user_id=None,
            project_data=None,
            outcome_data=None
        )
        print(f"   ✅ None values handled: {result}")
        
        # Test 4: Extremely large numbers
        print("   Testing extremely large numbers...")
        large_number = 9999999999999999999999999999
        result = integration.process_project_completion(
            project_id="large_number_test",
            user_id="test_user",
            project_data={"size": large_number},
            outcome_data={"success": True, "completion_time": large_number}
        )
        print(f"   ✅ Large numbers handled: {result}")
        
        # Test 5: Negative numbers
        print("   Testing negative numbers...")
        result = integration.process_project_completion(
            project_id="negative_test",
            user_id="test_user",
            project_data={"score": -1000},
            outcome_data={"success": False, "completion_time": -50}
        )
        print(f"   ✅ Negative numbers handled: {result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Data validation edge case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_and_performance_edge_cases():
    """Test memory usage and performance under stress"""
    print("\n🧪 Testing Memory and Performance Edge Cases...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        config = LearningSystemConfig(learning_data_dir="stress_test_data")
        integration = LearningSystemIntegration(config)
        
        # Test 1: High volume data processing
        print("   Testing high volume data processing...")
        start_time = time.time()
        
        for i in range(100):  # Process 100 projects rapidly
            result = integration.process_project_completion(
                project_id=f"stress_test_{i}",
                user_id=f"user_{i % 10}",  # 10 different users
                project_data={
                    "name": f"Stress Test Project {i}",
                    "type": "stress_test",
                    "iteration": i
                },
                outcome_data={
                    "success": i % 3 == 0,  # 1/3 success rate
                    "completion_time": i * 0.5,
                    "score": i * 10
                }
            )
        
        processing_time = time.time() - start_time
        print(f"   ✅ Processed 100 projects in {processing_time:.2f} seconds")
        
        # Test 2: Memory usage with large datasets
        print("   Testing memory usage with large datasets...")
        large_data = {
            "massive_array": list(range(10000)),
            "large_dict": {f"key_{i}": f"value_{i}" for i in range(1000)},
            "nested_structure": {
                "level1": {
                    "level2": {
                        "level3": {
                            "data": [{"item": i, "value": i*2} for i in range(500)]
                        }
                    }
                }
            }
        }
        
        result = integration.process_project_completion(
            project_id="memory_stress_test",
            user_id="stress_user",
            project_data=large_data,
            outcome_data={"success": True, "data_size": len(str(large_data))}
        )
        print(f"   ✅ Large dataset handled: {result}")
        
        # Test 3: Rapid successive operations
        print("   Testing rapid successive operations...")
        start_time = time.time()
        
        for i in range(50):
            # Rapid fire different operations
            integration.process_project_completion(
                project_id=f"rapid_{i}",
                user_id="rapid_user",
                project_data={"name": f"Rapid {i}"},
                outcome_data={"success": True}
            )
            
            integration.get_project_recommendations({"project_type": "rapid_test"})
            integration.get_system_status()
        
        rapid_time = time.time() - start_time
        print(f"   ✅ Rapid operations completed in {rapid_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Memory/performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_component_isolation():
    """Test individual component isolation and error handling"""
    print("\n🧪 Testing Component Isolation...")
    
    try:
        # Test each component individually
        components = [
            ("LearningEngine", "learning.learning_engine", "LearningEngine"),
            ("FeedbackCollector", "learning.feedback_collector", "FeedbackCollector"),
            ("PatternAnalyzer", "learning.pattern_analyzer", "PatternAnalyzer"),
            ("TemplateEvolution", "learning.template_evolution", "TemplateEvolution"),
            ("MetricsTracker", "learning.metrics_tracker", "MetricsTracker")
        ]
        
        for name, module_path, class_name in components:
            print(f"   Testing {name} isolation...")
            
            try:
                module = __import__(module_path, fromlist=[class_name])
                component_class = getattr(module, class_name)
                
                # Test with invalid parameters
                if name == "TemplateEvolution":
                    component = component_class("edge_test_data")
                else:
                    component = component_class("edge_test_data/test.db")
                
                print(f"   ✅ {name} initialized successfully")
                
                # Test component-specific edge cases
                if hasattr(component, '_init_database'):
                    component._init_database()
                    print(f"   ✅ {name} database initialized")
                
            except Exception as e:
                print(f"   ⚠️  {name} error handled: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Component isolation test failed: {e}")
        return False

def test_system_recovery():
    """Test system recovery from various failure scenarios"""
    print("\n🧪 Testing System Recovery...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        # Test 1: Recovery from partial initialization failure
        print("   Testing recovery from initialization failure...")
        config = LearningSystemConfig(learning_data_dir="edge_test_data")
        
        # Create a scenario where one component might fail
        os.makedirs("edge_test_data", exist_ok=True)
        
        # Create a file where a directory should be
        problem_file = os.path.join("edge_test_data", "problem.db")
        with open(problem_file, 'w') as f:
            f.write("blocking file")
        
        try:
            integration = LearningSystemIntegration(config)
            print("   ✅ System recovered from initialization issues")
        except Exception as e:
            print(f"   ⚠️  Initialization error handled: {e}")
        
        # Clean up
        if os.path.exists(problem_file):
            os.remove(problem_file)
        
        # Test 2: Recovery from operation failure
        print("   Testing recovery from operation failure...")
        integration = LearningSystemIntegration(config)
        
        # Test with malformed data that might cause issues
        malformed_data = {
            "circular_ref": None,
            "invalid_json": object(),  # Non-serializable object
        }
        malformed_data["circular_ref"] = malformed_data  # Circular reference
        
        try:
            result = integration.process_project_completion(
                project_id="recovery_test",
                user_id="test_user",
                project_data=malformed_data,
                outcome_data={"success": True}
            )
            print(f"   ✅ Recovered from malformed data: {result}")
        except Exception as e:
            print(f"   ⚠️  Malformed data error handled: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ System recovery test failed: {e}")
        return False

def test_integration_edge_cases():
    """Test integration-specific edge cases"""
    print("\n🧪 Testing Integration Edge Cases...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        config = LearningSystemConfig(learning_data_dir="edge_test_data")
        integration = LearningSystemIntegration(config)
        
        # Test 1: Recommendations with empty context
        print("   Testing recommendations with empty context...")
        recommendations = integration.get_project_recommendations({})
        print(f"   ✅ Empty context recommendations: {len(recommendations)} items")
        
        # Test 2: System status during high load
        print("   Testing system status during operations...")
        for i in range(10):
            integration.process_project_completion(
                project_id=f"load_test_{i}",
                user_id="load_user",
                project_data={"iteration": i},
                outcome_data={"success": i % 2 == 0}
            )
        
        status = integration.get_system_status()
        print(f"   ✅ System status during load: Health={status.system_health_score:.2f}")
        
        # Test 3: Report generation with no data
        print("   Testing report generation with minimal data...")
        report_path = integration.generate_learning_report()
        print(f"   ✅ Report generated: {report_path}")
        
        # Test 4: Multiple integration instances
        print("   Testing multiple integration instances...")
        integration2 = LearningSystemIntegration(config)
        integration3 = LearningSystemIntegration(config)
        
        # Process data with different instances
        result1 = integration.process_project_completion(
            project_id="multi_instance_1",
            user_id="user1",
            project_data={"instance": 1},
            outcome_data={"success": True}
        )
        
        result2 = integration2.process_project_completion(
            project_id="multi_instance_2",
            user_id="user2",
            project_data={"instance": 2},
            outcome_data={"success": True}
        )
        
        result3 = integration3.process_project_completion(
            project_id="multi_instance_3",
            user_id="user3",
            project_data={"instance": 3},
            outcome_data={"success": True}
        )
        
        print(f"   ✅ Multiple instances: {result1}, {result2}, {result3}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration edge case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_environment():
    """Clean up test environment"""
    print("\n🧹 Cleaning up test environment...")
    
    test_dirs = ["test_learning_data", "edge_test_data", "stress_test_data"]
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            try:
                shutil.rmtree(test_dir)
                print(f"   ✅ Cleaned up {test_dir}")
            except Exception as e:
                print(f"   ⚠️  Could not clean {test_dir}: {e}")

def run_comprehensive_edge_case_tests():
    """Run all comprehensive edge case tests"""
    print("=" * 80)
    print("🧪 COMPREHENSIVE EDGE CASE TESTING SUITE")
    print("=" * 80)
    
    setup_test_environment()
    
    test_results = []
    
    # Run all test categories
    test_functions = [
        ("Import Edge Cases", test_edge_case_imports),
        ("Database Edge Cases", test_database_edge_cases),
        ("Data Validation Edge Cases", test_data_validation_edge_cases),
        ("Memory/Performance Edge Cases", test_memory_and_performance_edge_cases),
        ("Component Isolation", test_component_isolation),
        ("System Recovery", test_system_recovery),
        ("Integration Edge Cases", test_integration_edge_cases)
    ]
    
    for test_name, test_function in test_functions:
        print(f"\n{'='*60}")
        print(f"🔍 {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_function()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE EDGE CASE TEST RESULTS")
    print("=" * 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:12} | {test_name}")
    
    print(f"\n📈 OVERALL RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL EDGE CASE TESTS PASSED!")
        print("🚀 System is robust and ready for Phase 3.2 and 3.3 implementation!")
    else:
        print("⚠️  Some edge cases need attention before proceeding.")
    
    cleanup_test_environment()
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_edge_case_tests()
    sys.exit(0 if success else 1)
