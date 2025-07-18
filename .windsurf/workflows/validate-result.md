---
description: Validate Project Implementation
---

# Validate Project Implementation

This workflow validates that the implemented project meets all requirements and success criteria.

// turbo-all

1. **Load Project Context**
   - Retrieve original project prompt and plan from memory
   - Review success criteria and requirements
   - Understand expected functionality

2. **Automated Security Scanning**
   - **SAST Analysis**: Run static application security testing
   - **Dependency Vulnerabilities**: Scan for known security issues in dependencies
   - **Secrets Detection**: Check for hardcoded API keys, passwords, tokens
   - **License Compliance**: Verify all dependencies have compatible licenses
   - **OWASP Top 10**: Check for common web application vulnerabilities

3. **Code Quality Metrics**
   - **Cyclomatic Complexity**: Analyze code complexity and maintainability
   - **Code Duplication**: Detect and report duplicate code blocks
   - **Maintainability Index**: Calculate overall code maintainability score
   - **Code Smells**: Identify potential design and implementation issues
   - **Technical Debt**: Assess and quantify technical debt

4. **Test Coverage Validation**
   - **Coverage Analysis**: Ensure minimum test coverage thresholds
   - **Test Quality Assessment**: Evaluate test effectiveness and completeness
   - **Edge Case Coverage**: Verify edge cases and error conditions are tested
   - **Integration Test Validation**: Check integration between components
   - **Performance Test Results**: Validate performance benchmarks

5. **Dependency Audit**
   - **Vulnerability Scanning**: Check for known security vulnerabilities
   - **License Compatibility**: Ensure license compliance
   - **Version Currency**: Identify outdated dependencies
   - **Supply Chain Security**: Verify dependency integrity
   - **Dependency Tree Analysis**: Check for conflicting dependencies

6. **Performance Bottleneck Detection**
   - **Database Query Analysis**: Identify slow or inefficient queries
   - **Memory Usage Profiling**: Check for memory leaks and excessive usage
   - **CPU Usage Analysis**: Identify CPU-intensive operations
   - **Network Latency Assessment**: Check for network performance issues
   - **Scalability Assessment**: Evaluate system scalability potential

7. **Documentation Check**
   - Verify README is complete and accurate
   - Check setup instructions work
   - Ensure API documentation is current

8. **Deployment Readiness**
   - Verify all dependencies are documented
   - Check configuration management
   - Ensure project can be easily deployed

9. **Generate Validation Report**
   - Summarize validation results
   - List any issues found
   - Provide recommendations for improvements

10. **Final Approval**
    - Mark project as validated if all checks pass
    - Provide next steps for deployment or iteration
