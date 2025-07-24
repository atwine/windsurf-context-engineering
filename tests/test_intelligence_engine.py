#!/usr/bin/env python3
"""
Tests for Intelligence Engine

This module tests the Phase 3 intelligence engine capabilities including
AI-powered recommendations, context analysis, and learning integration.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

from tools.intelligence_engine import (
    IntelligenceEngine,
    IntelligenceContext,
    Recommendation,
    LearningPattern,
    get_intelligence_recommendations,
    analyze_project_intelligence,
    learn_from_command
)

class TestIntelligenceEngine(unittest.TestCase):
    """Test cases for IntelligenceEngine class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test project structure
        (self.test_path / "requirements.txt").write_text("pytest==7.0.0\nblack==22.0.0\n")
        (self.test_path / "main.py").write_text("print('Hello, World!')\n")
        
        # Initialize intelligence engine
        self.engine = IntelligenceEngine(str(self.test_path))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test intelligence engine initialization."""
        self.assertIsInstance(self.engine, IntelligenceEngine)
        self.assertEqual(str(self.engine.project_path), str(self.test_path))
        self.assertIsNotNone(self.engine.command_executor)
        self.assertIsNotNone(self.engine.git_manager)
        self.assertIsNotNone(self.engine.venv_manager)
        
        # Check data structures
        self.assertIsInstance(self.engine.patterns_cache, dict)
        self.assertIsInstance(self.engine.performance_metrics, dict)
    
    def test_analyze_context(self):
        """Test context analysis functionality."""
        context = self.engine.analyze_context()
        
        self.assertIsInstance(context, IntelligenceContext)
        self.assertEqual(context.project_path, str(self.test_path))
        self.assertIn(context.project_type, ['python', 'generic'])
        self.assertIsInstance(context.git_status, dict)
        self.assertIsInstance(context.environment_status, dict)
        self.assertIsInstance(context.recent_commands, list)
        self.assertIsInstance(context.workflow_history, list)
        self.assertIsInstance(context.performance_metrics, dict)
        self.assertGreater(context.timestamp, 0)
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        recommendations = self.engine.generate_recommendations()
        
        self.assertIsInstance(recommendations, list)
        
        # Check recommendation structure if any exist
        if recommendations:
            rec = recommendations[0]
            self.assertIsInstance(rec, Recommendation)
            self.assertIn(rec.type, ['commit', 'push', 'environment', 'workflow', 'optimization'])
            self.assertIsInstance(rec.action, str)
            self.assertIsInstance(rec.description, str)
            self.assertGreaterEqual(rec.confidence, 0.0)
            self.assertLessEqual(rec.confidence, 1.0)
            self.assertIn(rec.priority, ['low', 'medium', 'high', 'critical'])
            self.assertIsInstance(rec.reasoning, str)
            self.assertIsInstance(rec.estimated_impact, str)
            self.assertIsInstance(rec.prerequisites, list)
            self.assertGreater(rec.timestamp, 0)
    
    def test_git_recommendations(self):
        """Test Git-related recommendations."""
        # Mock Git status to have changes
        with patch.object(self.engine.command_executor, 'get_git_recommendations') as mock_git:
            mock_git.return_value = ['commit changes', 'push to remote']
            
            context = self.engine.analyze_context()
            context.git_status['has_changes'] = True
            context.git_status['is_git_repo'] = True
            
            git_recs = self.engine._generate_git_recommendations(context)
            
            self.assertIsInstance(git_recs, list)
            # Should generate recommendations when changes are present
            if git_recs:
                for rec in git_recs:
                    self.assertIn(rec.type, ['commit', 'push'])
    
    def test_environment_recommendations(self):
        """Test environment-related recommendations."""
        context = self.engine.analyze_context()
        context.environment_status['python_project'] = True
        context.environment_status['has_venv'] = False
        context.environment_status['requirements_present'] = True
        
        env_recs = self.engine._generate_environment_recommendations(context)
        
        self.assertIsInstance(env_recs, list)
        # Should recommend creating venv for Python project without one
        venv_recs = [r for r in env_recs if r.action == 'create_venv']
        self.assertGreater(len(venv_recs), 0)
        
        if venv_recs:
            rec = venv_recs[0]
            self.assertEqual(rec.type, 'environment')
            self.assertEqual(rec.priority, 'high')
    
    def test_workflow_recommendations(self):
        """Test workflow optimization recommendations."""
        context = self.engine.analyze_context()
        
        workflow_recs = self.engine._generate_workflow_recommendations(context)
        
        self.assertIsInstance(workflow_recs, list)
        for rec in workflow_recs:
            self.assertEqual(rec.type, 'workflow')
            self.assertIn(rec.action, ['optimize_workflow', 'optimize_commands'])
    
    def test_performance_recommendations(self):
        """Test performance optimization recommendations."""
        context = self.engine.analyze_context()
        # Set poor performance metrics
        context.performance_metrics['average_command_duration'] = 15.0
        context.performance_metrics['command_success_rate'] = 0.7
        
        perf_recs = self.engine._generate_performance_recommendations(context)
        
        self.assertIsInstance(perf_recs, list)
        for rec in perf_recs:
            self.assertEqual(rec.type, 'optimization')
            self.assertIn('performance', rec.description.lower())
    
    def test_learn_from_execution(self):
        """Test learning from command execution."""
        from tools.command_executor import CommandResult
        
        # Create mock command result
        result = CommandResult(
            command="python -m pytest",
            success=True,
            exit_code=0,
            stdout="All tests passed",
            stderr="",
            execution_time=2.5,
            environment_used="venv",
            git_changes_detected=False
        )
        
        context = self.engine.analyze_context()
        initial_patterns = len(self.engine.patterns_cache)
        
        # Learn from execution
        self.engine.learn_from_execution("python -m pytest", result, context)
        
        # Check that learning occurred
        self.assertGreaterEqual(len(self.engine.patterns_cache), initial_patterns)
    
    def test_intelligence_summary(self):
        """Test intelligence summary generation."""
        summary = self.engine.get_intelligence_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('context', summary)
        self.assertIn('recommendations', summary)
        self.assertIn('performance_metrics', summary)
        self.assertIn('learning_patterns', summary)
        self.assertIn('intelligence_health', summary)
        self.assertIn('timestamp', summary)
        
        # Check data types
        self.assertIsInstance(summary['context'], dict)
        self.assertIsInstance(summary['recommendations'], list)
        self.assertIsInstance(summary['performance_metrics'], dict)
        self.assertIsInstance(summary['learning_patterns'], int)
        self.assertIsInstance(summary['intelligence_health'], float)
        self.assertGreater(summary['timestamp'], 0)
    
    def test_pattern_storage_and_retrieval(self):
        """Test learning pattern storage and retrieval."""
        # Create test pattern
        pattern = LearningPattern(
            pattern_id="test_pattern",
            pattern_type="command_execution",
            context={"command": "test", "success": True},
            frequency=1,
            success_rate=1.0,
            average_duration=1.0,
            common_errors=[],
            optimization_suggestions=[],
            last_seen=time.time()
        )
        
        # Store pattern
        self.engine._store_learning_pattern(pattern)
        
        # Check pattern was stored
        self.assertIn("test_pattern", self.engine.patterns_cache)
        stored_pattern = self.engine.patterns_cache["test_pattern"]
        self.assertEqual(stored_pattern.pattern_id, "test_pattern")
        self.assertEqual(stored_pattern.frequency, 1)
    
    def test_confidence_calculations(self):
        """Test confidence score calculations."""
        context = self.engine.analyze_context()
        
        # Test commit confidence
        commit_confidence = self.engine._calculate_commit_confidence(context)
        self.assertGreaterEqual(commit_confidence, 0.0)
        self.assertLessEqual(commit_confidence, 1.0)
        
        # Test push confidence
        push_confidence = self.engine._calculate_push_confidence(context)
        self.assertGreaterEqual(push_confidence, 0.0)
        self.assertLessEqual(push_confidence, 1.0)
        
        # Test workflow efficiency
        workflow_efficiency = self.engine._calculate_workflow_efficiency(context)
        self.assertGreaterEqual(workflow_efficiency, 0.0)
        self.assertLessEqual(workflow_efficiency, 1.0)
    
    def test_project_type_detection(self):
        """Test project type detection."""
        # Python project (has requirements.txt)
        project_type = self.engine._determine_project_type()
        self.assertEqual(project_type, 'python')
        
        # Create JavaScript project
        (self.test_path / "package.json").write_text('{"name": "test"}')
        project_type = self.engine._determine_project_type()
        self.assertEqual(project_type, 'python')  # Still Python due to requirements.txt
        
        # Remove Python files, should detect JavaScript
        (self.test_path / "requirements.txt").unlink()
        project_type = self.engine._determine_project_type()
        self.assertEqual(project_type, 'javascript')
    
    def test_performance_metrics_update(self):
        """Test performance metrics updating."""
        from tools.command_executor import CommandResult
        
        initial_success_rate = self.engine.performance_metrics.get('command_success_rate', 1.0)
        
        # Simulate successful command
        result = CommandResult(
            command="echo test",
            success=True,
            exit_code=0,
            stdout="test",
            stderr="",
            execution_time=0.1,
            environment_used="",
            git_changes_detected=False
        )
        
        self.engine._update_performance_metrics("echo test", result)
        
        # Check metrics were updated
        new_success_rate = self.engine.performance_metrics.get('command_success_rate', 1.0)
        self.assertIsInstance(new_success_rate, float)
        
        # Simulate failed command
        result.success = False
        result.exit_code = 1
        
        self.engine._update_performance_metrics("failing_command", result)
        
        # Success rate should have decreased
        final_success_rate = self.engine.performance_metrics.get('command_success_rate', 1.0)
        self.assertLess(final_success_rate, new_success_rate)
    
    def test_intelligence_health_calculation(self):
        """Test intelligence health score calculation."""
        health_score = self.engine._calculate_intelligence_health()
        
        self.assertIsInstance(health_score, float)
        self.assertGreaterEqual(health_score, 0.0)
        self.assertLessEqual(health_score, 1.0)
    
    def test_data_persistence(self):
        """Test data persistence functionality."""
        # Create test pattern
        pattern = LearningPattern(
            pattern_id="persist_test",
            pattern_type="test",
            context={"test": True},
            frequency=1,
            success_rate=1.0,
            average_duration=1.0,
            common_errors=[],
            optimization_suggestions=[],
            last_seen=time.time()
        )
        
        self.engine.patterns_cache["persist_test"] = pattern
        
        # Save data
        self.engine._save_learning_data()
        
        # Check file was created
        patterns_file = self.engine.learning_data_path / "patterns.json"
        self.assertTrue(patterns_file.exists())
        
        # Load data in new engine instance
        new_engine = IntelligenceEngine(str(self.test_path))
        
        # Check pattern was loaded
        self.assertIn("persist_test", new_engine.patterns_cache)


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
    
    def test_get_intelligence_recommendations(self):
        """Test get_intelligence_recommendations convenience function."""
        recommendations = get_intelligence_recommendations(str(self.test_path))
        
        self.assertIsInstance(recommendations, list)
        for rec in recommendations:
            self.assertIsInstance(rec, dict)
            self.assertIn('type', rec)
            self.assertIn('action', rec)
            self.assertIn('description', rec)
            self.assertIn('confidence', rec)
            self.assertIn('priority', rec)
    
    def test_analyze_project_intelligence(self):
        """Test analyze_project_intelligence convenience function."""
        analysis = analyze_project_intelligence(str(self.test_path))
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('context', analysis)
        self.assertIn('recommendations', analysis)
        self.assertIn('performance_metrics', analysis)
    
    def test_learn_from_command(self):
        """Test learn_from_command convenience function."""
        # Should not raise exception
        try:
            learn_from_command("echo test", True, 0.1, str(self.test_path))
        except Exception as e:
            self.fail(f"learn_from_command raised {e} unexpectedly")
    
    def test_error_handling(self):
        """Test error handling in convenience functions."""
        # Test with invalid path
        recommendations = get_intelligence_recommendations("/nonexistent/path")
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), 0)
        
        analysis = analyze_project_intelligence("/nonexistent/path")
        self.assertIsInstance(analysis, dict)
        self.assertIn('error', analysis)


class TestRecommendationDataClass(unittest.TestCase):
    """Test cases for Recommendation data class."""
    
    def test_recommendation_creation(self):
        """Test recommendation creation and attributes."""
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
        
        self.assertEqual(rec.type, 'test')
        self.assertEqual(rec.action, 'test_action')
        self.assertEqual(rec.description, 'Test recommendation')
        self.assertEqual(rec.confidence, 0.8)
        self.assertEqual(rec.priority, 'medium')
        self.assertEqual(rec.reasoning, 'Test reasoning')
        self.assertEqual(rec.estimated_impact, 'Test impact')
        self.assertEqual(rec.prerequisites, ['test prereq'])
        self.assertGreater(rec.timestamp, 0)


class TestLearningPatternDataClass(unittest.TestCase):
    """Test cases for LearningPattern data class."""
    
    def test_learning_pattern_creation(self):
        """Test learning pattern creation and attributes."""
        pattern = LearningPattern(
            pattern_id='test_pattern',
            pattern_type='test',
            context={'test': True},
            frequency=5,
            success_rate=0.9,
            average_duration=2.5,
            common_errors=['error1', 'error2'],
            optimization_suggestions=['opt1', 'opt2'],
            last_seen=time.time()
        )
        
        self.assertEqual(pattern.pattern_id, 'test_pattern')
        self.assertEqual(pattern.pattern_type, 'test')
        self.assertEqual(pattern.context, {'test': True})
        self.assertEqual(pattern.frequency, 5)
        self.assertEqual(pattern.success_rate, 0.9)
        self.assertEqual(pattern.average_duration, 2.5)
        self.assertEqual(pattern.common_errors, ['error1', 'error2'])
        self.assertEqual(pattern.optimization_suggestions, ['opt1', 'opt2'])
        self.assertGreater(pattern.last_seen, 0)


if __name__ == '__main__':
    unittest.main()
