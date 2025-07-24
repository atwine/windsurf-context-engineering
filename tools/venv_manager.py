#!/usr/bin/env python3
"""
Virtual Environment Manager
==========================

Comprehensive virtual environment management for Python projects in the
Windsurf Context Engineering Framework. Provides automatic detection,
creation, activation, and management of project-specific virtual environments.
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import shutil

logger = logging.getLogger(__name__)

@dataclass
class VenvInfo:
    """Information about a virtual environment"""
    path: str
    python_version: str
    is_active: bool
    created_date: str
    last_used: str
    packages_count: int
    requirements_hash: str
    status: str  # 'healthy', 'corrupted', 'outdated'

@dataclass
class VenvConfig:
    """Configuration for virtual environment creation"""
    python_executable: str = sys.executable
    venv_name: str = "venv"
    requirements_file: str = "requirements.txt"
    auto_activate: bool = True
    upgrade_pip: bool = True
    install_dev_requirements: bool = True
    dev_requirements_file: str = "requirements-dev.txt"

class VirtualEnvironmentManager:
    """
    Comprehensive virtual environment management system
    
    Features:
    - Automatic venv detection and creation
    - Cross-platform support (Windows/Linux/macOS)
    - Requirements management and synchronization
    - Health checking and validation
    - Integration with project context
    """
    
    def __init__(self, project_root: str = ".", config: Optional[VenvConfig] = None):
        """Initialize the virtual environment manager"""
        self.project_root = Path(project_root).resolve()
        self.config = config or VenvConfig()
        self.venv_path = self.project_root / self.config.venv_name
        self.is_windows = platform.system() == "Windows"
        
        # Platform-specific paths
        if self.is_windows:
            self.python_exe = self.venv_path / "Scripts" / "python.exe"
            self.pip_exe = self.venv_path / "Scripts" / "pip.exe"
            self.activate_script = self.venv_path / "Scripts" / "activate.bat"
        else:
            self.python_exe = self.venv_path / "bin" / "python"
            self.pip_exe = self.venv_path / "bin" / "pip"
            self.activate_script = self.venv_path / "bin" / "activate"
        
        # State tracking
        self.venv_info_file = self.project_root / ".venv_info.json"
        
        logger.debug(f"VirtualEnvironmentManager initialized for {self.project_root}")
    
    def detect_python_project(self) -> bool:
        """Detect if the current directory contains a Python project"""
        python_indicators = [
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "Pipfile",
            "environment.yml",
            "conda.yml"
        ]
        
        python_files = list(self.project_root.glob("*.py"))
        python_dirs = [
            d for d in self.project_root.iterdir() 
            if d.is_dir() and not d.name.startswith('.') and 
            list(d.glob("*.py"))
        ]
        
        has_indicators = any(
            (self.project_root / indicator).exists() 
            for indicator in python_indicators
        )
        
        has_python_files = len(python_files) > 0 or len(python_dirs) > 0
        
        result = has_indicators or has_python_files
        logger.info(f"Python project detection: {result}")
        return result
    
    def venv_exists(self) -> bool:
        """Check if virtual environment exists"""
        exists = (
            self.venv_path.exists() and 
            self.python_exe.exists() and 
            self.pip_exe.exists()
        )
        logger.debug(f"Virtual environment exists: {exists}")
        return exists
    
    def get_venv_info(self) -> Optional[VenvInfo]:
        """Get detailed information about the virtual environment"""
        if not self.venv_exists():
            return None
        
        try:
            # Get Python version
            result = subprocess.run(
                [str(self.python_exe), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            python_version = result.stdout.strip() if result.returncode == 0 else "Unknown"
            
            # Get package count
            result = subprocess.run(
                [str(self.pip_exe), "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            packages_count = 0
            if result.returncode == 0:
                try:
                    packages = json.loads(result.stdout)
                    packages_count = len(packages)
                except json.JSONDecodeError:
                    pass
            
            # Get requirements hash
            requirements_hash = self._get_requirements_hash()
            
            # Check if currently active
            is_active = self._is_venv_active()
            
            # Determine status
            status = self._check_venv_health()
            
            # Load or create venv info
            venv_info = VenvInfo(
                path=str(self.venv_path),
                python_version=python_version,
                is_active=is_active,
                created_date=self._get_creation_date(),
                last_used=self._get_last_used(),
                packages_count=packages_count,
                requirements_hash=requirements_hash,
                status=status
            )
            
            # Save venv info
            self._save_venv_info(venv_info)
            
            return venv_info
            
        except Exception as e:
            logger.error(f"Error getting venv info: {e}")
            return None
    
    def create_venv(self, force: bool = False) -> Tuple[bool, str]:
        """
        Create a new virtual environment
        
        Args:
            force: If True, recreate even if venv exists
            
        Returns:
            Tuple of (success, message)
        """
        if self.venv_exists() and not force:
            return True, f"Virtual environment already exists at {self.venv_path}"
        
        if force and self.venv_exists():
            logger.info("Removing existing virtual environment")
            shutil.rmtree(self.venv_path, ignore_errors=True)
        
        try:
            logger.info(f"Creating virtual environment at {self.venv_path}")
            
            # Create virtual environment
            cmd = [self.config.python_executable, "-m", "venv", str(self.venv_path)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                error_msg = f"Failed to create venv: {result.stderr}"
                logger.error(error_msg)
                return False, error_msg
            
            # Upgrade pip if requested
            if self.config.upgrade_pip:
                upgrade_success, upgrade_msg = self._upgrade_pip()
                if not upgrade_success:
                    logger.warning(f"Failed to upgrade pip: {upgrade_msg}")
            
            # Install requirements
            install_success, install_msg = self.install_requirements()
            if not install_success:
                logger.warning(f"Failed to install requirements: {install_msg}")
            
            logger.info("Virtual environment created successfully")
            return True, f"Virtual environment created at {self.venv_path}"
            
        except subprocess.TimeoutExpired:
            error_msg = "Virtual environment creation timed out"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error creating venv: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def install_requirements(self) -> Tuple[bool, str]:
        """Install requirements from requirements.txt and requirements-dev.txt"""
        if not self.venv_exists():
            return False, "Virtual environment does not exist"
        
        messages = []
        overall_success = True
        
        # Install main requirements
        requirements_file = self.project_root / self.config.requirements_file
        if requirements_file.exists():
            success, msg = self._install_requirements_file(requirements_file)
            messages.append(f"Main requirements: {msg}")
            if not success:
                overall_success = False
        
        # Install dev requirements
        if self.config.install_dev_requirements:
            dev_requirements_file = self.project_root / self.config.dev_requirements_file
            if dev_requirements_file.exists():
                success, msg = self._install_requirements_file(dev_requirements_file)
                messages.append(f"Dev requirements: {msg}")
                if not success:
                    overall_success = False
        
        return overall_success, "; ".join(messages) if messages else "No requirements files found"
    
    def get_activation_command(self) -> str:
        """Get the command to activate the virtual environment"""
        if self.is_windows:
            return f'"{self.activate_script}"'
        else:
            return f'source "{self.activate_script}"'
    
    def get_python_command(self, command: str) -> str:
        """Wrap a Python command to run in the virtual environment"""
        if not self.venv_exists():
            logger.warning("Virtual environment does not exist, using system Python")
            return command
        
        # Replace python/pip commands with venv versions
        if command.startswith("python "):
            command = command.replace("python ", f'"{self.python_exe}" ', 1)
        elif command.startswith("pip "):
            command = command.replace("pip ", f'"{self.pip_exe}" ', 1)
        elif command == "python":
            command = f'"{self.python_exe}"'
        elif command == "pip":
            command = f'"{self.pip_exe}"'
        
        return command
    
    def execute_in_venv(self, command: str, **kwargs) -> subprocess.CompletedProcess:
        """Execute a command in the virtual environment"""
        if not self.venv_exists():
            raise RuntimeError("Virtual environment does not exist")
        
        # Prepare environment
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = str(self.venv_path)
        env["PATH"] = f"{self.venv_path / ('Scripts' if self.is_windows else 'bin')}{os.pathsep}{env['PATH']}"
        
        # Remove PYTHONHOME if set (can interfere with venv)
        env.pop("PYTHONHOME", None)
        
        # Execute command
        return subprocess.run(
            command,
            env=env,
            shell=True,
            **kwargs
        )
    
    def validate_venv(self) -> Tuple[bool, List[str]]:
        """Validate virtual environment health and requirements"""
        issues = []
        
        if not self.venv_exists():
            issues.append("Virtual environment does not exist")
            return False, issues
        
        # Check Python executable
        try:
            result = subprocess.run(
                [str(self.python_exe), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                issues.append("Python executable is not working")
        except Exception as e:
            issues.append(f"Cannot execute Python: {e}")
        
        # Check pip
        try:
            result = subprocess.run(
                [str(self.pip_exe), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                issues.append("Pip is not working")
        except Exception as e:
            issues.append(f"Cannot execute pip: {e}")
        
        # Check requirements synchronization
        if not self._check_requirements_sync():
            issues.append("Requirements are out of sync")
        
        return len(issues) == 0, issues
    
    def cleanup_venv(self) -> Tuple[bool, str]:
        """Remove the virtual environment"""
        if not self.venv_exists():
            return True, "Virtual environment does not exist"
        
        try:
            shutil.rmtree(self.venv_path)
            
            # Remove info file
            if self.venv_info_file.exists():
                self.venv_info_file.unlink()
            
            logger.info("Virtual environment removed successfully")
            return True, "Virtual environment removed"
            
        except Exception as e:
            error_msg = f"Failed to remove virtual environment: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def ensure_venv(self) -> Tuple[bool, str]:
        """Ensure virtual environment exists and is healthy"""
        if not self.detect_python_project():
            return False, "Not a Python project"
        
        # Check if venv exists
        if not self.venv_exists():
            return self.create_venv()
        
        # Validate existing venv
        is_valid, issues = self.validate_venv()
        if not is_valid:
            logger.warning(f"Virtual environment has issues: {issues}")
            # Try to fix by recreating
            return self.create_venv(force=True)
        
        # Check requirements sync
        if not self._check_requirements_sync():
            logger.info("Requirements out of sync, updating...")
            success, msg = self.install_requirements()
            if not success:
                return False, f"Failed to sync requirements: {msg}"
        
        return True, "Virtual environment is ready"
    
    # Private helper methods
    
    def _upgrade_pip(self) -> Tuple[bool, str]:
        """Upgrade pip in the virtual environment"""
        try:
            result = subprocess.run(
                [str(self.python_exe), "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return True, "Pip upgraded successfully"
            else:
                return False, f"Pip upgrade failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Pip upgrade error: {e}"
    
    def _install_requirements_file(self, requirements_file: Path) -> Tuple[bool, str]:
        """Install requirements from a specific file"""
        try:
            result = subprocess.run(
                [str(self.pip_exe), "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return True, f"Installed from {requirements_file.name}"
            else:
                return False, f"Failed to install from {requirements_file.name}: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, f"Installation from {requirements_file.name} timed out"
        except Exception as e:
            return False, f"Installation error: {e}"
    
    def _get_requirements_hash(self) -> str:
        """Get hash of requirements files for change detection"""
        import hashlib
        
        content = ""
        for req_file in [self.config.requirements_file, self.config.dev_requirements_file]:
            req_path = self.project_root / req_file
            if req_path.exists():
                content += req_path.read_text()
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_venv_active(self) -> bool:
        """Check if the virtual environment is currently active"""
        virtual_env = os.environ.get("VIRTUAL_ENV")
        return virtual_env is not None and Path(virtual_env) == self.venv_path
    
    def _check_venv_health(self) -> str:
        """Check the health status of the virtual environment"""
        try:
            # Basic health check
            if not self.python_exe.exists() or not self.pip_exe.exists():
                return "corrupted"
            
            # Try to execute Python
            result = subprocess.run(
                [str(self.python_exe), "-c", "import sys; print(sys.version)"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return "corrupted"
            
            # Check if requirements are in sync
            if not self._check_requirements_sync():
                return "outdated"
            
            return "healthy"
            
        except Exception:
            return "corrupted"
    
    def _check_requirements_sync(self) -> bool:
        """Check if installed packages match requirements files"""
        try:
            current_hash = self._get_requirements_hash()
            
            # Load stored hash
            if self.venv_info_file.exists():
                with open(self.venv_info_file, 'r') as f:
                    stored_info = json.load(f)
                    stored_hash = stored_info.get('requirements_hash', '')
                    return current_hash == stored_hash
            
            return False
            
        except Exception:
            return False
    
    def _get_creation_date(self) -> str:
        """Get the creation date of the virtual environment"""
        try:
            if self.venv_path.exists():
                timestamp = self.venv_path.stat().st_ctime
                return str(timestamp)
        except Exception:
            pass
        return ""
    
    def _get_last_used(self) -> str:
        """Get the last used timestamp"""
        try:
            if self.venv_info_file.exists():
                with open(self.venv_info_file, 'r') as f:
                    info = json.load(f)
                    return info.get('last_used', '')
        except Exception:
            pass
        return ""
    
    def _save_venv_info(self, venv_info: VenvInfo):
        """Save virtual environment information"""
        try:
            import time
            info_dict = {
                'path': venv_info.path,
                'python_version': venv_info.python_version,
                'created_date': venv_info.created_date,
                'last_used': str(time.time()),
                'packages_count': venv_info.packages_count,
                'requirements_hash': venv_info.requirements_hash,
                'status': venv_info.status
            }
            
            with open(self.venv_info_file, 'w') as f:
                json.dump(info_dict, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to save venv info: {e}")


# Convenience functions for easy integration

def ensure_python_venv(project_root: str = ".") -> Tuple[bool, str, Optional[VirtualEnvironmentManager]]:
    """
    Ensure a Python project has a working virtual environment
    
    Returns:
        Tuple of (success, message, venv_manager)
    """
    try:
        venv_manager = VirtualEnvironmentManager(project_root)
        success, message = venv_manager.ensure_venv()
        return success, message, venv_manager
    except Exception as e:
        return False, f"Error ensuring venv: {e}", None

def get_venv_python_command(project_root: str = ".") -> str:
    """Get the Python command for the project's virtual environment"""
    try:
        venv_manager = VirtualEnvironmentManager(project_root)
        if venv_manager.venv_exists():
            return str(venv_manager.python_exe)
        else:
            return "python"
    except Exception:
        return "python"

def wrap_python_command(command: str, project_root: str = ".") -> str:
    """Wrap a Python command to run in the project's virtual environment"""
    try:
        venv_manager = VirtualEnvironmentManager(project_root)
        return venv_manager.get_python_command(command)
    except Exception:
        return command


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Virtual Environment Manager")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--create", action="store_true", help="Create virtual environment")
    parser.add_argument("--info", action="store_true", help="Show venv info")
    parser.add_argument("--validate", action="store_true", help="Validate venv")
    parser.add_argument("--cleanup", action="store_true", help="Remove venv")
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    venv_manager = VirtualEnvironmentManager(args.project_root)
    
    if args.create:
        success, message = venv_manager.create_venv()
        print(f"Create: {message}")
    
    if args.info:
        info = venv_manager.get_venv_info()
        if info:
            print(f"Path: {info.path}")
            print(f"Python: {info.python_version}")
            print(f"Active: {info.is_active}")
            print(f"Packages: {info.packages_count}")
            print(f"Status: {info.status}")
        else:
            print("No virtual environment found")
    
    if args.validate:
        is_valid, issues = venv_manager.validate_venv()
        print(f"Valid: {is_valid}")
        if issues:
            print("Issues:")
            for issue in issues:
                print(f"  - {issue}")
    
    if args.cleanup:
        success, message = venv_manager.cleanup_venv()
        print(f"Cleanup: {message}")
