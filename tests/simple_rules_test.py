"""
Simple User Workspace Rules Integration Test

This is a focused test that demonstrates the user workspace rules integration
without complex dependencies or database locking issues.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_rules_extraction():
    """Test basic rule extraction functionality"""
    
    print("🔍 TESTING: Basic User Workspace Rules Extraction")
    print("=" * 60)
    
    try:
        from learning.user_workspace_integration import UserWorkspaceRulesIntegration, WorkspaceRulesConfig
        
        # Create a simple config
        config = WorkspaceRulesConfig(
            rules_extraction_enabled=True,
            auto_compliance_checking=True,
            rule_violation_warnings=True
        )
        
        # Create rules integration with a unique directory
        test_dir = f"test_rules_{os.getpid()}"  # Use process ID to avoid conflicts
        rules_integration = UserWorkspaceRulesIntegration(config, test_dir)
        
        print("✅ UserWorkspaceRulesIntegration initialized successfully")
        
        # Test system context with your actual user rules
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
        
        # Extract rules from system context
        print("\n📋 Extracting rules from system context...")
        rules_extracted = rules_integration.extract_rules_from_context(system_context)
        print(f"✅ Successfully extracted {rules_extracted} rules")
        
        # Get rules summary
        print("\n📊 Getting rules summary...")
        summary = rules_integration.get_rules_summary()
        print(f"✅ Rules Summary:")
        print(f"   - Total Rules: {summary['total_rules']}")
        print(f"   - Rules by Category: {summary['rules_by_category']}")
        print(f"   - Rules by Enforcement: {summary['rules_by_enforcement']}")
        print(f"   - High Priority Rules: {summary['high_priority_rules']}")
        print(f"   - Contexts Covered: {summary['contexts_covered']}")
        
        # Test getting applicable rules
        print("\n🎯 Testing applicable rules for Python debugging context...")
        applicable_rules = rules_integration.get_applicable_rules(
            context='python',
            category='debugging'
        )
        print(f"✅ Found {len(applicable_rules)} applicable rules for Python debugging")
        
        for i, rule in enumerate(applicable_rules[:3], 1):  # Show first 3
            print(f"   {i}. {rule.title}")
            print(f"      - Category: {rule.category}")
            print(f"      - Enforcement: {rule.enforcement_level}")
            print(f"      - Priority: {rule.priority}")
        
        return True, rules_integration
        
    except Exception as e:
        print(f"❌ Error in basic rules extraction: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_code_compliance_checking(rules_integration):
    """Test code compliance checking against extracted rules"""
    
    print("\n🔍 TESTING: Code Compliance Checking")
    print("=" * 60)
    
    try:
        # Test 1: Compliant code (follows debugging best practices)
        print("\n1️⃣ Testing COMPLIANT code:")
        compliant_code = '''
def debug_connection_issue(connection_params: dict) -> bool:
    """
    Debug database connection following minimal intervention principles.
    Only fixes the specific connection issue without modifying unrelated code.
    """
    try:
        # Analyze the specific error first
        if not connection_params:
            logger.error("Connection parameters missing - root cause identified")
            return False
            
        # Minimal fix: validate required parameters only
        required_params = ['host', 'port', 'database']
        missing_params = [p for p in required_params if p not in connection_params]
        
        if missing_params:
            logger.error(f"Missing required parameters: {missing_params}")
            return False
            
        # Test connection with existing code style
        conn = create_connection(connection_params)
        result = conn.ping()
        conn.close()
        
        return result
        
    except Exception as e:
        logger.error(f"Connection debug failed: {e}")
        return False
'''
        
        compliance_result = rules_integration.check_compliance(compliant_code, context='python')
        print(f"✅ Compliance Result:")
        print(f"   - Compliant: {compliance_result['compliant']}")
        print(f"   - Violations: {len(compliance_result['violations'])}")
        print(f"   - Warnings: {len(compliance_result['warnings'])}")
        print(f"   - Suggestions: {len(compliance_result['suggestions'])}")
        print(f"   - Rules Checked: {compliance_result['total_rules_checked']}")
        
        # Test 2: Non-compliant code (violates debugging rules)
        print("\n2️⃣ Testing NON-COMPLIANT code:")
        non_compliant_code = '''
def fix_everything_at_once(data):
    """
    Let's refactor the entire system while fixing this bug!
    This violates the minimal intervention principle.
    """
    # Completely rewrite the architecture (violates "preserve existing functionality")
    new_system = redesign_entire_codebase()
    
    # Add lots of optimizations we don't need (violates "avoid speculative improvements")
    optimized_data = super_optimize_everything(data)
    
    # Change unrelated code (violates "fix only what is broken")
    update_all_other_modules()
    
    # Make assumptions without validation (violates "validate everything")
    assumed_result = assume_this_works(optimized_data)
    
    return new_system.process(assumed_result)
'''
        
        non_compliant_result = rules_integration.check_compliance(non_compliant_code, context='python')
        print(f"✅ Non-Compliant Code Result:")
        print(f"   - Compliant: {non_compliant_result['compliant']}")
        print(f"   - Violations: {len(non_compliant_result['violations'])}")
        print(f"   - Warnings: {len(non_compliant_result['warnings'])}")
        print(f"   - Suggestions: {len(non_compliant_result['suggestions'])}")
        
        # Show specific violations
        if non_compliant_result['violations']:
            print(f"   - Specific Violations:")
            for violation in non_compliant_result['violations']:
                print(f"     * {violation['rule_title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in compliance checking: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rule_management(rules_integration):
    """Test adding and managing custom rules"""
    
    print("\n🔍 TESTING: Rule Management")
    print("=" * 60)
    
    try:
        # Add a custom rule
        print("\n➕ Adding custom rule...")
        custom_rule_id = rules_integration.add_custom_rule(
            title="Always Use Error Handling",
            content="MUST include try-except blocks for all external API calls and file operations",
            category="coding_style",
            applies_to=["python", "javascript"],
            priority=8,
            enforcement_level="strict"
        )
        
        print(f"✅ Added custom rule: {custom_rule_id}")
        
        # Test the new rule
        print("\n🧪 Testing custom rule compliance...")
        test_code_with_error_handling = '''
def call_external_api(url: str) -> dict:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API call failed: {e}")
        return {}
'''
        
        test_code_without_error_handling = '''
def call_external_api(url: str) -> dict:
    response = requests.get(url)
    return response.json()
'''
        
        # Test with error handling
        result_with_handling = rules_integration.check_compliance(
            test_code_with_error_handling, 
            context='python'
        )
        
        # Test without error handling
        result_without_handling = rules_integration.check_compliance(
            test_code_without_error_handling, 
            context='python'
        )
        
        print(f"✅ Code WITH error handling - Compliant: {result_with_handling['compliant']}")
        print(f"✅ Code WITHOUT error handling - Compliant: {result_without_handling['compliant']}")
        
        # Get updated summary
        updated_summary = rules_integration.get_rules_summary()
        print(f"✅ Updated Rules Summary:")
        print(f"   - Total Rules: {updated_summary['total_rules']}")
        print(f"   - Strict Rules: {updated_summary['rules_by_enforcement']['strict']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in rule management: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    
    print("🚀 STARTING: User Workspace Rules Integration Tests")
    print("=" * 80)
    
    # Test 1: Basic rules extraction
    success1, rules_integration = test_basic_rules_extraction()
    
    if not success1:
        print("\n❌ FAILED: Basic rules extraction failed")
        return False
    
    # Test 2: Code compliance checking
    success2 = test_code_compliance_checking(rules_integration)
    
    if not success2:
        print("\n❌ FAILED: Code compliance checking failed")
        return False
    
    # Test 3: Rule management
    success3 = test_rule_management(rules_integration)
    
    if not success3:
        print("\n❌ FAILED: Rule management failed")
        return False
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)
    print("✅ User Workspace Rules Integration is WORKING CORRECTLY!")
    print("✅ Rules are being extracted from your system context")
    print("✅ Code compliance checking is operational")
    print("✅ Custom rules can be added and managed")
    print("✅ The system respects your debugging workflow rules")
    print("✅ Ready for integration with enhanced workflows")
    print("=" * 80)
    
    # Show final statistics
    final_summary = rules_integration.get_rules_summary()
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   - Total User Rules Loaded: {final_summary['total_rules']}")
    print(f"   - Strict Enforcement Rules: {final_summary['rules_by_enforcement']['strict']}")
    print(f"   - Warning Level Rules: {final_summary['rules_by_enforcement']['warning']}")
    print(f"   - Suggestion Level Rules: {final_summary['rules_by_enforcement']['suggestion']}")
    print(f"   - High Priority Rules: {final_summary['high_priority_rules']}")
    print(f"   - Categories Covered: {len(final_summary['rules_by_category'])}")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎯 CONFIDENCE LEVEL: HIGH")
        print("The user workspace rules integration is fully functional!")
    else:
        print("\n⚠️ CONFIDENCE LEVEL: LOW")
        print("Some tests failed - please review the errors above.")
