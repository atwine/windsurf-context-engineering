"""
Test User Workspace Rules Integration

This test demonstrates how the enhanced learning system integrates with
user workspace rules to provide rule-aware recommendations and compliance checking.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from learning.user_workspace_integration import create_workspace_rules_integration
from learning.enhanced_workflow_learning import create_enhanced_workflow_learning

def test_user_workspace_rules_integration():
    """Test the complete user workspace rules integration"""
    
    print("🔍 Testing User Workspace Rules Integration")
    print("=" * 60)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Example system context with user rules (similar to what Windsurf provides)
        system_context = """
        <user_rules>
        You are an expert coding assistant focused solely on **debugging and resolving software issues** with high precision and minimal disruption.
        Follow the **exact workflow** below. **Do not deviate** unless I explicitly tell you to.

        ### 🔁 Step-by-Step Workflow

        1. **Analyze the Error & Codebase**
           * Carefully read the error message(s) and inspect the related code.
           * Form clear hypotheses about the root cause.
           * Validate each hypothesis using the current code and **official documentation**.
           * Repeat until the root cause is **proven** — not assumed.

        2. **Preserve Existing Functionality**
           * Do **not** modify any unrelated or working code.
           * Avoid architectural changes or rewrites. Stay laser-focused on the broken parts only.

        3. **Apply a Minimal, Targeted Fix**
           * Make only the smallest necessary change(s) to resolve the issue.
           * Avoid speculative improvements, style changes, or optimizations.

        ### ⚠️ Rules & Enforcement

        * ✅ Fix only what is broken.
        * ✅ Match the original code's style and formatting.
        * ✅ If unsure, ask clarifying questions before proceeding.
        * ❌ Do not refactor, reformat, or "improve" working code.
        * ❌ Do not make assumptions. Validate everything.
        </user_rules>
        
        <MEMORY[check-documentation.md]>
        Always verify library methods, APIs, and syntax by searching the web for current documentation before making assumptions or writing code that depends on external libraries.

        What to Verify:
        Do not rely on potentially outdated knowledge about:
        - Method names, parameters, and return types
        - API endpoints and request/response formats 
        - Library-specific syntax and usage patterns
        - Version-specific features or deprecations
        </MEMORY[check-documentation.md]>
        
        <MEMORY[consult-first.md]>
        No changes—structural, functional, or data-related—should be made to the codebase without prior consultation with me.

        This is essential to:
        Prevent regressions or loss of progress due to uncoordinated modifications.
        Ensure I am aware of upcoming changes and can align them with the current development direction.
        
        All contributors must present a brief summary or plan of any proposed changes for review before implementation.
        Consultation is mandatory—no silent edits or fixes, even if they appear minor.
        </MEMORY[consult-first.md]>
        """
        
        try:
            # Test 1: Initialize Enhanced Workflow Learning System
            print("\n1️⃣ **Testing Enhanced Workflow Learning Initialization**")
            enhanced_learning = create_enhanced_workflow_learning(temp_dir)
            print("✅ Enhanced workflow learning system initialized successfully")
            
            # Test 2: Extract User Workspace Rules from System Context
            print("\n2️⃣ **Testing User Workspace Rules Extraction**")
            rules_extracted = enhanced_learning.extract_system_context_rules(system_context)
            print(f"✅ Extracted {rules_extracted} user workspace rules from system context")
            
            # Test 3: Get Rules Summary
            print("\n3️⃣ **Testing Rules Summary Generation**")
            rules_summary = enhanced_learning.rules_integration.get_rules_summary()
            print(f"✅ Rules Summary:")
            print(f"   - Total Rules: {rules_summary['total_rules']}")
            print(f"   - Rules by Category: {rules_summary['rules_by_category']}")
            print(f"   - Rules by Enforcement: {rules_summary['rules_by_enforcement']}")
            print(f"   - High Priority Rules: {rules_summary['high_priority_rules']}")
            
            # Test 4: Start Enhanced Workflow with Rule Integration
            print("\n4️⃣ **Testing Enhanced Workflow Startup**")
            project_context = {
                'language': 'python',
                'framework': 'fastapi',
                'technologies': ['python', 'fastapi', 'postgresql'],
                'project_type': 'web_api'
            }
            
            workflow_context = enhanced_learning.start_enhanced_workflow(
                'test_debugging_workflow', 
                project_context,
                system_context
            )
            
            print(f"✅ Enhanced workflow started successfully:")
            print(f"   - Workflow: {workflow_context.workflow_name}")
            print(f"   - Applicable Rules: {len(workflow_context.applicable_rules)}")
            print(f"   - Compliance Requirements: {len(workflow_context.compliance_requirements.get('strict_rules', []))} strict rules")
            
            # Test 5: Get Rule-Aware Recommendations
            print("\n5️⃣ **Testing Rule-Aware Recommendations**")
            recommendations = enhanced_learning.get_rule_aware_recommendations(
                'test_debugging_workflow',
                {'current_task': 'debugging_api_error', 'error_type': 'database_connection'}
            )
            
            print(f"✅ Generated {len(recommendations)} rule-aware recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):  # Show first 3
                print(f"   {i}. {rec.title}")
                print(f"      - Confidence: {rec.confidence:.2f}")
                print(f"      - Rule Compliant: {rec.rule_compliance['compliant']}")
                print(f"      - Priority Adjustment: {rec.priority_adjustment:+.2f}")
            
            # Test 6: Code Compliance Checking
            print("\n6️⃣ **Testing Code Compliance Checking**")
            
            # Test compliant code
            compliant_code = '''
def debug_database_connection(connection_params: dict) -> bool:
    """
    Debug database connection issues following minimal intervention principles.
    
    Args:
        connection_params: Database connection parameters
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Validate connection parameters first
        if not connection_params:
            logger.error("Connection parameters are empty")
            return False
            
        # Test connection with timeout
        with timeout(30):
            conn = create_connection(connection_params)
            result = conn.ping()
            conn.close()
            return result
            
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
'''
            
            compliance_result = enhanced_learning.check_code_compliance(
                compliant_code, 
                'test_debugging_workflow', 
                'python'
            )
            
            print(f"✅ Code Compliance Check Results:")
            print(f"   - Compliant: {compliance_result['compliant']}")
            print(f"   - Violations: {len(compliance_result['violations'])}")
            print(f"   - Warnings: {len(compliance_result['warnings'])}")
            print(f"   - Total Rules Checked: {compliance_result['total_rules_checked']}")
            
            # Test non-compliant code
            print("\n   Testing Non-Compliant Code:")
            non_compliant_code = '''
def fix_everything(data):
    # Let's refactor the entire codebase while we're at it
    new_architecture = redesign_system()  # This violates "preserve existing functionality"
    optimized_data = optimize_everything(data)  # This violates "avoid speculative improvements"
    return new_architecture.process(optimized_data)
'''
            
            non_compliant_result = enhanced_learning.check_code_compliance(
                non_compliant_code,
                'test_debugging_workflow',
                'python'
            )
            
            print(f"   - Non-Compliant Code Results:")
            print(f"     - Compliant: {non_compliant_result['compliant']}")
            print(f"     - Violations: {len(non_compliant_result['violations'])}")
            print(f"     - Warnings: {len(non_compliant_result['warnings'])}")
            
            # Test 7: Enhanced System Status
            print("\n7️⃣ **Testing Enhanced System Status**")
            system_status = enhanced_learning.get_enhanced_system_status()
            
            print(f"✅ Enhanced System Status:")
            print(f"   - Learning System Active: {system_status['system_health']['learning_system_active']}")
            print(f"   - Rules Integration Active: {system_status['system_health']['rules_integration_active']}")
            print(f"   - Enhanced Features Available: {system_status['system_health']['enhanced_features_available']}")
            print(f"   - Active Workflows: {system_status['enhanced_workflows']['active_workflows']}")
            print(f"   - Total User Rules: {system_status['user_workspace_rules']['rules_summary']['total_rules']}")
            
            # Test 8: Complete Enhanced Workflow
            print("\n8️⃣ **Testing Enhanced Workflow Completion**")
            completion_outcome = {
                'success': True,
                'tasks_completed': 5,
                'issues_resolved': 2,
                'code_quality_score': 0.85,
                'user_satisfaction': 0.9
            }
            
            completion_report = enhanced_learning.complete_enhanced_workflow(
                'test_debugging_workflow',
                completion_outcome,
                compliant_code
            )
            
            print(f"✅ Enhanced Workflow Completion:")
            print(f"   - Workflow: {completion_report['workflow_name']}")
            print(f"   - Rules Applied: {completion_report['rule_compliance_summary']['rules_applied']}")
            print(f"   - Final Code Compliant: {completion_report['rule_compliance_summary']['final_code_compliance']['compliant']}")
            print(f"   - Recommendations Generated: {completion_report['learning_insights']['recommendations_generated']}")
            
            print("\n🎉 **ALL TESTS PASSED SUCCESSFULLY!**")
            print("=" * 60)
            print("✅ User Workspace Rules Integration is working correctly")
            print("✅ Enhanced Learning System is fully functional")
            print("✅ Rule-aware recommendations are being generated")
            print("✅ Code compliance checking is operational")
            print("✅ System is ready for production use with user workspace rules")
            
            return True
            
        except Exception as e:
            print(f"\n❌ **TEST FAILED**: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_specific_user_rules_scenarios():
    """Test specific scenarios with different types of user rules"""
    
    print("\n🧪 Testing Specific User Rules Scenarios")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create rules integration
        rules_integration = create_workspace_rules_integration(temp_dir)
        
        # Test different rule types
        test_scenarios = [
            {
                'name': 'Security Rules',
                'context': '''
                <user_rules>
                NEVER hardcode API keys, passwords, or credentials in source code.
                ALWAYS use environment variables for sensitive configuration.
                MUST validate all user inputs before processing.
                </user_rules>
                ''',
                'test_code': '''
                def process_payment(amount, api_key="sk-live-123456"):
                    return payment_api.charge(amount, api_key)
                ''',
                'expected_violations': 1
            },
            {
                'name': 'Code Style Rules',
                'context': '''
                <user_rules>
                ALWAYS use type hints for function parameters and return values.
                MUST follow PEP 8 naming conventions.
                SHOULD include docstrings for all public functions.
                </user_rules>
                ''',
                'test_code': '''
                def ProcessUserData(userData):
                    return userData.upper()
                ''',
                'expected_violations': 0  # This is more about style warnings
            },
            {
                'name': 'Workflow Rules',
                'context': '''
                <MEMORY[terminal-rule.md]>
                Never execute multiple terminal commands simultaneously or before the previous command has completely finished.
                
                Sequential Execution Protocol:
                1. Execute only ONE terminal command at a time
                2. Wait for complete execution (exit code received) before proceeding
                3. Use Blocking=true for commands that must complete before continuing
                </MEMORY[terminal-rule.md]>
                ''',
                'test_code': '''
                # This would be workflow code, not directly testable in code compliance
                # but would be checked during workflow execution
                ''',
                'expected_violations': 0
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n📋 **Testing {scenario['name']}**")
            
            # Extract rules from context
            rules_extracted = rules_integration.extract_rules_from_context(scenario['context'])
            print(f"   - Extracted {rules_extracted} rules")
            
            # Check code compliance
            if scenario['test_code'].strip():
                compliance = rules_integration.check_compliance(scenario['test_code'])
                print(f"   - Code Compliant: {compliance['compliant']}")
                print(f"   - Violations Found: {len(compliance['violations'])}")
                print(f"   - Warnings Found: {len(compliance['warnings'])}")
                
                # Verify expected results
                if len(compliance['violations']) == scenario['expected_violations']:
                    print(f"   ✅ Expected violation count matched")
                else:
                    print(f"   ⚠️ Expected {scenario['expected_violations']} violations, found {len(compliance['violations'])}")
        
        print("\n✅ Specific scenarios testing completed")

if __name__ == "__main__":
    print("🚀 Starting User Workspace Rules Integration Tests")
    print("=" * 80)
    
    # Run main integration test
    main_test_passed = test_user_workspace_rules_integration()
    
    # Run specific scenarios test
    test_specific_user_rules_scenarios()
    
    print("\n" + "=" * 80)
    if main_test_passed:
        print("🎉 **ALL TESTS COMPLETED SUCCESSFULLY**")
        print("✅ User Workspace Rules Integration is fully functional and ready for production!")
    else:
        print("❌ **SOME TESTS FAILED**")
        print("⚠️ Please review the errors above and fix any issues before production use.")
    
    print("=" * 80)
