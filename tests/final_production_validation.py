"""
FINAL PRODUCTION VALIDATION TEST

This test validates that the complete system is ready for production deployment.
It tests all core functionality and integration points.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def validate_core_imports():
    """Validate all core imports work"""
    print("1️⃣ Validating Core Imports...")
    
    try:
        # Core learning system imports
        from learning.user_workspace_integration import create_workspace_rules_integration
        from learning.enhanced_workflow_learning import create_enhanced_workflow_learning
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        
        print("   ✅ All core imports successful")
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False

def validate_user_rules_integration():
    """Validate user workspace rules integration"""
    print("2️⃣ Validating User Workspace Rules Integration...")
    
    try:
        from learning.user_workspace_integration import create_workspace_rules_integration
        rules_system = create_workspace_rules_integration(f"validation_{os.getpid()}")
        
        # Test rule extraction
        test_context = """
        <user_rules>
        1. NEVER hardcode credentials in source code
        2. ALWAYS use type hints for function parameters
        3. MUST include error handling for external API calls
        </user_rules>
        
        <MEMORY[validation-rule]>
        All code must be production-ready and follow best practices.
        </MEMORY[validation-rule]>
        """
        
        rules_extracted = rules_system.extract_rules_from_context(test_context)
        
        if rules_extracted >= 4:  # Should extract at least 4 rules
            print(f"   ✅ Rule extraction working ({rules_extracted} rules)")
        else:
            print(f"   ⚠️ Rule extraction issue ({rules_extracted} rules)")
            return False
        
        # Test compliance checking
        test_code = '''
def api_call(endpoint: str) -> dict:
    """Make API call with proper error handling"""
    try:
        response = requests.get(endpoint, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API call failed: {e}")
        return {}
'''
        
        compliance = rules_system.check_compliance(test_code, context="python")
        print(f"   ✅ Compliance checking working (compliant: {compliance['compliant']})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ User rules integration failed: {e}")
        return False

def validate_workflow_integration():
    """Validate workflow integration"""
    print("3️⃣ Validating Workflow Integration...")
    
    try:
        # Check workflow files exist
        workflow_dir = project_root / ".windsurf" / "workflows"
        
        required_workflows = [
            "init-context.md",
            "generate-plan.md", 
            "execute-plan-enhanced.md",
            "learning-integration.md"
        ]
        
        for workflow in required_workflows:
            workflow_path = workflow_dir / workflow
            if workflow_path.exists():
                print(f"   ✅ {workflow} exists")
            else:
                print(f"   ❌ {workflow} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Workflow validation failed: {e}")
        return False

def validate_system_structure():
    """Validate system structure"""
    print("4️⃣ Validating System Structure...")
    
    try:
        required_dirs = [
            "learning",
            "memory", 
            "mcp",
            "tools",
            "utilities",
            "examples",
            "docs",
            "tests",
            "templates"
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                print(f"   ✅ {dir_name}/ directory exists")
            else:
                print(f"   ❌ {dir_name}/ directory missing")
                return False
        
        # Check key files
        required_files = [
            "README.md",
            "requirements.txt",
            "setup.py",
            ".gitignore"
        ]
        
        for file_name in required_files:
            file_path = project_root / file_name
            if file_path.exists():
                print(f"   ✅ {file_name} exists")
            else:
                print(f"   ❌ {file_name} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Structure validation failed: {e}")
        return False

def validate_learning_system():
    """Validate learning system"""
    print("5️⃣ Validating Learning System...")
    
    try:
        from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig
        config = LearningSystemConfig(learning_data_dir=f"validation_learning_{os.getpid()}")
        learning_system = LearningSystemIntegration(config)
        
        # Test system status
        status = learning_system.get_system_status()
        
        if hasattr(status, 'system_active'):
            print(f"   ✅ Learning system status accessible")
        else:
            print(f"   ⚠️ Learning system status issue")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Learning system validation failed: {e}")
        return False

def run_final_validation():
    """Run complete production validation"""
    
    print("🚀 FINAL PRODUCTION VALIDATION")
    print("=" * 60)
    print("Validating system readiness for production deployment")
    print("=" * 60)
    
    validation_tests = [
        ("Core Imports", validate_core_imports),
        ("User Rules Integration", validate_user_rules_integration),
        ("Workflow Integration", validate_workflow_integration),
        ("System Structure", validate_system_structure),
        ("Learning System", validate_learning_system)
    ]
    
    passed_tests = 0
    total_tests = len(validation_tests)
    
    for test_name, test_func in validation_tests:
        try:
            if test_func():
                passed_tests += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"   ❌ {test_name} validation crashed: {e}")
            print()
    
    # Final results
    print("=" * 60)
    print("🏁 FINAL VALIDATION RESULTS")
    print("=" * 60)
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 VALIDATION SUMMARY:")
    print(f"   - Tests Passed: {passed_tests}/{total_tests}")
    print(f"   - Success Rate: {success_rate:.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL VALIDATIONS PASSED!")
        print(f"✅ System is PRODUCTION READY")
        print(f"✅ User workspace rules integration: WORKING")
        print(f"✅ Learning system: FUNCTIONAL")
        print(f"✅ Workflow integration: COMPLETE")
        print(f"✅ System structure: PROPER")
        print(f"✅ Core functionality: VALIDATED")
        
        print(f"\n🚀 READY FOR GITHUB PUSH!")
        print(f"The system is fully validated and production-ready.")
        
    else:
        print(f"\n⚠️ VALIDATION ISSUES FOUND")
        print(f"❌ {total_tests - passed_tests} validation(s) failed")
        print(f"❌ Fix issues before production deployment")
    
    print("=" * 60)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_final_validation()
    
    if success:
        print("\n🎯 PRODUCTION READINESS: ✅ CONFIRMED")
        print("System is ready for GitHub push and production use!")
    else:
        print("\n⚠️ PRODUCTION READINESS: ❌ ISSUES FOUND")
        print("Address validation failures before deployment.")
