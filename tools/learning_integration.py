#!/usr/bin/env python3
"""
Learning System Integration for Windsurf Context Engineering Framework

This module integrates the intelligence engine with the existing learning system
to provide continuous improvement and adaptive recommendations.

Phase 3: Learning Integration
- Connect with existing learning modules
- Continuous improvement based on execution data
- Adaptive workflow optimization
- Pattern recognition and prediction
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import importlib
import sys

from .intelligence_engine import IntelligenceEngine, Recommendation, LearningPattern

logger = logging.getLogger(__name__)

class LearningSystemIntegration:
    """
    Integration layer between intelligence engine and existing learning system.
    
    Provides:
    - Seamless integration with existing learning modules
    - Data synchronization between systems
    - Unified learning interface
    - Adaptive optimization based on historical data
    """
    
    def __init__(self, project_path: str = "."):
        """Initialize learning system integration."""
        self.project_path = Path(project_path).resolve()
        self.intelligence_engine = IntelligenceEngine(str(self.project_path))
        
        # Learning system components
        self.learning_modules = {}
        self.learning_data_path = self.project_path / ".windsurf" / "learning_integration"
        self.learning_data_path.mkdir(parents=True, exist_ok=True)
        
        # Integration state
        self.integration_active = False
        self.last_sync_time = 0.0
        
        # Initialize learning system integration
        self._initialize_learning_integration()
        
        logger.info(f"Learning system integration initialized for: {self.project_path}")
    
    def _initialize_learning_integration(self):
        """Initialize integration with existing learning system."""
        try:
            # Try to load existing learning modules
            learning_path = self.project_path / "learning"
            if learning_path.exists():
                self._load_learning_modules()
                # Activate only if at least one module loaded
                self.integration_active = len(self.learning_modules) > 0
                if self.integration_active:
                    logger.info("Successfully integrated with existing learning system")
                else:
                    logger.info("Learning path found but no modules loaded; integration remains inactive")
            else:
                logger.info("No existing learning system found - running in standalone mode")
                
        except Exception as e:
            logger.warning(f"Error initializing learning integration: {e}")
            self.integration_active = False
    
    def _load_learning_modules(self):
        """Load existing learning modules for integration."""
        try:
            learning_path = self.project_path / "learning"
            
            # Add learning path to Python path temporarily
            if str(learning_path) not in sys.path:
                sys.path.insert(0, str(learning_path))
            
            # Load modules that actually exist in learning/ (surgical change)
            learning_module_names = [
                'pattern_analyzer',
                'template_evolution',
                'learning_engine',
                'metrics_tracker',
                'feedback_collector',
                'enhanced_workflow_learning',
                'user_workspace_integration'
            ]
            
            for module_name in learning_module_names:
                try:
                    module = importlib.import_module(module_name)
                    self.learning_modules[module_name] = module
                    logger.debug(f"Loaded learning module: {module_name}")
                except ImportError:
                    logger.debug(f"Learning module not found: {module_name}")
            
            logger.info(f"Loaded {len(self.learning_modules)} learning modules")
            
        except Exception as e:
            logger.warning(f"Error loading learning modules: {e}")
    
    def get_enhanced_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations enhanced with learning system data."""
        try:
            # Get base recommendations from intelligence engine
            base_recommendations = self.intelligence_engine.generate_recommendations()
            
            # Enhance with learning system data if available
            if self.integration_active:
                enhanced_recommendations = []
                
                for rec in base_recommendations:
                    enhanced_rec = self._enhance_recommendation_with_learning(rec)
                    enhanced_recommendations.append(enhanced_rec)
                
                # Add learning-specific recommendations
                learning_recommendations = self._generate_learning_recommendations()
                enhanced_recommendations.extend(learning_recommendations)
                
                return [self._recommendation_to_dict(rec) for rec in enhanced_recommendations]
            else:
                return [self._recommendation_to_dict(rec) for rec in base_recommendations]
                
        except Exception as e:
            logger.error(f"Error getting enhanced recommendations: {e}")
            return []
    
    def _enhance_recommendation_with_learning(self, recommendation: Recommendation) -> Recommendation:
        """Enhance a recommendation with learning system data."""
        try:
            # Check if we have learning data for this type of recommendation
            learning_data = self._get_learning_data_for_recommendation(recommendation)
            
            if learning_data:
                # Adjust confidence based on historical success
                historical_success = learning_data.get('success_rate', 0.5)
                adjusted_confidence = (recommendation.confidence + historical_success) / 2
                
                # Update reasoning with learning insights
                learning_insight = learning_data.get('insight', '')
                if learning_insight:
                    recommendation.reasoning += f" | Learning insight: {learning_insight}"
                
                # Adjust priority based on learning data
                if historical_success > 0.8 and recommendation.priority == 'low':
                    recommendation.priority = 'medium'
                elif historical_success < 0.3 and recommendation.priority == 'high':
                    recommendation.priority = 'medium'
                
                recommendation.confidence = min(1.0, max(0.0, adjusted_confidence))
            
            return recommendation
            
        except Exception as e:
            logger.warning(f"Error enhancing recommendation with learning: {e}")
            return recommendation
    
    def _generate_learning_recommendations(self) -> List[Recommendation]:
        """Generate recommendations based on learning system analysis."""
        recommendations = []
        
        try:
            if not self.integration_active:
                return recommendations
            
            # Analyze learning patterns for recommendations
            learning_patterns = self._analyze_learning_patterns()
            
            for pattern in learning_patterns:
                if pattern.get('confidence', 0) > 0.7:
                    rec = Recommendation(
                        type='learning',
                        action=pattern.get('action', 'optimize'),
                        description=pattern.get('description', 'Learning-based optimization'),
                        confidence=pattern.get('confidence', 0.7),
                        priority=pattern.get('priority', 'medium'),
                        reasoning=pattern.get('reasoning', 'Based on learning analysis'),
                        estimated_impact=pattern.get('impact', 'Improved efficiency'),
                        prerequisites=pattern.get('prerequisites', []),
                        timestamp=pattern.get('timestamp', 0.0)
                    )
                    recommendations.append(rec)
            
        except Exception as e:
            logger.warning(f"Error generating learning recommendations: {e}")
        
        return recommendations
    
    def _analyze_learning_patterns(self) -> List[Dict[str, Any]]:
        """Analyze learning patterns for optimization opportunities."""
        patterns = []
        
        try:
            # This would integrate with the actual learning system
            # For now, return some example patterns
            
            patterns.append({
                'action': 'optimize_command_sequence',
                'description': 'Optimize frequently used command sequences',
                'confidence': 0.8,
                'priority': 'medium',
                'reasoning': 'Detected repetitive command patterns that can be optimized',
                'impact': 'Reduced development time by 15-20%',
                'prerequisites': ['Review command history'],
                'timestamp': datetime.now().timestamp()
            })
            
            patterns.append({
                'action': 'improve_error_handling',
                'description': 'Enhance error handling based on common failure patterns',
                'confidence': 0.75,
                'priority': 'high',
                'reasoning': 'Analysis shows recurring error patterns that can be prevented',
                'impact': 'Reduced error rate by 30%',
                'prerequisites': ['Analyze error logs'],
                'timestamp': datetime.now().timestamp()
            })
            
        except Exception as e:
            logger.warning(f"Error analyzing learning patterns: {e}")
        
        return patterns
    
    def _get_learning_data_for_recommendation(self, recommendation: Recommendation) -> Optional[Dict[str, Any]]:
        """Get learning data relevant to a specific recommendation."""
        try:
            # This would query the learning system for relevant data
            # For now, return mock data based on recommendation type
            
            mock_data = {
                'commit': {
                    'success_rate': 0.85,
                    'insight': 'Commits with descriptive messages have 90% higher acceptance rate'
                },
                'push': {
                    'success_rate': 0.92,
                    'insight': 'Pushes after successful tests have 95% success rate'
                },
                'environment': {
                    'success_rate': 0.88,
                    'insight': 'Virtual environments reduce dependency conflicts by 80%'
                },
                'workflow': {
                    'success_rate': 0.78,
                    'insight': 'Optimized workflows reduce execution time by 25%'
                }
            }
            
            return mock_data.get(recommendation.type)
            
        except Exception as e:
            logger.warning(f"Error getting learning data: {e}")
            return None
    
    def sync_with_learning_system(self):
        """Synchronize data with the existing learning system."""
        try:
            if not self.integration_active:
                logger.debug("Learning system integration not active - skipping sync")
                return
            
            # Get intelligence data
            intelligence_summary = self.intelligence_engine.get_intelligence_summary()
            
            # Sync with learning modules
            for module_name, module in self.learning_modules.items():
                try:
                    if hasattr(module, 'update_from_intelligence'):
                        module.update_from_intelligence(intelligence_summary)
                        logger.debug(f"Synced with learning module: {module_name}")
                except Exception as e:
                    logger.warning(f"Error syncing with {module_name}: {e}")
            
            # Update sync time
            self.last_sync_time = datetime.now().timestamp()
            
            logger.info("Successfully synced with learning system")
            
        except Exception as e:
            logger.error(f"Error syncing with learning system: {e}")
    
    def learn_from_workflow_execution(self, workflow_name: str, execution_data: Dict[str, Any]):
        """Learn from workflow execution for continuous improvement."""
        try:
            # Extract learning insights from workflow execution
            learning_data = {
                'workflow_name': workflow_name,
                'execution_time': execution_data.get('duration', 0),
                'success': execution_data.get('success', False),
                'errors': execution_data.get('errors', []),
                'commands_executed': execution_data.get('commands', []),
                'environment_used': execution_data.get('environment', {}),
                'git_operations': execution_data.get('git_operations', []),
                'timestamp': datetime.now().timestamp()
            }
            
            # Store learning data
            self._store_workflow_learning_data(learning_data)
            
            # Update intelligence engine
            context = self.intelligence_engine.analyze_context()
            
            # Simulate command results for learning
            for command in execution_data.get('commands', []):
                from .command_executor import CommandResult
                # Align with tools/command_executor.CommandResult
                result = CommandResult(
                    success=command.get('success', True),
                    returncode=command.get('exit_code', 0),  # Align with CommandResult field name
                    stdout=command.get('output', ''),
                    stderr=command.get('error', ''),
                    command=command.get('command', ''),
                    execution_time=command.get('duration', 0),
                    venv_used=bool(command.get('environment', '')),  # CommandResult expects boolean venv_used
                    git_changes_detected=command.get('git_changes', False)
                )
                
                self.intelligence_engine.learn_from_execution(
                    command.get('command', ''), result, context
                )
            
            logger.info(f"Learned from workflow execution: {workflow_name}")
            
        except Exception as e:
            logger.error(f"Error learning from workflow execution: {e}")
    
    def _store_workflow_learning_data(self, learning_data: Dict[str, Any]):
        """Store workflow learning data for future analysis."""
        try:
            # Store in learning integration directory
            workflow_name = learning_data.get('workflow_name', 'unknown')
            timestamp = learning_data.get('timestamp', 0)
            
            filename = f"workflow_{workflow_name}_{int(timestamp)}.json"
            filepath = self.learning_data_path / filename
            
            with open(filepath, 'w') as f:
                json.dump(learning_data, f, indent=2)
            
            logger.debug(f"Stored workflow learning data: {filename}")
            
        except Exception as e:
            logger.warning(f"Error storing workflow learning data: {e}")
    
    def get_learning_integration_status(self) -> Dict[str, Any]:
        """Get status of learning system integration."""
        return {
            'integration_active': self.integration_active,
            'learning_modules_loaded': len(self.learning_modules),
            'learning_modules': list(self.learning_modules.keys()),
            'last_sync_time': self.last_sync_time,
            'intelligence_engine_health': self.intelligence_engine._calculate_intelligence_health(),
            'learning_data_path': str(self.learning_data_path),
            'timestamp': datetime.now().timestamp()
        }
    
    def _recommendation_to_dict(self, rec: Recommendation) -> Dict[str, Any]:
        """Convert recommendation to dictionary format."""
        return {
            'type': rec.type,
            'action': rec.action,
            'description': rec.description,
            'confidence': rec.confidence,
            'priority': rec.priority,
            'reasoning': rec.reasoning,
            'estimated_impact': rec.estimated_impact,
            'prerequisites': rec.prerequisites,
            'timestamp': rec.timestamp
        }


# Convenience functions for easy integration

def get_learning_enhanced_recommendations(project_path: str = ".") -> List[Dict[str, Any]]:
    """Get recommendations enhanced with learning system integration."""
    try:
        integration = LearningSystemIntegration(project_path)
        return integration.get_enhanced_recommendations()
    except Exception as e:
        logger.error(f"Error getting learning enhanced recommendations: {e}")
        return []

def sync_intelligence_with_learning(project_path: str = "."):
    """Synchronize intelligence engine with learning system."""
    try:
        integration = LearningSystemIntegration(project_path)
        integration.sync_with_learning_system()
    except Exception as e:
        logger.error(f"Error syncing intelligence with learning: {e}")

def learn_from_workflow(workflow_name: str, execution_data: Dict[str, Any], project_path: str = "."):
    """Learn from workflow execution for continuous improvement."""
    try:
        integration = LearningSystemIntegration(project_path)
        integration.learn_from_workflow_execution(workflow_name, execution_data)
    except Exception as e:
        logger.error(f"Error learning from workflow: {e}")

def get_integration_status(project_path: str = ".") -> Dict[str, Any]:
    """Get learning integration status."""
    try:
        integration = LearningSystemIntegration(project_path)
        return integration.get_learning_integration_status()
    except Exception as e:
        logger.error(f"Error getting integration status: {e}")
        return {'error': str(e)}
