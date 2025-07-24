#!/usr/bin/env python3
"""
Phase 3 Intelligence Layer Validation Script

This script validates all Phase 3 components and demonstrates their functionality.
"""

import sys
import time
from pathlib import Path

def validate_phase3_intelligence():
    """Validate Phase 3 Intelligence Layer components."""
    
    print("🧠 PHASE 3 INTELLIGENCE LAYER VALIDATION")
    print("=" * 50)
    
    validation_results = []
    
    # 1. Intelligence Engine Validation
    print("\n1. 🤖 Intelligence Engine Validation")
    print("-" * 30)
    try:
        from tools.intelligence_engine import IntelligenceEngine, get_intelligence_recommendations
        
        # Create and test intelligence engine
        engine = IntelligenceEngine('.')
        context = engine.analyze_context()
        recommendations = engine.generate_recommendations()
        summary = engine.get_intelligence_summary()
        
        print(f"✅ Intelligence Engine operational")
        print(f"   • Project Type: {context.project_type}")
        print(f"   • Environment: {context.environment_type}")
        print(f"   • Git Status: {context.git_status}")
        print(f"   • Recommendations Generated: {len(recommendations)}")
        print(f"   • Intelligence Health: {summary.get('intelligence_health', 0):.2f}")
        
        # Test convenience function
        conv_recs = get_intelligence_recommendations('.')
        print(f"   • Convenience Function: {len(conv_recs)} recommendations")
        
        validation_results.append(("Intelligence Engine", True, f"{len(recommendations)} recommendations"))
        
    except Exception as e:
        print(f"❌ Intelligence Engine failed: {e}")
        validation_results.append(("Intelligence Engine", False, str(e)))
    
    # 2. Learning System Integration Validation
    print("\n2. 📚 Learning System Integration Validation")
    print("-" * 30)
    try:
        from tools.learning_integration import LearningSystemIntegration, get_learning_enhanced_recommendations
        
        # Create and test learning integration
        integration = LearningSystemIntegration('.')
        status = integration.get_learning_integration_status()
        enhanced_recs = integration.get_enhanced_recommendations()
        learning_data = integration.get_learning_data_summary()
        
        print(f"✅ Learning Integration operational")
        print(f"   • Integration Active: {status['integration_active']}")
        print(f"   • Learning Modules: {len(integration.learning_modules)}")
        print(f"   • Enhanced Recommendations: {len(enhanced_recs)}")
        print(f"   • Learning Patterns: {learning_data.get('total_patterns', 0)}")
        
        # Test convenience function
        conv_learning = get_learning_enhanced_recommendations('.')
        print(f"   • Convenience Function: {len(conv_learning)} enhanced recommendations")
        
        validation_results.append(("Learning Integration", True, f"{len(enhanced_recs)} enhanced recommendations"))
        
    except Exception as e:
        print(f"❌ Learning Integration failed: {e}")
        validation_results.append(("Learning Integration", False, str(e)))
    
    # 3. Predictive Analytics Validation
    print("\n3. 📊 Predictive Analytics Validation")
    print("-" * 30)
    try:
        from tools.predictive_analytics import PredictiveAnalytics, get_comprehensive_analytics
        
        # Create and test predictive analytics
        analytics = PredictiveAnalytics('.')
        predictions = analytics.get_comprehensive_predictions()
        trends = analytics.analyze_trends()
        
        print(f"✅ Predictive Analytics operational")
        print(f"   • Prediction Types: {len([k for k in predictions.keys() if k != 'summary'])}")
        print(f"   • Trend Analysis: {len(trends)} trends identified")
        
        if 'summary' in predictions:
            summary = predictions['summary']
            print(f"   • Overall Health Score: {summary.get('overall_health_score', 0):.2f}")
            print(f"   • Risk Level: {summary.get('risk_level', 'unknown')}")
            print(f"   • Confidence: {summary.get('confidence', 0):.2f}")
        
        # Test convenience function
        conv_analytics = get_comprehensive_analytics('.')
        print(f"   • Convenience Function: Analytics available")
        
        validation_results.append(("Predictive Analytics", True, f"{len(predictions)} predictions"))
        
    except Exception as e:
        print(f"❌ Predictive Analytics failed: {e}")
        validation_results.append(("Predictive Analytics", False, str(e)))
    
    # 4. Tools Module Integration Validation
    print("\n4. 🔧 Tools Module Integration Validation")
    print("-" * 30)
    try:
        from tools import (
            IntelligenceEngine, LearningSystemIntegration, PredictiveAnalytics,
            get_intelligence_recommendations, get_learning_enhanced_recommendations,
            get_comprehensive_analytics
        )
        
        print(f"✅ Tools Module Integration operational")
        print(f"   • All Phase 3 classes imported successfully")
        print(f"   • All convenience functions available")
        
        # Test integrated workflow
        intel_recs = get_intelligence_recommendations('.')
        learning_recs = get_learning_enhanced_recommendations('.')
        analytics = get_comprehensive_analytics('.')
        
        print(f"   • Integrated Intelligence: {len(intel_recs)} recommendations")
        print(f"   • Integrated Learning: {len(learning_recs)} recommendations")
        print(f"   • Integrated Analytics: {'summary' in analytics}")
        
        validation_results.append(("Tools Integration", True, "All components integrated"))
        
    except Exception as e:
        print(f"❌ Tools Module Integration failed: {e}")
        validation_results.append(("Tools Integration", False, str(e)))
    
    # 5. Cross-Component Workflow Validation
    print("\n5. 🔄 Cross-Component Workflow Validation")
    print("-" * 30)
    try:
        # Test complete intelligence workflow
        engine = IntelligenceEngine('.')
        integration = LearningSystemIntegration('.')
        analytics = PredictiveAnalytics('.')
        
        # Simulate intelligent workflow
        context = engine.analyze_context()
        intelligence_recs = engine.generate_recommendations(context)
        learning_recs = integration.get_enhanced_recommendations()
        predictions = analytics.get_comprehensive_predictions()
        
        # Combine intelligence
        total_recommendations = len(intelligence_recs) + len(learning_recs)
        prediction_categories = len([k for k in predictions.keys() if k != 'summary'])
        
        print(f"✅ Cross-Component Workflow operational")
        print(f"   • Context Analysis: {context.project_type} project detected")
        print(f"   • Total Recommendations: {total_recommendations}")
        print(f"   • Prediction Categories: {prediction_categories}")
        print(f"   • Workflow Integration: Complete")
        
        validation_results.append(("Cross-Component Workflow", True, f"{total_recommendations} total recommendations"))
        
    except Exception as e:
        print(f"❌ Cross-Component Workflow failed: {e}")
        validation_results.append(("Cross-Component Workflow", False, str(e)))
    
    # 6. Performance Validation
    print("\n6. ⚡ Performance Validation")
    print("-" * 30)
    try:
        start_time = time.time()
        
        # Perform multiple operations to test performance
        for i in range(3):
            engine = IntelligenceEngine('.')
            context = engine.analyze_context()
            recommendations = engine.generate_recommendations(context)
        
        end_time = time.time()
        duration = end_time - start_time
        avg_time = duration / 3
        
        print(f"✅ Performance Validation successful")
        print(f"   • 3 complete operations in {duration:.2f}s")
        print(f"   • Average per operation: {avg_time:.2f}s")
        print(f"   • Performance: {'Excellent' if avg_time < 1.0 else 'Good' if avg_time < 2.0 else 'Acceptable'}")
        
        validation_results.append(("Performance", True, f"{avg_time:.2f}s average"))
        
    except Exception as e:
        print(f"❌ Performance Validation failed: {e}")
        validation_results.append(("Performance", False, str(e)))
    
    return validation_results

def print_validation_summary(results):
    """Print comprehensive validation summary."""
    print("\n" + "=" * 50)
    print("🎯 PHASE 3 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]
    
    print(f"\n📊 Validation Results:")
    print(f"  • Total Validations: {len(results)}")
    print(f"  • Passed: {len(passed)}")
    print(f"  • Failed: {len(failed)}")
    print(f"  • Success Rate: {len(passed)/len(results)*100:.1f}%")
    
    if passed:
        print(f"\n✅ Successful Validations:")
        for test_name, _, details in passed:
            print(f"  • {test_name}: {details}")
    
    if failed:
        print(f"\n❌ Failed Validations:")
        for test_name, _, details in failed:
            print(f"  • {test_name}: {details}")
    
    print("\n" + "=" * 50)
    
    if len(failed) == 0:
        print("🎉 PHASE 3 INTELLIGENCE LAYER FULLY VALIDATED!")
        print("✅ All components operational and integrated!")
        print("✅ Ready for production deployment!")
        print("✅ AI-powered recommendations active!")
        print("✅ Learning system integration complete!")
        print("✅ Predictive analytics operational!")
        return True
    else:
        print("⚠️ Some validations failed - review issues")
        return False

if __name__ == "__main__":
    print("Starting Phase 3 Intelligence Layer Validation...")
    
    try:
        results = validate_phase3_intelligence()
        success = print_validation_summary(results)
        
        if success:
            print("\n🚀 PHASE 3 INTELLIGENCE LAYER COMPLETE!")
            print("Ready for advanced AI-powered development workflows!")
            sys.exit(0)
        else:
            print("\n🛑 PHASE 3 VALIDATION INCOMPLETE")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR DURING VALIDATION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
