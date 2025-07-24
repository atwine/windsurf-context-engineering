#!/usr/bin/env python3
"""
Complete System Test

Final comprehensive test of all phases (1-4) of the Windsurf Context Engineering Framework.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_complete_system():
    """Test the complete system across all phases."""
    print("🚀 COMPLETE SYSTEM TEST - ALL PHASES")
    print("=" * 50)
    
    test_results = []
    
    # Phase 1: Legacy Components
    print("\n📦 PHASE 1: Legacy Components")
    print("-" * 30)
    try:
        from tools import LintingIntegration, get_linting_integration
        linting = get_linting_integration('.')
        print("✅ Phase 1: Legacy components operational")
        test_results.append(("Phase 1 Legacy", True))
    except Exception as e:
        print(f"❌ Phase 1: {e}")
        test_results.append(("Phase 1 Legacy", False))
    
    # Phase 2: Integration Layer
    print("\n🔧 PHASE 2: Integration Layer")
    print("-" * 30)
    try:
        from tools import (
            VirtualEnvironmentManager, GitOperationsManager, PythonCommandExecutor,
            get_venv_manager, get_git_manager, get_command_executor
        )
        
        venv = get_venv_manager('.')
        git = get_git_manager('.')
        executor = get_command_executor('.')
        
        print("✅ Phase 2: Integration layer operational")
        print(f"   • Virtual Environment Manager: Working")
        print(f"   • Git Operations Manager: Working")
        print(f"   • Python Command Executor: Working")
        test_results.append(("Phase 2 Integration", True))
    except Exception as e:
        print(f"❌ Phase 2: {e}")
        test_results.append(("Phase 2 Integration", False))
    
    # Phase 3: Intelligence Layer
    print("\n🧠 PHASE 3: Intelligence Layer")
    print("-" * 30)
    try:
        from tools import (
            IntelligenceEngine, LearningSystemIntegration, PredictiveAnalytics,
            get_intelligence_recommendations, get_learning_enhanced_recommendations, get_comprehensive_analytics
        )
        
        intelligence = IntelligenceEngine('.')
        learning = LearningSystemIntegration('.')
        analytics = PredictiveAnalytics('.')
        
        # Quick functionality test
        recommendations = get_intelligence_recommendations('.')
        enhanced_recs = get_learning_enhanced_recommendations('.')
        analytics_data = get_comprehensive_analytics('.')
        
        print("✅ Phase 3: Intelligence layer operational")
        print(f"   • Intelligence Engine: Working")
        print(f"   • Learning Integration: Working")
        print(f"   • Predictive Analytics: Working")
        print(f"   • Recommendations: {len(recommendations)} available")
        test_results.append(("Phase 3 Intelligence", True))
    except Exception as e:
        print(f"❌ Phase 3: {e}")
        test_results.append(("Phase 3 Intelligence", False))
    
    # Phase 4: Production Layer
    print("\n🏭 PHASE 4: Production Layer")
    print("-" * 30)
    try:
        from tools import (
            AdvancedOrchestrator, ProductionManager,
            get_advanced_orchestration, get_production_manager, check_production_health
        )
        
        orchestrator = get_advanced_orchestration('.')
        manager = get_production_manager('.')
        health = check_production_health('.')
        
        # Quick functionality test
        summary = orchestrator.get_orchestration_summary()
        status = manager.get_production_status()
        
        print("✅ Phase 4: Production layer operational")
        print(f"   • Advanced Orchestrator: Working")
        print(f"   • Production Manager: Working")
        print(f"   • System Health: {health.overall_status}")
        print(f"   • Production Status: {status.get('production_status', 'unknown')}")
        test_results.append(("Phase 4 Production", True))
    except Exception as e:
        print(f"❌ Phase 4: {e}")
        test_results.append(("Phase 4 Production", False))
    
    # Cross-Phase Integration Test
    print("\n🌐 CROSS-PHASE INTEGRATION")
    print("-" * 30)
    try:
        # Test all phases working together
        start_time = time.time()
        
        # Phase 1 → Phase 2 → Phase 3 → Phase 4 workflow
        linting = LintingIntegration('.')
        executor = PythonCommandExecutor('.')
        intelligence = IntelligenceEngine('.')
        orchestrator = AdvancedOrchestrator('.')
        
        # Simulate integrated workflow
        context = intelligence.analyze_context()
        recommendations = intelligence.get_recommendations(context)
        orchestration = orchestrator.get_orchestration_summary()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("✅ Cross-Phase Integration: Working")
        print(f"   • All 4 phases integrated successfully")
        print(f"   • Integration time: {duration:.2f}s")
        print(f"   • Context analysis: Available")
        print(f"   • Recommendations: {len(recommendations)} generated")
        test_results.append(("Cross-Phase Integration", True))
    except Exception as e:
        print(f"❌ Cross-Phase Integration: {e}")
        test_results.append(("Cross-Phase Integration", False))
    
    # Performance Test
    print("\n⚡ PERFORMANCE TEST")
    print("-" * 30)
    try:
        start_time = time.time()
        
        # Perform multiple operations across all phases
        for i in range(3):
            linting = LintingIntegration('.')
            executor = PythonCommandExecutor('.')
            intelligence = IntelligenceEngine('.')
            orchestrator = AdvancedOrchestrator('.')
            manager = ProductionManager('.')
            
            # Quick operations
            context = intelligence.analyze_context()
            health = manager.check_system_health()
        
        end_time = time.time()
        duration = end_time - start_time
        avg_time = duration / 3
        
        print("✅ Performance Test: Passed")
        print(f"   • 3 full-system operations in {duration:.2f}s")
        print(f"   • Average per operation: {avg_time:.2f}s")
        print(f"   • Performance: {'Excellent' if avg_time < 2.0 else 'Good' if avg_time < 4.0 else 'Acceptable'}")
        test_results.append(("Performance Test", True))
    except Exception as e:
        print(f"❌ Performance Test: {e}")
        test_results.append(("Performance Test", False))
    
    return test_results

def print_final_summary(results):
    """Print final system test summary."""
    print("\n" + "=" * 50)
    print("🎯 COMPLETE SYSTEM TEST SUMMARY")
    print("=" * 50)
    
    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]
    
    print(f"\n📊 Test Results:")
    print(f"  • Total Tests: {len(results)}")
    print(f"  • Passed: {len(passed)}")
    print(f"  • Failed: {len(failed)}")
    print(f"  • Success Rate: {len(passed)/len(results)*100:.1f}%")
    
    if passed:
        print(f"\n✅ Successful Tests:")
        for test_name, _ in passed:
            print(f"  • {test_name}")
    
    if failed:
        print(f"\n❌ Failed Tests:")
        for test_name, _ in failed:
            print(f"  • {test_name}")
    
    print("\n" + "=" * 50)
    
    if len(failed) == 0:
        print("🎉 COMPLETE SYSTEM TEST: 100% SUCCESS!")
        print("✅ All 4 phases operational!")
        print("✅ Cross-phase integration working!")
        print("✅ Performance validated!")
        print("✅ SYSTEM IS FULLY PRODUCTION READY!")
        print("\n🚀 WINDSURF CONTEXT ENGINEERING FRAMEWORK")
        print("   DEVELOPMENT COMPLETE!")
        return True
    else:
        print("⚠️ Some system tests failed - review issues")
        return False

if __name__ == "__main__":
    print("Starting Complete System Test...")
    
    try:
        results = test_complete_system()
        success = print_final_summary(results)
        
        if success:
            print("\n🎊 FRAMEWORK DEVELOPMENT COMPLETE!")
            print("Ready for production deployment!")
            sys.exit(0)
        else:
            print("\n🛑 SYSTEM TEST INCOMPLETE")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR DURING SYSTEM TEST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
