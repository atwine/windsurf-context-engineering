#!/usr/bin/env python3
"""
Tools module for Windsurf Context Engineering Framework

This module provides comprehensive tools for development workflow automation,
including virtual environment management, Git operations, command execution,
and intelligent recommendations.

Phase 2: Integration Layer
- Automatic virtual environment management
- Intelligent Git operations
- Enhanced command execution

Phase 3: Intelligence Layer  
- AI-powered recommendations
- Learning system integration
- Predictive analytics
"""

# Legacy components (Phase 1)
from .linting_integration import LintingIntegration
from .testing_integration import TestingIntegration
from .cicd_integration import CICDIntegration
from .dev_environment import DevEnvironmentSetup

# Phase 2 Integration Components
from .command_executor import (
    PythonCommandExecutor,
    CommandResult,
    ExecutionContext,
    execute_with_venv,
    run_python_with_venv,
    get_project_recommendations
)

from .venv_manager import (
    VirtualEnvironmentManager,
    VenvInfo,
    ensure_python_venv,
    get_venv_python_command,
    wrap_python_command
)

from .git_manager import (
    GitOperationsManager,
    CommitRecommendation,
    get_git_status,
    should_commit_now,
    should_push_now
)

# Phase 3 Intelligence Layer Components
from .intelligence_engine import (
    IntelligenceEngine,
    IntelligenceContext,
    Recommendation,
    LearningPattern,
    get_intelligence_recommendations,
    analyze_project_intelligence,
    learn_from_command
)

from .learning_integration import (
    LearningSystemIntegration,
    get_learning_enhanced_recommendations,
    sync_intelligence_with_learning,
    learn_from_workflow,
    get_integration_status
)

from .predictive_analytics import (
    PredictiveAnalytics,
    PredictionResult,
    PerformanceMetrics,
    TrendAnalysis,
    get_performance_prediction,
    get_issue_prediction,
    get_comprehensive_analytics,
    record_performance_metrics
)

__all__ = [
    # Legacy Components
    'LintingIntegration',
    'TestingIntegration',
    'CICDIntegration',
    'DevEnvironmentSetup',
    
    # Phase 2 Components
    'PythonCommandExecutor',
    'CommandResult', 
    'ExecutionContext',
    'VirtualEnvironmentManager',
    'VenvInfo',
    'GitOperationsManager',
    'CommitRecommendation',
    
    # Phase 2 Convenience Functions
    'execute_with_venv',
    'run_python_with_venv',
    'get_project_recommendations',
    'ensure_python_venv',
    'get_venv_python_command',
    'wrap_python_command',
    'get_git_status',
    'should_commit_now',
    'should_push_now',
    
    # Phase 3 Intelligence Components
    'IntelligenceEngine',
    'IntelligenceContext',
    'Recommendation',
    'LearningPattern',
    'LearningSystemIntegration',
    'PredictiveAnalytics',
    'PredictionResult',
    'PerformanceMetrics',
    'TrendAnalysis',
    
    # Phase 3 Convenience Functions
    'get_intelligence_recommendations',
    'analyze_project_intelligence',
    'learn_from_command',
    'get_learning_enhanced_recommendations',
    'sync_intelligence_with_learning',
    'learn_from_workflow',
    'get_integration_status',
    'get_performance_prediction',
    'get_issue_prediction',
    'get_comprehensive_analytics',
    'record_performance_metrics'
]
