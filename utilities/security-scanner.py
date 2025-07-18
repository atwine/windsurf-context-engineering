#!/usr/bin/env python3
"""
Security Scanner Utilities
Provides comprehensive security scanning for generated code projects.
"""

import os
import re
import json
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityScanner:
    """Comprehensive security scanner for code projects."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results = {
            'secrets': [],
            'vulnerabilities': [],
            'dependencies': [],
            'owasp_issues': [],
            'license_issues': []
        }
    
    def scan_all(self) -> Dict[str, any]:
        """Run comprehensive security scan."""
        logger.info(f"Starting security scan for {self.project_path}")
        
        # Run all security checks
        self.scan_secrets()
        self.scan_dependencies()
        self.scan_owasp_issues()
        self.scan_license_compliance()
        
        # Generate security report
        return self.generate_security_report()
    
    def scan_secrets(self) -> List[Dict[str, any]]:
        """Scan for hardcoded secrets and sensitive information."""
        logger.info("Scanning for hardcoded secrets...")
        
        # Common secret patterns
        secret_patterns = {
            'api_key': r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'password': r'(?i)(password|pwd|pass)\s*[:=]\s*["\']([^"\'\\s]{8,})["\']',
            'token': r'(?i)(token|auth[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'secret': r'(?i)(secret|secret[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'private_key': r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'github_token': r'ghp_[0-9a-zA-Z]{36}',
            'slack_token': r'xox[baprs]-[0-9a-zA-Z-]{10,48}',
            'jwt_token': r'eyJ[0-9a-zA-Z_-]*\.eyJ[0-9a-zA-Z_-]*\.[0-9a-zA-Z_-]*'
        }
        
        secrets_found = []
        
        # Scan all text files
        for file_path in self._get_scannable_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for secret_type, pattern in secret_patterns.items():
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        secret_info = {
                            'type': secret_type,
                            'file': str(file_path.relative_to(self.project_path)),
                            'line': line_num,
                            'severity': self._get_secret_severity(secret_type),
                            'context': self._get_line_context(content, match.start()),
                            'recommendation': self._get_secret_recommendation(secret_type)
                        }
                        
                        secrets_found.append(secret_info)
                        
            except Exception as e:
                logger.warning(f"Could not scan {file_path}: {e}")
        
        self.results['secrets'] = secrets_found
        return secrets_found
    
    def scan_dependencies(self) -> List[Dict[str, any]]:
        """Scan dependencies for known vulnerabilities."""
        logger.info("Scanning dependencies for vulnerabilities...")
        
        dependency_issues = []
        
        # Check Python dependencies
        requirements_files = [
            'requirements.txt', 'requirements-dev.txt', 'requirements-test.txt',
            'Pipfile', 'pyproject.toml', 'setup.py'
        ]
        
        for req_file in requirements_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                issues = self._scan_python_dependencies(req_path)
                dependency_issues.extend(issues)
        
        # Check Node.js dependencies
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            issues = self._scan_nodejs_dependencies(package_json)
            dependency_issues.extend(issues)
        
        self.results['dependencies'] = dependency_issues
        return dependency_issues
    
    def scan_owasp_issues(self) -> List[Dict[str, any]]:
        """Scan for OWASP Top 10 vulnerabilities."""
        logger.info("Scanning for OWASP Top 10 vulnerabilities...")
        
        owasp_issues = []
        
        # OWASP patterns to check
        owasp_patterns = {
            'sql_injection': {
                'pattern': r'(?i)(query|execute|cursor\.execute)\s*\(\s*["\'].*%s.*["\']',
                'severity': 'HIGH',
                'description': 'Potential SQL injection vulnerability'
            },
            'xss': {
                'pattern': r'(?i)(innerHTML|outerHTML|document\.write)\s*=.*\+',
                'severity': 'HIGH',
                'description': 'Potential XSS vulnerability'
            },
            'path_traversal': {
                'pattern': r'(?i)(open|file|read)\s*\([^)]*\.\./.*\)',
                'severity': 'MEDIUM',
                'description': 'Potential path traversal vulnerability'
            },
            'weak_crypto': {
                'pattern': r'(?i)(md5|sha1|des|rc4)\s*\(',
                'severity': 'MEDIUM',
                'description': 'Weak cryptographic algorithm'
            },
            'hardcoded_credentials': {
                'pattern': r'(?i)(password|pwd)\s*=\s*["\'][^"\']{1,}["\']',
                'severity': 'HIGH',
                'description': 'Hardcoded credentials'
            }
        }
        
        # Scan all code files
        for file_path in self._get_scannable_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for vuln_type, vuln_info in owasp_patterns.items():
                    matches = re.finditer(vuln_info['pattern'], content, re.MULTILINE)
                    
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        issue = {
                            'type': vuln_type,
                            'file': str(file_path.relative_to(self.project_path)),
                            'line': line_num,
                            'severity': vuln_info['severity'],
                            'description': vuln_info['description'],
                            'context': self._get_line_context(content, match.start()),
                            'recommendation': self._get_owasp_recommendation(vuln_type)
                        }
                        
                        owasp_issues.append(issue)
                        
            except Exception as e:
                logger.warning(f"Could not scan {file_path}: {e}")
        
        self.results['owasp_issues'] = owasp_issues
        return owasp_issues
    
    def scan_license_compliance(self) -> List[Dict[str, any]]:
        """Scan for license compliance issues."""
        logger.info("Scanning for license compliance issues...")
        
        license_issues = []
        
        # Check for license files
        license_files = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'COPYING']
        has_license = any((self.project_path / lf).exists() for lf in license_files)
        
        if not has_license:
            license_issues.append({
                'type': 'missing_license',
                'severity': 'MEDIUM',
                'description': 'No license file found',
                'recommendation': 'Add a LICENSE file to specify project licensing terms'
            })
        
        # Check dependency licenses (simplified check)
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    
                # Check for GPL dependencies (potential licensing conflict)
                dependencies = data.get('dependencies', {})
                for dep_name in dependencies:
                    if 'gpl' in dep_name.lower():
                        license_issues.append({
                            'type': 'potential_gpl_conflict',
                            'dependency': dep_name,
                            'severity': 'LOW',
                            'description': f'Potential GPL license conflict with {dep_name}',
                            'recommendation': 'Verify license compatibility'
                        })
                        
            except Exception as e:
                logger.warning(f"Could not check package.json licenses: {e}")
        
        self.results['license_issues'] = license_issues
        return license_issues
    
    def generate_security_report(self) -> Dict[str, any]:
        """Generate comprehensive security report."""
        total_issues = (
            len(self.results['secrets']) +
            len(self.results['vulnerabilities']) +
            len(self.results['dependencies']) +
            len(self.results['owasp_issues']) +
            len(self.results['license_issues'])
        )
        
        # Calculate severity distribution
        severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for category in self.results.values():
            for issue in category:
                severity = issue.get('severity', 'LOW')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate security score (0-100)
        security_score = max(0, 100 - (
            severity_counts['HIGH'] * 20 +
            severity_counts['MEDIUM'] * 10 +
            severity_counts['LOW'] * 5
        ))
        
        report = {
            'summary': {
                'total_issues': total_issues,
                'security_score': security_score,
                'severity_distribution': severity_counts,
                'scan_timestamp': self._get_timestamp()
            },
            'details': self.results,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _get_scannable_files(self) -> List[Path]:
        """Get list of files to scan."""
        scannable_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.sql', '.yaml', '.yml', '.json', '.xml', '.html', '.css',
            '.sh', '.bash', '.ps1', '.bat', '.cmd'
        }
        
        ignore_dirs = {
            '.git', '.svn', '.hg', '__pycache__', 'node_modules', '.venv',
            'venv', 'env', '.env', 'build', 'dist', '.pytest_cache',
            '.mypy_cache', '.tox', 'coverage', '.coverage'
        }
        
        files = []
        
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file():
                # Skip files in ignored directories
                if any(ignored in file_path.parts for ignored in ignore_dirs):
                    continue
                
                # Include files with scannable extensions
                if file_path.suffix.lower() in scannable_extensions:
                    files.append(file_path)
                
                # Include common config files without extensions
                if file_path.name in ['Dockerfile', 'Makefile', 'requirements.txt']:
                    files.append(file_path)
        
        return files
    
    def _scan_python_dependencies(self, req_file: Path) -> List[Dict[str, any]]:
        """Scan Python dependencies for vulnerabilities."""
        issues = []
        
        # Known vulnerable packages (simplified - in real implementation, use safety DB)
        vulnerable_packages = {
            'django': ['<3.2.0', 'Security vulnerabilities in older versions'],
            'flask': ['<2.0.0', 'Security vulnerabilities in older versions'],
            'requests': ['<2.20.0', 'Security vulnerabilities in older versions'],
            'pyyaml': ['<5.4.0', 'Code execution vulnerability'],
            'pillow': ['<8.1.1', 'Security vulnerabilities in image processing']
        }
        
        try:
            with open(req_file, 'r') as f:
                content = f.read()
                
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse package name and version
                    package_match = re.match(r'([a-zA-Z0-9_-]+)([>=<!=]+.*)?', line)
                    if package_match:
                        package_name = package_match.group(1).lower()
                        version_spec = package_match.group(2) or ''
                        
                        if package_name in vulnerable_packages:
                            vuln_info = vulnerable_packages[package_name]
                            issues.append({
                                'type': 'vulnerable_dependency',
                                'package': package_name,
                                'version_spec': version_spec,
                                'vulnerability': vuln_info[0],
                                'description': vuln_info[1],
                                'severity': 'HIGH',
                                'file': str(req_file.relative_to(self.project_path)),
                                'recommendation': f'Update {package_name} to latest version'
                            })
                            
        except Exception as e:
            logger.warning(f"Could not scan {req_file}: {e}")
        
        return issues
    
    def _scan_nodejs_dependencies(self, package_json: Path) -> List[Dict[str, any]]:
        """Scan Node.js dependencies for vulnerabilities."""
        issues = []
        
        # Known vulnerable packages (simplified)
        vulnerable_packages = {
            'lodash': ['<4.17.21', 'Prototype pollution vulnerability'],
            'minimist': ['<1.2.6', 'Prototype pollution vulnerability'],
            'express': ['<4.17.0', 'Security vulnerabilities'],
            'axios': ['<0.21.2', 'Server-side request forgery vulnerability']
        }
        
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)
                
            dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            
            for package_name, version in dependencies.items():
                if package_name in vulnerable_packages:
                    vuln_info = vulnerable_packages[package_name]
                    issues.append({
                        'type': 'vulnerable_dependency',
                        'package': package_name,
                        'version': version,
                        'vulnerability': vuln_info[0],
                        'description': vuln_info[1],
                        'severity': 'HIGH',
                        'file': str(package_json.relative_to(self.project_path)),
                        'recommendation': f'Update {package_name} to latest version'
                    })
                    
        except Exception as e:
            logger.warning(f"Could not scan {package_json}: {e}")
        
        return issues
    
    def _get_secret_severity(self, secret_type: str) -> str:
        """Get severity level for secret type."""
        high_severity = {'api_key', 'private_key', 'aws_access_key', 'github_token'}
        medium_severity = {'password', 'token', 'secret'}
        
        if secret_type in high_severity:
            return 'HIGH'
        elif secret_type in medium_severity:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_secret_recommendation(self, secret_type: str) -> str:
        """Get recommendation for secret type."""
        recommendations = {
            'api_key': 'Use environment variables or secure key management',
            'password': 'Use environment variables or secure credential storage',
            'token': 'Use environment variables or secure token management',
            'secret': 'Use environment variables or secure secret management',
            'private_key': 'Store private keys securely, never in code',
            'aws_access_key': 'Use IAM roles or AWS credential files',
            'github_token': 'Use GitHub secrets or environment variables',
            'slack_token': 'Use environment variables or secure token storage'
        }
        
        return recommendations.get(secret_type, 'Store securely using environment variables')
    
    def _get_owasp_recommendation(self, vuln_type: str) -> str:
        """Get recommendation for OWASP vulnerability type."""
        recommendations = {
            'sql_injection': 'Use parameterized queries or prepared statements',
            'xss': 'Sanitize user input and use safe DOM manipulation methods',
            'path_traversal': 'Validate and sanitize file paths, use allowlists',
            'weak_crypto': 'Use strong cryptographic algorithms (AES, SHA-256+)',
            'hardcoded_credentials': 'Use environment variables or secure credential storage'
        }
        
        return recommendations.get(vuln_type, 'Follow OWASP security guidelines')
    
    def _get_line_context(self, content: str, position: int) -> str:
        """Get context around a specific position in content."""
        lines = content.split('\n')
        line_num = content[:position].count('\n')
        
        start_line = max(0, line_num - 1)
        end_line = min(len(lines), line_num + 2)
        
        context_lines = []
        for i in range(start_line, end_line):
            prefix = '>>> ' if i == line_num else '    '
            context_lines.append(f"{prefix}{lines[i]}")
        
        return '\n'.join(context_lines)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _generate_recommendations(self) -> List[str]:
        """Generate overall security recommendations."""
        recommendations = []
        
        if self.results['secrets']:
            recommendations.append("Remove hardcoded secrets and use environment variables")
        
        if self.results['dependencies']:
            recommendations.append("Update vulnerable dependencies to latest versions")
        
        if self.results['owasp_issues']:
            recommendations.append("Address OWASP Top 10 vulnerabilities")
        
        if self.results['license_issues']:
            recommendations.append("Ensure proper license compliance")
        
        # General recommendations
        recommendations.extend([
            "Implement input validation and sanitization",
            "Use HTTPS for all external communications",
            "Implement proper error handling and logging",
            "Regular security audits and dependency updates",
            "Use security headers and CSRF protection"
        ])
        
        return recommendations

# Utility functions
def scan_project_security(project_path: str) -> Dict[str, any]:
    """Scan a project for security issues."""
    scanner = SecurityScanner(project_path)
    return scanner.scan_all()

def generate_security_report(project_path: str, output_file: str = None) -> Dict[str, any]:
    """Generate and optionally save security report."""
    report = scan_project_security(project_path)
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Security report saved to {output_file}")
    
    return report

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python security-scanner.py <project_path> [output_file]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🔒 Security Scanner")
    print(f"Scanning project: {project_path}")
    print("=" * 50)
    
    try:
        report = generate_security_report(project_path, output_file)
        
        # Print summary
        summary = report['summary']
        print(f"\n📊 Security Scan Results:")
        print(f"  Total Issues: {summary['total_issues']}")
        print(f"  Security Score: {summary['security_score']}/100")
        print(f"  High Severity: {summary['severity_distribution']['HIGH']}")
        print(f"  Medium Severity: {summary['severity_distribution']['MEDIUM']}")
        print(f"  Low Severity: {summary['severity_distribution']['LOW']}")
        
        if summary['security_score'] >= 90:
            print("  ✅ EXCELLENT - High security standards")
        elif summary['security_score'] >= 70:
            print("  ⚠️ GOOD - Some security improvements needed")
        else:
            print("  ❌ NEEDS WORK - Significant security issues found")
            
    except Exception as e:
        print(f"❌ Security scan failed: {e}")
        sys.exit(1)
