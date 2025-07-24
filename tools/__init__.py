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
from .venv_manager import (
    VirtualEnvironmentManager,
    VenvInfo,
    VenvConfig,
    ensure_python_venv,
    get_venv_python_command,
    wrap_python_command
)
from .git_manager import (
    GitOperationsManager,
    GitStatus,
    CommitRecommendation,
    PushRecommendation,
    CollaborationInfo,
    get_git_status,
    should_commit_now,
    should_push_now
)
from .command_executor import (
    PythonCommandExecutor,
    CommandResult,
    ExecutionContext,
    execute_with_venv,
    run_python_with_venv,
    get_project_recommendations
)

__all__ = [
    'LintingIntegration',
    'TestingIntegration', 
    'CICDIntegration',
    'DevEnvironmentSetup',
    'ConfigurationManager',
    'VirtualEnvironmentManager',
    'GitOperationsManager',
    'PythonCommandExecutor',
    'CommandResult',
    'ExecutionContext',
    'execute_with_venv',
    'run_python_with_venv',
    'get_project_recommendations',
    'VenvInfo',
    'VenvConfig',
    'ensure_python_venv',
    'get_venv_python_command',
    'wrap_python_command',
    'GitStatus',
    'CommitRecommendation',
    'PushRecommendation',
    'CollaborationInfo',
    'get_git_status',
    'should_commit_now',
    'should_push_now'
]

__version__ = '1.0.0'
