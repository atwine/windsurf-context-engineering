"""
Learning and Feedback System for Windsurf Context Engineering Framework

This module provides intelligent learning capabilities that enable the framework
to continuously improve based on project outcomes, user feedback, and pattern analysis.

Key Components:
- FeedbackCollector: Collects and processes user feedback
- PatternAnalyzer: Analyzes success/failure patterns
- TemplateEvolution: Evolves templates based on performance
- MetricsTracker: Tracks performance and improvement metrics
- LearningEngine: Orchestrates all learning processes
"""

from .feedback_collector import FeedbackCollector
from .pattern_analyzer import PatternAnalyzer
from .template_evolution import TemplateEvolution
from .metrics_tracker import MetricsTracker
from .learning_engine import LearningEngine

__all__ = [
    'FeedbackCollector',
    'PatternAnalyzer', 
    'TemplateEvolution',
    'MetricsTracker',
    'LearningEngine'
]

__version__ = '1.0.0'
