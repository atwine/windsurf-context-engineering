#!/usr/bin/env python3
"""
Simple Phase 4 Test

Quick validation of Phase 4 core components.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_phase4_simple():
    """Simple Phase 4 component test."""
    print("🚀 PHASE 4 SIMPLE TEST")
    print("=" * 30)
    
    # Test 1: Advanced Orchestrator Import
    print("\n1. Testing Advanced Orchestrator...")
    try:
        from tools.advanced_orchestrator import AdvancedOrchestrator, get_advanced_orchestration
        orchestrator = AdvancedOrchestrator('.')
        print("✅ Advanced Orchestrator: Working")
    except Exception as e:
        print(f"❌ Advanced Orchestrator: {e}")
        return False
    
    # Test 2: Production Manager Import
    print("\n2. Testing Production Manager...")
    try:
        from tools.production_manager import ProductionManager, get_production_manager
        manager = ProductionManager('.')
        print("✅ Production Manager: Working")
    except Exception as e:
        print(f"❌ Production Manager: {e}")
        return False
    
    # Test 3: Tools Module Integration
    print("\n3. Testing Tools Integration...")
    try:
        from tools import (
            AdvancedOrchestrator, ProductionManager,
            get_advanced_orchestration, get_production_manager
        )
        print("✅ Tools Integration: Working")
    except Exception as e:
        print(f"❌ Tools Integration: {e}")
        return False
    
    # Test 4: Basic Functionality
    print("\n4. Testing Basic Functionality...")
    try:
        orchestrator = get_advanced_orchestration('.')
        manager = get_production_manager('.')
        
        # Quick operations
        summary = orchestrator.get_orchestration_summary()
        health = manager.check_system_health()
        
        print(f"✅ Basic Functionality: Working")
        print(f"   • Orchestration Status: {summary.get('orchestration_status', 'unknown')}")
        print(f"   • System Health: {health.overall_status}")
    except Exception as e:
        print(f"❌ Basic Functionality: {e}")
        return False
    
    print("\n" + "=" * 30)
    print("🎉 PHASE 4 SIMPLE TEST: ALL PASSED!")
    print("✅ Advanced Orchestrator operational")
    print("✅ Production Manager operational")
    print("✅ Tools integration working")
    print("✅ Basic functionality validated")
    return True

if __name__ == "__main__":
    success = test_phase4_simple()
    sys.exit(0 if success else 1)
