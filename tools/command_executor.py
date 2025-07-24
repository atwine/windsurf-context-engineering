"""
Command Executor with Virtual Environment Integration

This module provides intelligent command execution with automatic virtual environment
management and Git integration for the Windsurf Context Engineering Framework.

Author: Windsurf Context Engineering Team
Version: 1.0.0
"""

import os
import subprocess
import logging
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path

from .venv_manager import VirtualEnvironmentManager, VenvInfo
from .git_manager import GitOperationsManager, GitStatus


@dataclass
class CommandResult:
    """Result of command execution with environment context."""
    success: bool
    returncode: int
    stdout: str
    stderr: str
    command: str
    execution_time: float
    venv_used: bool
    git_changes_detected: bool


@dataclass
class ExecutionContext:
    """Context for command execution with environment awareness."""
    working_directory: Path
    virtual_environment: Optional[VenvInfo]
    git_status: Optional[GitStatus]
    environment_variables: Dict[str, str]
    python_project: bool
    git_repository: bool


class PythonCommandExecutor:
    """
    Intelligent command executor with virtual environment and Git integration.
    
    This class provides seamless command execution with automatic virtual environment
    management, Git operation awareness, and intelligent recommendations for the
    Windsurf Context Engineering Framework.
    """
    
    def __init__(self, project_path: str = "."):
        """
        Initialize the command executor.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path).resolve()
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.venv_manager = VirtualEnvironmentManager(str(self.project_path))
        self.git_manager = GitOperationsManager(str(self.project_path))
        
        # Execution context
        self.context = self._analyze_execution_context()
        
        self.logger.info(f"PythonCommandExecutor initialized for {self.project_path}")
    
    def _analyze_execution_context(self) -> ExecutionContext:
        """Analyze the project environment and create execution context."""
        try:
            # Check if it's a Python project
            python_project = self.venv_manager.detect_python_project()
            
            # Get virtual environment info if Python project
            venv_info = None
            if python_project:
                venv_info = self.venv_manager.get_venv_info()
            
            # Check if it's a Git repository
            git_repository = (self.project_path / ".git").exists()
            
            # Get Git status if repository
            git_status = None
            if git_repository:
                try:
                    git_status = self.git_manager.get_git_status()
                except Exception as e:
                    self.logger.warning(f"Could not get Git status: {e}")
            
            # Prepare environment variables
            env_vars = os.environ.copy()
            
            context = ExecutionContext(
                working_directory=self.project_path,
                virtual_environment=venv_info,
                git_status=git_status,
                environment_variables=env_vars,
                python_project=python_project,
                git_repository=git_repository
            )
            
            self.logger.info(f"Execution context: Python={python_project}, Git={git_repository}, VEnv={venv_info is not None}")
            return context
            
        except Exception as e:
            self.logger.error(f"Error analyzing execution context: {e}")
            # Return minimal context
            return ExecutionContext(
                working_directory=self.project_path,
                virtual_environment=None,
                git_status=None,
                environment_variables=os.environ.copy(),
                python_project=False,
                git_repository=False
            )
    
    def ensure_python_environment(self) -> Tuple[bool, str]:
        """
        Ensure Python virtual environment is ready for execution.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.context.python_project:
            return True, "Not a Python project, no virtual environment needed"
        
        try:
            # Check if virtual environment exists
            if not self.venv_manager.venv_exists():
                self.logger.info("Creating virtual environment for Python project")
                success, message = self.venv_manager.create_venv()
                if not success:
                    return False, f"Failed to create virtual environment: {message}"
            
            # Validate virtual environment health
            if not self.venv_manager.validate_venv():
                self.logger.warning("Virtual environment validation failed, recreating")
                success, message = self.venv_manager.create_venv(force=True)
                if not success:
                    return False, f"Failed to recreate virtual environment: {message}"
            
            # Update context with new venv info
            self.context.virtual_environment = self.venv_manager.get_venv_info()
            
            return True, "Virtual environment is ready"
            
        except Exception as e:
            error_msg = f"Error ensuring Python environment: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def execute_command(
        self,
        command: Union[str, List[str]],
        use_venv: bool = True,
        capture_output: bool = True,
        timeout: Optional[float] = None,
        check_git_changes: bool = True
    ) -> CommandResult:
        """
        Execute a command with intelligent environment management.
        
        Args:
            command: Command to execute (string or list)
            use_venv: Whether to use virtual environment for Python commands
            capture_output: Whether to capture stdout/stderr
            timeout: Command timeout in seconds
            check_git_changes: Whether to check for Git changes after execution
            
        Returns:
            CommandResult with execution details
        """
        import time
        start_time = time.time()
        
        # Convert command to list if string
        if isinstance(command, str):
            cmd_list = command.split()
        else:
            cmd_list = command.copy()
        
        original_command = " ".join(cmd_list)
        venv_used = False
        
        try:
            # Ensure Python environment if needed
            if self.context.python_project and use_venv:
                env_success, env_message = self.ensure_python_environment()
                if not env_success:
                    return CommandResult(
                        success=False,
                        returncode=-1,
                        stdout="",
                        stderr=f"Environment setup failed: {env_message}",
                        command=original_command,
                        execution_time=time.time() - start_time,
                        venv_used=False,
                        git_changes_detected=False
                    )
            
            # Wrap Python commands with virtual environment
            if self.context.python_project and use_venv and self._is_python_command(cmd_list[0]):
                wrapped_command = self.venv_manager.get_python_command(" ".join(cmd_list))
                cmd_list = wrapped_command.split()
                venv_used = True
                self.logger.info(f"Using virtual environment for command: {wrapped_command}")
            
            # Execute the command
            result = subprocess.run(
                cmd_list,
                cwd=self.context.working_directory,
                env=self.context.environment_variables,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            # Check for Git changes if requested
            git_changes_detected = False
            if check_git_changes and self.context.git_repository:
                try:
                    new_git_status = self.git_manager.get_git_status()
                    git_changes_detected = (
                        new_git_status.staged_files or 
                        new_git_status.unstaged_files or 
                        new_git_status.untracked_files
                    )
                except Exception as e:
                    self.logger.warning(f"Could not check Git changes: {e}")
            
            command_result = CommandResult(
                success=result.returncode == 0,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                command=original_command,
                execution_time=execution_time,
                venv_used=venv_used,
                git_changes_detected=git_changes_detected
            )
            
            self.logger.info(f"Command executed: {original_command} (success={command_result.success}, time={execution_time:.2f}s)")
            return command_result
            
        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Command timed out: {original_command}")
            return CommandResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                command=original_command,
                execution_time=execution_time,
                venv_used=venv_used,
                git_changes_detected=False
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error executing command: {e}"
            self.logger.error(error_msg)
            return CommandResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=error_msg,
                command=original_command,
                execution_time=execution_time,
                venv_used=venv_used,
                git_changes_detected=False
            )
    
    def execute_python_script(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        timeout: Optional[float] = None
    ) -> CommandResult:
        """
        Execute a Python script with virtual environment.
        
        Args:
            script_path: Path to the Python script
            args: Additional arguments for the script
            timeout: Execution timeout in seconds
            
        Returns:
            CommandResult with execution details
        """
        command = ["python", script_path]
        if args:
            command.extend(args)
        
        return self.execute_command(command, use_venv=True, timeout=timeout)
    
    def install_requirements(self, requirements_file: str = "requirements.txt") -> CommandResult:
        """
        Install requirements using virtual environment.
        
        Args:
            requirements_file: Path to requirements file
            
        Returns:
            CommandResult with installation details
        """
        command = ["pip", "install", "-r", requirements_file]
        return self.execute_command(command, use_venv=True, timeout=300)  # 5 minute timeout
    
    def run_tests(self, test_path: str = "tests", framework: str = "pytest") -> CommandResult:
        """
        Run tests using virtual environment.
        
        Args:
            test_path: Path to tests directory or file
            framework: Testing framework (pytest, unittest)
            
        Returns:
            CommandResult with test execution details
        """
        if framework == "pytest":
            command = ["python", "-m", "pytest", test_path, "-v"]
        elif framework == "unittest":
            command = ["python", "-m", "unittest", "discover", test_path]
        else:
            raise ValueError(f"Unsupported test framework: {framework}")
        
        return self.execute_command(command, use_venv=True, timeout=600)  # 10 minute timeout
    
    def get_git_recommendations(self) -> Optional[Dict]:
        """
        Get intelligent Git recommendations based on current state.
        
        Returns:
            Dictionary with commit and push recommendations, or None if not a Git repository
        """
        if not self.context.git_repository:
            return None
        
        try:
            commit_rec = self.git_manager.get_commit_recommendation()
            push_rec = self.git_manager.get_push_recommendation()
            
            return {
                "commit": {
                    "should_commit": commit_rec.should_commit,
                    "confidence": commit_rec.confidence,
                    "message": commit_rec.suggested_message,
                    "reasoning": commit_rec.reasoning
                },
                "push": {
                    "should_push": push_rec.should_push,
                    "confidence": push_rec.confidence,
                    "timing": push_rec.recommended_timing,
                    "reasoning": push_rec.reasoning
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting Git recommendations: {e}")
            return None
    
    def _is_python_command(self, command: str) -> bool:
        """Check if a command is a Python-related command that should use venv."""
        python_commands = {"python", "python3", "pip", "pip3", "pytest", "flake8", "black", "mypy"}
        return command in python_commands
    
    def get_execution_summary(self) -> Dict:
        """
        Get a summary of the current execution context.
        
        Returns:
            Dictionary with context information
        """
        return {
            "project_path": str(self.context.working_directory),
            "python_project": self.context.python_project,
            "git_repository": self.context.git_repository,
            "virtual_environment": {
                "exists": self.context.virtual_environment is not None,
                "path": str(self.context.virtual_environment.venv_path) if self.context.virtual_environment else None,
                "python_executable": str(self.context.virtual_environment.python_executable) if self.context.virtual_environment else None,
                "is_healthy": self.context.virtual_environment.is_healthy if self.context.virtual_environment else False
            },
            "git_status": {
                "staged_files": len(self.context.git_status.staged_files) if self.context.git_status else 0,
                "unstaged_files": len(self.context.git_status.unstaged_files) if self.context.git_status else 0,
                "untracked_files": len(self.context.git_status.untracked_files) if self.context.git_status else 0,
                "is_clean": self.context.git_status.is_clean if self.context.git_status else True
            }
        }


# Convenience functions for easy integration
def execute_with_venv(command: Union[str, List[str]], project_path: str = ".") -> CommandResult:
    """
    Convenience function to execute a command with virtual environment management.
    
    Args:
        command: Command to execute
        project_path: Path to the project directory
        
    Returns:
        CommandResult with execution details
    """
    executor = PythonCommandExecutor(project_path)
    return executor.execute_command(command)


def run_python_with_venv(script_path: str, args: Optional[List[str]] = None, project_path: str = ".") -> CommandResult:
    """
    Convenience function to run a Python script with virtual environment.
    
    Args:
        script_path: Path to the Python script
        args: Additional arguments for the script
        project_path: Path to the project directory
        
    Returns:
        CommandResult with execution details
    """
    executor = PythonCommandExecutor(project_path)
    return executor.execute_python_script(script_path, args)


def get_project_recommendations(project_path: str = ".") -> Optional[Dict]:
    """
    Convenience function to get Git recommendations for a project.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Dictionary with recommendations or None
    """
    executor = PythonCommandExecutor(project_path)
    return executor.get_git_recommendations()
