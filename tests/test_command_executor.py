"""
Tests for PythonCommandExecutor

This module contains comprehensive tests for the PythonCommandExecutor class
and related functionality in the Windsurf Context Engineering Framework.

Author: Windsurf Context Engineering Team
Version: 1.0.0
"""

import os
import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from tools.command_executor import (
    PythonCommandExecutor,
    CommandResult,
    ExecutionContext,
    execute_with_venv,
    run_python_with_venv,
    get_project_recommendations
)
from tools.venv_manager import VenvInfo
from tools.git_manager import GitStatus


class TestPythonCommandExecutor:
    """Test cases for PythonCommandExecutor class."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            project_path.mkdir()
            yield str(project_path)
    
    @pytest.fixture
    def mock_venv_manager(self):
        """Mock VirtualEnvironmentManager for testing."""
        with patch('tools.command_executor.VirtualEnvironmentManager') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def mock_git_manager(self):
        """Mock GitOperationsManager for testing."""
        with patch('tools.command_executor.GitOperationsManager') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance
    
    def test_initialization(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test PythonCommandExecutor initialization."""
        # Setup mocks
        mock_venv_manager.detect_python_project.return_value = True
        mock_venv_manager.get_venv_info.return_value = VenvInfo(
            venv_path=Path(temp_project_dir) / "venv",
            python_executable=Path(temp_project_dir) / "venv" / "Scripts" / "python.exe",
            is_healthy=True,
            requirements_synced=True
        )
        mock_git_manager.get_git_status.return_value = GitStatus(
            staged_files=[],
            unstaged_files=[],
            untracked_files=[],
            is_clean=True,
            ahead=0,
            behind=0,
            current_branch="main"
        )
        
        # Create .git directory to simulate Git repository
        git_dir = Path(temp_project_dir) / ".git"
        git_dir.mkdir()
        
        executor = PythonCommandExecutor(temp_project_dir)
        
        assert executor.project_path == Path(temp_project_dir).resolve()
        assert executor.context.python_project == True
        assert executor.context.git_repository == True
        assert executor.context.working_directory == Path(temp_project_dir).resolve()
        
        mock_venv_manager.detect_python_project.assert_called_once()
        mock_git_manager.get_git_status.assert_called_once()
    
    def test_analyze_execution_context_python_project(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test execution context analysis for Python project."""
        # Setup Python project indicators
        (Path(temp_project_dir) / "requirements.txt").touch()
        (Path(temp_project_dir) / ".git").mkdir()
        
        mock_venv_manager.detect_python_project.return_value = True
        mock_venv_manager.get_venv_info.return_value = VenvInfo(
            venv_path=Path(temp_project_dir) / "venv",
            python_executable=Path(temp_project_dir) / "venv" / "Scripts" / "python.exe",
            is_healthy=True,
            requirements_synced=True
        )
        mock_git_manager.get_git_status.return_value = GitStatus(
            staged_files=[],
            unstaged_files=[],
            untracked_files=[],
            is_clean=True,
            ahead=0,
            behind=0,
            current_branch="main"
        )
        
        executor = PythonCommandExecutor(temp_project_dir)
        
        assert executor.context.python_project == True
        assert executor.context.git_repository == True
        assert executor.context.virtual_environment is not None
        assert executor.context.git_status is not None
    
    def test_analyze_execution_context_non_python_project(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test execution context analysis for non-Python project."""
        mock_venv_manager.detect_python_project.return_value = False
        
        executor = PythonCommandExecutor(temp_project_dir)
        
        assert executor.context.python_project == False
        assert executor.context.virtual_environment is None
        mock_venv_manager.get_venv_info.assert_not_called()
    
    def test_ensure_python_environment_non_python_project(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test ensure_python_environment for non-Python project."""
        mock_venv_manager.detect_python_project.return_value = False
        
        executor = PythonCommandExecutor(temp_project_dir)
        success, message = executor.ensure_python_environment()
        
        assert success == True
        assert "Not a Python project" in message
    
    def test_ensure_python_environment_existing_venv(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test ensure_python_environment with existing virtual environment."""
        mock_venv_manager.detect_python_project.return_value = True
        mock_venv_manager.venv_exists.return_value = True
        mock_venv_manager.validate_venv.return_value = True
        mock_venv_manager.get_venv_info.return_value = VenvInfo(
            venv_path=Path(temp_project_dir) / "venv",
            python_executable=Path(temp_project_dir) / "venv" / "Scripts" / "python.exe",
            is_healthy=True,
            requirements_synced=True
        )
        
        executor = PythonCommandExecutor(temp_project_dir)
        success, message = executor.ensure_python_environment()
        
        assert success == True
        assert "Virtual environment is ready" in message
        mock_venv_manager.validate_venv.assert_called_once()
    
    def test_ensure_python_environment_create_venv(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test ensure_python_environment creating new virtual environment."""
        mock_venv_manager.detect_python_project.return_value = True
        mock_venv_manager.venv_exists.return_value = False
        mock_venv_manager.create_venv.return_value = (True, "Virtual environment created successfully")
        mock_venv_manager.get_venv_info.return_value = VenvInfo(
            venv_path=Path(temp_project_dir) / "venv",
            python_executable=Path(temp_project_dir) / "venv" / "Scripts" / "python.exe",
            is_healthy=True,
            requirements_synced=True
        )
        
        executor = PythonCommandExecutor(temp_project_dir)
        success, message = executor.ensure_python_environment()
        
        assert success == True
        assert "Virtual environment is ready" in message
        mock_venv_manager.create_venv.assert_called_once()
    
    def test_ensure_python_environment_create_venv_failure(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test ensure_python_environment with venv creation failure."""
        mock_venv_manager.detect_python_project.return_value = True
        mock_venv_manager.venv_exists.return_value = False
        mock_venv_manager.create_venv.return_value = (False, "Failed to create virtual environment")
        
        executor = PythonCommandExecutor(temp_project_dir)
        success, message = executor.ensure_python_environment()
        
        assert success == False
        assert "Failed to create virtual environment" in message
    
    @patch('subprocess.run')
    def test_execute_command_basic(self, mock_subprocess, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test basic command execution."""
        mock_venv_manager.detect_python_project.return_value = False
        
        # Mock subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Command output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_project_dir)
        result = executor.execute_command("echo hello")
        
        assert result.success == True
        assert result.returncode == 0
        assert result.stdout == "Command output"
        assert result.stderr == ""
        assert result.command == "echo hello"
        assert result.venv_used == False
        
        mock_subprocess.assert_called_once()
    
    @patch('subprocess.run')
    def test_execute_command_with_venv(self, mock_subprocess, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test command execution with virtual environment."""
        mock_venv_manager.detect_python_project.return_value = True
        mock_venv_manager.venv_exists.return_value = True
        mock_venv_manager.validate_venv.return_value = True
        mock_venv_manager.get_venv_info.return_value = VenvInfo(
            venv_path=Path(temp_project_dir) / "venv",
            python_executable=Path(temp_project_dir) / "venv" / "Scripts" / "python.exe",
            is_healthy=True,
            requirements_synced=True
        )
        mock_venv_manager.get_python_command.return_value = "venv/Scripts/python.exe -m pytest"
        
        # Mock subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Test output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_project_dir)
        result = executor.execute_command("python -m pytest")
        
        assert result.success == True
        assert result.venv_used == True
        mock_venv_manager.get_python_command.assert_called_once_with("python -m pytest")
    
    @patch('subprocess.run')
    def test_execute_command_failure(self, mock_subprocess, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test command execution failure."""
        mock_venv_manager.detect_python_project.return_value = False
        
        # Mock subprocess result with failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed"
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_project_dir)
        result = executor.execute_command("false")
        
        assert result.success == False
        assert result.returncode == 1
        assert result.stderr == "Command failed"
    
    @patch('subprocess.run')
    def test_execute_command_timeout(self, mock_subprocess, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test command execution timeout."""
        mock_venv_manager.detect_python_project.return_value = False
        
        # Mock subprocess timeout
        mock_subprocess.side_effect = subprocess.TimeoutExpired("sleep 10", 5)
        
        executor = PythonCommandExecutor(temp_project_dir)
        result = executor.execute_command("sleep 10", timeout=5)
        
        assert result.success == False
        assert result.returncode == -1
        assert "timed out" in result.stderr
    
    @patch('subprocess.run')
    def test_execute_python_script(self, mock_subprocess, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test Python script execution."""
        mock_venv_manager.detect_python_project.return_value = True
        mock_venv_manager.venv_exists.return_value = True
        mock_venv_manager.validate_venv.return_value = True
        mock_venv_manager.get_venv_info.return_value = VenvInfo(
            venv_path=Path(temp_project_dir) / "venv",
            python_executable=Path(temp_project_dir) / "venv" / "Scripts" / "python.exe",
            is_healthy=True,
            requirements_synced=True
        )
        mock_venv_manager.get_python_command.return_value = "venv/Scripts/python.exe script.py arg1 arg2"
        
        # Mock subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Script output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_project_dir)
        result = executor.execute_python_script("script.py", ["arg1", "arg2"])
        
        assert result.success == True
        assert result.venv_used == True
        mock_venv_manager.get_python_command.assert_called_once_with("python script.py arg1 arg2")
    
    @patch('subprocess.run')
    def test_install_requirements(self, mock_subprocess, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test requirements installation."""
        mock_venv_manager.detect_python_project.return_value = True
        mock_venv_manager.venv_exists.return_value = True
        mock_venv_manager.validate_venv.return_value = True
        mock_venv_manager.get_venv_info.return_value = VenvInfo(
            venv_path=Path(temp_project_dir) / "venv",
            python_executable=Path(temp_project_dir) / "venv" / "Scripts" / "python.exe",
            is_healthy=True,
            requirements_synced=True
        )
        mock_venv_manager.get_python_command.return_value = "venv/Scripts/pip.exe install -r requirements.txt"
        
        # Mock subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Successfully installed packages"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_project_dir)
        result = executor.install_requirements()
        
        assert result.success == True
        assert result.venv_used == True
        mock_venv_manager.get_python_command.assert_called_once_with("pip install -r requirements.txt")
    
    @patch('subprocess.run')
    def test_run_tests_pytest(self, mock_subprocess, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test running tests with pytest."""
        mock_venv_manager.detect_python_project.return_value = True
        mock_venv_manager.venv_exists.return_value = True
        mock_venv_manager.validate_venv.return_value = True
        mock_venv_manager.get_venv_info.return_value = VenvInfo(
            venv_path=Path(temp_project_dir) / "venv",
            python_executable=Path(temp_project_dir) / "venv" / "Scripts" / "python.exe",
            is_healthy=True,
            requirements_synced=True
        )
        mock_venv_manager.get_python_command.return_value = "venv/Scripts/python.exe -m pytest tests -v"
        
        # Mock subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "All tests passed"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_project_dir)
        result = executor.run_tests()
        
        assert result.success == True
        assert result.venv_used == True
        mock_venv_manager.get_python_command.assert_called_once_with("python -m pytest tests -v")
    
    @patch('subprocess.run')
    def test_run_tests_unittest(self, mock_subprocess, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test running tests with unittest."""
        mock_venv_manager.detect_python_project.return_value = True
        mock_venv_manager.venv_exists.return_value = True
        mock_venv_manager.validate_venv.return_value = True
        mock_venv_manager.get_venv_info.return_value = VenvInfo(
            venv_path=Path(temp_project_dir) / "venv",
            python_executable=Path(temp_project_dir) / "venv" / "Scripts" / "python.exe",
            is_healthy=True,
            requirements_synced=True
        )
        mock_venv_manager.get_python_command.return_value = "venv/Scripts/python.exe -m unittest discover tests"
        
        # Mock subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "All tests passed"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_project_dir)
        result = executor.run_tests(framework="unittest")
        
        assert result.success == True
        assert result.venv_used == True
        mock_venv_manager.get_python_command.assert_called_once_with("python -m unittest discover tests")
    
    def test_run_tests_unsupported_framework(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test running tests with unsupported framework."""
        mock_venv_manager.detect_python_project.return_value = True
        
        executor = PythonCommandExecutor(temp_project_dir)
        
        with pytest.raises(ValueError, match="Unsupported test framework"):
            executor.run_tests(framework="nose")
    
    def test_get_git_recommendations(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test getting Git recommendations."""
        from tools.git_manager import CommitRecommendation, PushRecommendation
        
        mock_venv_manager.detect_python_project.return_value = False
        
        # Create .git directory to simulate Git repository
        git_dir = Path(temp_project_dir) / ".git"
        git_dir.mkdir()
        
        # Mock Git recommendations
        commit_rec = CommitRecommendation(
            should_commit=True,
            confidence=0.85,
            suggested_message="feat: add new feature",
            reasoning="Significant changes detected"
        )
        push_rec = PushRecommendation(
            should_push=True,
            confidence=0.90,
            recommended_timing="now",
            reasoning="All tests passing, ready to push"
        )
        
        mock_git_manager.get_commit_recommendation.return_value = commit_rec
        mock_git_manager.get_push_recommendation.return_value = push_rec
        
        executor = PythonCommandExecutor(temp_project_dir)
        recommendations = executor.get_git_recommendations()
        
        assert recommendations is not None
        assert recommendations["commit"]["should_commit"] == True
        assert recommendations["commit"]["confidence"] == 0.85
        assert recommendations["push"]["should_push"] == True
        assert recommendations["push"]["confidence"] == 0.90
    
    def test_get_git_recommendations_non_git_project(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test getting Git recommendations for non-Git project."""
        mock_venv_manager.detect_python_project.return_value = False
        
        executor = PythonCommandExecutor(temp_project_dir)
        recommendations = executor.get_git_recommendations()
        
        assert recommendations is None
    
    def test_is_python_command(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test Python command detection."""
        mock_venv_manager.detect_python_project.return_value = False
        
        executor = PythonCommandExecutor(temp_project_dir)
        
        assert executor._is_python_command("python") == True
        assert executor._is_python_command("python3") == True
        assert executor._is_python_command("pip") == True
        assert executor._is_python_command("pytest") == True
        assert executor._is_python_command("flake8") == True
        assert executor._is_python_command("black") == True
        assert executor._is_python_command("mypy") == True
        assert executor._is_python_command("echo") == False
        assert executor._is_python_command("ls") == False
    
    def test_get_execution_summary(self, temp_project_dir, mock_venv_manager, mock_git_manager):
        """Test execution summary generation."""
        mock_venv_manager.detect_python_project.return_value = True
        mock_venv_manager.get_venv_info.return_value = VenvInfo(
            venv_path=Path(temp_project_dir) / "venv",
            python_executable=Path(temp_project_dir) / "venv" / "Scripts" / "python.exe",
            is_healthy=True,
            requirements_synced=True
        )
        mock_git_manager.get_git_status.return_value = GitStatus(
            staged_files=["file1.py"],
            unstaged_files=["file2.py"],
            untracked_files=["file3.py"],
            is_clean=False,
            ahead=1,
            behind=0,
            current_branch="main"
        )
        
        # Create .git directory to simulate Git repository
        git_dir = Path(temp_project_dir) / ".git"
        git_dir.mkdir()
        
        executor = PythonCommandExecutor(temp_project_dir)
        summary = executor.get_execution_summary()
        
        assert summary["python_project"] == True
        assert summary["git_repository"] == True
        assert summary["virtual_environment"]["exists"] == True
        assert summary["virtual_environment"]["is_healthy"] == True
        assert summary["git_status"]["staged_files"] == 1
        assert summary["git_status"]["unstaged_files"] == 1
        assert summary["git_status"]["untracked_files"] == 1
        assert summary["git_status"]["is_clean"] == False


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            project_path.mkdir()
            yield str(project_path)
    
    @patch('tools.command_executor.PythonCommandExecutor')
    def test_execute_with_venv(self, mock_executor_class, temp_project_dir):
        """Test execute_with_venv convenience function."""
        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor
        
        expected_result = CommandResult(
            success=True,
            returncode=0,
            stdout="output",
            stderr="",
            command="echo hello",
            execution_time=0.1,
            venv_used=False,
            git_changes_detected=False
        )
        mock_executor.execute_command.return_value = expected_result
        
        result = execute_with_venv("echo hello", temp_project_dir)
        
        assert result == expected_result
        mock_executor_class.assert_called_once_with(temp_project_dir)
        mock_executor.execute_command.assert_called_once_with("echo hello")
    
    @patch('tools.command_executor.PythonCommandExecutor')
    def test_run_python_with_venv(self, mock_executor_class, temp_project_dir):
        """Test run_python_with_venv convenience function."""
        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor
        
        expected_result = CommandResult(
            success=True,
            returncode=0,
            stdout="script output",
            stderr="",
            command="python script.py",
            execution_time=0.2,
            venv_used=True,
            git_changes_detected=False
        )
        mock_executor.execute_python_script.return_value = expected_result
        
        result = run_python_with_venv("script.py", ["arg1"], temp_project_dir)
        
        assert result == expected_result
        mock_executor_class.assert_called_once_with(temp_project_dir)
        mock_executor.execute_python_script.assert_called_once_with("script.py", ["arg1"])
    
    @patch('tools.command_executor.PythonCommandExecutor')
    def test_get_project_recommendations(self, mock_executor_class, temp_project_dir):
        """Test get_project_recommendations convenience function."""
        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor
        
        expected_recommendations = {
            "commit": {"should_commit": True, "confidence": 0.8},
            "push": {"should_push": False, "confidence": 0.6}
        }
        mock_executor.get_git_recommendations.return_value = expected_recommendations
        
        result = get_project_recommendations(temp_project_dir)
        
        assert result == expected_recommendations
        mock_executor_class.assert_called_once_with(temp_project_dir)
        mock_executor.get_git_recommendations.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
