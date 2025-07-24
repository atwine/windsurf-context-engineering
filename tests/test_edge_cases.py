"""
Comprehensive Edge Case Tests for Phase 2 Integration

This module contains extensive edge case testing to ensure robustness
and reliability of all Phase 2 components under various scenarios.

Author: Windsurf Context Engineering Team
Version: 1.0.0
"""

import os
import pytest
import tempfile
import subprocess
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

from tools.command_executor import PythonCommandExecutor, CommandResult
from tools.venv_manager import VirtualEnvironmentManager
from tools.git_manager import GitOperationsManager


class TestEdgeCasesEnvironmentManagement:
    """Edge case tests for virtual environment management."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_nonexistent_project_path(self):
        """Test with completely nonexistent project path."""
        nonexistent_path = "/absolutely/nonexistent/path/12345"
        
        # Should not crash, but handle gracefully
        try:
            executor = PythonCommandExecutor(nonexistent_path)
            summary = executor.get_execution_summary()
            
            # Should return valid summary even with invalid path
            assert isinstance(summary, dict)
            assert "project_path" in summary
            assert "python_project" in summary
            assert "git_repository" in summary
            
        except Exception as e:
            # If it fails, should be a controlled failure
            assert "not found" in str(e).lower() or "does not exist" in str(e).lower()
    
    def test_empty_directory(self, temp_dir):
        """Test with completely empty directory."""
        empty_dir = Path(temp_dir) / "empty"
        empty_dir.mkdir()
        
        executor = PythonCommandExecutor(str(empty_dir))
        
        # Should detect as non-Python project
        assert executor.context.python_project == False
        assert executor.context.git_repository == False
        
        # Should handle environment setup gracefully
        success, message = executor.ensure_python_environment()
        assert success == True  # Should succeed for non-Python projects
        assert "Not a Python project" in message
    
    def test_corrupted_requirements_file(self, temp_dir):
        """Test with corrupted requirements.txt file."""
        project_dir = Path(temp_dir) / "corrupted_project"
        project_dir.mkdir()
        
        # Create corrupted requirements.txt
        (project_dir / "requirements.txt").write_text("invalid\n<<<corrupted>>>\n@#$%^&*()")
        
        executor = PythonCommandExecutor(str(project_dir))
        
        # Should still detect as Python project
        assert executor.context.python_project == True
        
        # Should handle corrupted requirements gracefully
        success, message = executor.ensure_python_environment()
        # May fail due to corrupted requirements, but should not crash
        assert isinstance(success, bool)
        assert isinstance(message, str)
    
    def test_permission_denied_directory(self, temp_dir):
        """Test with directory that has permission issues."""
        if os.name == 'nt':  # Windows
            pytest.skip("Permission testing complex on Windows")
        
        restricted_dir = Path(temp_dir) / "restricted"
        restricted_dir.mkdir()
        
        # Create Python project files
        (restricted_dir / "requirements.txt").write_text("pytest>=6.0.0")
        
        # Restrict permissions
        os.chmod(restricted_dir, 0o444)  # Read-only
        
        try:
            executor = PythonCommandExecutor(str(restricted_dir))
            
            # Should handle permission issues gracefully
            success, message = executor.ensure_python_environment()
            # May fail due to permissions, but should not crash
            assert isinstance(success, bool)
            assert isinstance(message, str)
            
        finally:
            # Restore permissions for cleanup
            os.chmod(restricted_dir, 0o755)
    
    def test_very_long_project_path(self, temp_dir):
        """Test with extremely long project path."""
        # Create nested directory structure
        long_path = Path(temp_dir)
        for i in range(10):
            long_path = long_path / f"very_long_directory_name_{i}_with_many_characters"
        
        try:
            long_path.mkdir(parents=True)
            (long_path / "requirements.txt").write_text("pytest>=6.0.0")
            
            executor = PythonCommandExecutor(str(long_path))
            
            # Should handle long paths
            assert executor.context.python_project == True
            summary = executor.get_execution_summary()
            assert isinstance(summary, dict)
            
        except OSError as e:
            # Path too long on some systems - acceptable failure
            pytest.skip(f"Path too long for filesystem: {e}")
    
    def test_special_characters_in_path(self, temp_dir):
        """Test with special characters in project path."""
        special_chars = "test-project_with.special@chars"
        project_dir = Path(temp_dir) / special_chars
        project_dir.mkdir()
        
        (project_dir / "requirements.txt").write_text("pytest>=6.0.0")
        
        executor = PythonCommandExecutor(str(project_dir))
        
        # Should handle special characters in path
        assert executor.context.python_project == True
        summary = executor.get_execution_summary()
        assert special_chars in summary["project_path"]
    
    def test_unicode_characters_in_path(self, temp_dir):
        """Test with Unicode characters in project path."""
        unicode_name = "test_项目_プロジェクト_проект"
        project_dir = Path(temp_dir) / unicode_name
        
        try:
            project_dir.mkdir()
            (project_dir / "requirements.txt").write_text("pytest>=6.0.0")
            
            executor = PythonCommandExecutor(str(project_dir))
            
            # Should handle Unicode characters
            assert executor.context.python_project == True
            summary = executor.get_execution_summary()
            assert isinstance(summary, dict)
            
        except (UnicodeError, OSError) as e:
            # Some filesystems don't support Unicode - acceptable
            pytest.skip(f"Unicode not supported on filesystem: {e}")


class TestEdgeCasesCommandExecution:
    """Edge case tests for command execution."""
    
    @pytest.fixture
    def temp_python_project(self):
        """Create a temporary Python project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            project_path.mkdir()
            (project_path / "requirements.txt").write_text("pytest>=6.0.0")
            yield str(project_path)
    
    @patch('subprocess.run')
    def test_command_timeout_handling(self, mock_subprocess, temp_python_project):
        """Test command timeout handling."""
        # Mock timeout exception
        mock_subprocess.side_effect = subprocess.TimeoutExpired("sleep 10", 1)
        
        executor = PythonCommandExecutor(temp_python_project)
        result = executor.execute_command("sleep 10", timeout=1)
        
        assert result.success == False
        assert result.returncode == -1
        assert "timed out" in result.stderr.lower()
        assert result.execution_time > 0
    
    @patch('subprocess.run')
    def test_command_with_very_long_output(self, mock_subprocess, temp_python_project):
        """Test command with extremely long output."""
        # Mock command with very long output
        long_output = "x" * 100000  # 100KB of output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = long_output
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        executor = PythonCommandExecutor(temp_python_project)
        result = executor.execute_command("echo long_output")
        
        assert result.success == True
        assert len(result.stdout) == 100000
        assert result.stderr == ""
    
    @patch('subprocess.run')
    def test_command_with_binary_output(self, mock_subprocess, temp_python_project):
        """Test command that produces binary output."""
        # Mock command with binary output
        mock_subprocess.side_effect = UnicodeDecodeError(
            'utf-8', b'\x80\x81\x82', 0, 1, 'invalid start byte'
        )
        
        executor = PythonCommandExecutor(temp_python_project)
        result = executor.execute_command("binary_command")
        
        # Should handle binary output gracefully
        assert result.success == False
        assert "Error executing command" in result.stderr
    
    def test_empty_command(self, temp_python_project):
        """Test with empty command."""
        executor = PythonCommandExecutor(temp_python_project)
        
        # Should handle empty command gracefully
        result = executor.execute_command("")
        assert result.success == False
        assert result.command == ""
    
    def test_command_with_special_characters(self, temp_python_project):
        """Test command with special characters."""
        executor = PythonCommandExecutor(temp_python_project)
        
        # Test with various special characters
        special_commands = [
            "echo 'hello world'",
            'echo "double quotes"',
            "echo $HOME",
            "echo `date`",
            "echo hello & echo world",
            "echo hello | grep hello"
        ]
        
        for cmd in special_commands:
            result = executor.execute_command(cmd)
            # Should not crash, regardless of success/failure
            assert isinstance(result.success, bool)
            assert isinstance(result.command, str)
    
    @patch('subprocess.run')
    def test_command_interrupted(self, mock_subprocess, temp_python_project):
        """Test command that gets interrupted."""
        # Mock KeyboardInterrupt
        mock_subprocess.side_effect = KeyboardInterrupt()
        
        executor = PythonCommandExecutor(temp_python_project)
        result = executor.execute_command("long_running_command")
        
        # Should handle interruption gracefully
        assert result.success == False
        assert "Error executing command" in result.stderr
    
    def test_multiple_rapid_commands(self, temp_python_project):
        """Test executing multiple commands rapidly."""
        executor = PythonCommandExecutor(temp_python_project)
        
        # Execute multiple commands rapidly
        results = []
        for i in range(10):
            result = executor.execute_command(f"echo test_{i}")
            results.append(result)
        
        # All commands should be handled properly
        for i, result in enumerate(results):
            assert isinstance(result.success, bool)
            assert f"test_{i}" in result.command


class TestEdgeCasesGitIntegration:
    """Edge case tests for Git integration."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_corrupted_git_repository(self, temp_dir):
        """Test with corrupted Git repository."""
        project_dir = Path(temp_dir) / "corrupted_git"
        project_dir.mkdir()
        
        # Create .git directory but corrupt it
        git_dir = project_dir / ".git"
        git_dir.mkdir()
        (git_dir / "corrupted_file").write_text("not a valid git file")
        
        executor = PythonCommandExecutor(str(project_dir))
        
        # Should detect as Git repository but handle corruption
        assert executor.context.git_repository == True
        
        # Git operations should handle corruption gracefully
        recommendations = executor.get_git_recommendations()
        # May return None due to corruption, but should not crash
        assert recommendations is None or isinstance(recommendations, dict)
    
    def test_git_repository_without_commits(self, temp_dir):
        """Test with Git repository that has no commits."""
        project_dir = Path(temp_dir) / "empty_git"
        project_dir.mkdir()
        
        # Initialize empty Git repository
        subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=project_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_dir, capture_output=True)
        
        executor = PythonCommandExecutor(str(project_dir))
        
        # Should handle empty repository
        assert executor.context.git_repository == True
        recommendations = executor.get_git_recommendations()
        
        # Should provide recommendations even for empty repo
        if recommendations:
            assert "commit" in recommendations
            assert "push" in recommendations
    
    def test_git_repository_with_conflicts(self, temp_dir):
        """Test with Git repository that has merge conflicts."""
        project_dir = Path(temp_dir) / "conflict_git"
        project_dir.mkdir()
        
        # Create Git repository with potential conflicts
        subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=project_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_dir, capture_output=True)
        
        # Create file and commit
        (project_dir / "test.txt").write_text("original content")
        subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=project_dir, capture_output=True)
        
        # Modify file to simulate conflict
        (project_dir / "test.txt").write_text("modified content")
        
        executor = PythonCommandExecutor(str(project_dir))
        recommendations = executor.get_git_recommendations()
        
        # Should handle repository with changes
        assert recommendations is not None
        assert "commit" in recommendations
    
    def test_git_without_git_command(self, temp_dir):
        """Test Git operations when git command is not available."""
        project_dir = Path(temp_dir) / "no_git_cmd"
        project_dir.mkdir()
        
        # Create .git directory to simulate Git repo
        (project_dir / ".git").mkdir()
        
        with patch('subprocess.run') as mock_run:
            # Mock git command not found
            mock_run.side_effect = FileNotFoundError("git command not found")
            
            executor = PythonCommandExecutor(str(project_dir))
            recommendations = executor.get_git_recommendations()
            
            # Should handle missing git command gracefully
            assert recommendations is None or isinstance(recommendations, dict)


class TestEdgeCasesErrorRecovery:
    """Edge case tests for error recovery and resilience."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_memory_pressure_simulation(self, temp_dir):
        """Test behavior under simulated memory pressure."""
        project_dir = Path(temp_dir) / "memory_test"
        project_dir.mkdir()
        (project_dir / "requirements.txt").write_text("pytest>=6.0.0")
        
        # Create multiple executors to simulate memory usage
        executors = []
        try:
            for i in range(50):  # Create many instances
                executor = PythonCommandExecutor(str(project_dir))
                executors.append(executor)
                
                # Test basic functionality still works
                summary = executor.get_execution_summary()
                assert isinstance(summary, dict)
                
        except MemoryError:
            # Acceptable if system runs out of memory
            pytest.skip("System ran out of memory during test")
        finally:
            # Clean up
            del executors
    
    def test_disk_space_simulation(self, temp_dir):
        """Test behavior when disk space is limited."""
        project_dir = Path(temp_dir) / "disk_test"
        project_dir.mkdir()
        (project_dir / "requirements.txt").write_text("pytest>=6.0.0")
        
        executor = PythonCommandExecutor(str(project_dir))
        
        # Simulate disk full error during venv creation
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = OSError("No space left on device")
            
            success, message = executor.ensure_python_environment()
            
            # Should handle disk space issues gracefully
            assert success == False
            assert "Error ensuring Python environment" in message
    
    def test_network_unavailable_simulation(self, temp_dir):
        """Test behavior when network is unavailable."""
        project_dir = Path(temp_dir) / "network_test"
        project_dir.mkdir()
        (project_dir / "requirements.txt").write_text("requests>=2.25.0")
        
        executor = PythonCommandExecutor(str(project_dir))
        
        # Simulate network error during pip install
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Could not fetch URL: Network is unreachable"
            mock_run.return_value = mock_result
            
            result = executor.install_requirements()
            
            # Should handle network issues gracefully
            assert result.success == False
            assert "Network is unreachable" in result.stderr
    
    def test_concurrent_access_simulation(self, temp_dir):
        """Test behavior with concurrent access to same project."""
        project_dir = Path(temp_dir) / "concurrent_test"
        project_dir.mkdir()
        (project_dir / "requirements.txt").write_text("pytest>=6.0.0")
        
        # Create multiple executors for same project
        executor1 = PythonCommandExecutor(str(project_dir))
        executor2 = PythonCommandExecutor(str(project_dir))
        
        # Both should work without interfering
        summary1 = executor1.get_execution_summary()
        summary2 = executor2.get_execution_summary()
        
        assert isinstance(summary1, dict)
        assert isinstance(summary2, dict)
        assert summary1["project_path"] == summary2["project_path"]
    
    def test_rapid_initialization_destruction(self, temp_dir):
        """Test rapid creation and destruction of executors."""
        project_dir = Path(temp_dir) / "rapid_test"
        project_dir.mkdir()
        (project_dir / "requirements.txt").write_text("pytest>=6.0.0")
        
        # Rapidly create and destroy executors
        for i in range(20):
            executor = PythonCommandExecutor(str(project_dir))
            summary = executor.get_execution_summary()
            assert isinstance(summary, dict)
            del executor  # Explicit cleanup
    
    def test_exception_during_initialization(self, temp_dir):
        """Test handling of exceptions during initialization."""
        project_dir = Path(temp_dir) / "exception_test"
        project_dir.mkdir()
        
        # Mock exception during manager initialization
        with patch('tools.command_executor.VirtualEnvironmentManager') as mock_venv:
            mock_venv.side_effect = Exception("Initialization failed")
            
            # Should handle initialization failure gracefully
            try:
                executor = PythonCommandExecutor(str(project_dir))
                # If it doesn't crash, it should have minimal functionality
                summary = executor.get_execution_summary()
                assert isinstance(summary, dict)
            except Exception as e:
                # If it does fail, should be controlled
                assert "Initialization failed" in str(e)


class TestEdgeCasesWorkflowIntegration:
    """Edge case tests for workflow integration."""
    
    def test_workflow_files_missing(self):
        """Test behavior when workflow files are missing."""
        workflow_dir = Path(".windsurf/workflows")
        
        # Test that missing workflows don't break the system
        workflows = ["execute-plan.md", "execute-plan-enhanced.md", "init-context.md"]
        
        for workflow in workflows:
            workflow_path = workflow_dir / workflow
            if workflow_path.exists():
                # File exists - good
                content = workflow_path.read_text()
                assert len(content) > 0
            else:
                # File missing - should be handled gracefully
                pytest.skip(f"Workflow {workflow} not found - acceptable for testing")
    
    def test_workflow_files_corrupted(self):
        """Test behavior with corrupted workflow files."""
        workflow_dir = Path(".windsurf/workflows")
        
        # Check if workflows exist and have valid content
        workflows = ["execute-plan.md", "execute-plan-enhanced.md", "init-context.md"]
        
        for workflow in workflows:
            workflow_path = workflow_dir / workflow
            if workflow_path.exists():
                content = workflow_path.read_text()
                
                # Check for basic structure
                assert "---" in content  # YAML frontmatter
                assert "description:" in content
                assert len(content) > 100  # Reasonable content length
    
    def test_tools_module_import_edge_cases(self):
        """Test edge cases in tools module imports."""
        # Test that all imports work correctly
        try:
            from tools import (
                PythonCommandExecutor,
                CommandResult,
                ExecutionContext,
                execute_with_venv,
                run_python_with_venv,
                get_project_recommendations
            )
            
            # Test that classes can be instantiated
            temp_dir = Path.cwd()
            executor = PythonCommandExecutor(str(temp_dir))
            assert executor is not None
            
            # Test that functions are callable
            assert callable(execute_with_venv)
            assert callable(run_python_with_venv)
            assert callable(get_project_recommendations)
            
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Run all edge case tests
    pytest.main([__file__, "-v", "--tb=short", "-x"])  # Stop on first failure
