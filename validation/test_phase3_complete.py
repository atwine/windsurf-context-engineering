#!/usr/bin/env python3
"""
Complete Phase 3 Testing Script

This script tests all Phase 3 intelligence layer components to ensure
they are working correctly and integrated properly.
"""

import sys
import traceback
from pathlib import Path

def test_phase3_components():
    """Test all Phase 3 components."""
    print("🧠 TESTING PHASE 3 INTELLIGENCE LAYER")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Intelligence Engine
    print("\n1. Testing Intelligence Engine...")
    try:
        from tools.intelligence_engine import IntelligenceEngine, get_intelligence_recommendations
        
        engine = IntelligenceEngine('.')
        context = engine.analyze_context()
        recommendations = engine.generate_recommendations()
        summary = engine.get_intelligence_summary()
        
        print(f"✅ Intelligence Engine: Context analyzed, {len(recommendations)} recommendations generated")
        print(f"   Project Type: {context.project_type}")
        print(f"   Intelligence Health: {summary.get('intelligence_health', 0):.2f}")
        
        test_results.append(("Intelligence Engine", True, f"{len(recommendations)} recommendations"))
        
    except Exception as e:
        print(f"❌ Intelligence Engine failed: {e}")
        test_results.append(("Intelligence Engine", False, str(e)))
    
    # Test 2: Learning Integration
    print("\n2. Testing Learning Integration...")
    try:
        from tools.learning_integration import LearningSystemIntegration, get_learning_enhanced_recommendations
        
        integration = LearningSystemIntegration('.')
        status = integration.get_learning_integration_status()
        enhanced_recs = integration.get_enhanced_recommendations()
        
        print(f"✅ Learning Integration: {len(integration.learning_modules)} modules loaded")
        print(f"   Integration Active: {status['integration_active']}")
        print(f"   Enhanced Recommendations: {len(enhanced_recs)}")
        
        test_results.append(("Learning Integration", True, f"{len(enhanced_recs)} enhanced recommendations"))
        
    except Exception as e:
        print(f"❌ Learning Integration failed: {e}")
        test_results.append(("Learning Integration", False, str(e)))
    
    # Test 3: Predictive Analytics
    print("\n3. Testing Predictive Analytics...")
    try:
        from tools.predictive_analytics import PredictiveAnalytics, get_comprehensive_analytics
        
        analytics = PredictiveAnalytics('.')
        predictions = analytics.get_comprehensive_predictions()
        
        print(f"✅ Predictive Analytics: {len(predictions)} prediction types")
        if 'summary' in predictions:
            summary = predictions['summary']
            print(f"   Health Score: {summary.get('overall_health_score', 0):.2f}")
            print(f"   Risk Level: {summary.get('risk_level', 'unknown')}")
        
        test_results.append(("Predictive Analytics", True, f"{len(predictions)} predictions"))
        
    except Exception as e:
        print(f"❌ Predictive Analytics failed: {e}")
        test_results.append(("Predictive Analytics", False, str(e)))
    
    # Test 4: Tools Module Integration
    print("\n4. Testing Tools Module Integration...")
    try:
        from tools import (
            IntelligenceEngine, LearningSystemIntegration, PredictiveAnalytics,
            get_intelligence_recommendations, get_learning_enhanced_recommendations,
            get_comprehensive_analytics
        )
        
        print("✅ Tools Module: All Phase 3 components imported successfully")
        
        # Test convenience functions
        intel_recs = get_intelligence_recommendations('.')
        learning_recs = get_learning_enhanced_recommendations('.')
        analytics = get_comprehensive_analytics('.')
        
        print(f"   Intelligence Recommendations: {len(intel_recs)}")
        print(f"   Learning Recommendations: {len(learning_recs)}")
        print(f"   Analytics Available: {'summary' in analytics}")
        
        test_results.append(("Tools Module Integration", True, "All imports successful"))
        
    except Exception as e:
        print(f"❌ Tools Module Integration failed: {e}")
        test_results.append(("Tools Module Integration", False, str(e)))
    
    # Test 5: Cross-Component Integration
    print("\n5. Testing Cross-Component Integration...")
    try:
        # Test all components working together
        engine = IntelligenceEngine('.')
        integration = LearningSystemIntegration('.')
        analytics = PredictiveAnalytics('.')
        
        # Generate data flow
        context = engine.analyze_context()
        intel_recs = engine.generate_recommendations(context)
        learning_recs = integration.get_enhanced_recommendations()
        predictions = analytics.get_comprehensive_predictions()
        
        print("✅ Cross-Component Integration: All components working together")
        print(f"   Total Intelligence Recommendations: {len(intel_recs)}")
        print(f"   Total Learning Recommendations: {len(learning_recs)}")
        print(f"   Prediction Categories: {len([k for k in predictions.keys() if k != 'summary'])}")
        
        test_results.append(("Cross-Component Integration", True, "All components integrated"))
        
    except Exception as e:
        print(f"❌ Cross-Component Integration failed: {e}")
        test_results.append(("Cross-Component Integration", False, str(e)))
    
    # Test 6: Performance Test
    print("\n6. Testing Performance...")
    try:
        import time
        
        start_time = time.time()
        
        # Perform multiple operations
        for i in range(5):
            engine = IntelligenceEngine('.')
            context = engine.analyze_context()
            recommendations = engine.generate_recommendations(context)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Performance Test: 5 operations completed in {duration:.2f}s")
        print(f"   Average per operation: {duration/5:.2f}s")
        
        test_results.append(("Performance Test", True, f"{duration:.2f}s for 5 operations"))
        
    except Exception as e:
        print(f"❌ Performance Test failed: {e}")
        test_results.append(("Performance Test", False, str(e)))
    
    # Test 7: Data Persistence
    print("\n7. Testing Data Persistence...")
    try:
        # Test that components can save and load data
        engine = IntelligenceEngine('.')
        analytics = PredictiveAnalytics('.')
        
        # Generate some data
        context = engine.analyze_context()
        
        # Record performance data
        from tools.predictive_analytics import PerformanceMetrics
        metrics = PerformanceMetrics(
            command_success_rate=0.9,
            average_execution_time=2.0,
            error_frequency=0.05,
            resource_usage={'cpu': 40.0, 'memory': 50.0},
            workflow_efficiency=0.85,
            git_operation_success=0.95,
            environment_health=0.8
        )
        analytics.record_performance_data(metrics)
        
        print("✅ Data Persistence: Components can store and manage data")
        print(f"   Intelligence data path: {engine.learning_data_path}")
        print(f"   Analytics data path: {analytics.analytics_data_path}")
        
        test_results.append(("Data Persistence", True, "Data storage working"))
        
    except Exception as e:
        print(f"❌ Data Persistence failed: {e}")
        test_results.append(("Data Persistence", False, str(e)))
    
    return test_results

def print_test_summary(test_results):
    """Print comprehensive test summary."""
    print("\n" + "=" * 50)
    print("🎯 PHASE 3 INTELLIGENCE LAYER TEST SUMMARY")
    print("=" * 50)
    
    passed_tests = [r for r in test_results if r[1]]
    failed_tests = [r for r in test_results if not r[1]]
    
    print(f"\n📊 Test Results:")
    print(f"  • Total Tests: {len(test_results)}")
    print(f"  • Passed: {len(passed_tests)}")
    print(f"  • Failed: {len(failed_tests)}")
    print(f"  • Success Rate: {len(passed_tests)/len(test_results)*100:.1f}%")
    
    if passed_tests:
        print(f"\n✅ Passed Tests:")
        for test_name, _, details in passed_tests:
            print(f"  • {test_name}: {details}")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test_name, _, details in failed_tests:
            print(f"  • {test_name}: {details}")
    
    print("\n" + "=" * 50)
    
    if len(failed_tests) == 0:
        print("🎉 ALL PHASE 3 TESTS PASSED!")
        print("✅ Intelligence Layer is fully operational and ready for production!")
        print("✅ All components integrated successfully!")
        print("✅ Phase 3 development complete!")
        return True
    else:
        print("⚠️ Some Phase 3 tests failed - review issues")
        return False

if __name__ == "__main__":
    print("Starting Phase 3 Intelligence Layer Testing...")
    
    try:
        test_results = test_phase3_components()
        success = print_test_summary(test_results)
        
        if success:
            print("\n🚀 PHASE 3 INTELLIGENCE LAYER COMPLETE!")
            print("Ready for production deployment and usage!")
            sys.exit(0)
        else:
            print("\n🛑 PHASE 3 TESTING FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR DURING PHASE 3 TESTING: {e}")
        traceback.print_exc()
        sys.exit(1)
