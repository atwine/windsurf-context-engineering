"""
Development Tool Ecosystem Integration
=====================================

This module provides integration with popular development tools including:
- Linting tools (ESLint, Prettier, Black, Pylint)
- Testing frameworks (Jest, Pytest, Cypress)
- CI/CD pipelines (GitHub Actions, GitLab CI)
- Development environments (VS Code, Docker)
- Configuration management

The tool integration system enables seamless workflow automation and
ensures consistent development practices across projects.
"""

from .linting_integration import LintingIntegration
from .testing_integration import TestingIntegration
from .cicd_integration import CICDIntegration
from .dev_environment import DevEnvironmentSetup
from .config_manager import ConfigurationManager

__all__ = [
    'LintingIntegration',
    'TestingIntegration', 
    'CICDIntegration',
    'DevEnvironmentSetup',
    'ConfigurationManager'
]

__version__ = '1.0.0'
