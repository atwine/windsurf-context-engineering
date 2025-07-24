#!/usr/bin/env python3
"""
Unit Tests for Git Operations Manager
====================================

Comprehensive test suite for the GitOperationsManager class,
testing Git operations, commit recommendations, and push analysis.
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

from tools.git_manager import (
    GitOperationsManager,
    GitStatus,
    CommitRecommendation,
    PushRecommendation,
    CollaborationInfo,
    get_git_status,
    should_commit_now,
    should_push_now
)

class TestGitOperationsManager(unittest.TestCase):
    """Test cases for GitOperationsManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.git_manager = GitOperationsManager(str(self.project_root))
        
        # Create test files
        self.test_py_file = self.project_root / "test_script.py"
        self.test_py_file.write_text("print('Hello, World!')\n")
        
        self.readme_file = self.project_root / "README.md"
        self.readme_file.write_text("# Test Project\n")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test GitOperationsManager initialization"""
        self.assertEqual(self.git_manager.project_root, self.project_root)
        self.assertTrue(self.git_manager.enable_ai_features)
        self.assertIsInstance(self.git_manager.config, dict)
    
    def test_init_without_ai(self):
        """Test GitOperationsManager initialization without AI features"""
        manager = GitOperationsManager(str(self.project_root), enable_ai_features=False)
        self.assertFalse(manager.enable_ai_features)
    
    def test_is_git_repository_false(self):
        """Test is_git_repository when not a Git repo"""
        result = self.git_manager.is_git_repository()
        self.assertFalse(result)
    
    def test_get_git_status_not_repo(self):
        """Test get_git_status when not a Git repository"""
        status = self.git_manager.get_git_status()
        
        self.assertIsInstance(status, GitStatus)
        self.assertFalse(status.is_repo)
        self.assertEqual(status.branch, "")
        self.assertFalse(status.has_changes)
        self.assertEqual(len(status.staged_files), 0)
    
    @patch('subprocess.run')
    def test_get_status_with_subprocess(self, mock_run):
        """Test _get_status_with_subprocess"""
        # Mock git commands - need to match the actual command structure
        def mock_git_command(*args, **kwargs):
            cmd = args[0] if args else kwargs.get('args', [])
            if cmd == ["git", "branch", "--show-current"]:
                return Mock(returncode=0, stdout="main")
            elif cmd == ["git", "status", "--porcelain"]:
                return Mock(returncode=0, stdout=" M test_script.py\n?? new_file.py")
            elif cmd == ["git", "rev-parse", "--short", "HEAD"]:
                return Mock(returncode=0, stdout="abc1234")
            elif cmd == ["git", "log", "-1", "--pretty=format:%s"]:
                return Mock(returncode=0, stdout="Initial commit")
            elif cmd == ["git", "log", "-1", "--pretty=format:%cI"]:
                return Mock(returncode=0, stdout="2023-01-01T12:00:00Z")
            elif cmd == ["git", "remote", "get-url", "origin"]:
                return Mock(returncode=0, stdout="https://github.com/user/repo.git")
            else:
                return Mock(returncode=0, stdout="")
        
        mock_run.side_effect = mock_git_command
        
        with patch.object(self.git_manager, 'is_git_repository', return_value=True):
            status = self.git_manager._get_status_with_subprocess()
            
            self.assertTrue(status.is_repo)
            self.assertEqual(status.branch, "main")
            self.assertTrue(status.has_changes)
            self.assertIn("test_script.py", status.unstaged_files)
            self.assertIn("new_file.py", status.untracked_files)
    
    def test_analyze_file_types(self):
        """Test _analyze_file_types"""
        files = ["script.py", "README.md", "config.json", "test.py"]
        file_types = self.git_manager._analyze_file_types(files)
        
        self.assertEqual(file_types['.py'], 2)
        self.assertEqual(file_types['.md'], 1)
        self.assertEqual(file_types['.json'], 1)
    
    def test_detect_change_patterns(self):
        """Test _detect_change_patterns"""
        files = ["test_script.py", "README.md", "requirements.txt"]
        patterns = self.git_manager._detect_change_patterns(files)
        
        self.assertIn("tests", patterns)
        self.assertIn("documentation", patterns)
        self.assertIn("dependencies", patterns)
    
    def test_determine_commit_type_feature(self):
        """Test _determine_commit_type for feature"""
        file_types = {'.py': 2}
        patterns = []
        context = "add new feature for user authentication"
        
        commit_type = self.git_manager._determine_commit_type(file_types, patterns, context)
        self.assertEqual(commit_type, "feat")
    
    def test_determine_commit_type_fix(self):
        """Test _determine_commit_type for fix"""
        file_types = {'.py': 1}
        patterns = []
        context = "fix bug in login validation"
        
        commit_type = self.git_manager._determine_commit_type(file_types, patterns, context)
        self.assertEqual(commit_type, "fix")
    
    def test_determine_commit_type_docs(self):
        """Test _determine_commit_type for documentation"""
        file_types = {'.md': 1}
        patterns = ["documentation"]
        context = ""
        
        commit_type = self.git_manager._determine_commit_type(file_types, patterns, context)
        self.assertEqual(commit_type, "docs")
    
    def test_generate_basic_commit_message(self):
        """Test _generate_basic_commit_message"""
        files = ["script.py", "helper.py"]
        message = self.git_manager._generate_basic_commit_message("feat", files)
        
        self.assertTrue(message.startswith("feat:"))
        self.assertIn("script.py", message)
    
    def test_summarize_files_single(self):
        """Test _summarize_files with single file"""
        files = ["script.py"]
        summary = self.git_manager._summarize_files(files)
        self.assertEqual(summary, "script.py")
    
    def test_summarize_files_multiple(self):
        """Test _summarize_files with multiple files"""
        files = ["script.py", "helper.py", "config.json"]
        summary = self.git_manager._summarize_files(files)
        self.assertEqual(summary, "script.py, helper.py, config.json")
    
    def test_summarize_files_many(self):
        """Test _summarize_files with many files"""
        files = ["file1.py", "file2.py", "file3.py", "file4.py", "file5.py"]
        summary = self.git_manager._summarize_files(files)
        self.assertEqual(summary, "5 files")
    
    def test_select_files_to_stage(self):
        """Test _select_files_to_stage"""
        files = ["script.py", "__pycache__/test.pyc", "README.md", ".DS_Store"]
        selected = self.git_manager._select_files_to_stage(files)
        
        self.assertIn("script.py", selected)
        self.assertIn("README.md", selected)
        self.assertNotIn("__pycache__/test.pyc", selected)
        self.assertNotIn(".DS_Store", selected)
    
    def test_calculate_commit_confidence(self):
        """Test _calculate_commit_confidence"""
        files = ["script.py", "helper.py"]
        context = "add new feature"
        confidence = self.git_manager._calculate_commit_confidence(files, context)
        
        self.assertGreater(confidence, 0.5)
        self.assertLessEqual(confidence, 1.0)
    
    def test_generate_commit_reasoning(self):
        """Test _generate_commit_reasoning"""
        files = ["script.py", "helper.py"]
        reasoning = self.git_manager._generate_commit_reasoning(files, "feat", 0.8)
        
        self.assertIn("2 files", reasoning)
        self.assertIn("feat", reasoning)
    
    def test_get_commit_recommendation_no_changes(self):
        """Test get_commit_recommendation with no changes"""
        with patch.object(self.git_manager, 'get_git_status') as mock_status:
            mock_status.return_value = GitStatus(
                is_repo=True, branch="main", has_changes=False,
                staged_files=[], unstaged_files=[], untracked_files=[],
                commits_ahead=0, commits_behind=0,
                last_commit_hash="", last_commit_message="", last_commit_date="",
                remote_url=""
            )
            
            recommendation = self.git_manager.get_commit_recommendation()
            
            self.assertFalse(recommendation.should_commit)
            self.assertEqual(recommendation.confidence, 1.0)
            self.assertIn("No changes", recommendation.reasoning)
    
    def test_get_commit_recommendation_with_changes(self):
        """Test get_commit_recommendation with changes"""
        with patch.object(self.git_manager, 'get_git_status') as mock_status:
            mock_status.return_value = GitStatus(
                is_repo=True, branch="main", has_changes=True,
                staged_files=[], unstaged_files=["script.py"], untracked_files=[],
                commits_ahead=0, commits_behind=0,
                last_commit_hash="", last_commit_message="", last_commit_date="",
                remote_url=""
            )
            
            recommendation = self.git_manager.get_commit_recommendation("add new feature")
            
            self.assertIsInstance(recommendation, CommitRecommendation)
            self.assertIsInstance(recommendation.should_commit, bool)
            self.assertIsInstance(recommendation.confidence, float)
            self.assertIsInstance(recommendation.suggested_message, str)
    
    def test_get_push_recommendation_no_commits(self):
        """Test get_push_recommendation with no commits to push"""
        with patch.object(self.git_manager, 'get_git_status') as mock_status:
            mock_status.return_value = GitStatus(
                is_repo=True, branch="main", has_changes=False,
                staged_files=[], unstaged_files=[], untracked_files=[],
                commits_ahead=0, commits_behind=0,
                last_commit_hash="", last_commit_message="", last_commit_date="",
                remote_url=""
            )
            
            recommendation = self.git_manager.get_push_recommendation()
            
            self.assertFalse(recommendation.should_push)
            self.assertEqual(recommendation.confidence, 1.0)
            self.assertIn("No commits", recommendation.reasoning)
    
    def test_get_push_recommendation_with_commits(self):
        """Test get_push_recommendation with commits to push"""
        with patch.object(self.git_manager, 'get_git_status') as mock_status:
            with patch.object(self.git_manager, '_analyze_collaboration') as mock_collab:
                mock_status.return_value = GitStatus(
                    is_repo=True, branch="main", has_changes=False,
                    staged_files=[], unstaged_files=[], untracked_files=[],
                    commits_ahead=2, commits_behind=0,
                    last_commit_hash="abc123", last_commit_message="Test commit", last_commit_date="",
                    remote_url="https://github.com/user/repo.git"
                )
                
                mock_collab.return_value = CollaborationInfo(
                    active_branches=[], recent_commits=[], potential_conflicts=[],
                    team_activity_level='low', last_team_push=""
                )
                
                recommendation = self.git_manager.get_push_recommendation(quality_score=0.9)
                
                self.assertIsInstance(recommendation, PushRecommendation)
                self.assertIsInstance(recommendation.should_push, bool)
                self.assertIsInstance(recommendation.confidence, float)
    
    def test_assess_collaboration_risk(self):
        """Test _assess_collaboration_risk"""
        # Low risk
        collab_info = CollaborationInfo(
            active_branches=[], recent_commits=[], potential_conflicts=[],
            team_activity_level='low', last_team_push=""
        )
        risk = self.git_manager._assess_collaboration_risk(collab_info)
        self.assertEqual(risk, 'low')
        
        # High risk
        collab_info.team_activity_level = 'high'
        risk = self.git_manager._assess_collaboration_risk(collab_info)
        self.assertEqual(risk, 'high')
        
        # Medium risk
        collab_info.team_activity_level = 'low'
        collab_info.potential_conflicts = ['conflict1']
        risk = self.git_manager._assess_collaboration_risk(collab_info)
        self.assertEqual(risk, 'medium')
    
    def test_check_blocking_issues(self):
        """Test _check_blocking_issues"""
        # No issues
        issues = self.git_manager._check_blocking_issues(0.9)
        self.assertEqual(len(issues), 0)
        
        # Quality issue
        issues = self.git_manager._check_blocking_issues(0.5)
        self.assertEqual(len(issues), 1)
        self.assertIn("Quality score", issues[0])
    
    def test_calculate_optimal_timing(self):
        """Test _calculate_optimal_timing"""
        collab_info = CollaborationInfo(
            active_branches=[], recent_commits=[], potential_conflicts=[],
            team_activity_level='low', last_team_push=""
        )
        
        with patch('tools.git_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value.hour = 14  # 2 PM
            timing = self.git_manager._calculate_optimal_timing(collab_info)
            self.assertIn("optimal", timing)
    
    def test_calculate_push_confidence(self):
        """Test _calculate_push_confidence"""
        confidence = self.git_manager._calculate_push_confidence(0.8, 'low', [])
        self.assertGreater(confidence, 0.8)
        
        confidence = self.git_manager._calculate_push_confidence(0.8, 'high', ['issue1'])
        self.assertLess(confidence, 0.8)
    
    @patch('subprocess.run')
    def test_stage_files_success(self, mock_run):
        """Test stage_files success"""
        mock_run.return_value = Mock(returncode=0)
        
        with patch.object(self.git_manager, 'is_git_repository', return_value=True):
            success, message = self.git_manager.stage_files(["file1.py", "file2.py"])
            
            self.assertTrue(success)
            self.assertIn("Staged 2 files", message)
    
    def test_stage_files_not_repo(self):
        """Test stage_files when not a Git repository"""
        success, message = self.git_manager.stage_files(["file1.py"])
        
        self.assertFalse(success)
        self.assertIn("Not a Git repository", message)
    
    @patch('subprocess.run')
    def test_commit_changes_success(self, mock_run):
        """Test commit_changes success"""
        mock_run.return_value = Mock(returncode=0)
        
        with patch.object(self.git_manager, 'is_git_repository', return_value=True):
            with patch.object(self.git_manager, 'stage_files', return_value=(True, "Staged")):
                success, message = self.git_manager.commit_changes("Test commit", ["file1.py"])
                
                self.assertTrue(success)
                self.assertIn("Committed with message", message)
    
    def test_commit_changes_not_repo(self):
        """Test commit_changes when not a Git repository"""
        success, message = self.git_manager.commit_changes("Test commit")
        
        self.assertFalse(success)
        self.assertIn("Not a Git repository", message)
    
    @patch('subprocess.run')
    def test_push_changes_success(self, mock_run):
        """Test push_changes success"""
        mock_run.return_value = Mock(returncode=0)
        
        with patch.object(self.git_manager, 'is_git_repository', return_value=True):
            success, message = self.git_manager.push_changes()
            
            self.assertTrue(success)
            self.assertIn("pushed successfully", message)
    
    def test_push_changes_not_repo(self):
        """Test push_changes when not a Git repository"""
        success, message = self.git_manager.push_changes()
        
        self.assertFalse(success)
        self.assertIn("Not a Git repository", message)


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('tools.git_manager.GitOperationsManager')
    def test_get_git_status(self, mock_manager_class):
        """Test get_git_status convenience function"""
        mock_manager = Mock()
        mock_status = GitStatus(
            is_repo=True, branch="main", has_changes=False,
            staged_files=[], unstaged_files=[], untracked_files=[],
            commits_ahead=0, commits_behind=0,
            last_commit_hash="", last_commit_message="", last_commit_date="",
            remote_url=""
        )
        mock_manager.get_git_status.return_value = mock_status
        mock_manager_class.return_value = mock_manager
        
        status = get_git_status(str(self.project_root))
        self.assertEqual(status, mock_status)
    
    @patch('tools.git_manager.GitOperationsManager')
    def test_should_commit_now(self, mock_manager_class):
        """Test should_commit_now convenience function"""
        mock_manager = Mock()
        mock_recommendation = CommitRecommendation(
            should_commit=True, confidence=0.8, suggested_message="Test commit",
            reasoning="Test reasoning", files_to_stage=[], commit_type="feat"
        )
        mock_manager.get_commit_recommendation.return_value = mock_recommendation
        mock_manager_class.return_value = mock_manager
        
        should_commit, reasoning = should_commit_now(str(self.project_root), "test context")
        
        self.assertTrue(should_commit)
        self.assertEqual(reasoning, "Test reasoning")
    
    @patch('tools.git_manager.GitOperationsManager')
    def test_should_push_now(self, mock_manager_class):
        """Test should_push_now convenience function"""
        mock_manager = Mock()
        mock_recommendation = PushRecommendation(
            should_push=True, confidence=0.9, reasoning="Test reasoning",
            optimal_timing="optimal", collaboration_risk="low",
            quality_score=0.8, blocking_issues=[]
        )
        mock_manager.get_push_recommendation.return_value = mock_recommendation
        mock_manager_class.return_value = mock_manager
        
        should_push, reasoning = should_push_now(str(self.project_root), 0.8)
        
        self.assertTrue(should_push)
        self.assertEqual(reasoning, "Test reasoning")


class TestDataClasses(unittest.TestCase):
    """Test cases for data classes"""
    
    def test_git_status_creation(self):
        """Test GitStatus creation"""
        status = GitStatus(
            is_repo=True, branch="main", has_changes=True,
            staged_files=["file1.py"], unstaged_files=["file2.py"], untracked_files=["file3.py"],
            commits_ahead=2, commits_behind=1,
            last_commit_hash="abc123", last_commit_message="Test commit", last_commit_date="2023-01-01",
            remote_url="https://github.com/user/repo.git"
        )
        
        self.assertTrue(status.is_repo)
        self.assertEqual(status.branch, "main")
        self.assertTrue(status.has_changes)
        self.assertEqual(len(status.staged_files), 1)
        self.assertEqual(status.commits_ahead, 2)
    
    def test_commit_recommendation_creation(self):
        """Test CommitRecommendation creation"""
        recommendation = CommitRecommendation(
            should_commit=True, confidence=0.8, suggested_message="feat: add new feature",
            reasoning="Clear feature addition", files_to_stage=["feature.py"], commit_type="feat"
        )
        
        self.assertTrue(recommendation.should_commit)
        self.assertEqual(recommendation.confidence, 0.8)
        self.assertEqual(recommendation.commit_type, "feat")
        self.assertIn("feat:", recommendation.suggested_message)
    
    def test_push_recommendation_creation(self):
        """Test PushRecommendation creation"""
        recommendation = PushRecommendation(
            should_push=True, confidence=0.9, reasoning="Good quality, low risk",
            optimal_timing="optimal", collaboration_risk="low",
            quality_score=0.85, blocking_issues=[]
        )
        
        self.assertTrue(recommendation.should_push)
        self.assertEqual(recommendation.confidence, 0.9)
        self.assertEqual(recommendation.collaboration_risk, "low")
        self.assertEqual(len(recommendation.blocking_issues), 0)
    
    def test_collaboration_info_creation(self):
        """Test CollaborationInfo creation"""
        info = CollaborationInfo(
            active_branches=["feature/auth", "bugfix/login"],
            recent_commits=[{"author": "user1", "message": "fix bug"}],
            potential_conflicts=["auth.py"],
            team_activity_level="medium",
            last_team_push="2023-01-01T12:00:00Z"
        )
        
        self.assertEqual(len(info.active_branches), 2)
        self.assertEqual(len(info.recent_commits), 1)
        self.assertEqual(info.team_activity_level, "medium")


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2)
