#!/usr/bin/env python3
"""
Integration Test Script for Documentation Validation
Tests the research automation and validation utilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import with hyphenated filename
import importlib.util
spec = importlib.util.spec_from_file_location("doc_validation", "doc-validation.py")
doc_validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doc_validation)

# Import the classes and functions
DocumentationValidator = doc_validation.DocumentationValidator
APIValidator = doc_validation.APIValidator
VersionCompatibilityChecker = doc_validation.VersionCompatibilityChecker
validate_documentation_urls = doc_validation.validate_documentation_urls
check_api_endpoints = doc_validation.check_api_endpoints
check_package_versions = doc_validation.check_package_versions

def test_popular_frameworks():
    """Test research automation with popular frameworks."""
    print("🔍 Testing Research Automation with Popular Frameworks")
    print("=" * 60)
    
    # Test popular framework documentation
    framework_docs = [
        "https://reactjs.org/docs/getting-started.html",
        "https://vuejs.org/guide/",
        "https://docs.djangoproject.com/en/stable/",
        "https://expressjs.com/en/starter/installing.html",
        "https://flask.palletsprojects.com/en/2.3.x/"
    ]
    
    print("\n📚 Validating Framework Documentation:")
    results = validate_documentation_urls(framework_docs)
    
    for result in results:
        status = "✅ ACCESSIBLE" if result['accessible'] else "❌ FAILED"
        response_time = f"{result['response_time']:.2f}s" if result['response_time'] else "N/A"
        print(f"  {status} | {result['url']} | {response_time}")
        
        if result['error']:
            print(f"    Error: {result['error']}")
    
    return results

def test_api_endpoint_validation():
    """Test API endpoint validation accuracy."""
    print("\n🔌 Testing API Endpoint Validation:")
    print("-" * 40)
    
    # Test popular APIs
    test_apis = [
        "https://api.github.com",
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://httpbin.org/get",
        "https://api.invalid-endpoint-test.com"  # This should fail
    ]
    
    results = check_api_endpoints(test_apis)
    
    for result in results:
        status = "✅ ACCESSIBLE" if result['accessible'] else "❌ FAILED"
        status_code = result['status_code'] if result['status_code'] else "N/A"
        response_time = f"{result['response_time']:.2f}s" if result['response_time'] else "N/A"
        print(f"  {status} | {result['endpoint']} | {status_code} | {response_time}")
        
        if result['error']:
            print(f"    Error: {result['error']}")
    
    return results

def test_documentation_freshness():
    """Test documentation freshness detection."""
    print("\n📅 Testing Documentation Freshness Detection:")
    print("-" * 50)
    
    validator = DocumentationValidator()
    
    test_urls = [
        "https://reactjs.org/docs/getting-started.html",
        "https://docs.python.org/3/"
    ]
    
    for url in test_urls:
        freshness = validator.check_freshness(url)
        
        if freshness['age_days'] is not None:
            age_status = "🟢 FRESH" if freshness['is_fresh'] else "🟡 AGING"
            score = f"{freshness['freshness_score']:.1f}/1.0"
            print(f"  {age_status} | {url}")
            print(f"    Age: {freshness['age_days']} days | Score: {score}")
        else:
            print(f"  ❓ UNKNOWN | {url} | Could not determine age")

def test_version_compatibility():
    """Test version compatibility checking."""
    print("\n📦 Testing Version Compatibility:")
    print("-" * 40)
    
    # Test popular packages
    test_packages = [
        ("react", "^18.0.0"),
        ("express", "^4.18.0"),
        ("django", "4.2"),
        ("flask", "2.3.0"),
        ("invalid-package-name-test", "1.0.0")  # This should fail
    ]
    
    results = check_package_versions(test_packages)
    
    for result in results:
        if result['error']:
            print(f"  ❌ ERROR | {result['package']} | {result['error']}")
        else:
            compat_status = "✅ COMPATIBLE" if result['compatible'] else "⚠️ INCOMPATIBLE"
            latest = result['latest_version'] or "Unknown"
            requested = result['requested_version'] or "Any"
            print(f"  {compat_status} | {result['package']} | Latest: {latest} | Requested: {requested}")

def test_failure_scenarios():
    """Test failure scenarios and fallbacks."""
    print("\n🚨 Testing Failure Scenarios:")
    print("-" * 35)
    
    # Test invalid URLs
    invalid_urls = [
        "https://this-domain-does-not-exist-12345.com",
        "http://localhost:99999/invalid-port",
        "not-a-valid-url-at-all"
    ]
    
    print("\n  Testing Invalid URLs:")
    for url in invalid_urls:
        validator = DocumentationValidator()
        result = validator.validate_url(url)
        
        status = "✅ HANDLED" if result['error'] else "❌ UNHANDLED"
        print(f"    {status} | {url}")
        if result['error']:
            print(f"      Error: {result['error']}")

def generate_research_quality_report(doc_results, api_results):
    """Generate a research quality report."""
    print("\n📊 Research Quality Report:")
    print("=" * 30)
    
    # Documentation metrics
    total_docs = len(doc_results)
    accessible_docs = sum(1 for r in doc_results if r['accessible'])
    doc_success_rate = (accessible_docs / total_docs) * 100 if total_docs > 0 else 0
    
    print(f"\n📚 Documentation Validation:")
    print(f"  Total URLs tested: {total_docs}")
    print(f"  Accessible: {accessible_docs}")
    print(f"  Success rate: {doc_success_rate:.1f}%")
    
    # API metrics
    total_apis = len(api_results)
    accessible_apis = sum(1 for r in api_results if r['accessible'])
    api_success_rate = (accessible_apis / total_apis) * 100 if total_apis > 0 else 0
    
    print(f"\n🔌 API Endpoint Validation:")
    print(f"  Total endpoints tested: {total_apis}")
    print(f"  Accessible: {accessible_apis}")
    print(f"  Success rate: {api_success_rate:.1f}%")
    
    # Overall assessment
    overall_success = (doc_success_rate + api_success_rate) / 2
    
    print(f"\n🎯 Overall Research Quality:")
    if overall_success >= 80:
        print(f"  ✅ EXCELLENT ({overall_success:.1f}%) - Research automation working well")
    elif overall_success >= 60:
        print(f"  ⚠️ GOOD ({overall_success:.1f}%) - Some improvements needed")
    else:
        print(f"  ❌ NEEDS WORK ({overall_success:.1f}%) - Research automation needs attention")

def main():
    """Run all integration tests."""
    print("🚀 Context Engineering Research Automation Tests")
    print("=" * 55)
    print("Testing enhanced research phase integration...")
    
    try:
        # Run all tests
        doc_results = test_popular_frameworks()
        api_results = test_api_endpoint_validation()
        test_documentation_freshness()
        test_version_compatibility()
        test_failure_scenarios()
        
        # Generate report
        generate_research_quality_report(doc_results, api_results)
        
        print("\n✅ All integration tests completed!")
        print("\nNext steps:")
        print("  1. Review test results above")
        print("  2. Address any failed validations")
        print("  3. Integrate research automation into workflows")
        print("  4. Test with real project scenarios")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
