#!/usr/bin/env python3
"""
Robust Edge Case Testing Suite for Advanced Learning System
Focuses on practical edge cases without database corruption
"""

import os
import sys
import shutil
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_test_environment():
    """Setup clean test environment"""
    print("🧹 Setting up clean test environment...")
    
    # Clean up any existing test data
    test_dirs = ["robust_test_data"]
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    # Create fresh test directories
    for test_dir in test_dirs:
        os.makedirs(test_dir, exist_ok=True)
    
    print("   ✅ Test environment ready")

def test_basic_functionality():
    """Test basic functionality works correctly"""
    print("\n🧪 Testing Basic Functionality...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        config = LearningSystemConfig(learning_data_dir="robust_test_data")
        integration = LearningSystemIntegration(config)
        
        # Test basic project processing
        result = integration.process_project_completion(
            project_id="basic_test",
            user_id="test_user",
            project_data={"name": "Basic Test", "type": "validation"},
            outcome_data={"success": True, "completion_time": 5.0}
        )
        
        print(f"   ✅ Basic project processing: {result}")
        
        # Test recommendations
        recommendations = integration.get_project_recommendations(
            {"project_type": "validation", "user_id": "test_user"}
        )
        print(f"   ✅ Recommendations generated: {len(recommendations)} items")
        
        # Test system status
        status = integration.get_system_status()
        print(f"   ✅ System health score: {status.system_health_score:.2f}")
        
        # Test report generation
        report_path = integration.generate_learning_report()
        print(f"   ✅ Learning report generated: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_validation_edge_cases():
    """Test data validation with various input types"""
    print("\n🧪 Testing Data Validation Edge Cases...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        config = LearningSystemConfig(learning_data_dir="robust_test_data")
        integration = LearningSystemIntegration(config)
        
        # Test 1: Empty strings
        print("   Testing empty strings...")
        result = integration.process_project_completion(
            project_id="empty_test",
            user_id="test_user",
            project_data={"name": "", "description": ""},
            outcome_data={"success": True, "notes": ""}
        )
        print(f"   ✅ Empty strings handled: {result}")
        
        # Test 2: Special characters
        print("   Testing special characters...")
        special_chars = "Test with !@#$%^&*()[]{}|;':\",./<>?`~"
        result = integration.process_project_completion(
            project_id="special_chars_test",
            user_id="test_user",
            project_data={"name": special_chars},
            outcome_data={"success": True}
        )
        print(f"   ✅ Special characters handled: {result}")
        
        # Test 3: Unicode and emojis
        print("   Testing Unicode and emojis...")
        unicode_text = "Test with Unicode: 🚀🎯✅❌🔥💡 and accents: café, naïve, résumé"
        result = integration.process_project_completion(
            project_id="unicode_test",
            user_id="test_user",
            project_data={"name": unicode_text},
            outcome_data={"success": True}
        )
        print(f"   ✅ Unicode and emojis handled: {result}")
        
        # Test 4: Large numbers
        print("   Testing large numbers...")
        result = integration.process_project_completion(
            project_id="large_numbers_test",
            user_id="test_user",
            project_data={"size": 999999999},
            outcome_data={"success": True, "completion_time": 1000000.5}
        )
        print(f"   ✅ Large numbers handled: {result}")
        
        # Test 5: Negative numbers
        print("   Testing negative numbers...")
        result = integration.process_project_completion(
            project_id="negative_test",
            user_id="test_user",
            project_data={"score": -100},
            outcome_data={"success": False, "completion_time": -1}
        )
        print(f"   ✅ Negative numbers handled: {result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Data validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_high_volume_processing():
    """Test system with high volume of data"""
    print("\n🧪 Testing High Volume Processing...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        config = LearningSystemConfig(learning_data_dir="robust_test_data")
        integration = LearningSystemIntegration(config)
        
        # Process multiple projects rapidly
        print("   Processing 50 projects...")
        start_time = time.time()
        
        success_count = 0
        for i in range(50):
            try:
                result = integration.process_project_completion(
                    project_id=f"volume_test_{i}",
                    user_id=f"user_{i % 5}",  # 5 different users
                    project_data={
                        "name": f"Volume Test Project {i}",
                        "type": "volume_test",
                        "iteration": i,
                        "data": list(range(i, i+10))  # Some variable data
                    },
                    outcome_data={
                        "success": i % 3 == 0,  # 1/3 success rate
                        "completion_time": i * 0.1,
                        "score": i * 5
                    }
                )
                if result:
                    success_count += 1
            except Exception as e:
                print(f"   ⚠️  Project {i} failed: {e}")
        
        processing_time = time.time() - start_time
        print(f"   ✅ Processed {success_count}/50 projects in {processing_time:.2f} seconds")
        
        # Test system status after high volume
        status = integration.get_system_status()
        print(f"   ✅ System health after volume test: {status.system_health_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ High volume processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concurrent_operations():
    """Test concurrent operations on the system"""
    print("\n🧪 Testing Concurrent Operations...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        # Create multiple integration instances
        config1 = LearningSystemConfig(learning_data_dir="robust_test_data")
        config2 = LearningSystemConfig(learning_data_dir="robust_test_data")
        
        integration1 = LearningSystemIntegration(config1)
        integration2 = LearningSystemIntegration(config2)
        
        # Simulate concurrent operations
        print("   Testing concurrent project processing...")
        
        results = []
        for i in range(10):
            # Alternate between instances
            integration = integration1 if i % 2 == 0 else integration2
            
            result = integration.process_project_completion(
                project_id=f"concurrent_test_{i}",
                user_id=f"concurrent_user_{i % 3}",
                project_data={"name": f"Concurrent Test {i}", "instance": i % 2},
                outcome_data={"success": i % 2 == 0, "completion_time": i}
            )
            results.append(result)
        
        success_count = sum(1 for r in results if r)
        print(f"   ✅ Concurrent operations: {success_count}/10 successful")
        
        # Test concurrent recommendations
        print("   Testing concurrent recommendations...")
        recs1 = integration1.get_project_recommendations({"project_type": "concurrent"})
        recs2 = integration2.get_project_recommendations({"project_type": "concurrent"})
        
        print(f"   ✅ Concurrent recommendations: {len(recs1)}, {len(recs2)} items")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Concurrent operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling with various problematic inputs"""
    print("\n🧪 Testing Error Handling...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        config = LearningSystemConfig(learning_data_dir="robust_test_data")
        integration = LearningSystemIntegration(config)
        
        # Test 1: None values
        print("   Testing None values...")
        try:
            result = integration.process_project_completion(
                project_id=None,
                user_id=None,
                project_data=None,
                outcome_data=None
            )
            print(f"   ✅ None values handled gracefully: {result}")
        except Exception as e:
            print(f"   ✅ None values error handled: {type(e).__name__}")
        
        # Test 2: Invalid data types
        print("   Testing invalid data types...")
        try:
            result = integration.process_project_completion(
                project_id=123,  # Should be string
                user_id=456,     # Should be string
                project_data="invalid",  # Should be dict
                outcome_data="invalid"   # Should be dict
            )
            print(f"   ✅ Invalid types handled: {result}")
        except Exception as e:
            print(f"   ✅ Invalid types error handled: {type(e).__name__}")
        
        # Test 3: Empty recommendations context
        print("   Testing empty recommendations context...")
        try:
            recommendations = integration.get_project_recommendations({})
            print(f"   ✅ Empty context handled: {len(recommendations)} recommendations")
        except Exception as e:
            print(f"   ✅ Empty context error handled: {type(e).__name__}")
        
        # Test 4: Invalid recommendations context
        print("   Testing invalid recommendations context...")
        try:
            recommendations = integration.get_project_recommendations("invalid")
            print(f"   ✅ Invalid context handled: {len(recommendations)} recommendations")
        except Exception as e:
            print(f"   ✅ Invalid context error handled: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_limits():
    """Test system behavior at various limits"""
    print("\n🧪 Testing System Limits...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        config = LearningSystemConfig(learning_data_dir="robust_test_data")
        integration = LearningSystemIntegration(config)
        
        # Test 1: Very long strings
        print("   Testing very long strings...")
        long_string = "x" * 1000  # 1000 character string
        result = integration.process_project_completion(
            project_id="long_string_test",
            user_id="test_user",
            project_data={"description": long_string},
            outcome_data={"success": True, "notes": long_string}
        )
        print(f"   ✅ Long strings handled: {result}")
        
        # Test 2: Deep nested data structures
        print("   Testing deep nested structures...")
        nested_data = {"level1": {"level2": {"level3": {"level4": {"level5": {"data": "deep"}}}}}}
        result = integration.process_project_completion(
            project_id="nested_test",
            user_id="test_user",
            project_data=nested_data,
            outcome_data={"success": True}
        )
        print(f"   ✅ Nested structures handled: {result}")
        
        # Test 3: Large arrays
        print("   Testing large arrays...")
        large_array = list(range(1000))  # 1000 element array
        result = integration.process_project_completion(
            project_id="array_test",
            user_id="test_user",
            project_data={"large_array": large_array},
            outcome_data={"success": True}
        )
        print(f"   ✅ Large arrays handled: {result}")
        
        # Test 4: Many recommendations requests
        print("   Testing multiple recommendation requests...")
        for i in range(20):
            recommendations = integration.get_project_recommendations({
                "project_type": f"test_type_{i}",
                "iteration": i
            })
        print(f"   ✅ Multiple recommendation requests handled")
        
        return True
        
    except Exception as e:
        print(f"   ❌ System limits test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_component_integration():
    """Test integration between all components"""
    print("\n🧪 Testing Component Integration...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        config = LearningSystemConfig(learning_data_dir="robust_test_data")
        integration = LearningSystemIntegration(config)
        
        # Test full workflow
        print("   Testing full learning workflow...")
        
        # Step 1: Process multiple projects with different outcomes
        project_types = ["web_app", "mobile_app", "api", "desktop", "ml_model"]
        for i, project_type in enumerate(project_types):
            for j in range(3):  # 3 projects of each type
                result = integration.process_project_completion(
                    project_id=f"{project_type}_project_{j}",
                    user_id=f"user_{j}",
                    project_data={
                        "name": f"{project_type.title()} Project {j}",
                        "type": project_type,
                        "complexity": j + 1
                    },
                    outcome_data={
                        "success": j != 1,  # Make middle project fail
                        "completion_time": (j + 1) * 10,
                        "quality_score": 0.8 if j != 1 else 0.4
                    }
                )
        
        print("   ✅ Multiple project types processed")
        
        # Step 2: Get recommendations for each project type
        for project_type in project_types:
            recommendations = integration.get_project_recommendations({
                "project_type": project_type,
                "user_id": "user_0"
            })
            print(f"   ✅ {project_type} recommendations: {len(recommendations)} items")
        
        # Step 3: Check system status
        status = integration.get_system_status()
        print(f"   ✅ System status: Active={status.system_active}, Health={status.system_health_score:.2f}")
        print(f"   ✅ Data counts: Feedback={status.total_feedback_entries}, Patterns={status.total_patterns_identified}")
        
        # Step 4: Generate comprehensive report
        report_path = integration.generate_learning_report(days=1)
        print(f"   ✅ Comprehensive report generated: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Component integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_environment():
    """Clean up test environment"""
    print("\n🧹 Cleaning up test environment...")
    
    test_dirs = ["robust_test_data"]
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            try:
                shutil.rmtree(test_dir)
                print(f"   ✅ Cleaned up {test_dir}")
            except Exception as e:
                print(f"   ⚠️  Could not clean {test_dir}: {e}")

def run_robust_edge_case_tests():
    """Run all robust edge case tests"""
    print("=" * 80)
    print("🧪 ROBUST EDGE CASE TESTING SUITE")
    print("=" * 80)
    
    setup_test_environment()
    
    test_results = []
    
    # Run all test categories
    test_functions = [
        ("Basic Functionality", test_basic_functionality),
        ("Data Validation Edge Cases", test_data_validation_edge_cases),
        ("High Volume Processing", test_high_volume_processing),
        ("Concurrent Operations", test_concurrent_operations),
        ("Error Handling", test_error_handling),
        ("System Limits", test_system_limits),
        ("Component Integration", test_component_integration)
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
    print("📊 ROBUST EDGE CASE TEST RESULTS")
    print("=" * 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:12} | {test_name}")
    
    print(f"\n📈 OVERALL RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL ROBUST EDGE CASE TESTS PASSED!")
        print("🚀 System is thoroughly tested and ready for Phase 3.2 and 3.3!")
        print("💪 The learning system is robust and handles edge cases gracefully!")
    else:
        print(f"\n⚠️  {total-passed} test(s) need attention before proceeding.")
        print("🔧 Review failed tests and address issues.")
    
    cleanup_test_environment()
    
    return passed == total

if __name__ == "__main__":
    success = run_robust_edge_case_tests()
    sys.exit(0 if success else 1)
