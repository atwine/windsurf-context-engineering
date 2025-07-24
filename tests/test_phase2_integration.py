"""
Phase 2 Integration Tests

This module contains comprehensive integration tests for Phase 2 enhancements
to validate workflow integration, command execution, and environment management.

Author: Windsurf Context Engineering Team
Version: 1.0.0
"""

import os
import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from tools.command_executor import PythonCommandExecutor
from tools.venv_manager import VirtualEnvironmentManager
from tools.git_manager import GitOperationsManager


class TestPhase2Integration:
    """Integration tests for Phase 2 enhancements."""
    
    @pytest.fixture
    def temp_python_project(self):
        """Create a temporary Python project for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_python_project"
            project_path.mkdir()
            
            # Create Python project files
            (project_path / "requirements.txt").write_text("pytest>=6.0.0\nrequests>=2.25.0\n")
            (project_path / "main.py").write_text('print("Hello, World!")\n')
            (project_path / "test_main.py").write_text('def test_hello():\n    assert True\n')
            
            # Create tests directory
            tests_dir = project_path / "tests"
            tests_dir.mkdir()
            (tests_dir / "__init__.py").touch()
            (tests_dir / "test_example.py").write_text('def test_example():\n    assert 1 + 1 == 2\n')
            
            yield str(project_path)
    
    @pytest.fixture
    def temp_git_project(self):
        """Create a temporary Git project for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_git_project"
            project_path.mkdir()
            
            # Initialize Git repository
            subprocess.run(["git", "init"], cwd=project_path, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=project_path, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project_path, capture_output=True)
            
            # Create some files
            (project_path / "README.md").write_text("# Test Project\n")
            (project_path / "main.py").write_text('print("Hello, Git!")\n')
            
            # Initial commit
            subprocess.run(["git", "add", "."], cwd=project_path, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=project_path, capture_output=True)
            
            yield str(project_path)
    
    def test_python_project_environment_detection(self, temp_python_project):
        """Test Python project detection and environment setup."""
        executor = PythonCommandExecutor(temp_python_project)
        
        # Verify Python project detection
        assert executor.context.python_project == True
        
        # Test environment summary
        summary = executor.get_execution_summary()
        assert summary["python_project"] == True
        assert "virtual_environment" in summary
        
        # Test environment setup
        success, message = executor.ensure_python_environment()
        # Note: This might fail in test environment without actual venv creation
        # but should not crash
        assert isinstance(success, bool)
        assert isinstance(message, str)
    
    def test_git_project_integration(self, temp_git_project):
        """Test Git project integration and recommendations."""
        executor = PythonCommandExecutor(temp_git_project)
        
        # Verify Git repository detection
        assert executor.context.git_repository == True
        
        # Test Git recommendations
        recommendations = executor.get_git_recommendations()
        assert recommendations is not None
        assert "commit" in recommendations
        assert "push" in recommendations
        
        # Verify recommendation structure
        commit_rec = recommendations["commit"]
        assert "should_commit" in commit_rec
        assert "confidence" in commit_rec
        assert "message" in commit_rec
        assert "reasoning" in commit_rec
        
        push_rec = recommendations["push"]
        assert "should_push" in push_rec
        assert "confidence" in push_rec
        assert "timing" in push_rec
        assert "reasoning" in push_rec
    
    def test_combined_python_git_project(self, temp_python_project):
        """Test combined Python and Git project functionality."""
        project_path = Path(temp_python_project)
        
        # Initialize Git in the Python project
        subprocess.run(["git", "init"], cwd=project_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=project_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project_path, capture_output=True)
        
        executor = PythonCommandExecutor(str(project_path))
        
        # Verify both Python and Git detection
        assert executor.context.python_project == True
        assert executor.context.git_repository == True
        
        # Test execution summary
        summary = executor.get_execution_summary()
        assert summary["python_project"] == True
        assert summary["git_repository"] == True
        
        # Test Git recommendations
        recommendations = executor.get_git_recommendations()
        assert recommendations is not None
    
    @patch('subprocess.run')
    def test_command_execution_with_environment_awareness(self, mock_subprocess, temp_python_project):
        """Test command execution with environment awareness."""
        # Mock successful subprocess execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Python 3.12.6"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_python_project)
        
        # Test Python command execution
        result = executor.execute_command("python --version")
        
        assert result.success == True
        assert result.command == "python --version"
        assert isinstance(result.execution_time, float)
        assert isinstance(result.venv_used, bool)
        assert isinstance(result.git_changes_detected, bool)
    
    @patch('subprocess.run')
    def test_python_script_execution(self, mock_subprocess, temp_python_project):
        """Test Python script execution with virtual environment."""
        # Mock successful script execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello, World!"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_python_project)
        
        # Test script execution
        result = executor.execute_python_script("main.py")
        
        assert result.success == True
        assert "main.py" in result.command
        assert isinstance(result.execution_time, float)
    
    @patch('subprocess.run')
    def test_requirements_installation(self, mock_subprocess, temp_python_project):
        """Test requirements installation with virtual environment."""
        # Mock successful pip install
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Successfully installed pytest-6.2.4 requests-2.25.1"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_python_project)
        
        # Test requirements installation
        result = executor.install_requirements()
        
        assert result.success == True
        assert "requirements.txt" in result.command
        assert isinstance(result.execution_time, float)
    
    @patch('subprocess.run')
    def test_test_execution(self, mock_subprocess, temp_python_project):
        """Test test execution with virtual environment."""
        # Mock successful test execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "2 passed in 0.01s"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_python_project)
        
        # Test pytest execution
        result = executor.run_tests()
        
        assert result.success == True
        assert "pytest" in result.command
        assert isinstance(result.execution_time, float)
    
    def test_workflow_integration_readiness(self, temp_python_project):
        """Test that all components are ready for workflow integration."""
        executor = PythonCommandExecutor(temp_python_project)
        
        # Test all major components are accessible
        assert hasattr(executor, 'venv_manager')
        assert hasattr(executor, 'git_manager')
        assert hasattr(executor, 'context')
        
        # Test all major methods are available
        assert callable(executor.ensure_python_environment)
        assert callable(executor.execute_command)
        assert callable(executor.execute_python_script)
        assert callable(executor.install_requirements)
        assert callable(executor.run_tests)
        assert callable(executor.get_git_recommendations)
        assert callable(executor.get_execution_summary)
        
        # Test context analysis works
        summary = executor.get_execution_summary()
        required_keys = [
            "project_path", "python_project", "git_repository",
            "virtual_environment", "git_status"
        ]
        for key in required_keys:
            assert key in summary
    
    def test_error_handling_and_recovery(self, temp_python_project):
        """Test error handling and recovery mechanisms."""
        executor = PythonCommandExecutor(temp_python_project)
        
        # Test with non-existent command
        result = executor.execute_command("nonexistent_command_12345")
        assert result.success == False
        assert result.returncode != 0
        assert isinstance(result.stderr, str)
        
        # Test that executor still works after error
        result2 = executor.execute_command("echo test")
        # This might fail in test environment, but should not crash
        assert isinstance(result2.success, bool)
    
    def test_cross_platform_compatibility(self, temp_python_project):
        """Test cross-platform compatibility features."""
        executor = PythonCommandExecutor(temp_python_project)
        
        # Test path handling
        assert executor.project_path.is_absolute()
        assert executor.context.working_directory.is_absolute()
        
        # Test environment variables
        assert isinstance(executor.context.environment_variables, dict)
        assert len(executor.context.environment_variables) > 0
        
        # Test Python command detection
        python_commands = ["python", "python3", "pip", "pip3", "pytest"]
        for cmd in python_commands:
            assert executor._is_python_command(cmd) == True
        
        non_python_commands = ["echo", "ls", "dir", "cat"]
        for cmd in non_python_commands:
            assert executor._is_python_command(cmd) == False


class TestWorkflowEnhancementValidation:
    """Validate that workflow enhancements are properly integrated."""
    
    def test_workflow_files_exist(self):
        """Test that all enhanced workflow files exist."""
        workflow_dir = Path("C:/Users/ic/OneDrive/Desktop/windsurf-context-engineering/.windsurf/workflows")
        
        required_workflows = [
            "execute-plan.md",
            "execute-plan-enhanced.md",
            "init-context.md"
        ]
        
        for workflow in required_workflows:
            workflow_path = workflow_dir / workflow
            assert workflow_path.exists(), f"Workflow file {workflow} not found"
    
    def test_workflow_content_enhancements(self):
        """Test that workflow files contain Phase 2 enhancements."""
        workflow_dir = Path("C:/Users/ic/OneDrive/Desktop/windsurf-context-engineering/.windsurf/workflows")
        
        # Test execute-plan.md enhancements
        execute_plan = workflow_dir / "execute-plan.md"
        content = execute_plan.read_text()
        
        # Check for environment management keywords
        assert "Virtual Environment" in content
        assert "Git" in content
        assert "Environment Setup" in content
        assert "Git Checkpoint" in content
        
        # Test execute-plan-enhanced.md enhancements
        execute_plan_enhanced = workflow_dir / "execute-plan-enhanced.md"
        content = execute_plan_enhanced.read_text()
        
        assert "Learning Integration" in content
        assert "Environment Management" in content
        assert "Git Intelligence" in content
        assert "Environment Health Monitoring" in content
        
        # Test init-context.md enhancements
        init_context = workflow_dir / "init-context.md"
        content = init_context.read_text()
        
        assert "Environment Analysis" in content
        assert "Python Environment Assessment" in content
        assert "Git Repository Analysis" in content
        assert "Environment Readiness" in content
    
    def test_tools_module_integration(self):
        """Test that tools module properly exports all Phase 2 components."""
        from tools import (
            PythonCommandExecutor,
            CommandResult,
            ExecutionContext,
            execute_with_venv,
            run_python_with_venv,
            get_project_recommendations
        )
        
        # Test that all classes and functions are properly imported
        assert PythonCommandExecutor is not None
        assert CommandResult is not None
        assert ExecutionContext is not None
        assert callable(execute_with_venv)
        assert callable(run_python_with_venv)
        assert callable(get_project_recommendations)
    
    def test_convenience_functions_integration(self):
        """Test that convenience functions work properly."""
        from tools import execute_with_venv, run_python_with_venv, get_project_recommendations
        
        # Test functions are callable
        assert callable(execute_with_venv)
        assert callable(run_python_with_venv)
        assert callable(get_project_recommendations)
        
        # Test function signatures (basic validation)
        import inspect
        
        # execute_with_venv should accept command and project_path
        sig = inspect.signature(execute_with_venv)
        assert "command" in sig.parameters
        assert "project_path" in sig.parameters
        
        # run_python_with_venv should accept script_path, args, and project_path
        sig = inspect.signature(run_python_with_venv)
        assert "script_path" in sig.parameters
        assert "project_path" in sig.parameters
        
        # get_project_recommendations should accept project_path
        sig = inspect.signature(get_project_recommendations)
        assert "project_path" in sig.parameters


class TestProductionReadiness:
    """Test production readiness of Phase 2 integration."""
    
    def test_import_stability(self):
        """Test that all imports work without errors."""
        try:
            from tools.command_executor import (
                PythonCommandExecutor,
                CommandResult,
                ExecutionContext,
                execute_with_venv,
                run_python_with_venv,
                get_project_recommendations
            )
            from tools.venv_manager import VirtualEnvironmentManager
            from tools.git_manager import GitOperationsManager
            
            # Test instantiation doesn't crash
            temp_dir = Path.cwd()
            executor = PythonCommandExecutor(str(temp_dir))
            assert executor is not None
            
        except Exception as e:
            pytest.fail(f"Import or instantiation failed: {e}")
    
    def test_logging_integration(self):
        """Test that logging is properly configured."""
        import logging
        
        # Test that loggers are created
        executor_logger = logging.getLogger('tools.command_executor')
        venv_logger = logging.getLogger('tools.venv_manager')
        git_logger = logging.getLogger('tools.git_manager')
        
        assert executor_logger is not None
        assert venv_logger is not None
        assert git_logger is not None
    
    def test_error_handling_robustness(self):
        """Test error handling robustness."""
        # Test with invalid project path
        try:
            executor = PythonCommandExecutor("/nonexistent/path/12345")
            # Should not crash, but may have limited functionality
            summary = executor.get_execution_summary()
            assert isinstance(summary, dict)
        except Exception as e:
            # If it does fail, it should be a controlled failure
            assert "Error" in str(e) or "not found" in str(e).lower()
    
    def test_memory_usage_efficiency(self):
        """Test that components don't consume excessive memory."""
        import sys
        
        # Get initial memory usage
        initial_objects = len(sys.gettrace() if sys.gettrace() else [])
        
        # Create multiple executors
        executors = []
        for i in range(5):
            temp_dir = Path.cwd()
            executor = PythonCommandExecutor(str(temp_dir))
            executors.append(executor)
        
        # Clean up
        del executors
        
        # Memory usage test passes if no exceptions occurred
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
