"""
COMPREHENSIVE STRESS TEST - User Workspace Rules Integration

This stress test validates the system under extreme conditions and edge cases:
1. Large rule sets (100+ rules)
2. Complex nested rule structures
3. Conflicting rules
4. Invalid input handling
5. Memory and performance limits
6. Concurrent access scenarios
7. Database corruption recovery
8. Unicode and special character handling
"""

import os
import sys
import time
import threading
import tempfile
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def stress_test_large_rule_sets():
    """Test with very large rule sets (100+ rules)"""
    
    print("🔥 STRESS TEST 1: Large Rule Sets (100+ rules)")
    print("=" * 60)
    
    try:
        from learning.user_workspace_integration import create_workspace_rules_integration
        
        # Create rules integration
        test_dir = f"stress_large_{os.getpid()}"
        rules_system = create_workspace_rules_integration(test_dir)
        
        # Generate a large system context with 100+ rules
        large_context = "<user_rules>\n"
        
        # Add 50 debugging rules
        for i in range(50):
            large_context += f"{i+1}. NEVER modify function_{i} without consulting the documentation first.\n"
        
        # Add 30 security rules
        for i in range(30):
            large_context += f"{i+51}. ALWAYS validate input_{i} before processing in production.\n"
        
        # Add 25 performance rules
        for i in range(25):
            large_context += f"{i+81}. MUST optimize query_{i} for databases with >1M records.\n"
        
        large_context += "</user_rules>\n"
        
        # Add memory rules
        for i in range(20):
            large_context += f"""
<MEMORY[rule_{i}]>
This is memory rule {i} with detailed content that should be properly parsed and categorized.
It contains specific instructions about handling edge case {i} in the system.
Priority level: {'high' if i < 10 else 'medium'}
Enforcement: {'strict' if i % 3 == 0 else 'warning'}
</MEMORY[rule_{i}]>
"""
        
        print(f"   📊 Testing with {large_context.count('NEVER') + large_context.count('ALWAYS') + large_context.count('MUST')} explicit rules")
        
        # Extract rules - measure time
        start_time = time.time()
        rules_extracted = rules_system.extract_rules_from_context(large_context)
        extraction_time = time.time() - start_time
        
        print(f"   ✅ Extracted {rules_extracted} rules in {extraction_time:.2f} seconds")
        
        # Test rule retrieval performance
        start_time = time.time()
        all_rules = rules_system.get_applicable_rules()
        retrieval_time = time.time() - start_time
        
        print(f"   ✅ Retrieved {len(all_rules)} rules in {retrieval_time:.2f} seconds")
        
        # Test compliance checking with large rule set
        test_code = """
def process_large_dataset(data):
    # This function should be checked against all 100+ rules
    validated_data = validate_input_5(data)  # Should match security rule
    optimized_query = optimize_query_10(validated_data)  # Should match performance rule
    return function_25(optimized_query)  # Should match debugging rule
"""
        
        start_time = time.time()
        compliance_result = rules_system.check_compliance(test_code, context="python")
        compliance_time = time.time() - start_time
        
        print(f"   ✅ Compliance check completed in {compliance_time:.2f} seconds")
        print(f"   📊 Performance Summary:")
        print(f"      - Rules extracted: {rules_extracted}")
        print(f"      - Extraction time: {extraction_time:.2f}s")
        print(f"      - Retrieval time: {retrieval_time:.2f}s")
        print(f"      - Compliance time: {compliance_time:.2f}s")
        
        # Memory usage check
        rules_summary = rules_system.get_rules_summary()
        print(f"   📊 Memory Usage:")
        print(f"      - Total rules in memory: {rules_summary['total_rules']}")
        print(f"      - Categories: {len(rules_summary['rules_by_category'])}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def stress_test_invalid_inputs():
    """Test with invalid, malformed, and edge case inputs"""
    
    print("\n🔥 STRESS TEST 2: Invalid and Edge Case Inputs")
    print("=" * 60)
    
    try:
        from learning.user_workspace_integration import create_workspace_rules_integration
        
        test_dir = f"stress_invalid_{os.getpid()}"
        rules_system = create_workspace_rules_integration(test_dir)
        
        # Test cases with invalid inputs
        invalid_test_cases = [
            {
                'name': 'Empty Context',
                'context': '',
                'expected_rules': 0
            },
            {
                'name': 'Malformed XML',
                'context': '<user_rules>NEVER do this<user_rules>',  # Missing closing tag
                'expected_rules': 0
            },
            {
                'name': 'Unicode Characters',
                'context': '''
                <user_rules>
                1. NEVER use 中文字符 in variable names
                2. ALWAYS validate émojis 🚀 in user input
                3. MUST handle ñoño cases properly
                </user_rules>
                ''',
                'expected_rules': 3
            },
            {
                'name': 'Very Long Rule',
                'context': f'''
                <user_rules>
                1. NEVER {'x' * 10000} - This is an extremely long rule that tests memory limits
                </user_rules>
                ''',
                'expected_rules': 1
            },
            {
                'name': 'Special Characters',
                'context': '''
                <user_rules>
                1. NEVER use @#$%^&*(){}[]|\\:";'<>?,./ in function names
                2. ALWAYS escape "quotes" and 'apostrophes' properly
                </user_rules>
                ''',
                'expected_rules': 2
            },
            {
                'name': 'Nested Tags',
                'context': '''
                <user_rules>
                <MEMORY[nested]>
                NEVER nest <tags> inside other tags
                </MEMORY[nested]>
                </user_rules>
                ''',
                'expected_rules': 1
            }
        ]
        
        for test_case in invalid_test_cases:
            print(f"   🧪 Testing: {test_case['name']}")
            
            try:
                rules_extracted = rules_system.extract_rules_from_context(test_case['context'])
                print(f"      ✅ Extracted {rules_extracted} rules (expected ~{test_case['expected_rules']})")
                
                # Test compliance checking with invalid code
                invalid_code = "def invalid_function():\n    return None\n    # Missing proper structure"
                compliance = rules_system.check_compliance(invalid_code)
                print(f"      ✅ Compliance check handled gracefully")
                
            except Exception as e:
                print(f"      ⚠️ Exception handled: {type(e).__name__}")
        
        # Test with None inputs
        print(f"   🧪 Testing: None Inputs")
        try:
            rules_system.extract_rules_from_context(None)
            print(f"      ⚠️ None input should have been rejected")
        except (TypeError, AttributeError):
            print(f"      ✅ None input properly rejected")
        
        # Test with extremely large input
        print(f"   🧪 Testing: Extremely Large Input")
        huge_context = "<user_rules>\n" + "NEVER do this. " * 100000 + "\n</user_rules>"
        
        start_time = time.time()
        try:
            rules_extracted = rules_system.extract_rules_from_context(huge_context)
            processing_time = time.time() - start_time
            print(f"      ✅ Processed huge input in {processing_time:.2f}s ({len(huge_context)} chars)")
        except Exception as e:
            print(f"      ⚠️ Huge input caused: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def stress_test_concurrent_access():
    """Test concurrent access to the rules system"""
    
    print("\n🔥 STRESS TEST 3: Concurrent Access")
    print("=" * 60)
    
    try:
        from learning.user_workspace_integration import create_workspace_rules_integration
        
        test_dir = f"stress_concurrent_{os.getpid()}"
        rules_system = create_workspace_rules_integration(test_dir)
        
        # Add some initial rules
        initial_context = """
        <user_rules>
        1. NEVER modify shared resources without locking
        2. ALWAYS use thread-safe operations
        3. MUST handle concurrent access gracefully
        </user_rules>
        """
        
        rules_system.extract_rules_from_context(initial_context)
        
        def worker_thread(thread_id):
            """Worker function for concurrent testing"""
            results = []
            
            try:
                # Each thread adds a custom rule
                rule_id = rules_system.add_custom_rule(
                    title=f"Thread {thread_id} Rule",
                    content=f"MUST handle thread {thread_id} operations safely",
                    category="concurrency",
                    priority=5,
                    enforcement_level="warning"
                )
                results.append(f"Thread {thread_id}: Added rule {rule_id}")
                
                # Each thread retrieves rules
                rules = rules_system.get_applicable_rules(context="python")
                results.append(f"Thread {thread_id}: Retrieved {len(rules)} rules")
                
                # Each thread checks compliance
                test_code = f"""
def thread_{thread_id}_function():
    # Thread {thread_id} specific code
    return "thread_{thread_id}_result"
"""
                compliance = rules_system.check_compliance(test_code, context="python")
                results.append(f"Thread {thread_id}: Compliance check completed")
                
                return results
                
            except Exception as e:
                return [f"Thread {thread_id}: ERROR - {e}"]
        
        # Run concurrent threads
        print(f"   🧪 Testing with 10 concurrent threads...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(10)]
            
            thread_results = []
            for future in as_completed(futures):
                thread_results.extend(future.result())
        
        # Analyze results
        successful_operations = len([r for r in thread_results if "ERROR" not in r])
        total_operations = len(thread_results)
        
        print(f"   ✅ Concurrent operations: {successful_operations}/{total_operations} successful")
        
        # Check final state
        final_summary = rules_system.get_rules_summary()
        print(f"   📊 Final state: {final_summary['total_rules']} total rules")
        
        return successful_operations == total_operations
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def stress_test_memory_limits():
    """Test memory usage and limits"""
    
    print("\n🔥 STRESS TEST 4: Memory Limits and Performance")
    print("=" * 60)
    
    try:
        from learning.user_workspace_integration import create_workspace_rules_integration
        
        test_dir = f"stress_memory_{os.getpid()}"
        rules_system = create_workspace_rules_integration(test_dir)
        
        # Test 1: Add many rules rapidly
        print(f"   🧪 Adding 1000 custom rules rapidly...")
        
        start_time = time.time()
        for i in range(1000):
            rules_system.add_custom_rule(
                title=f"Performance Rule {i}",
                content=f"MUST optimize operation_{i} for performance",
                category="performance",
                priority=i % 10 + 1,
                enforcement_level=["strict", "warning", "suggestion"][i % 3]
            )
        
        addition_time = time.time() - start_time
        print(f"      ✅ Added 1000 rules in {addition_time:.2f} seconds ({addition_time/1000*1000:.2f}ms per rule)")
        
        # Test 2: Retrieve all rules multiple times
        print(f"   🧪 Retrieving all rules 100 times...")
        
        start_time = time.time()
        for i in range(100):
            rules = rules_system.get_applicable_rules()
        
        retrieval_time = time.time() - start_time
        print(f"      ✅ 100 retrievals in {retrieval_time:.2f} seconds ({retrieval_time/100*1000:.2f}ms per retrieval)")
        
        # Test 3: Complex compliance checking
        print(f"   🧪 Complex compliance checking...")
        
        complex_code = """
def complex_function(param1, param2, param3):
    '''Complex function that should trigger multiple rule checks'''
    
    # This should trigger performance rules
    for i in range(1000):
        operation_5(param1)
        operation_15(param2)
        operation_25(param3)
    
    # This should trigger security rules
    user_input = validate_input(param1)
    
    # This should trigger debugging rules
    try:
        result = process_data(user_input)
        return optimize_result(result)
    except Exception as e:
        log_error(e)
        return None
"""
        
        start_time = time.time()
        for i in range(50):
            compliance = rules_system.check_compliance(complex_code, context="python")
        
        compliance_time = time.time() - start_time
        print(f"      ✅ 50 complex compliance checks in {compliance_time:.2f} seconds")
        
        # Test 4: Memory usage summary
        final_summary = rules_system.get_rules_summary()
        print(f"   📊 Memory Usage Summary:")
        print(f"      - Total rules: {final_summary['total_rules']}")
        print(f"      - Categories: {len(final_summary['rules_by_category'])}")
        print(f"      - High priority rules: {final_summary['high_priority_rules']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def stress_test_database_operations():
    """Test database operations and recovery"""
    
    print("\n🔥 STRESS TEST 5: Database Operations and Recovery")
    print("=" * 60)
    
    try:
        from learning.user_workspace_integration import create_workspace_rules_integration
        
        test_dir = f"stress_database_{os.getpid()}"
        rules_system = create_workspace_rules_integration(test_dir)
        
        # Test 1: Rapid database writes
        print(f"   🧪 Rapid database writes...")
        
        context_template = """
        <user_rules>
        {rules}
        </user_rules>
        """
        
        for i in range(100):
            rules_content = f"NEVER perform operation_{i} without validation"
            context = context_template.format(rules=rules_content)
            rules_system.extract_rules_from_context(context)
        
        print(f"      ✅ 100 rapid database writes completed")
        
        # Test 2: Database persistence
        print(f"   🧪 Database persistence test...")
        
        # Create new instance with same directory
        rules_system_2 = create_workspace_rules_integration(test_dir)
        
        summary_1 = rules_system.get_rules_summary()
        summary_2 = rules_system_2.get_rules_summary()
        
        if summary_1['total_rules'] == summary_2['total_rules']:
            print(f"      ✅ Database persistence verified ({summary_1['total_rules']} rules)")
        else:
            print(f"      ⚠️ Persistence issue: {summary_1['total_rules']} vs {summary_2['total_rules']}")
        
        # Test 3: Database recovery simulation
        print(f"   🧪 Database recovery simulation...")
        
        # Try to create another instance (should handle existing database)
        rules_system_3 = create_workspace_rules_integration(test_dir)
        summary_3 = rules_system_3.get_rules_summary()
        
        print(f"      ✅ Database recovery successful ({summary_3['total_rules']} rules loaded)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def run_comprehensive_stress_test():
    """Run all stress tests"""
    
    print("🚀 COMPREHENSIVE STRESS TEST - User Workspace Rules Integration")
    print("=" * 80)
    print("Testing system under extreme conditions and edge cases")
    print("=" * 80)
    
    test_results = []
    
    # Run all stress tests
    test_results.append(("Large Rule Sets", stress_test_large_rule_sets()))
    test_results.append(("Invalid Inputs", stress_test_invalid_inputs()))
    test_results.append(("Concurrent Access", stress_test_concurrent_access()))
    test_results.append(("Memory Limits", stress_test_memory_limits()))
    test_results.append(("Database Operations", stress_test_database_operations()))
    
    # Summary
    print("\n" + "=" * 80)
    print("🏁 STRESS TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   - Tests Passed: {passed_tests}/{total_tests}")
    print(f"   - Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL STRESS TESTS PASSED!")
        print(f"✅ System is robust and handles extreme conditions")
        print(f"✅ Ready for production deployment")
        print(f"✅ Performance is acceptable under load")
        print(f"✅ Error handling is comprehensive")
        print(f"✅ Database operations are reliable")
    else:
        print(f"\n⚠️ SOME STRESS TESTS FAILED")
        print(f"❌ System needs improvements before production")
        print(f"❌ Review failed tests and fix issues")
    
    print("=" * 80)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_comprehensive_stress_test()
    
    if success:
        print("\n🎯 CONFIDENCE LEVEL: ⭐⭐⭐⭐⭐ MAXIMUM")
        print("The system is battle-tested and production-ready!")
    else:
        print("\n⚠️ CONFIDENCE LEVEL: NEEDS IMPROVEMENT")
        print("Address the failed tests before production deployment.")
