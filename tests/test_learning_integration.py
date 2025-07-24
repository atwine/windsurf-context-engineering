#!/usr/bin/env python3
"""
Tests for Learning System Integration

This module tests the Phase 3 learning system integration capabilities
including enhanced recommendations and workflow learning.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

from tools.learning_integration import (
    LearningSystemIntegration,
    get_learning_enhanced_recommendations,
    sync_intelligence_with_learning,
    learn_from_workflow,
    get_integration_status
)

class TestLearningSystemIntegration(unittest.TestCase):
    """Test cases for LearningSystemIntegration class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test project structure
        (self.test_path / "requirements.txt").write_text("pytest==7.0.0\nblack==22.0.0\n")
        (self.test_path / "main.py").write_text("print('Hello, World!')\n")
        
        # Initialize learning integration
        self.integration = LearningSystemIntegration(str(self.test_path))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test learning integration initialization."""
        self.assertIsInstance(self.integration, LearningSystemIntegration)
        self.assertEqual(str(self.integration.project_path), str(self.test_path))
        self.assertIsNotNone(self.integration.intelligence_engine)
        
        # Check data structures
        self.assertIsInstance(self.integration.learning_modules, dict)
        self.assertIsInstance(self.integration.integration_active, bool)
        self.assertIsInstance(self.integration.last_sync_time, float)
    
    def test_initialization_without_learning_system(self):
        """Test initialization when no existing learning system is present."""
        # Should initialize successfully even without learning directory
        self.assertIsInstance(self.integration, LearningSystemIntegration)
        self.assertFalse(self.integration.integration_active)
        self.assertEqual(len(self.integration.learning_modules), 0)
    
    def test_initialization_with_learning_system(self):
        """Test initialization with existing learning system."""
        # Create mock learning directory
        learning_dir = self.test_path / "learning"
        learning_dir.mkdir()
        
        # Create mock learning module
        (learning_dir / "pattern_recognition.py").write_text("""
def update_from_intelligence(data):
    pass
""")
        
        # Initialize new integration
        integration = LearningSystemIntegration(str(self.test_path))
        
        # Should detect learning system (though import might fail)
        # The integration_active state depends on successful module loading
        self.assertIsInstance(integration.learning_modules, dict)
    
    def test_get_enhanced_recommendations(self):
        """Test enhanced recommendations generation."""
        recommendations = self.integration.get_enhanced_recommendations()
        
        self.assertIsInstance(recommendations, list)
        
        # Check recommendation structure if any exist
        if recommendations:
            rec = recommendations[0]
            self.assertIsInstance(rec, dict)
            self.assertIn('type', rec)
            self.assertIn('action', rec)
            self.assertIn('description', rec)
            self.assertIn('confidence', rec)
            self.assertIn('priority', rec)
            self.assertIn('reasoning', rec)
            self.assertIn('estimated_impact', rec)
            self.assertIn('prerequisites', rec)
            self.assertIn('timestamp', rec)
    
    def test_enhance_recommendation_with_learning(self):
        """Test recommendation enhancement with learning data."""
        from tools.intelligence_engine import Recommendation
        
        # Create test recommendation
        rec = Recommendation(
            type='commit',
            action='git_commit',
            description='Test commit recommendation',
            confidence=0.7,
            priority='medium',
            reasoning='Test reasoning',
            estimated_impact='Test impact',
            prerequisites=['test'],
            timestamp=time.time()
        )
        
        # Enhance recommendation
        enhanced_rec = self.integration._enhance_recommendation_with_learning(rec)
        
        self.assertIsInstance(enhanced_rec, Recommendation)
        self.assertEqual(enhanced_rec.type, 'commit')
        self.assertEqual(enhanced_rec.action, 'git_commit')
        # Confidence might be adjusted
        self.assertGreaterEqual(enhanced_rec.confidence, 0.0)
        self.assertLessEqual(enhanced_rec.confidence, 1.0)
    
    def test_generate_learning_recommendations(self):
        """Test learning-specific recommendations generation."""
        learning_recs = self.integration._generate_learning_recommendations()
        
        self.assertIsInstance(learning_recs, list)
        
        # Check recommendation structure if any exist
        for rec in learning_recs:
            from tools.intelligence_engine import Recommendation
            self.assertIsInstance(rec, Recommendation)
            self.assertEqual(rec.type, 'learning')
            self.assertGreater(rec.confidence, 0.0)
    
    def test_analyze_learning_patterns(self):
        """Test learning pattern analysis."""
        patterns = self.integration._analyze_learning_patterns()
        
        self.assertIsInstance(patterns, list)
        
        # Check pattern structure if any exist
        for pattern in patterns:
            self.assertIsInstance(pattern, dict)
            self.assertIn('action', pattern)
            self.assertIn('description', pattern)
            self.assertIn('confidence', pattern)
            self.assertIn('priority', pattern)
            self.assertIn('reasoning', pattern)
            self.assertIn('impact', pattern)
            self.assertIn('prerequisites', pattern)
            self.assertIn('timestamp', pattern)
    
    def test_get_learning_data_for_recommendation(self):
        """Test learning data retrieval for recommendations."""
        from tools.intelligence_engine import Recommendation
        
        # Create test recommendation
        rec = Recommendation(
            type='commit',
            action='git_commit',
            description='Test',
            confidence=0.7,
            priority='medium',
            reasoning='Test',
            estimated_impact='Test',
            prerequisites=[],
            timestamp=time.time()
        )
        
        learning_data = self.integration._get_learning_data_for_recommendation(rec)
        
        if learning_data:
            self.assertIsInstance(learning_data, dict)
            self.assertIn('success_rate', learning_data)
            self.assertIn('insight', learning_data)
    
    def test_sync_with_learning_system(self):
        """Test synchronization with learning system."""
        # Should not raise exception even without active learning system
        try:
            self.integration.sync_with_learning_system()
        except Exception as e:
            self.fail(f"sync_with_learning_system raised {e} unexpectedly")
        
        # Check sync time was updated if integration is active
        if self.integration.integration_active:
            self.assertGreater(self.integration.last_sync_time, 0)
    
    def test_learn_from_workflow_execution(self):
        """Test learning from workflow execution."""
        execution_data = {
            'duration': 30.0,
            'success': True,
            'errors': [],
            'commands': [
                {
                    'command': 'python -m pytest',
                    'success': True,
                    'exit_code': 0,
                    'output': 'All tests passed',
                    'error': '',
                    'duration': 5.0,
                    'environment': 'venv',
                    'git_changes': False
                }
            ],
            'environment': {'python_version': '3.9', 'venv_active': True},
            'git_operations': ['commit', 'push']
        }
        
        # Should not raise exception
        try:
            self.integration.learn_from_workflow_execution('test_workflow', execution_data)
        except Exception as e:
            self.fail(f"learn_from_workflow_execution raised {e} unexpectedly")
    
    def test_store_workflow_learning_data(self):
        """Test workflow learning data storage."""
        learning_data = {
            'workflow_name': 'test_workflow',
            'execution_time': 30.0,
            'success': True,
            'errors': [],
            'commands_executed': ['python -m pytest'],
            'environment_used': {'venv': True},
            'git_operations': ['commit'],
            'timestamp': time.time()
        }
        
        # Store learning data
        self.integration._store_workflow_learning_data(learning_data)
        
        # Check file was created
        learning_files = list(self.integration.learning_data_path.glob("workflow_test_workflow_*.json"))
        self.assertGreater(len(learning_files), 0)
        
        # Check file content
        if learning_files:
            with open(learning_files[0], 'r') as f:
                stored_data = json.load(f)
            
            self.assertEqual(stored_data['workflow_name'], 'test_workflow')
            self.assertEqual(stored_data['success'], True)
    
    def test_get_learning_integration_status(self):
        """Test learning integration status retrieval."""
        status = self.integration.get_learning_integration_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('integration_active', status)
        self.assertIn('learning_modules_loaded', status)
        self.assertIn('learning_modules', status)
        self.assertIn('last_sync_time', status)
        self.assertIn('intelligence_engine_health', status)
        self.assertIn('learning_data_path', status)
        self.assertIn('timestamp', status)
        
        # Check data types
        self.assertIsInstance(status['integration_active'], bool)
        self.assertIsInstance(status['learning_modules_loaded'], int)
        self.assertIsInstance(status['learning_modules'], list)
        self.assertIsInstance(status['last_sync_time'], float)
        self.assertIsInstance(status['intelligence_engine_health'], float)
        self.assertIsInstance(status['learning_data_path'], str)
        self.assertGreater(status['timestamp'], 0)
    
    def test_recommendation_to_dict(self):
        """Test recommendation to dictionary conversion."""
        from tools.intelligence_engine import Recommendation
        
        rec = Recommendation(
            type='test',
            action='test_action',
            description='Test recommendation',
            confidence=0.8,
            priority='medium',
            reasoning='Test reasoning',
            estimated_impact='Test impact',
            prerequisites=['test prereq'],
            timestamp=time.time()
        )
        
        rec_dict = self.integration._recommendation_to_dict(rec)
        
        self.assertIsInstance(rec_dict, dict)
        self.assertEqual(rec_dict['type'], 'test')
        self.assertEqual(rec_dict['action'], 'test_action')
        self.assertEqual(rec_dict['description'], 'Test recommendation')
        self.assertEqual(rec_dict['confidence'], 0.8)
        self.assertEqual(rec_dict['priority'], 'medium')
        self.assertEqual(rec_dict['reasoning'], 'Test reasoning')
        self.assertEqual(rec_dict['estimated_impact'], 'Test impact')
        self.assertEqual(rec_dict['prerequisites'], ['test prereq'])
        self.assertGreater(rec_dict['timestamp'], 0)


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test project
        (self.test_path / "requirements.txt").write_text("pytest==7.0.0\n")
        (self.test_path / "main.py").write_text("print('Hello')\n")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_get_learning_enhanced_recommendations(self):
        """Test get_learning_enhanced_recommendations convenience function."""
        recommendations = get_learning_enhanced_recommendations(str(self.test_path))
        
        self.assertIsInstance(recommendations, list)
        for rec in recommendations:
            self.assertIsInstance(rec, dict)
            self.assertIn('type', rec)
            self.assertIn('action', rec)
            self.assertIn('description', rec)
            self.assertIn('confidence', rec)
            self.assertIn('priority', rec)
    
    def test_sync_intelligence_with_learning(self):
        """Test sync_intelligence_with_learning convenience function."""
        # Should not raise exception
        try:
            sync_intelligence_with_learning(str(self.test_path))
        except Exception as e:
            self.fail(f"sync_intelligence_with_learning raised {e} unexpectedly")
    
    def test_learn_from_workflow(self):
        """Test learn_from_workflow convenience function."""
        execution_data = {
            'duration': 10.0,
            'success': True,
            'errors': [],
            'commands': [{'command': 'echo test', 'success': True}],
            'environment': {},
            'git_operations': []
        }
        
        # Should not raise exception
        try:
            learn_from_workflow('test_workflow', execution_data, str(self.test_path))
        except Exception as e:
            self.fail(f"learn_from_workflow raised {e} unexpectedly")
    
    def test_get_integration_status(self):
        """Test get_integration_status convenience function."""
        status = get_integration_status(str(self.test_path))
        
        self.assertIsInstance(status, dict)
        self.assertIn('integration_active', status)
        self.assertIn('learning_modules_loaded', status)
    
    def test_error_handling(self):
        """Test error handling in convenience functions."""
        # Test with invalid path
        recommendations = get_learning_enhanced_recommendations("/nonexistent/path")
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), 0)
        
        status = get_integration_status("/nonexistent/path")
        self.assertIsInstance(status, dict)
        self.assertIn('error', status)


class TestLearningModuleLoading(unittest.TestCase):
    """Test cases for learning module loading functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create learning directory
        self.learning_dir = self.test_path / "learning"
        self.learning_dir.mkdir()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_load_learning_modules_success(self):
        """Test successful learning module loading."""
        # Create mock learning module
        module_content = """
def update_from_intelligence(data):
    '''Mock function for testing'''
    return data

class MockLearningClass:
    def __init__(self):
        self.data = {}
"""
        
        (self.learning_dir / "pattern_recognition.py").write_text(module_content)
        
        # Initialize integration
        integration = LearningSystemIntegration(str(self.test_path))
        
        # Should attempt to load modules (may not succeed due to import path issues)
        self.assertIsInstance(integration.learning_modules, dict)
    
    def test_load_learning_modules_failure(self):
        """Test learning module loading with import failures."""
        # Create invalid Python file
        (self.learning_dir / "invalid_module.py").write_text("invalid python syntax !!!")
        
        # Should handle import errors gracefully
        integration = LearningSystemIntegration(str(self.test_path))
        
        # Should not crash and should have empty modules dict
        self.assertIsInstance(integration.learning_modules, dict)


class TestLearningDataPersistence(unittest.TestCase):
    """Test cases for learning data persistence."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test project
        (self.test_path / "requirements.txt").write_text("pytest==7.0.0\n")
        
        self.integration = LearningSystemIntegration(str(self.test_path))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_workflow_learning_data_persistence(self):
        """Test workflow learning data is persisted correctly."""
        # Create test execution data
        execution_data = {
            'duration': 25.0,
            'success': True,
            'errors': ['minor warning'],
            'commands': [
                {
                    'command': 'python setup.py test',
                    'success': True,
                    'exit_code': 0,
                    'output': 'Tests completed',
                    'error': '',
                    'duration': 20.0,
                    'environment': 'venv',
                    'git_changes': True
                }
            ],
            'environment': {'python_version': '3.9', 'venv_active': True},
            'git_operations': ['add', 'commit']
        }
        
        # Learn from workflow
        self.integration.learn_from_workflow_execution('integration_test', execution_data)
        
        # Check learning data directory exists
        self.assertTrue(self.integration.learning_data_path.exists())
        
        # Check learning data file was created
        learning_files = list(self.integration.learning_data_path.glob("workflow_integration_test_*.json"))
        self.assertGreater(len(learning_files), 0)
        
        # Verify file content
        if learning_files:
            with open(learning_files[0], 'r') as f:
                stored_data = json.load(f)
            
            self.assertEqual(stored_data['workflow_name'], 'integration_test')
            self.assertEqual(stored_data['execution_time'], 25.0)
            self.assertTrue(stored_data['success'])
            self.assertEqual(len(stored_data['commands_executed']), 1)
            self.assertIn('python_version', stored_data['environment_used'])


if __name__ == '__main__':
    unittest.main()
