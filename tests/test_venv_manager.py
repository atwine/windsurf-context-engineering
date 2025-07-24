#!/usr/bin/env python3
"""
Unit Tests for Virtual Environment Manager
==========================================

Comprehensive test suite for the VirtualEnvironmentManager class,
testing virtual environment creation, management, and integration.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.venv_manager import (
    VirtualEnvironmentManager, 
    VenvInfo, 
    VenvConfig,
    ensure_python_venv,
    get_venv_python_command,
    wrap_python_command
)

class TestVirtualEnvironmentManager(unittest.TestCase):
    """Test cases for VirtualEnvironmentManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.venv_manager = VirtualEnvironmentManager(str(self.project_root))
        
        # Create test files
        self.requirements_file = self.project_root / "requirements.txt"
        self.requirements_file.write_text("requests>=2.25.0\nnumpy>=1.20.0\n")
        
        self.test_py_file = self.project_root / "test_script.py"
        self.test_py_file.write_text("print('Hello, World!')\n")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test VirtualEnvironmentManager initialization"""
        self.assertEqual(self.venv_manager.project_root, self.project_root)
        self.assertIsInstance(self.venv_manager.config, VenvConfig)
        self.assertEqual(self.venv_manager.venv_path, self.project_root / "venv")
    
    def test_detect_python_project_with_requirements(self):
        """Test Python project detection with requirements.txt"""
        result = self.venv_manager.detect_python_project()
        self.assertTrue(result)
    
    def test_detect_python_project_with_python_files(self):
        """Test Python project detection with Python files"""
        # Remove requirements.txt
        self.requirements_file.unlink()
        
        result = self.venv_manager.detect_python_project()
        self.assertTrue(result)  # Should detect test_script.py
    
    def test_detect_python_project_no_indicators(self):
        """Test Python project detection with no indicators"""
        # Remove all Python indicators
        self.requirements_file.unlink()
        self.test_py_file.unlink()
        
        result = self.venv_manager.detect_python_project()
        self.assertFalse(result)
    
    def test_venv_exists_false(self):
        """Test venv_exists when no venv exists"""
        result = self.venv_manager.venv_exists()
        self.assertFalse(result)
    
    def test_venv_config_defaults(self):
        """Test VenvConfig default values"""
        config = VenvConfig()
        self.assertEqual(config.python_executable, sys.executable)
        self.assertEqual(config.venv_name, "venv")
        self.assertEqual(config.requirements_file, "requirements.txt")
        self.assertTrue(config.auto_activate)
        self.assertTrue(config.upgrade_pip)
    
    def test_get_activation_command_windows(self):
        """Test activation command generation for Windows"""
        with patch('platform.system', return_value='Windows'):
            manager = VirtualEnvironmentManager(str(self.project_root))
            command = manager.get_activation_command()
            self.assertIn("activate.bat", command)
    
    def test_get_activation_command_unix(self):
        """Test activation command generation for Unix"""
        with patch('platform.system', return_value='Linux'):
            manager = VirtualEnvironmentManager(str(self.project_root))
            command = manager.get_activation_command()
            self.assertIn("source", command)
            self.assertIn("activate", command)
    
    def test_get_python_command_no_venv(self):
        """Test Python command wrapping when no venv exists"""
        command = self.venv_manager.get_python_command("python script.py")
        self.assertEqual(command, "python script.py")
    
    def test_get_python_command_with_mock_venv(self):
        """Test Python command wrapping with mocked venv"""
        with patch.object(self.venv_manager, 'venv_exists', return_value=True):
            command = self.venv_manager.get_python_command("python script.py")
            self.assertIn(str(self.venv_manager.python_exe), command)
    
    def test_get_requirements_hash(self):
        """Test requirements file hashing"""
        hash1 = self.venv_manager._get_requirements_hash()
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 32)  # MD5 hash length
        
        # Modify requirements and check hash changes
        self.requirements_file.write_text("requests>=2.26.0\nnumpy>=1.21.0\n")
        hash2 = self.venv_manager._get_requirements_hash()
        self.assertNotEqual(hash1, hash2)
    
    @patch('subprocess.run')
    def test_create_venv_success(self, mock_run):
        """Test successful virtual environment creation"""
        # Mock successful subprocess calls
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="")
        
        with patch.object(self.venv_manager, 'venv_exists', side_effect=[False, True]):
            with patch.object(self.venv_manager, '_upgrade_pip', return_value=(True, "Success")):
                with patch.object(self.venv_manager, 'install_requirements', return_value=(True, "Success")):
                    success, message = self.venv_manager.create_venv()
                    
                    self.assertTrue(success)
                    self.assertIn("created", message.lower())
    
    @patch('subprocess.run')
    def test_create_venv_failure(self, mock_run):
        """Test virtual environment creation failure"""
        # Mock failed subprocess call
        mock_run.return_value = Mock(returncode=1, stderr="Error creating venv", stdout="")
        
        success, message = self.venv_manager.create_venv()
        self.assertFalse(success)
        self.assertIn("Failed", message)
    
    def test_validate_venv_no_venv(self):
        """Test validation when no venv exists"""
        is_valid, issues = self.venv_manager.validate_venv()
        self.assertFalse(is_valid)
        self.assertIn("does not exist", issues[0])
    
    @patch('subprocess.run')
    def test_validate_venv_success(self, mock_run):
        """Test successful venv validation"""
        # Mock successful subprocess calls
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="Python 3.9.0")
        
        with patch.object(self.venv_manager, 'venv_exists', return_value=True):
            with patch.object(self.venv_manager, '_check_requirements_sync', return_value=True):
                is_valid, issues = self.venv_manager.validate_venv()
                self.assertTrue(is_valid)
                self.assertEqual(len(issues), 0)
    
    def test_cleanup_venv_no_venv(self):
        """Test cleanup when no venv exists"""
        success, message = self.venv_manager.cleanup_venv()
        self.assertTrue(success)
        self.assertIn("does not exist", message)
    
    def test_ensure_venv_not_python_project(self):
        """Test ensure_venv when not a Python project"""
        # Remove all Python indicators
        self.requirements_file.unlink()
        self.test_py_file.unlink()
        
        success, message = self.venv_manager.ensure_venv()
        self.assertFalse(success)
        self.assertIn("Not a Python project", message)
    
    @patch('subprocess.run')
    def test_ensure_venv_create_new(self, mock_run):
        """Test ensure_venv creating new venv"""
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="")
        
        with patch.object(self.venv_manager, 'venv_exists', return_value=False):
            with patch.object(self.venv_manager, 'create_venv', return_value=(True, "Created")):
                success, message = self.venv_manager.ensure_venv()
                self.assertTrue(success)
    
    def test_is_venv_active_false(self):
        """Test venv active detection when not active"""
        result = self.venv_manager._is_venv_active()
        self.assertFalse(result)
    
    def test_is_venv_active_true(self):
        """Test venv active detection when active"""
        with patch.dict(os.environ, {'VIRTUAL_ENV': str(self.venv_manager.venv_path)}):
            result = self.venv_manager._is_venv_active()
            self.assertTrue(result)
    
    def test_check_venv_health_no_executables(self):
        """Test health check when executables don't exist"""
        status = self.venv_manager._check_venv_health()
        self.assertEqual(status, "corrupted")
    
    @patch('subprocess.run')
    def test_check_venv_health_healthy(self, mock_run):
        """Test health check for healthy venv"""
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="Python 3.9.0")
        
        with patch.object(self.venv_manager.python_exe, 'exists', return_value=True):
            with patch.object(self.venv_manager.pip_exe, 'exists', return_value=True):
                with patch.object(self.venv_manager, '_check_requirements_sync', return_value=True):
                    status = self.venv_manager._check_venv_health()
                    self.assertEqual(status, "healthy")


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create test Python project
        requirements_file = self.project_root / "requirements.txt"
        requirements_file.write_text("requests>=2.25.0\n")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('tools.venv_manager.VirtualEnvironmentManager')
    def test_ensure_python_venv_success(self, mock_manager_class):
        """Test ensure_python_venv success"""
        mock_manager = Mock()
        mock_manager.ensure_venv.return_value = (True, "Success")
        mock_manager_class.return_value = mock_manager
        
        success, message, manager = ensure_python_venv(str(self.project_root))
        
        self.assertTrue(success)
        self.assertEqual(message, "Success")
        self.assertIsNotNone(manager)
    
    @patch('tools.venv_manager.VirtualEnvironmentManager')
    def test_ensure_python_venv_failure(self, mock_manager_class):
        """Test ensure_python_venv failure"""
        mock_manager_class.side_effect = Exception("Test error")
        
        success, message, manager = ensure_python_venv(str(self.project_root))
        
        self.assertFalse(success)
        self.assertIn("Error ensuring venv", message)
        self.assertIsNone(manager)
    
    @patch('tools.venv_manager.VirtualEnvironmentManager')
    def test_get_venv_python_command_with_venv(self, mock_manager_class):
        """Test get_venv_python_command with existing venv"""
        mock_manager = Mock()
        mock_manager.venv_exists.return_value = True
        mock_manager.python_exe = "/path/to/venv/python"
        mock_manager_class.return_value = mock_manager
        
        command = get_venv_python_command(str(self.project_root))
        self.assertEqual(command, "/path/to/venv/python")
    
    @patch('tools.venv_manager.VirtualEnvironmentManager')
    def test_get_venv_python_command_no_venv(self, mock_manager_class):
        """Test get_venv_python_command without venv"""
        mock_manager = Mock()
        mock_manager.venv_exists.return_value = False
        mock_manager_class.return_value = mock_manager
        
        command = get_venv_python_command(str(self.project_root))
        self.assertEqual(command, "python")
    
    @patch('tools.venv_manager.VirtualEnvironmentManager')
    def test_wrap_python_command(self, mock_manager_class):
        """Test wrap_python_command"""
        mock_manager = Mock()
        mock_manager.get_python_command.return_value = "wrapped_command"
        mock_manager_class.return_value = mock_manager
        
        wrapped = wrap_python_command("python script.py", str(self.project_root))
        self.assertEqual(wrapped, "wrapped_command")


class TestVenvInfo(unittest.TestCase):
    """Test cases for VenvInfo dataclass"""
    
    def test_venv_info_creation(self):
        """Test VenvInfo creation"""
        info = VenvInfo(
            path="/path/to/venv",
            python_version="Python 3.9.0",
            is_active=True,
            created_date="2023-01-01",
            last_used="2023-01-02",
            packages_count=10,
            requirements_hash="abc123",
            status="healthy"
        )
        
        self.assertEqual(info.path, "/path/to/venv")
        self.assertEqual(info.python_version, "Python 3.9.0")
        self.assertTrue(info.is_active)
        self.assertEqual(info.status, "healthy")


class TestVenvConfig(unittest.TestCase):
    """Test cases for VenvConfig dataclass"""
    
    def test_venv_config_defaults(self):
        """Test VenvConfig default values"""
        config = VenvConfig()
        
        self.assertEqual(config.python_executable, sys.executable)
        self.assertEqual(config.venv_name, "venv")
        self.assertEqual(config.requirements_file, "requirements.txt")
        self.assertTrue(config.auto_activate)
        self.assertTrue(config.upgrade_pip)
        self.assertTrue(config.install_dev_requirements)
        self.assertEqual(config.dev_requirements_file, "requirements-dev.txt")
    
    def test_venv_config_custom(self):
        """Test VenvConfig with custom values"""
        config = VenvConfig(
            python_executable="/usr/bin/python3.9",
            venv_name="myenv",
            requirements_file="deps.txt",
            auto_activate=False,
            upgrade_pip=False
        )
        
        self.assertEqual(config.python_executable, "/usr/bin/python3.9")
        self.assertEqual(config.venv_name, "myenv")
        self.assertEqual(config.requirements_file, "deps.txt")
        self.assertFalse(config.auto_activate)
        self.assertFalse(config.upgrade_pip)


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2)
