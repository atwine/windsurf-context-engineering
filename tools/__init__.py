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

# Phase 2 Convenience Functions
def get_linting_integration(project_path='.'):
    """Get linting integration instance."""
    return LintingIntegration(project_path)

def get_venv_manager(project_path='.'):
    """Get virtual environment manager instance."""
    return VirtualEnvironmentManager(project_path)

def get_git_manager(project_path='.'):
    """Get git operations manager instance."""
    return GitOperationsManager(project_path)

def get_command_executor(project_path='.'):
    """Get python command executor instance."""
    return PythonCommandExecutor(project_path)

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

# Phase 4 Production Components
from .advanced_orchestrator import (
    AdvancedOrchestrator,
    OrchestrationTask,
    ProductionMetrics,
    get_advanced_orchestration,
    execute_production_workflow,
    get_production_status
)

from .production_manager import (
    ProductionManager,
    DeploymentConfig,
    SystemHealth,
    DeploymentStatus,
    get_production_manager,
    deploy_to_production,
    check_production_health
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
    'get_linting_integration',
    'get_venv_manager',
    'get_git_manager',
    'get_command_executor',
    
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
    'record_performance_metrics',
    
    # Phase 4 Production Components
    'AdvancedOrchestrator',
    'OrchestrationTask',
    'ProductionManager',
    'DeploymentConfig',
    'SystemHealth',
    'DeploymentStatus',
    
    # Phase 4 Convenience Functions
    'get_advanced_orchestration',
    'execute_production_workflow',
    'get_production_status',
    'get_production_manager',
    'deploy_to_production',
    'check_production_health',
]
