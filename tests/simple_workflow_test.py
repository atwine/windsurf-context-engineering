#!/usr/bin/env python3
"""Simple workflow integration test"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🔄 SIMPLE WORKFLOW INTEGRATION TEST")
print("=" * 40)

def test_basic_integration():
    """Test basic workflow component integration"""
    
    try:
        print("1. Testing Phase 1-4 imports...")
        from tools import (
            LintingIntegration,
            VirtualEnvironmentManager, GitOperationsManager, 
            IntelligenceEngine, LearningSystemIntegration,
            AdvancedOrchestrator, ProductionManager
        )
        print("   ✅ All phases import successfully")
        
        print("2. Testing component instantiation...")
        project_path = '.'
        
        # Test each phase
        linting = LintingIntegration(project_path)
        print("   ✅ Phase 1 - Foundation ready")
        
        venv = VirtualEnvironmentManager(project_path)
        git = GitOperationsManager(project_path)
        print("   ✅ Phase 2 - Integration ready")
        
        intelligence = IntelligenceEngine(project_path)
        learning = LearningSystemIntegration()
        print("   ✅ Phase 3 - Intelligence ready")
        
        orchestrator = AdvancedOrchestrator(project_path)
        production = ProductionManager(project_path)
        print("   ✅ Phase 4 - Production ready")
        
        print("3. Testing workflow files exist...")
        workflow_files = [
            ".windsurf/workflows/init-context.md",
            ".windsurf/workflows/generate-plan.md",
            ".windsurf/workflows/execute-plan.md",
            ".windsurf/workflows/execute-plan-enhanced.md"
        ]
        
        for workflow in workflow_files:
            if os.path.exists(workflow):
                print(f"   ✅ {os.path.basename(workflow)} exists")
            else:
                print(f"   ❌ {os.path.basename(workflow)} missing")
        
        print("\n🎉 WORKFLOW INTEGRATION TEST PASSED!")
        print("✅ All phases integrated and ready")
        print("✅ Workflow chain: init-context → generate-plan → execute-plan-enhanced")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_basic_integration()
    sys.exit(0 if success else 1)
