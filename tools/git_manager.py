#!/usr/bin/env python3
"""
Git Operations Manager
=====================

Intelligent Git operations management for the Windsurf Context Engineering Framework.
Provides smart commit message generation, push recommendations, and collaboration awareness.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import re

try:
    import git
    from git import Repo, InvalidGitRepositoryError
    GIT_PYTHON_AVAILABLE = True
except ImportError:
    GIT_PYTHON_AVAILABLE = False
    git = None
    Repo = None
    InvalidGitRepositoryError = Exception

logger = logging.getLogger(__name__)

@dataclass
class GitStatus:
    """Git repository status information"""
    is_repo: bool
    branch: str
    has_changes: bool
    staged_files: List[str]
    unstaged_files: List[str]
    untracked_files: List[str]
    commits_ahead: int
    commits_behind: int
    last_commit_hash: str
    last_commit_message: str
    last_commit_date: str
    remote_url: str

    # Backward-compatibility properties
    @property
    def is_clean(self) -> bool:
        """Backward-compat: repository considered clean when no changes are detected.
        This maps to the existing `has_changes` flag to avoid touching callers.
        """
        return not self.has_changes

    @property
    def current_branch(self) -> str:
        """Backward-compat: alias for `branch` used by examples and utilities."""
        return self.branch

@dataclass
class CommitRecommendation:
    """Commit recommendation with AI-generated message"""
    should_commit: bool
    confidence: float
    suggested_message: str
    reasoning: str
    files_to_stage: List[str]
    commit_type: str  # 'feature', 'fix', 'docs', 'refactor', 'test', 'chore'

@dataclass
class PushRecommendation:
    """Push recommendation with timing and collaboration analysis"""
    should_push: bool
    confidence: float
    reasoning: str
    optimal_timing: str
    collaboration_risk: str  # 'low', 'medium', 'high'
    quality_score: float
    blocking_issues: List[str]

    # Backward-compatibility alias for older callers expecting `recommended_timing`
    @property
    def recommended_timing(self) -> str:
        return self.optimal_timing

@dataclass
class CollaborationInfo:
    """Information about team collaboration activity"""
    active_branches: List[str]
    recent_commits: List[Dict[str, Any]]
    potential_conflicts: List[str]
    team_activity_level: str  # 'low', 'medium', 'high'
    last_team_push: str

class GitOperationsManager:
    """
    Intelligent Git operations management system
    
    Features:
    - Smart git status analysis
    - AI-powered commit message generation
    - Push timing optimization
    - Collaboration conflict detection
    - Quality gate integration
    """
    
    def __init__(self, project_root: str = ".", enable_ai_features: bool = True):
        """Initialize the Git operations manager"""
        self.project_root = Path(project_root).resolve()
        self.enable_ai_features = enable_ai_features
        self.repo = None
        
        # Initialize repository if it exists
        self._init_repository()
        
        # Configuration
        self.config = {
            'commit_message_max_length': 72,
            'push_quality_threshold': 0.7,
            'collaboration_check_hours': 24,
            'auto_stage_patterns': ['*.py', '*.md', '*.txt', '*.json', '*.yml', '*.yaml'],
            'ignore_patterns': ['__pycache__', '*.pyc', '.DS_Store', 'node_modules', '.venv', 'venv']
        }
        
        logger.debug(f"GitOperationsManager initialized for {self.project_root}")
    
    def _init_repository(self):
        """Initialize Git repository connection"""
        if not GIT_PYTHON_AVAILABLE:
            logger.warning("GitPython not available, using subprocess fallback")
            return
        
        try:
            self.repo = Repo(self.project_root)
            logger.debug("Git repository initialized successfully")
        except InvalidGitRepositoryError:
            logger.debug("Not a Git repository")
            self.repo = None
        except Exception as e:
            logger.error(f"Error initializing Git repository: {e}")
            self.repo = None
    
    def is_git_repository(self) -> bool:
        """Check if the current directory is a Git repository"""
        if self.repo:
            return True
        
        # Fallback check
        git_dir = self.project_root / '.git'
        return git_dir.exists()
    
    def get_git_status(self) -> GitStatus:
        """Get comprehensive Git repository status"""
        if not self.is_git_repository():
            return GitStatus(
                is_repo=False, branch="", has_changes=False,
                staged_files=[], unstaged_files=[], untracked_files=[],
                commits_ahead=0, commits_behind=0,
                last_commit_hash="", last_commit_message="", last_commit_date="",
                remote_url=""
            )
        
        try:
            if self.repo:
                return self._get_status_with_gitpython()
            else:
                return self._get_status_with_subprocess()
        except Exception as e:
            logger.error(f"Error getting Git status: {e}")
            return GitStatus(
                is_repo=True, branch="unknown", has_changes=False,
                staged_files=[], unstaged_files=[], untracked_files=[],
                commits_ahead=0, commits_behind=0,
                last_commit_hash="", last_commit_message="", last_commit_date="",
                remote_url=""
            )
    
    def _get_status_with_gitpython(self) -> GitStatus:
        """Get status using GitPython library"""
        # Current branch
        try:
            branch = self.repo.active_branch.name
        except:
            branch = "HEAD"
        
        # File changes
        staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
        unstaged_files = [item.a_path for item in self.repo.index.diff(None)]
        untracked_files = self.repo.untracked_files
        
        has_changes = len(staged_files) > 0 or len(unstaged_files) > 0 or len(untracked_files) > 0
        
        # Commit information
        try:
            last_commit = self.repo.head.commit
            last_commit_hash = last_commit.hexsha[:8]
            last_commit_message = last_commit.message.strip()
            last_commit_date = datetime.fromtimestamp(last_commit.committed_date).isoformat()
        except:
            last_commit_hash = ""
            last_commit_message = ""
            last_commit_date = ""
        
        # Remote information
        commits_ahead = 0
        commits_behind = 0
        remote_url = ""
        
        try:
            if self.repo.remotes:
                remote = self.repo.remotes.origin
                remote_url = list(remote.urls)[0]
                
                # Get ahead/behind count
                try:
                    remote.fetch()
                    commits_ahead = len(list(self.repo.iter_commits(f'origin/{branch}..{branch}')))
                    commits_behind = len(list(self.repo.iter_commits(f'{branch}..origin/{branch}')))
                except:
                    pass
        except:
            pass
        
        return GitStatus(
            is_repo=True,
            branch=branch,
            has_changes=has_changes,
            staged_files=staged_files,
            unstaged_files=unstaged_files,
            untracked_files=untracked_files,
            commits_ahead=commits_ahead,
            commits_behind=commits_behind,
            last_commit_hash=last_commit_hash,
            last_commit_message=last_commit_message,
            last_commit_date=last_commit_date,
            remote_url=remote_url
        )
    
    def _get_status_with_subprocess(self) -> GitStatus:
        """Get status using subprocess git commands"""
        def run_git_command(cmd: List[str]) -> str:
            try:
                result = subprocess.run(
                    ["git"] + cmd,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.stdout.strip() if result.returncode == 0 else ""
            except:
                return ""
        
        # Current branch
        branch = run_git_command(["branch", "--show-current"]) or "HEAD"
        
        # File status
        status_output = run_git_command(["status", "--porcelain"])
        staged_files = []
        unstaged_files = []
        untracked_files = []
        
        for line in status_output.split('\n'):
            if not line:
                continue
            status_code = line[:2]
            filename = line[3:]
            
            if status_code[0] in ['A', 'M', 'D', 'R', 'C']:
                staged_files.append(filename)
            if status_code[1] in ['M', 'D']:
                unstaged_files.append(filename)
            if status_code == '??':
                untracked_files.append(filename)
        
        has_changes = len(staged_files) > 0 or len(unstaged_files) > 0 or len(untracked_files) > 0
        
        # Last commit info
        last_commit_hash = run_git_command(["rev-parse", "--short", "HEAD"])
        last_commit_message = run_git_command(["log", "-1", "--pretty=format:%s"])
        last_commit_date = run_git_command(["log", "-1", "--pretty=format:%cI"])
        
        # Remote info
        remote_url = run_git_command(["remote", "get-url", "origin"])
        
        # Ahead/behind count
        commits_ahead = 0
        commits_behind = 0
        try:
            ahead_behind = run_git_command(["rev-list", "--left-right", "--count", f"origin/{branch}...{branch}"])
            if ahead_behind:
                behind, ahead = ahead_behind.split('\t')
                commits_ahead = int(ahead)
                commits_behind = int(behind)
        except:
            pass
        
        return GitStatus(
            is_repo=True,
            branch=branch,
            has_changes=has_changes,
            staged_files=staged_files,
            unstaged_files=unstaged_files,
            untracked_files=untracked_files,
            commits_ahead=commits_ahead,
            commits_behind=commits_behind,
            last_commit_hash=last_commit_hash,
            last_commit_message=last_commit_message,
            last_commit_date=last_commit_date,
            remote_url=remote_url
        )
    
    def generate_commit_message(self, files: List[str], context: str = "") -> str:
        """Generate intelligent commit message based on changed files and context"""
        if not files:
            return "chore: update project files"
        
        # Analyze file types and changes
        file_types = self._analyze_file_types(files)
        change_patterns = self._detect_change_patterns(files)
        
        # Determine commit type
        commit_type = self._determine_commit_type(file_types, change_patterns, context)
        
        # Generate message based on patterns
        if self.enable_ai_features:
            message = self._generate_ai_commit_message(commit_type, files, context)
        else:
            message = self._generate_basic_commit_message(commit_type, files)
        
        # Ensure message length compliance
        if len(message) > self.config['commit_message_max_length']:
            message = message[:self.config['commit_message_max_length'] - 3] + "..."
        
        return message
    
    def get_commit_recommendation(self, context: str = "") -> CommitRecommendation:
        """Get intelligent commit recommendation"""
        status = self.get_git_status()
        
        if not status.has_changes:
            return CommitRecommendation(
                should_commit=False,
                confidence=1.0,
                suggested_message="",
                reasoning="No changes to commit",
                files_to_stage=[],
                commit_type="none"
            )
        
        # Analyze changes
        all_files = status.staged_files + status.unstaged_files + status.untracked_files
        files_to_stage = self._select_files_to_stage(all_files)
        
        # Generate commit message
        commit_message = self.generate_commit_message(files_to_stage, context)
        commit_type = self._determine_commit_type(
            self._analyze_file_types(files_to_stage),
            self._detect_change_patterns(files_to_stage),
            context
        )
        
        # Calculate confidence
        confidence = self._calculate_commit_confidence(files_to_stage, context)
        
        # Generate reasoning
        reasoning = self._generate_commit_reasoning(files_to_stage, commit_type, confidence)
        
        return CommitRecommendation(
            should_commit=confidence > 0.5,
            confidence=confidence,
            suggested_message=commit_message,
            reasoning=reasoning,
            files_to_stage=files_to_stage,
            commit_type=commit_type
        )
    
    def get_push_recommendation(self, quality_score: float = 0.8) -> PushRecommendation:
        """Get intelligent push recommendation with timing and collaboration analysis"""
        status = self.get_git_status()
        
        if status.commits_ahead == 0:
            return PushRecommendation(
                should_push=False,
                confidence=1.0,
                reasoning="No commits to push",
                optimal_timing="N/A",
                collaboration_risk="low",
                quality_score=quality_score,
                blocking_issues=[]
            )
        
        # Analyze collaboration risk
        collaboration_info = self._analyze_collaboration()
        collaboration_risk = self._assess_collaboration_risk(collaboration_info)
        
        # Check for blocking issues
        blocking_issues = self._check_blocking_issues(quality_score)
        
        # Calculate optimal timing
        optimal_timing = self._calculate_optimal_timing(collaboration_info)
        
        # Generate recommendation
        should_push = (
            len(blocking_issues) == 0 and
            quality_score >= self.config['push_quality_threshold'] and
            collaboration_risk != 'high'
        )
        
        confidence = self._calculate_push_confidence(
            quality_score, collaboration_risk, blocking_issues
        )
        
        reasoning = self._generate_push_reasoning(
            should_push, quality_score, collaboration_risk, blocking_issues
        )
        
        return PushRecommendation(
            should_push=should_push,
            confidence=confidence,
            reasoning=reasoning,
            optimal_timing=optimal_timing,
            collaboration_risk=collaboration_risk,
            quality_score=quality_score,
            blocking_issues=blocking_issues
        )
    
    def stage_files(self, files: List[str]) -> Tuple[bool, str]:
        """Stage files for commit"""
        if not self.is_git_repository():
            return False, "Not a Git repository"
        
        try:
            if self.repo:
                self.repo.index.add(files)
            else:
                subprocess.run(
                    ["git", "add"] + files,
                    cwd=self.project_root,
                    check=True,
                    timeout=30
                )
            
            return True, f"Staged {len(files)} files"
        except Exception as e:
            return False, f"Failed to stage files: {e}"
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> Tuple[bool, str]:
        """Commit changes with the given message"""
        if not self.is_git_repository():
            return False, "Not a Git repository"
        
        try:
            # Stage files if provided
            if files:
                success, stage_msg = self.stage_files(files)
                if not success:
                    return False, f"Failed to stage files: {stage_msg}"
            
            # Commit
            if self.repo:
                self.repo.index.commit(message)
            else:
                subprocess.run(
                    ["git", "commit", "-m", message],
                    cwd=self.project_root,
                    check=True,
                    timeout=30
                )
            
            return True, f"Committed with message: {message}"
        except Exception as e:
            return False, f"Failed to commit: {e}"
    
    def push_changes(self, branch: Optional[str] = None) -> Tuple[bool, str]:
        """Push changes to remote repository"""
        if not self.is_git_repository():
            return False, "Not a Git repository"
        
        try:
            if self.repo and self.repo.remotes:
                origin = self.repo.remotes.origin
                origin.push(branch or self.repo.active_branch.name)
            else:
                cmd = ["git", "push"]
                if branch:
                    cmd.extend(["origin", branch])
                
                subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    check=True,
                    timeout=120
                )
            
            return True, "Changes pushed successfully"
        except Exception as e:
            return False, f"Failed to push: {e}"
    
    # Private helper methods
    
    def _analyze_file_types(self, files: List[str]) -> Dict[str, int]:
        """Analyze file types in the change set"""
        file_types = {}
        for file in files:
            ext = Path(file).suffix.lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
            else:
                file_types['no_ext'] = file_types.get('no_ext', 0) + 1
        return file_types
    
    def _detect_change_patterns(self, files: List[str]) -> List[str]:
        """Detect patterns in changed files"""
        patterns = []
        
        # Check for common patterns
        if any('test' in f.lower() for f in files):
            patterns.append('tests')
        if any(f.endswith('.md') for f in files):
            patterns.append('documentation')
        if any(f in ['requirements.txt', 'setup.py', 'pyproject.toml'] for f in files):
            patterns.append('dependencies')
        if any(f.startswith('.') for f in files):
            patterns.append('config')
        
        return patterns
    
    def _determine_commit_type(self, file_types: Dict[str, int], patterns: List[str], context: str) -> str:
        """Determine the type of commit based on analysis"""
        context_lower = context.lower()
        
        # Context-based detection
        if any(word in context_lower for word in ['fix', 'bug', 'error', 'issue']):
            return 'fix'
        if any(word in context_lower for word in ['feature', 'add', 'new', 'implement']):
            return 'feat'
        if 'documentation' in patterns or any(word in context_lower for word in ['doc', 'readme']):
            return 'docs'
        if 'tests' in patterns or any(word in context_lower for word in ['test', 'testing']):
            return 'test'
        if 'dependencies' in patterns:
            return 'chore'
        if any(word in context_lower for word in ['refactor', 'cleanup', 'improve']):
            return 'refactor'
        
        # File-based detection
        if '.py' in file_types and len(file_types) == 1:
            return 'feat'  # Assume new feature for Python files
        if 'config' in patterns:
            return 'chore'
        
        return 'chore'  # Default
    
    def _generate_ai_commit_message(self, commit_type: str, files: List[str], context: str) -> str:
        """Generate AI-powered commit message (placeholder for future AI integration)"""
        # This is a placeholder for future AI integration
        # For now, use rule-based generation
        return self._generate_basic_commit_message(commit_type, files)
    
    def _generate_basic_commit_message(self, commit_type: str, files: List[str]) -> str:
        """Generate basic commit message using rules"""
        file_summary = self._summarize_files(files)
        
        templates = {
            'feat': f"feat: add {file_summary}",
            'fix': f"fix: resolve issues in {file_summary}",
            'docs': f"docs: update {file_summary}",
            'test': f"test: add tests for {file_summary}",
            'refactor': f"refactor: improve {file_summary}",
            'chore': f"chore: update {file_summary}"
        }
        
        return templates.get(commit_type, f"update {file_summary}")
    
    def _summarize_files(self, files: List[str]) -> str:
        """Create a summary of changed files"""
        if len(files) == 1:
            return Path(files[0]).name
        elif len(files) <= 3:
            return ", ".join(Path(f).name for f in files)
        else:
            return f"{len(files)} files"
    
    def _select_files_to_stage(self, files: List[str]) -> List[str]:
        """Select which files should be staged for commit"""
        # Filter out ignored patterns
        filtered_files = []
        for file in files:
            should_ignore = False
            for pattern in self.config['ignore_patterns']:
                if pattern in file:
                    should_ignore = True
                    break
            if not should_ignore:
                filtered_files.append(file)
        
        return filtered_files
    
    def _calculate_commit_confidence(self, files: List[str], context: str) -> float:
        """Calculate confidence score for commit recommendation"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for clear patterns
        if len(files) > 0:
            confidence += 0.2
        if context:
            confidence += 0.2
        if any(f.endswith('.py') for f in files):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_commit_reasoning(self, files: List[str], commit_type: str, confidence: float) -> str:
        """Generate reasoning for commit recommendation"""
        reasons = []
        
        if len(files) > 0:
            reasons.append(f"Found {len(files)} files with changes")
        if commit_type != 'chore':
            reasons.append(f"Detected {commit_type} type changes")
        if confidence > 0.7:
            reasons.append("High confidence in change analysis")
        
        return "; ".join(reasons) if reasons else "Basic file changes detected"
    
    def _analyze_collaboration(self) -> CollaborationInfo:
        """Analyze team collaboration activity"""
        # Placeholder for collaboration analysis
        # In a real implementation, this would check:
        # - Recent commits from other team members
        # - Active branches
        # - Potential merge conflicts
        
        return CollaborationInfo(
            active_branches=[],
            recent_commits=[],
            potential_conflicts=[],
            team_activity_level='low',
            last_team_push=""
        )
    
    def _assess_collaboration_risk(self, collaboration_info: CollaborationInfo) -> str:
        """Assess risk of collaboration conflicts"""
        # Simple risk assessment based on activity
        if collaboration_info.team_activity_level == 'high':
            return 'high'
        elif len(collaboration_info.potential_conflicts) > 0:
            return 'medium'
        else:
            return 'low'
    
    def _check_blocking_issues(self, quality_score: float) -> List[str]:
        """Check for issues that should block pushing"""
        issues = []
        
        if quality_score < self.config['push_quality_threshold']:
            issues.append(f"Quality score ({quality_score:.2f}) below threshold ({self.config['push_quality_threshold']})")
        
        # Check for common blocking issues
        # This could be extended to check:
        # - Failing tests
        # - Lint errors
        # - Security vulnerabilities
        
        return issues
    
    def _calculate_optimal_timing(self, collaboration_info: CollaborationInfo) -> str:
        """Calculate optimal timing for push"""
        current_hour = datetime.now().hour
        
        # Business hours are generally better for collaboration
        if 9 <= current_hour <= 17:
            return "optimal (business hours)"
        elif 17 < current_hour <= 20:
            return "good (evening)"
        else:
            return "acceptable (off-hours)"
    
    def _calculate_push_confidence(self, quality_score: float, collaboration_risk: str, blocking_issues: List[str]) -> float:
        """Calculate confidence for push recommendation"""
        confidence = quality_score
        
        # Adjust for collaboration risk
        if collaboration_risk == 'low':
            confidence += 0.1
        elif collaboration_risk == 'high':
            confidence -= 0.2
        
        # Adjust for blocking issues
        confidence -= len(blocking_issues) * 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_push_reasoning(self, should_push: bool, quality_score: float, collaboration_risk: str, blocking_issues: List[str]) -> str:
        """Generate reasoning for push recommendation"""
        reasons = []
        
        if should_push:
            reasons.append(f"Quality score ({quality_score:.2f}) meets threshold")
            reasons.append(f"Collaboration risk is {collaboration_risk}")
            if not blocking_issues:
                reasons.append("No blocking issues detected")
        else:
            if blocking_issues:
                reasons.append(f"Blocking issues: {', '.join(blocking_issues)}")
            if collaboration_risk == 'high':
                reasons.append("High collaboration risk detected")
        
        return "; ".join(reasons) if reasons else "Standard push analysis"


# Convenience functions

def get_git_status(project_root: str = ".") -> GitStatus:
    """Get Git status for a project"""
    manager = GitOperationsManager(project_root)
    return manager.get_git_status()

def should_commit_now(project_root: str = ".", context: str = "") -> Tuple[bool, str]:
    """Check if it's a good time to commit"""
    manager = GitOperationsManager(project_root)
    recommendation = manager.get_commit_recommendation(context)
    return recommendation.should_commit, recommendation.reasoning

def should_push_now(project_root: str = ".", quality_score: float = 0.8) -> Tuple[bool, str]:
    """Check if it's a good time to push"""
    manager = GitOperationsManager(project_root)
    recommendation = manager.get_push_recommendation(quality_score)
    return recommendation.should_push, recommendation.reasoning


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Operations Manager")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--status", action="store_true", help="Show git status")
    parser.add_argument("--commit-check", action="store_true", help="Check commit recommendation")
    parser.add_argument("--push-check", action="store_true", help="Check push recommendation")
    parser.add_argument("--context", default="", help="Context for recommendations")
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    manager = GitOperationsManager(args.project_root)
    
    if args.status:
        status = manager.get_git_status()
        print(f"Repository: {status.is_repo}")
        print(f"Branch: {status.branch}")
        print(f"Changes: {status.has_changes}")
        print(f"Staged: {len(status.staged_files)}")
        print(f"Unstaged: {len(status.unstaged_files)}")
        print(f"Untracked: {len(status.untracked_files)}")
        print(f"Ahead: {status.commits_ahead}")
        print(f"Behind: {status.commits_behind}")
    
    if args.commit_check:
        recommendation = manager.get_commit_recommendation(args.context)
        print(f"Should commit: {recommendation.should_commit}")
        print(f"Confidence: {recommendation.confidence:.2f}")
        print(f"Message: {recommendation.suggested_message}")
        print(f"Reasoning: {recommendation.reasoning}")
    
    if args.push_check:
        recommendation = manager.get_push_recommendation()
        print(f"Should push: {recommendation.should_push}")
        print(f"Confidence: {recommendation.confidence:.2f}")
        print(f"Timing: {recommendation.optimal_timing}")
        print(f"Risk: {recommendation.collaboration_risk}")
        print(f"Reasoning: {recommendation.reasoning}")
