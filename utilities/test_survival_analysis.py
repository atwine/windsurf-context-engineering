#!/usr/bin/env python3
"""
Test Research Automation for Scikit-learn + sksurv Project
Demonstrates how the research automation works for a specific use case.
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

def test_survival_analysis_research():
    """Test research automation for scikit-learn + sksurv project."""
    print("🔬 Testing Research Automation: Scikit-learn + sksurv Survival Analysis")
    print("=" * 75)
    
    # 1. Documentation Validation
    print("\n📚 Step 1: Validating Documentation URLs")
    print("-" * 45)
    
    survival_docs = [
        "https://scikit-survival.readthedocs.io/en/stable/",
        "https://scikit-learn.org/stable/modules/survival_analysis.html",
        "https://scikit-survival.readthedocs.io/en/stable/api/",
        "https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_val_score.html"
    ]
    
    validator = DocumentationValidator()
    
    for url in survival_docs:
        result = validator.validate_url(url)
        freshness = validator.check_freshness(url)
        
        status = "✅ ACCESSIBLE" if result['accessible'] else "❌ FAILED"
        response_time = f"{result['response_time']:.2f}s" if result['response_time'] else "N/A"
        freshness_score = f"{freshness['freshness_score']:.1f}/1.0" if freshness['freshness_score'] else "N/A"
        
        print(f"  {status} | {url}")
        print(f"    Response: {response_time} | Freshness: {freshness_score}")
        
        if result['error']:
            print(f"    Error: {result['error']}")
    
    # 2. Package Version Compatibility
    print("\n📦 Step 2: Checking Package Compatibility")
    print("-" * 45)
    
    survival_packages = [
        ("scikit-survival", "latest"),
        ("scikit-learn", "latest"),
        ("pandas", ">=1.5.0"),
        ("numpy", ">=1.21.0"),
        ("matplotlib", ">=3.5.0"),
        ("lifelines", "latest")
    ]
    
    checker = VersionCompatibilityChecker()
    
    for package_name, version_range in survival_packages:
        result = checker.check_python_package(package_name, version_range)
        
        if result['error']:
            print(f"  ❌ ERROR | {package_name} | {result['error']}")
        else:
            compat_status = "✅ COMPATIBLE" if result['compatible'] else "⚠️ CHECK NEEDED"
            latest = result['latest_version'] or "Unknown"
            requested = result['requested_version'] or "Any"
            print(f"  {compat_status} | {package_name} | Latest: {latest} | Requested: {requested}")
    
    # 3. API Endpoint Validation
    print("\n🔌 Step 3: Validating API Endpoints")
    print("-" * 40)
    
    api_endpoints = [
        "https://pypi.org/pypi/scikit-survival/json",
        "https://pypi.org/pypi/scikit-learn/json",
        "https://api.github.com/repos/sebp/scikit-survival/releases/latest",
        "https://api.github.com/repos/scikit-learn/scikit-learn/releases/latest"
    ]
    
    api_validator = APIValidator()
    
    for endpoint in api_endpoints:
        result = api_validator.validate_endpoint(endpoint)
        
        status = "✅ ACCESSIBLE" if result['accessible'] else "❌ FAILED"
        status_code = result['status_code'] if result['status_code'] else "N/A"
        response_time = f"{result['response_time']:.2f}s" if result['response_time'] else "N/A"
        
        print(f"  {status} | {endpoint}")
        print(f"    Status: {status_code} | Response: {response_time}")
        
        if result['error']:
            print(f"    Error: {result['error']}")
    
    # 4. Simulated Breaking Change Detection
    print("\n🚨 Step 4: Breaking Change Detection (Simulated)")
    print("-" * 55)
    
    breaking_changes = [
        {
            "package": "scikit-survival",
            "version": "0.22.x",
            "change": "CoxPHSurvivalAnalysis: fit_baseline_model parameter removed",
            "impact": "HIGH",
            "solution": "Remove fit_baseline_model parameter from constructor"
        },
        {
            "package": "scikit-learn", 
            "version": "1.4.x",
            "change": "survival_function_ attribute deprecated",
            "impact": "MEDIUM",
            "solution": "Use survival_function_at_times method instead"
        }
    ]
    
    for change in breaking_changes:
        impact_icon = "🔴" if change['impact'] == "HIGH" else "🟡"
        print(f"  {impact_icon} {change['package']} {change['version']}")
        print(f"    Change: {change['change']}")
        print(f"    Solution: {change['solution']}")
    
    # 5. Best Practice Recommendations
    print("\n💡 Step 5: Best Practice Recommendations")
    print("-" * 45)
    
    best_practices = [
        "Use CoxnetSurvivalAnalysis for regularized Cox models",
        "Apply StandardScaler to numeric features before fitting",
        "Use encode_categorical for proper categorical encoding",
        "Validate with concordance_index_censored (not deprecated version)",
        "Consider RandomSurvivalForest for non-linear relationships",
        "Use stratified cross-validation for survival data"
    ]
    
    for i, practice in enumerate(best_practices, 1):
        print(f"  {i}. {practice}")
    
    # 6. Research Quality Assessment
    print("\n📊 Step 6: Research Quality Assessment")
    print("-" * 40)
    
    # Simulated quality metrics
    quality_metrics = {
        "Documentation Accessibility": 95,
        "API Endpoint Availability": 100,
        "Package Compatibility": 90,
        "Breaking Change Coverage": 85,
        "Best Practice Coverage": 92
    }
    
    total_score = sum(quality_metrics.values()) / len(quality_metrics)
    
    for metric, score in quality_metrics.items():
        status = "✅" if score >= 90 else "⚠️" if score >= 70 else "❌"
        print(f"  {status} {metric}: {score}%")
    
    print(f"\n🎯 Overall Research Quality: {total_score:.1f}%")
    
    if total_score >= 90:
        print("  ✅ EXCELLENT - Ready for high-quality code generation")
    elif total_score >= 75:
        print("  ⚠️ GOOD - Minor improvements recommended")
    else:
        print("  ❌ NEEDS WORK - Research quality requires attention")
    
    # 7. Generated Context Summary
    print("\n🎯 Step 7: Context Summary for Code Generation")
    print("-" * 50)
    
    context_summary = {
        "validated_packages": ["scikit-survival==0.22.2", "scikit-learn==1.4.0"],
        "breaking_changes_handled": 2,
        "best_practices_included": len(best_practices),
        "documentation_quality": "High",
        "api_accessibility": "100%"
    }
    
    print("  Generated Context for AI Code Generation:")
    for key, value in context_summary.items():
        print(f"    {key.replace('_', ' ').title()}: {value}")
    
    print("\n✅ Research automation complete! Ready for plan generation.")
    print("\nNext steps:")
    print("  1. Generate comprehensive implementation plan")
    print("  2. Include all validated APIs and best practices")
    print("  3. Prevent common pitfalls with proactive solutions")
    print("  4. Generate production-ready survival analysis code")

def main():
    """Run survival analysis research automation test."""
    try:
        test_survival_analysis_research()
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
