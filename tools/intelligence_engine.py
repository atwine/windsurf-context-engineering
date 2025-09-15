#!/usr/bin/env python3
"""
Intelligence Engine for Windsurf Context Engineering Framework

This module provides advanced AI-powered recommendations, learning integration,
and intelligent decision-making capabilities for workflow optimization.

Phase 3: Intelligence Layer
- Advanced AI-powered recommendations
- Learning system integration
- Predictive analytics
- Workflow optimization
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
from collections import defaultdict, deque

from .command_executor import PythonCommandExecutor, CommandResult
from .git_manager import GitOperationsManager
from .venv_manager import VirtualEnvironmentManager

logger = logging.getLogger(__name__)

@dataclass
class IntelligenceContext:
    """Context information for intelligence decisions."""
    project_path: str
    project_type: str
    git_status: Dict[str, Any]
    environment_status: Dict[str, Any]
    recent_commands: List[Dict[str, Any]]
    workflow_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    timestamp: float

@dataclass
class Recommendation:
    """AI-powered recommendation with confidence scoring."""
    type: str  # 'commit', 'push', 'environment', 'workflow', 'optimization'
    action: str
    description: str
    confidence: float  # 0.0 to 1.0
    priority: str  # 'low', 'medium', 'high', 'critical'
    reasoning: str
    estimated_impact: str
    prerequisites: List[str]
    timestamp: float

@dataclass
class LearningPattern:
    """Learned pattern from workflow execution."""
    pattern_id: str
    pattern_type: str
    context: Dict[str, Any]
    frequency: int
    success_rate: float
    average_duration: float
    common_errors: List[str]
    optimization_suggestions: List[str]
    last_seen: float

class IntelligenceEngine:
    """
    Advanced AI-powered intelligence engine for workflow optimization.
    
    Provides:
    - Smart commit and push recommendations
    - Workflow optimization suggestions
    - Learning-based pattern recognition
    - Predictive analytics for development workflows
    - Performance optimization recommendations
    """
    
    def __init__(self, project_path: str = "."):
        """Initialize the intelligence engine."""
        self.project_path = Path(project_path).resolve()
        self.command_executor = PythonCommandExecutor(str(self.project_path))
        self.git_manager = GitOperationsManager(str(self.project_path))
        self.venv_manager = VirtualEnvironmentManager(str(self.project_path))
        
        # Intelligence data storage
        self.learning_data_path = self.project_path / ".windsurf" / "intelligence"
        self.learning_data_path.mkdir(parents=True, exist_ok=True)
        
        # In-memory caches
        self.patterns_cache: Dict[str, LearningPattern] = {}
        self.context_history: deque = deque(maxlen=100)
        self.recommendation_history: deque = deque(maxlen=50)
        
        # Performance tracking
        self.performance_metrics = {
            'command_success_rate': 0.0,
            'average_command_duration': 0.0,
            'git_operation_success_rate': 0.0,
            'environment_health_score': 0.0,
            'workflow_efficiency_score': 0.0
        }
        
        # Load existing learning data
        self._load_learning_data()
        
        logger.info(f"Intelligence engine initialized for project: {self.project_path}")
    
    def analyze_context(self) -> IntelligenceContext:
        """Analyze current project context for intelligent decision-making."""
        try:
            # Get execution summary
            exec_summary = self.command_executor.get_execution_summary()
            
            # Get Git status
            git_status = {}
            try:
                git_status = {
                    'is_git_repo': exec_summary.get('git_repository', False),
                    'has_changes': False,
                    'ahead_commits': 0,
                    'behind_commits': 0,
                    'branch': 'unknown'
                }
                
                if exec_summary.get('git_repository', False):
                    git_recommendations = self.command_executor.get_git_recommendations()
                    if git_recommendations:
                        git_status.update({
                            'has_changes': len(git_recommendations) > 0,
                            'recommendations': git_recommendations
                        })
            except Exception as e:
                logger.warning(f"Error getting Git status: {e}")
            
            # Get environment status
            env_status = {
                'python_project': exec_summary.get('python_project', False),
                'has_venv': exec_summary.get('virtual_environment', {}).get('exists', False),  # get_execution_summary() exposes 'exists' (not 'active')
                'venv_path': exec_summary.get('virtual_environment', {}).get('path', ''),
                'requirements_present': (self.project_path / 'requirements.txt').exists(),
                'setup_py_present': (self.project_path / 'setup.py').exists()
            }
            
            # Get recent command history
            recent_commands = self._get_recent_commands()
            
            # Get workflow history
            workflow_history = self._get_workflow_history()
            
            # Create context
            context = IntelligenceContext(
                project_path=str(self.project_path),
                project_type=self._determine_project_type(),
                git_status=git_status,
                environment_status=env_status,
                recent_commands=recent_commands,
                workflow_history=workflow_history,
                performance_metrics=self.performance_metrics.copy(),
                timestamp=time.time()
            )
            
            # Cache context for learning
            self.context_history.append(asdict(context))
            
            return context
            
        except Exception as e:
            logger.error(f"Error analyzing context: {e}")
            # Return minimal context
            return IntelligenceContext(
                project_path=str(self.project_path),
                project_type="unknown",
                git_status={},
                environment_status={},
                recent_commands=[],
                workflow_history=[],
                performance_metrics={},
                timestamp=time.time()
            )
    
    def generate_recommendations(self, context: Optional[IntelligenceContext] = None) -> List[Recommendation]:
        """Generate AI-powered recommendations based on current context."""
        if context is None:
            context = self.analyze_context()
        
        recommendations = []
        
        try:
            # Git-related recommendations
            git_recs = self._generate_git_recommendations(context)
            recommendations.extend(git_recs)
            
            # Environment recommendations
            env_recs = self._generate_environment_recommendations(context)
            recommendations.extend(env_recs)
            
            # Workflow optimization recommendations
            workflow_recs = self._generate_workflow_recommendations(context)
            recommendations.extend(workflow_recs)
            
            # Performance optimization recommendations
            perf_recs = self._generate_performance_recommendations(context)
            recommendations.extend(perf_recs)
            
            # Sort by priority and confidence
            recommendations.sort(key=lambda r: (
                {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[r.priority],
                r.confidence
            ), reverse=True)
            
            # Cache recommendations for learning
            for rec in recommendations:
                self.recommendation_history.append(asdict(rec))
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def get_recommendations(self, context: Optional[IntelligenceContext] = None) -> List[Recommendation]:
        """Alias for generate_recommendations for backward compatibility."""
        return self.generate_recommendations(context)
    
    def _generate_git_recommendations(self, context: IntelligenceContext) -> List[Recommendation]:
        """Generate Git-related recommendations."""
        recommendations = []
        
        if not context.git_status.get('is_git_repo', False):
            return recommendations
        
        try:
            # Smart commit recommendations
            if context.git_status.get('has_changes', False):
                # Analyze commit patterns
                commit_confidence = self._calculate_commit_confidence(context)
                
                if commit_confidence > 0.7:
                    recommendations.append(Recommendation(
                        type='commit',
                        action='git_commit',
                        description='Smart commit recommended based on change analysis',
                        confidence=commit_confidence,
                        priority='high' if commit_confidence > 0.9 else 'medium',
                        reasoning=f'Changes detected with {commit_confidence:.1%} confidence for commit readiness',
                        estimated_impact='Improved version control and collaboration',
                        prerequisites=['Ensure tests pass', 'Review changes'],
                        timestamp=time.time()
                    ))
            
            # Smart push recommendations
            push_confidence = self._calculate_push_confidence(context)
            if push_confidence > 0.6:
                recommendations.append(Recommendation(
                    type='push',
                    action='git_push',
                    description='Intelligent push timing recommendation',
                    confidence=push_confidence,
                    priority='medium' if push_confidence > 0.8 else 'low',
                    reasoning=f'Optimal push timing detected with {push_confidence:.1%} confidence',
                    estimated_impact='Enhanced team collaboration and code sharing',
                    prerequisites=['Commit changes', 'Run tests'],
                    timestamp=time.time()
                ))
            
        except Exception as e:
            logger.warning(f"Error generating Git recommendations: {e}")
        
        return recommendations
    
    def _generate_environment_recommendations(self, context: IntelligenceContext) -> List[Recommendation]:
        """Generate environment-related recommendations."""
        recommendations = []
        
        try:
            # Virtual environment recommendations
            if context.environment_status.get('python_project', False):
                if not context.environment_status.get('has_venv', False):
                    recommendations.append(Recommendation(
                        type='environment',
                        action='create_venv',
                        description='Create virtual environment for Python project',
                        confidence=0.95,
                        priority='high',
                        reasoning='Python project detected without virtual environment',
                        estimated_impact='Improved dependency isolation and project stability',
                        prerequisites=['Python installed'],
                        timestamp=time.time()
                    ))
                
                # Requirements file recommendations
                if not context.environment_status.get('requirements_present', False):
                    recommendations.append(Recommendation(
                        type='environment',
                        action='create_requirements',
                        description='Generate requirements.txt for dependency management',
                        confidence=0.8,
                        priority='medium',
                        reasoning='Python project without requirements.txt detected',
                        estimated_impact='Better dependency management and reproducibility',
                        prerequisites=['Virtual environment active'],
                        timestamp=time.time()
                    ))
            
        except Exception as e:
            logger.warning(f"Error generating environment recommendations: {e}")
        
        return recommendations
    
    def _generate_workflow_recommendations(self, context: IntelligenceContext) -> List[Recommendation]:
        """Generate workflow optimization recommendations."""
        recommendations = []
        
        try:
            # Analyze workflow patterns
            workflow_efficiency = self._calculate_workflow_efficiency(context)
            
            if workflow_efficiency < 0.7:
                recommendations.append(Recommendation(
                    type='workflow',
                    action='optimize_workflow',
                    description='Workflow optimization opportunities detected',
                    confidence=0.75,
                    priority='medium',
                    reasoning=f'Current workflow efficiency: {workflow_efficiency:.1%}',
                    estimated_impact='Improved development velocity and reduced errors',
                    prerequisites=['Review current workflow patterns'],
                    timestamp=time.time()
                ))
            
            # Command sequence optimization
            if len(context.recent_commands) > 5:
                optimization_potential = self._analyze_command_patterns(context.recent_commands)
                if optimization_potential > 0.6:
                    recommendations.append(Recommendation(
                        type='workflow',
                        action='optimize_commands',
                        description='Command sequence optimization available',
                        confidence=optimization_potential,
                        priority='low',
                        reasoning='Repetitive command patterns detected',
                        estimated_impact='Reduced manual work and faster execution',
                        prerequisites=['Review command history'],
                        timestamp=time.time()
                    ))
            
        except Exception as e:
            logger.warning(f"Error generating workflow recommendations: {e}")
        
        return recommendations
    
    def _generate_performance_recommendations(self, context: IntelligenceContext) -> List[Recommendation]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        try:
            # Analyze performance metrics
            avg_duration = context.performance_metrics.get('average_command_duration', 0)
            success_rate = context.performance_metrics.get('command_success_rate', 1.0)
            
            if avg_duration > 10.0:  # Commands taking more than 10 seconds
                recommendations.append(Recommendation(
                    type='optimization',
                    action='optimize_performance',
                    description='Performance optimization opportunities detected',
                    confidence=0.7,
                    priority='low',
                    reasoning=f'Average command duration: {avg_duration:.1f}s',
                    estimated_impact='Faster development cycles',
                    prerequisites=['Profile slow commands'],
                    timestamp=time.time()
                ))
            
            if success_rate < 0.9:
                recommendations.append(Recommendation(
                    type='optimization',
                    action='improve_reliability',
                    description='Command reliability improvement needed',
                    confidence=0.8,
                    priority='medium',
                    reasoning=f'Command success rate: {success_rate:.1%}',
                    estimated_impact='Reduced errors and improved stability',
                    prerequisites=['Analyze failed commands'],
                    timestamp=time.time()
                ))
            
        except Exception as e:
            logger.warning(f"Error generating performance recommendations: {e}")
        
        return recommendations
    
    def learn_from_execution(self, command: str, result: CommandResult, context: IntelligenceContext):
        """Learn from command execution to improve future recommendations."""
        try:
            # Update performance metrics
            self._update_performance_metrics(command, result)
            
            # Extract and store patterns
            pattern = self._extract_execution_pattern(command, result, context)
            if pattern:
                self._store_learning_pattern(pattern)
            
            # Update recommendation effectiveness
            self._update_recommendation_effectiveness(command, result)
            
            logger.debug(f"Learned from execution: {command[:50]}...")
            
        except Exception as e:
            logger.error(f"Error learning from execution: {e}")
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get comprehensive intelligence summary."""
        try:
            context = self.analyze_context()
            recommendations = self.generate_recommendations(context)
            
            return {
                'context': asdict(context),
                'recommendations': [asdict(r) for r in recommendations],
                'performance_metrics': self.performance_metrics.copy(),
                'learning_patterns': len(self.patterns_cache),
                'context_history_size': len(self.context_history),
                'recommendation_history_size': len(self.recommendation_history),
                'intelligence_health': self._calculate_intelligence_health(),
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error generating intelligence summary: {e}")
            return {
                'error': str(e),
                'timestamp': time.time()
            }
    
    # Helper methods
    
    def _determine_project_type(self) -> str:
        """Determine the type of project."""
        if (self.project_path / 'requirements.txt').exists() or (self.project_path / 'setup.py').exists():
            return 'python'
        elif (self.project_path / 'package.json').exists():
            return 'javascript'
        elif (self.project_path / 'Cargo.toml').exists():
            return 'rust'
        elif (self.project_path / 'go.mod').exists():
            return 'go'
        else:
            return 'generic'
    
    def _get_recent_commands(self) -> List[Dict[str, Any]]:
        """Get recent command history."""
        # This would typically read from a command history file
        # For now, return empty list
        return []
    
    def _get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get workflow execution history."""
        # This would typically read from workflow execution logs
        # For now, return empty list
        return []
    
    def _calculate_commit_confidence(self, context: IntelligenceContext) -> float:
        """Calculate confidence score for commit recommendation."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on factors
        if context.git_status.get('has_changes', False):
            confidence += 0.3
        
        # Decrease confidence if there are recent commits
        if len(context.recent_commands) > 0:
            recent_commits = [cmd for cmd in context.recent_commands 
                            if cmd.get('command', '').startswith('git commit')]
            if recent_commits and time.time() - recent_commits[-1].get('timestamp', 0) < 3600:
                confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_push_confidence(self, context: IntelligenceContext) -> float:
        """Calculate confidence score for push recommendation."""
        confidence = 0.4  # Base confidence
        
        # Increase confidence based on factors
        if context.git_status.get('ahead_commits', 0) > 0:
            confidence += 0.4
        
        # Consider time since last push
        confidence += 0.2  # Assume some time has passed
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_workflow_efficiency(self, context: IntelligenceContext) -> float:
        """Calculate workflow efficiency score."""
        # Simple calculation based on success rate and performance
        success_rate = context.performance_metrics.get('command_success_rate', 1.0)
        return success_rate  # Simplified for now
    
    def _analyze_command_patterns(self, commands: List[Dict[str, Any]]) -> float:
        """Analyze command patterns for optimization potential."""
        if len(commands) < 3:
            return 0.0
        
        # Simple pattern detection - look for repeated commands
        command_counts = defaultdict(int)
        for cmd in commands:
            command_counts[cmd.get('command', '')] += 1
        
        # Calculate repetition ratio
        total_commands = len(commands)
        repeated_commands = sum(count for count in command_counts.values() if count > 1)
        
        return repeated_commands / total_commands if total_commands > 0 else 0.0
    
    def _update_performance_metrics(self, command: str, result: CommandResult):
        """Update performance metrics based on execution results."""
        try:
            # Update success rate
            current_success = self.performance_metrics.get('command_success_rate', 1.0)
            self.performance_metrics['command_success_rate'] = (current_success * 0.9) + (0.1 if result.success else 0.0)
            
            # Update average duration
            if result.execution_time > 0:
                current_avg = self.performance_metrics.get('average_command_duration', 0.0)
                self.performance_metrics['average_command_duration'] = (current_avg * 0.9) + (result.execution_time * 0.1)
            
        except Exception as e:
            logger.warning(f"Error updating performance metrics: {e}")
    
    def _extract_execution_pattern(self, command: str, result: CommandResult, context: IntelligenceContext) -> Optional[LearningPattern]:
        """Extract learning pattern from execution."""
        try:
            pattern_id = f"{command[:20]}_{context.project_type}"
            
            return LearningPattern(
                pattern_id=pattern_id,
                pattern_type='command_execution',
                context={
                    'command': command,
                    'project_type': context.project_type,
                    'success': result.success,
                    'duration': result.execution_time
                },
                frequency=1,
                success_rate=1.0 if result.success else 0.0,
                average_duration=result.execution_time,
                common_errors=[result.stderr] if result.stderr else [],  # Use stderr from CommandResult; fix attribute mismatch
                optimization_suggestions=[],
                last_seen=time.time()
            )
            
        except Exception as e:
            logger.warning(f"Error extracting execution pattern: {e}")
            return None
    
    def _store_learning_pattern(self, pattern: LearningPattern):
        """Store learning pattern for future use."""
        try:
            # Update existing pattern or store new one
            if pattern.pattern_id in self.patterns_cache:
                existing = self.patterns_cache[pattern.pattern_id]
                existing.frequency += 1
                existing.success_rate = (existing.success_rate + pattern.success_rate) / 2
                existing.average_duration = (existing.average_duration + pattern.average_duration) / 2
                existing.last_seen = pattern.last_seen
            else:
                self.patterns_cache[pattern.pattern_id] = pattern
            
            # Persist to disk periodically
            if len(self.patterns_cache) % 10 == 0:
                self._save_learning_data()
                
        except Exception as e:
            logger.warning(f"Error storing learning pattern: {e}")
    
    def _update_recommendation_effectiveness(self, command: str, result: CommandResult):
        """Update effectiveness of recommendations based on outcomes."""
        # This would track which recommendations led to successful outcomes
        # For now, just log the information
        logger.debug(f"Tracking recommendation effectiveness for: {command}")
    
    def _calculate_intelligence_health(self) -> float:
        """Calculate overall health score of the intelligence system."""
        try:
            # Combine various health indicators
            metrics_health = sum(self.performance_metrics.values()) / len(self.performance_metrics) if self.performance_metrics else 0.5
            data_health = min(1.0, len(self.patterns_cache) / 10)  # Normalize to 0-1
            context_health = min(1.0, len(self.context_history) / 50)  # Normalize to 0-1
            
            return (metrics_health + data_health + context_health) / 3
            
        except Exception as e:
            logger.warning(f"Error calculating intelligence health: {e}")
            return 0.5
    
    def _load_learning_data(self):
        """Load learning data from disk."""
        try:
            patterns_file = self.learning_data_path / "patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                    for pattern_data in data:
                        pattern = LearningPattern(**pattern_data)
                        self.patterns_cache[pattern.pattern_id] = pattern
                
                logger.info(f"Loaded {len(self.patterns_cache)} learning patterns")
            
        except Exception as e:
            logger.warning(f"Error loading learning data: {e}")
    
    def _save_learning_data(self):
        """Save learning data to disk."""
        try:
            patterns_file = self.learning_data_path / "patterns.json"
            patterns_data = [asdict(pattern) for pattern in self.patterns_cache.values()]
            
            with open(patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)
            
            logger.debug(f"Saved {len(patterns_data)} learning patterns")
            
        except Exception as e:
            logger.warning(f"Error saving learning data: {e}")


# Convenience functions for easy integration

def get_intelligence_recommendations(project_path: str = ".") -> List[Dict[str, Any]]:
    """Get AI-powered recommendations for the project."""
    try:
        engine = IntelligenceEngine(project_path)
        recommendations = engine.generate_recommendations()
        return [asdict(rec) for rec in recommendations]
    except Exception as e:
        logger.error(f"Error getting intelligence recommendations: {e}")
        return []

def analyze_project_intelligence(project_path: str = ".") -> Dict[str, Any]:
    """Analyze project with full intelligence capabilities."""
    try:
        engine = IntelligenceEngine(project_path)
        return engine.get_intelligence_summary()
    except Exception as e:
        logger.error(f"Error analyzing project intelligence: {e}")
        return {'error': str(e)}

def learn_from_command(command: str, success: bool, duration: float, project_path: str = "."):
    """Learn from command execution for future optimization."""
    try:
        engine = IntelligenceEngine(project_path)
        context = engine.analyze_context()
        
        # Create mock result for learning
        from .command_executor import CommandResult
        result = CommandResult(
            success=success,
            returncode=0 if success else 1,  # Match CommandResult field name (tools/command_executor.CommandResult)
            stdout="",
            stderr="",
            command=command,
            execution_time=duration,
            venv_used=False,  # Use boolean venv_used per CommandResult; not used in this learning path
            git_changes_detected=False
        )
        
        engine.learn_from_execution(command, result, context)
        
    except Exception as e:
        logger.error(f"Error learning from command: {e}")
