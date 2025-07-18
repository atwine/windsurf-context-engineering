#!/usr/bin/env python3
"""
Testing Framework Integration
============================

Integrates popular testing frameworks for comprehensive test automation:
- Jest for JavaScript testing
- Pytest for Python testing  
- Cypress for E2E testing
- React Testing Library integration
- Test template generation
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class TestingIntegration:
    """Manages integration with testing frameworks."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.testing_configs = {}
        
    def detect_testing_needs(self) -> Dict[str, List[str]]:
        """Detect what testing frameworks are needed."""
        needs = {
            'unit': [],
            'integration': [],
            'e2e': [],
            'component': []
        }
        
        # JavaScript/TypeScript - Jest
        if self._has_js_files():
            needs['unit'].append('jest')
            if self._has_react():
                needs['component'].append('react-testing-library')
        
        # Python - Pytest
        if self._has_python_files():
            needs['unit'].append('pytest')
            needs['integration'].append('pytest')
        
        # Web applications - Cypress
        if self._is_web_app():
            needs['e2e'].append('cypress')
        
        return needs
    
    def setup_testing_framework(self, framework: str) -> Dict[str, Any]:
        """Set up specific testing framework."""
        if framework == 'jest':
            return self._setup_jest()
        elif framework == 'pytest':
            return self._setup_pytest()
        elif framework == 'cypress':
            return self._setup_cypress()
        elif framework == 'react-testing-library':
            return self._setup_react_testing_library()
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _setup_jest(self) -> Dict[str, Any]:
        """Set up Jest configuration."""
        config = {
            "testEnvironment": "jsdom",
            "setupFilesAfterEnv": ["<rootDir>/src/setupTests.js"],
            "moduleNameMapping": {
                "\\.(css|less|scss|sass)$": "identity-obj-proxy"
            },
            "collectCoverageFrom": [
                "src/**/*.{js,jsx,ts,tsx}",
                "!src/index.js",
                "!src/reportWebVitals.js"
            ],
            "coverageThreshold": {
                "global": {
                    "branches": 80,
                    "functions": 80,
                    "lines": 80,
                    "statements": 80
                }
            }
        }
        
        # Write jest.config.js
        config_path = self.project_root / 'jest.config.js'
        with open(config_path, 'w') as f:
            f.write(f"module.exports = {json.dumps(config, indent=2)};")
        
        # Create setupTests.js
        setup_content = """
import '@testing-library/jest-dom';

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  warn: jest.fn(),
  error: jest.fn(),
};
"""
        
        src_dir = self.project_root / 'src'
        src_dir.mkdir(exist_ok=True)
        
        setup_path = src_dir / 'setupTests.js'
        with open(setup_path, 'w') as f:
            f.write(setup_content.strip())
        
        # Update package.json
        self._update_package_json_testing('jest')
        
        logger.info(f"Jest configuration created: {config_path}")
        return config
    
    def _setup_pytest(self) -> Dict[str, Any]:
        """Set up Pytest configuration."""
        config_content = """
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --cov=src --cov-report=html --cov-report=term-missing"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
"""
        
        # Add to pyproject.toml
        pyproject_path = self.project_root / 'pyproject.toml'
        if pyproject_path.exists():
            with open(pyproject_path, 'a') as f:
                f.write(config_content)
        else:
            with open(pyproject_path, 'w') as f:
                f.write(config_content.strip())
        
        # Create tests directory structure
        tests_dir = self.project_root / 'tests'
        tests_dir.mkdir(exist_ok=True)
        
        # Create conftest.py
        conftest_content = """
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

@pytest.fixture
def sample_data():
    return {"test": "data"}

@pytest.fixture
def mock_config():
    return {
        "debug": True,
        "testing": True
    }
"""
        
        conftest_path = tests_dir / 'conftest.py'
        with open(conftest_path, 'w') as f:
            f.write(conftest_content.strip())
        
        logger.info(f"Pytest configuration added to: {pyproject_path}")
        return {"config_file": str(pyproject_path)}
    
    def _setup_cypress(self) -> Dict[str, Any]:
        """Set up Cypress configuration."""
        config = {
            "baseUrl": "http://localhost:3000",
            "viewportWidth": 1280,
            "viewportHeight": 720,
            "video": False,
            "screenshotOnRunFailure": True,
            "defaultCommandTimeout": 10000,
            "requestTimeout": 10000,
            "responseTimeout": 10000,
            "e2e": {
                "setupNodeEvents": "(on, config) => {}",
                "specPattern": "cypress/e2e/**/*.cy.{js,jsx,ts,tsx}"
            }
        }
        
        # Write cypress.config.js
        config_path = self.project_root / 'cypress.config.js'
        with open(config_path, 'w') as f:
            f.write(f"const {{ defineConfig }} = require('cypress');\n\n")
            f.write(f"module.exports = defineConfig({json.dumps(config, indent=2)});")
        
        # Create cypress directory structure
        cypress_dir = self.project_root / 'cypress'
        cypress_dir.mkdir(exist_ok=True)
        
        (cypress_dir / 'e2e').mkdir(exist_ok=True)
        (cypress_dir / 'fixtures').mkdir(exist_ok=True)
        (cypress_dir / 'support').mkdir(exist_ok=True)
        
        # Create example test
        example_test = """
describe('App E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should display the app', () => {
    cy.contains('Welcome').should('be.visible');
  });

  it('should be accessible', () => {
    cy.injectAxe();
    cy.checkA11y();
  });
});
"""
        
        test_path = cypress_dir / 'e2e' / 'app.cy.js'
        with open(test_path, 'w') as f:
            f.write(example_test.strip())
        
        # Update package.json
        self._update_package_json_testing('cypress')
        
        logger.info(f"Cypress configuration created: {config_path}")
        return config
    
    def _setup_react_testing_library(self) -> Dict[str, Any]:
        """Set up React Testing Library."""
        # Create example component test
        test_content = """
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Example component test
describe('Component Tests', () => {
  test('renders component correctly', () => {
    render(<div>Test Component</div>);
    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });

  test('handles user interactions', () => {
    const handleClick = jest.fn();
    render(<button onClick={handleClick}>Click me</button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
"""
        
        src_dir = self.project_root / 'src'
        src_dir.mkdir(exist_ok=True)
        
        test_path = src_dir / 'App.test.js'
        with open(test_path, 'w') as f:
            f.write(test_content.strip())
        
        # Update package.json with RTL dependencies
        self._update_package_json_testing('react-testing-library')
        
        logger.info(f"React Testing Library setup complete")
        return {"example_test": str(test_path)}
    
    def _update_package_json_testing(self, framework: str):
        """Update package.json with testing dependencies and scripts."""
        package_json_path = self.project_root / 'package.json'
        
        if package_json_path.exists():
            with open(package_json_path) as f:
                package_data = json.load(f)
        else:
            package_data = {
                "name": self.project_root.name,
                "version": "1.0.0"
            }
        
        # Initialize sections
        if 'scripts' not in package_data:
            package_data['scripts'] = {}
        if 'devDependencies' not in package_data:
            package_data['devDependencies'] = {}
        
        # Add framework-specific dependencies and scripts
        if framework == 'jest':
            package_data['devDependencies'].update({
                "jest": "^29.0.0",
                "@testing-library/jest-dom": "^6.0.0",
                "identity-obj-proxy": "^3.0.0"
            })
            package_data['scripts'].update({
                "test": "jest",
                "test:watch": "jest --watch",
                "test:coverage": "jest --coverage"
            })
        
        elif framework == 'cypress':
            package_data['devDependencies'].update({
                "cypress": "^13.0.0",
                "cypress-axe": "^1.5.0"
            })
            package_data['scripts'].update({
                "cypress:open": "cypress open",
                "cypress:run": "cypress run",
                "test:e2e": "cypress run"
            })
        
        elif framework == 'react-testing-library':
            package_data['devDependencies'].update({
                "@testing-library/react": "^14.0.0",
                "@testing-library/user-event": "^14.0.0"
            })
        
        # Write updated package.json
        with open(package_json_path, 'w') as f:
            json.dump(package_data, f, indent=2)
        
        logger.info(f"Updated package.json for {framework}")
    
    def _has_js_files(self) -> bool:
        """Check if project has JavaScript files."""
        patterns = ['*.js', '*.jsx', '*.ts', '*.tsx']
        for pattern in patterns:
            if list(self.project_root.rglob(pattern)):
                return True
        return False
    
    def _has_python_files(self) -> bool:
        """Check if project has Python files."""
        return bool(list(self.project_root.rglob('*.py')))
    
    def _has_react(self) -> bool:
        """Check if project uses React."""
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    return 'react' in deps
            except:
                pass
        return False
    
    def _is_web_app(self) -> bool:
        """Check if project is a web application."""
        indicators = [
            'package.json',
            'index.html',
            'public/index.html',
            'src/index.js',
            'src/App.js'
        ]
        
        for indicator in indicators:
            if (self.project_root / indicator).exists():
                return True
        return False
    
    def generate_test_templates(self, test_type: str, component_name: str) -> str:
        """Generate test templates for different types."""
        if test_type == 'unit_js':
            return self._generate_js_unit_test(component_name)
        elif test_type == 'unit_py':
            return self._generate_python_unit_test(component_name)
        elif test_type == 'integration_py':
            return self._generate_python_integration_test(component_name)
        elif test_type == 'e2e':
            return self._generate_e2e_test(component_name)
        else:
            raise ValueError(f"Unknown test type: {test_type}")
    
    def _generate_js_unit_test(self, component_name: str) -> str:
        """Generate JavaScript unit test template."""
        return f"""
import {{ render, screen, fireEvent }} from '@testing-library/react';
import '@testing-library/jest-dom';
import {component_name} from './{component_name}';

describe('{component_name}', () => {{
  test('renders without crashing', () => {{
    render(<{component_name} />);
  }});

  test('displays expected content', () => {{
    render(<{component_name} />);
    // Add your assertions here
  }});

  test('handles user interactions', () => {{
    render(<{component_name} />);
    // Add interaction tests here
  }});
}});
"""
    
    def _generate_python_unit_test(self, module_name: str) -> str:
        """Generate Python unit test template."""
        return f"""
import pytest
from src.{module_name.lower()} import {module_name}

class Test{module_name}:
    def test_initialization(self):
        instance = {module_name}()
        assert instance is not None
    
    def test_basic_functionality(self):
        instance = {module_name}()
        # Add your test logic here
        pass
    
    def test_edge_cases(self):
        instance = {module_name}()
        # Test edge cases here
        pass
"""
    
    def _generate_python_integration_test(self, module_name: str) -> str:
        """Generate Python integration test template."""
        return f"""
import pytest
from src.{module_name.lower()} import {module_name}

class TestIntegration{module_name}:
    @pytest.fixture
    def setup_integration(self):
        # Setup integration test environment
        return {module_name}()
    
    def test_integration_workflow(self, setup_integration):
        # Test complete workflow
        pass
    
    def test_external_dependencies(self, setup_integration):
        # Test external service integration
        pass
"""
    
    def _generate_e2e_test(self, feature_name: str) -> str:
        """Generate E2E test template."""
        return f"""
describe('{feature_name} E2E Tests', () => {{
  beforeEach(() => {{
    cy.visit('/');
  }});

  it('should complete {feature_name.lower()} workflow', () => {{
    // Add your E2E test steps here
    cy.get('[data-testid="start-button"]').click();
    cy.url().should('include', '/{feature_name.lower()}');
  }});

  it('should handle error scenarios', () => {{
    // Test error handling
  }});
}});
"""

# Example usage
if __name__ == "__main__":
    testing = TestingIntegration()
    
    # Detect testing needs
    needs = testing.detect_testing_needs()
    print(f"Testing needs: {needs}")
    
    # Set up frameworks
    for category, frameworks in needs.items():
        for framework in frameworks:
            try:
                config = testing.setup_testing_framework(framework)
                print(f"Set up {framework}: {config}")
            except Exception as e:
                print(f"Failed to set up {framework}: {e}")
