#!/usr/bin/env python3
"""Simple Phase 3 Test"""

def test_intelligence_engine():
    """Test Intelligence Engine"""
    print("Testing Intelligence Engine...")
    try:
        from tools.intelligence_engine import IntelligenceEngine
        print("✅ Intelligence Engine imported successfully")
        
        engine = IntelligenceEngine('.')
        print("✅ Intelligence Engine created successfully")
        
        context = engine.analyze_context()
        print(f"✅ Context analyzed: {context.project_type}")
        
        recommendations = engine.generate_recommendations()
        print(f"✅ Generated {len(recommendations)} recommendations")
        
        return True
    except Exception as e:
        print(f"❌ Intelligence Engine failed: {e}")
        return False

def test_learning_integration():
    """Test Learning Integration"""
    print("\nTesting Learning Integration...")
    try:
        from tools.learning_integration import LearningSystemIntegration
        print("✅ Learning Integration imported successfully")
        
        integration = LearningSystemIntegration('.')
        print("✅ Learning Integration created successfully")
        
        status = integration.get_learning_integration_status()
        print(f"✅ Integration status: {status['integration_active']}")
        
        return True
    except Exception as e:
        print(f"❌ Learning Integration failed: {e}")
        return False

def test_predictive_analytics():
    """Test Predictive Analytics"""
    print("\nTesting Predictive Analytics...")
    try:
        from tools.predictive_analytics import PredictiveAnalytics
        print("✅ Predictive Analytics imported successfully")
        
        analytics = PredictiveAnalytics('.')
        print("✅ Predictive Analytics created successfully")
        
        predictions = analytics.get_comprehensive_predictions()
        print(f"✅ Generated {len(predictions)} prediction types")
        
        return True
    except Exception as e:
        print(f"❌ Predictive Analytics failed: {e}")
        return False

def test_tools_integration():
    """Test Tools Module Integration"""
    print("\nTesting Tools Module Integration...")
    try:
        from tools import (
            IntelligenceEngine, LearningSystemIntegration, PredictiveAnalytics,
            get_intelligence_recommendations, get_learning_enhanced_recommendations,
            get_comprehensive_analytics
        )
        print("✅ All Phase 3 components imported from tools module")
        
        # Test convenience functions
        intel_recs = get_intelligence_recommendations('.')
        learning_recs = get_learning_enhanced_recommendations('.')
        analytics = get_comprehensive_analytics('.')
        
        print(f"✅ Intelligence Recommendations: {len(intel_recs)}")
        print(f"✅ Learning Recommendations: {len(learning_recs)}")
        print(f"✅ Analytics Available: {'summary' in analytics}")
        
        return True
    except Exception as e:
        print(f"❌ Tools Module Integration failed: {e}")
        return False

if __name__ == "__main__":
    print("Phase 3 Intelligence Layer Simple Test")
    print("=" * 40)
    
    tests = [
        test_intelligence_engine,
        test_learning_integration,
        test_predictive_analytics,
        test_tools_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*40}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 ALL PHASE 3 TESTS PASSED!")
        print("✅ Phase 3 Intelligence Layer is operational!")
    else:
        print("⚠️ Some tests failed")
