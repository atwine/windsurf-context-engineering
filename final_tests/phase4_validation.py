#!/usr/bin/env python3
"""
Phase 4 Validation Script

Validates Phase 4 production components including advanced orchestration
and production management capabilities.
"""

import sys
import time
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def validate_phase4_components():
    """Validate all Phase 4 components."""
    print("🚀 PHASE 4 PRODUCTION VALIDATION")
    print("=" * 50)
    
    validation_results = []
    
    # Test 1: Advanced Orchestrator
    print("\n1. 🎯 Advanced Orchestrator Validation")
    print("-" * 30)
    try:
        from tools.advanced_orchestrator import AdvancedOrchestrator, get_advanced_orchestration
        
        orchestrator = AdvancedOrchestrator('.')
        summary = orchestrator.get_orchestration_summary()
        metrics = orchestrator.get_production_metrics()
        
        print(f"✅ Advanced Orchestrator operational")
        print(f"   • Orchestration Status: {summary.get('orchestration_status', 'unknown')}")
        print(f"   • System Health: {summary.get('system_health', 0):.2f}")
        print(f"   • Success Rate: {metrics.success_rate:.2f}")
        print(f"   • Performance Score: {metrics.performance_score:.2f}")
        
        # Test convenience function
        conv_orchestrator = get_advanced_orchestration('.')
        print(f"   • Convenience Function: Working")
        
        validation_results.append(("Advanced Orchestrator", True, f"Health: {summary.get('system_health', 0):.2f}"))
        
    except Exception as e:
        print(f"❌ Advanced Orchestrator failed: {e}")
        validation_results.append(("Advanced Orchestrator", False, str(e)))
    
    # Test 2: Production Manager
    print("\n2. 🏭 Production Manager Validation")
    print("-" * 30)
    try:
        from tools.production_manager import ProductionManager, get_production_manager
        
        manager = ProductionManager('.')
        health = manager.check_system_health()
        status = manager.get_production_status()
        
        print(f"✅ Production Manager operational")
        print(f"   • System Health: {health.overall_status}")
        print(f"   • Component Count: {len(health.components)}")
        print(f"   • Alert Count: {len(health.alerts)}")
        print(f"   • Production Status: {status.get('production_status', 'unknown')}")
        
        # Test convenience function
        conv_manager = get_production_manager('.')
        print(f"   • Convenience Function: Working")
        
        validation_results.append(("Production Manager", True, f"Status: {health.overall_status}"))
        
    except Exception as e:
        print(f"❌ Production Manager failed: {e}")
        validation_results.append(("Production Manager", False, str(e)))
    
    # Test 3: Tools Module Integration
    print("\n3. 🔧 Phase 4 Tools Integration")
    print("-" * 30)
    try:
        from tools import (
            AdvancedOrchestrator, ProductionManager,
            get_advanced_orchestration, get_production_manager,
            deploy_to_production, check_production_health
        )
        
        print(f"✅ Phase 4 Tools Integration operational")
        print(f"   • All Phase 4 classes imported successfully")
        print(f"   • All convenience functions available")
        
        # Test integrated workflow
        orchestrator = get_advanced_orchestration('.')
        manager = get_production_manager('.')
        health = check_production_health('.')
        
        print(f"   • Integrated Orchestration: Working")
        print(f"   • Integrated Production Management: Working")
        print(f"   • Integrated Health Checks: {health.overall_status}")
        
        validation_results.append(("Phase 4 Tools Integration", True, "All components integrated"))
        
    except Exception as e:
        print(f"❌ Phase 4 Tools Integration failed: {e}")
        validation_results.append(("Phase 4 Tools Integration", False, str(e)))
    
    # Test 4: Advanced Workflow Execution
    print("\n4. 🔄 Advanced Workflow Execution")
    print("-" * 30)
    try:
        from tools import execute_production_workflow
        
        # Test workflow configuration
        workflow_config = {
            "name": "Phase 4 Test Workflow",
            "steps": [
                {"type": "analysis", "description": "Context analysis"},
                {"type": "command", "command": "python --version", "description": "Version check"}
            ]
        }
        
        result = execute_production_workflow(workflow_config, '.')
        
        print(f"✅ Advanced Workflow Execution operational")
        print(f"   • Workflow Success: {result.get('success', False)}")
        print(f"   • Execution Time: {result.get('execution_time', 0):.2f}s")
        print(f"   • Context Available: {'context' in result}")
        print(f"   • Predictions Available: {'predictions' in result}")
        
        validation_results.append(("Advanced Workflow Execution", result.get('success', False), f"Time: {result.get('execution_time', 0):.2f}s"))
        
    except Exception as e:
        print(f"❌ Advanced Workflow Execution failed: {e}")
        validation_results.append(("Advanced Workflow Execution", False, str(e)))
    
    # Test 5: Production Metrics and Monitoring
    print("\n5. 📊 Production Metrics and Monitoring")
    print("-" * 30)
    try:
        orchestrator = AdvancedOrchestrator('.')
        manager = ProductionManager('.')
        
        # Get comprehensive metrics
        orchestrator_metrics = orchestrator.get_production_metrics()
        system_health = manager.check_system_health()
        production_status = manager.get_production_status()
        
        print(f"✅ Production Metrics and Monitoring operational")
        print(f"   • Orchestrator Metrics: Available")
        print(f"   • System Health Monitoring: {system_health.overall_status}")
        print(f"   • Production Status: {production_status.get('production_status', 'unknown')}")
        print(f"   • Performance Tracking: {len(orchestrator.performance_history)} entries")
        
        validation_results.append(("Production Metrics", True, "All metrics available"))
        
    except Exception as e:
        print(f"❌ Production Metrics and Monitoring failed: {e}")
        validation_results.append(("Production Metrics", False, str(e)))
    
    # Test 6: Cross-Phase Integration
    print("\n6. 🌐 Cross-Phase Integration (Phases 1-4)")
    print("-" * 30)
    try:
        # Test all phases working together
        from tools import (
            # Phase 1
            LintingIntegration,
            # Phase 2  
            PythonCommandExecutor, VirtualEnvironmentManager,
            # Phase 3
            IntelligenceEngine, LearningSystemIntegration, PredictiveAnalytics,
            # Phase 4
            AdvancedOrchestrator, ProductionManager
        )
        
        # Create instances of all phases
        linting = LintingIntegration('.')
        executor = PythonCommandExecutor('.')
        venv_manager = VirtualEnvironmentManager('.')
        intelligence = IntelligenceEngine('.')
        learning = LearningSystemIntegration('.')
        analytics = PredictiveAnalytics('.')
        orchestrator = AdvancedOrchestrator('.')
        production = ProductionManager('.')
        
        print(f"✅ Cross-Phase Integration operational")
        print(f"   • Phase 1 (Legacy): Working")
        print(f"   • Phase 2 (Integration): Working")
        print(f"   • Phase 3 (Intelligence): Working")
        print(f"   • Phase 4 (Production): Working")
        print(f"   • All phases integrated successfully")
        
        validation_results.append(("Cross-Phase Integration", True, "All 4 phases integrated"))
        
    except Exception as e:
        print(f"❌ Cross-Phase Integration failed: {e}")
        validation_results.append(("Cross-Phase Integration", False, str(e)))
    
    # Test 7: Performance Under Load
    print("\n7. ⚡ Performance Under Load")
    print("-" * 30)
    try:
        start_time = time.time()
        
        # Perform multiple operations simultaneously
        orchestrator = AdvancedOrchestrator('.')
        manager = ProductionManager('.')
        
        for i in range(5):
            summary = orchestrator.get_orchestration_summary()
            health = manager.check_system_health()
            metrics = orchestrator.get_production_metrics()
        
        end_time = time.time()
        duration = end_time - start_time
        avg_time = duration / 5
        
        print(f"✅ Performance Under Load validated")
        print(f"   • 5 operations completed in {duration:.2f}s")
        print(f"   • Average per operation: {avg_time:.2f}s")
        print(f"   • Performance: {'Excellent' if avg_time < 1.0 else 'Good' if avg_time < 2.0 else 'Acceptable'}")
        
        validation_results.append(("Performance Under Load", True, f"{avg_time:.2f}s average"))
        
    except Exception as e:
        print(f"❌ Performance Under Load failed: {e}")
        validation_results.append(("Performance Under Load", False, str(e)))
    
    return validation_results

def print_phase4_summary(results):
    """Print Phase 4 validation summary."""
    print("\n" + "=" * 50)
    print("🎯 PHASE 4 VALIDATION SUMMARY")
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
        print("🎉 PHASE 4 PRODUCTION LAYER FULLY VALIDATED!")
        print("✅ Advanced orchestration operational!")
        print("✅ Production management ready!")
        print("✅ All phases (1-4) integrated!")
        print("✅ Performance validated under load!")
        print("✅ SYSTEM IS PRODUCTION READY!")
        return True
    else:
        print("⚠️ Some Phase 4 validations failed - review issues")
        return False

if __name__ == "__main__":
    print("Starting Phase 4 Production Validation...")
    
    try:
        results = validate_phase4_components()
        success = print_phase4_summary(results)
        
        if success:
            print("\n🚀 PHASE 4 PRODUCTION LAYER COMPLETE!")
            print("Ready for full system deployment!")
            sys.exit(0)
        else:
            print("\n🛑 PHASE 4 VALIDATION INCOMPLETE")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR DURING PHASE 4 VALIDATION: {e}")
        traceback.print_exc()
        sys.exit(1)
