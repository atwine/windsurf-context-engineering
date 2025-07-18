#!/usr/bin/env python3
"""
Tool Integration System Test Suite
==================================

Comprehensive testing of the development tool ecosystem integration.
Tests all components: linting, testing, CI/CD, dev environment, and config management.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.linting_integration import LintingIntegration
from tools.testing_integration import TestingIntegration
from tools.cicd_integration import CICDIntegration
from tools.dev_environment import DevEnvironmentSetup
from tools.config_manager import ConfigurationManager

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class ToolIntegrationTestSuite:
    """Comprehensive test suite for tool integration system."""
    
    def __init__(self):
        self.test_results = {
            'linting_integration': {},
            'testing_integration': {},
            'cicd_integration': {},
            'dev_environment': {},
            'config_management': {},
            'end_to_end_integration': {},
            'overall_status': 'unknown'
        }
        
        # Create temporary test project
        self.temp_dir = None
        self.setup_test_project()
    
    def setup_test_project(self):
        """Create a temporary test project with sample files."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix='windsurf_tool_test_'))
        
        # Create project structure
        (self.temp_dir / 'src').mkdir()
        (self.temp_dir / 'tests').mkdir()
        (self.temp_dir / 'public').mkdir()
        
        # Create sample files
        self._create_sample_files()
        
        logger.info(f"Test project created: {self.temp_dir}")
    
    def _create_sample_files(self):
        """Create sample project files."""
        # package.json
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "description": "Test project for tool integration",
            "main": "src/index.js",
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            },
            "devDependencies": {}
        }
        
        with open(self.temp_dir / 'package.json', 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Sample JavaScript file
        js_content = """
import React from 'react';

const App = () => {
  const [count, setCount] = React.useState(0);
  
  return (
    <div>
      <h1>Hello World</h1>
      <button onClick={() => setCount(count + 1)}>
        Count: {count}
      </button>
    </div>
  );
};

export default App;
"""
        
        with open(self.temp_dir / 'src' / 'App.js', 'w') as f:
            f.write(js_content.strip())
        
        # Sample Python file
        py_content = """
def calculate_sum(a, b):
    \"\"\"Calculate sum of two numbers.\"\"\"
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
"""
        
        with open(self.temp_dir / 'src' / 'calculator.py', 'w') as f:
            f.write(py_content.strip())
        
        # requirements.txt
        requirements = """
flask>=2.0.0
requests>=2.25.0
pytest>=7.0.0
"""
        
        with open(self.temp_dir / 'requirements.txt', 'w') as f:
            f.write(requirements.strip())
        
        # index.html
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Test App</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>
"""
        
        with open(self.temp_dir / 'public' / 'index.html', 'w') as f:
            f.write(html_content.strip())
    
    def test_linting_integration(self) -> Dict[str, Any]:
        """Test linting integration functionality."""
        print("\n🔍 Testing Linting Integration...")
        
        try:
            linting = LintingIntegration(str(self.temp_dir))
            
            # Test language detection
            languages = linting.detect_project_languages()
            assert 'javascript' in languages, "Should detect JavaScript"
            assert 'python' in languages, "Should detect Python"
            
            # Test linting setup
            setup_results = linting.setup_linting_for_project(languages)
            assert len(setup_results['tools_configured']) > 0, "Should configure tools"
            assert len(setup_results['configurations_created']) > 0, "Should create configs"
            
            # Verify configuration files were created
            eslint_config = self.temp_dir / '.eslintrc.json'
            assert eslint_config.exists(), "ESLint config should be created"
            
            prettier_config = self.temp_dir / '.prettierrc.json'
            assert prettier_config.exists(), "Prettier config should be created"
            
            # Test configuration content
            with open(eslint_config) as f:
                eslint_data = json.load(f)
                assert 'rules' in eslint_data, "ESLint config should have rules"
                assert 'extends' in eslint_data, "ESLint config should have extends"
            
            self.test_results['linting_integration'] = {
                'status': 'passed',
                'languages_detected': languages,
                'tools_configured': setup_results['tools_configured'],
                'files_created': len(setup_results['configurations_created'])
            }
            
            print("  ✅ Linting integration test passed")
            return self.test_results['linting_integration']
            
        except Exception as e:
            self.test_results['linting_integration'] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"  ❌ Linting integration test failed: {e}")
            return self.test_results['linting_integration']
    
    def test_testing_integration(self) -> Dict[str, Any]:
        """Test testing framework integration."""
        print("\n🧪 Testing Framework Integration...")
        
        try:
            testing = TestingIntegration(str(self.temp_dir))
            
            # Test testing needs detection
            needs = testing.detect_testing_needs()
            assert 'jest' in needs['unit'], "Should detect Jest need"
            assert 'pytest' in needs['unit'], "Should detect Pytest need"
            
            # Test Jest setup
            jest_config = testing.setup_testing_framework('jest')
            assert 'testEnvironment' in jest_config, "Jest config should have testEnvironment"
            
            # Test Pytest setup
            pytest_config = testing.setup_testing_framework('pytest')
            assert 'config_file' in pytest_config, "Pytest should create config file"
            
            # Verify configuration files
            jest_config_file = self.temp_dir / 'jest.config.js'
            assert jest_config_file.exists(), "Jest config file should be created"
            
            # Test template generation
            js_test = testing.generate_test_templates('unit_js', 'App')
            assert 'describe' in js_test, "JS test template should have describe block"
            assert 'test' in js_test, "JS test template should have test cases"
            
            py_test = testing.generate_test_templates('unit_py', 'Calculator')
            assert 'class Test' in py_test, "Python test should have test class"
            assert 'def test_' in py_test, "Python test should have test methods"
            
            self.test_results['testing_integration'] = {
                'status': 'passed',
                'frameworks_detected': list(needs.keys()),
                'jest_setup': 'success',
                'pytest_setup': 'success',
                'template_generation': 'success'
            }
            
            print("  ✅ Testing integration test passed")
            return self.test_results['testing_integration']
            
        except Exception as e:
            self.test_results['testing_integration'] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"  ❌ Testing integration test failed: {e}")
            return self.test_results['testing_integration']
    
    def test_cicd_integration(self) -> Dict[str, Any]:
        """Test CI/CD pipeline integration."""
        print("\n🚀 Testing CI/CD Integration...")
        
        try:
            cicd = CICDIntegration(str(self.temp_dir))
            
            # Test deployment needs detection
            needs = cicd.detect_deployment_needs()
            assert 'node' in needs['runtime'], "Should detect Node.js runtime"
            assert 'python' in needs['runtime'], "Should detect Python runtime"
            
            # Test GitHub Actions setup
            github_result = cicd.create_github_actions(needs)
            assert len(github_result['workflows_created']) > 0, "Should create workflows"
            
            # Verify workflow files
            workflows_dir = self.temp_dir / '.github' / 'workflows'
            assert workflows_dir.exists(), "Workflows directory should be created"
            
            ci_workflow = workflows_dir / 'ci.yml'
            assert ci_workflow.exists(), "CI workflow should be created"
            
            # Test Docker configuration
            docker_files = cicd.create_docker_config(needs)
            assert 'Dockerfile' in docker_files, "Should create Dockerfile"
            
            dockerfile = self.temp_dir / 'Dockerfile'
            assert dockerfile.exists(), "Dockerfile should be created"
            
            # Test deployment scripts
            deploy_scripts = cicd.create_deployment_scripts(needs)
            assert len(deploy_scripts) > 0, "Should create deployment scripts"
            
            self.test_results['cicd_integration'] = {
                'status': 'passed',
                'deployment_needs': needs,
                'github_workflows': len(github_result['workflows_created']),
                'docker_files': len(docker_files),
                'deployment_scripts': len(deploy_scripts)
            }
            
            print("  ✅ CI/CD integration test passed")
            return self.test_results['cicd_integration']
            
        except Exception as e:
            self.test_results['cicd_integration'] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"  ❌ CI/CD integration test failed: {e}")
            return self.test_results['cicd_integration']
    
    def test_dev_environment(self) -> Dict[str, Any]:
        """Test development environment setup."""
        print("\n🛠️ Testing Development Environment Setup...")
        
        try:
            dev_env = DevEnvironmentSetup(str(self.temp_dir))
            
            # Test VS Code configuration
            languages = ['javascript', 'python']
            vscode_files = dev_env.create_vscode_config(languages)
            assert len(vscode_files) >= 4, "Should create VS Code config files"
            
            # Verify VS Code files
            vscode_dir = self.temp_dir / '.vscode'
            assert vscode_dir.exists(), "VS Code directory should be created"
            
            settings_file = vscode_dir / 'settings.json'
            assert settings_file.exists(), "VS Code settings should be created"
            
            # Test environment templates
            env_files = dev_env.create_env_templates()
            assert '.env.example' in env_files, "Should create .env.example"
            
            env_example = self.temp_dir / '.env.example'
            assert env_example.exists(), ".env.example should be created"
            
            # Test development scripts
            script_files = dev_env.create_dev_scripts(languages)
            assert len(script_files) >= 3, "Should create development scripts"
            
            scripts_dir = self.temp_dir / 'scripts'
            assert scripts_dir.exists(), "Scripts directory should be created"
            
            self.test_results['dev_environment'] = {
                'status': 'passed',
                'vscode_files': len(vscode_files),
                'env_files': len(env_files),
                'script_files': len(script_files)
            }
            
            print("  ✅ Development environment test passed")
            return self.test_results['dev_environment']
            
        except Exception as e:
            self.test_results['dev_environment'] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"  ❌ Development environment test failed: {e}")
            return self.test_results['dev_environment']
    
    def test_config_management(self) -> Dict[str, Any]:
        """Test configuration management."""
        print("\n⚙️ Testing Configuration Management...")
        
        try:
            config_manager = ConfigurationManager(str(self.temp_dir))
            
            # Test configuration detection
            existing_configs = config_manager.detect_existing_configs()
            assert len(existing_configs) > 0, "Should detect existing configurations"
            
            # Test configuration validation
            package_json_path = 'package.json'
            is_valid, errors = config_manager.validate_configuration('package_json', package_json_path)
            assert is_valid, f"package.json should be valid: {errors}"
            
            # Test configuration report
            report = config_manager.generate_config_report()
            assert 'existing_configs' in report, "Report should include existing configs"
            assert 'validation_results' in report, "Report should include validation results"
            assert 'recommendations' in report, "Report should include recommendations"
            
            # Test backup creation
            backup_path = config_manager.create_config_backup()
            assert Path(backup_path).exists(), "Backup directory should be created"
            
            self.test_results['config_management'] = {
                'status': 'passed',
                'configs_detected': sum(len(files) for files in existing_configs.values()),
                'validation_passed': is_valid,
                'backup_created': True,
                'report_generated': True
            }
            
            print("  ✅ Configuration management test passed")
            return self.test_results['config_management']
            
        except Exception as e:
            self.test_results['config_management'] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"  ❌ Configuration management test failed: {e}")
            return self.test_results['config_management']
    
    def test_end_to_end_integration(self) -> Dict[str, Any]:
        """Test complete end-to-end integration workflow."""
        print("\n🔄 Testing End-to-End Integration...")
        
        try:
            # Simulate complete project setup workflow
            languages = ['javascript', 'python']
            
            # Step 1: Set up linting
            linting = LintingIntegration(str(self.temp_dir))
            linting_result = linting.setup_linting_for_project(languages)
            
            # Step 2: Set up testing
            testing = TestingIntegration(str(self.temp_dir))
            testing.setup_testing_framework('jest')
            testing.setup_testing_framework('pytest')
            
            # Step 3: Set up CI/CD
            cicd = CICDIntegration(str(self.temp_dir))
            needs = cicd.detect_deployment_needs()
            cicd.setup_cicd_for_project('github')
            
            # Step 4: Set up development environment
            dev_env = DevEnvironmentSetup(str(self.temp_dir))
            dev_env.setup_dev_environment(languages)
            
            # Step 5: Validate all configurations
            config_manager = ConfigurationManager(str(self.temp_dir))
            final_report = config_manager.generate_config_report()
            
            # Verify complete setup
            expected_files = [
                '.eslintrc.json',
                '.prettierrc.json',
                'jest.config.js',
                '.github/workflows/ci.yml',
                'Dockerfile',
                '.vscode/settings.json',
                '.env.example'
            ]
            
            missing_files = []
            for file in expected_files:
                if not (self.temp_dir / file).exists():
                    missing_files.append(file)
            
            assert len(missing_files) == 0, f"Missing files: {missing_files}"
            
            self.test_results['end_to_end_integration'] = {
                'status': 'passed',
                'workflow_steps_completed': 5,
                'total_files_created': len([f for f in self.temp_dir.rglob('*') if f.is_file()]),
                'missing_files': missing_files,
                'final_validation': 'passed'
            }
            
            print("  ✅ End-to-end integration test passed")
            return self.test_results['end_to_end_integration']
            
        except Exception as e:
            self.test_results['end_to_end_integration'] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"  ❌ End-to-end integration test failed: {e}")
            return self.test_results['end_to_end_integration']
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites."""
        print("🧪 Running Tool Integration Test Suite")
        print("=" * 50)
        
        # Run individual test suites
        self.test_linting_integration()
        self.test_testing_integration()
        self.test_cicd_integration()
        self.test_dev_environment()
        self.test_config_management()
        self.test_end_to_end_integration()
        
        # Determine overall status
        failed_tests = [
            name for name, result in self.test_results.items()
            if isinstance(result, dict) and result.get('status') == 'failed'
        ]
        
        if len(failed_tests) == 0:
            self.test_results['overall_status'] = 'passed'
            print("\n🎉 All tests passed!")
        else:
            self.test_results['overall_status'] = 'failed'
            print(f"\n❌ {len(failed_tests)} test(s) failed: {failed_tests}")
        
        # Print summary
        self.print_test_summary()
        
        return self.test_results
    
    def print_test_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        for test_name, result in self.test_results.items():
            if test_name == 'overall_status':
                continue
                
            status_icon = "✅" if result.get('status') == 'passed' else "❌"
            print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result.get('status', 'unknown')}")
            
            if result.get('status') == 'failed':
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n🎯 Overall Status: {self.test_results['overall_status'].upper()}")
        print("=" * 50)
    
    def cleanup(self):
        """Clean up test environment."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up test directory: {self.temp_dir}")

def main():
    """Main test execution."""
    test_suite = ToolIntegrationTestSuite()
    
    try:
        results = test_suite.run_all_tests()
        
        # Save results to file
        results_file = Path('tool_integration_test_results.json')
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        # Return appropriate exit code
        return 0 if results['overall_status'] == 'passed' else 1
        
    finally:
        test_suite.cleanup()

if __name__ == "__main__":
    sys.exit(main())
