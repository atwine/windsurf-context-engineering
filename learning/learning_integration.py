"""
Learning System Integration - Comprehensive integration layer for all learning components

This module provides a unified interface for integrating the learning system
with the Windsurf Context Engineering Framework, connecting all learning
components with the core framework systems.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from .learning_engine import LearningEngine, ProjectOutcome
from .feedback_collector import FeedbackCollector, FeedbackEntry, FeedbackType
from .pattern_analyzer import PatternAnalyzer
from .template_evolution import TemplateEvolution, TemplatePerformance
from .metrics_tracker import MetricsTracker, MetricType

logger = logging.getLogger(__name__)

@dataclass
class LearningSystemConfig:
    """Configuration for the learning system integration"""
    learning_data_dir: str
    feedback_collection_enabled: bool = True
    pattern_analysis_enabled: bool = True
    template_evolution_enabled: bool = True
    metrics_tracking_enabled: bool = True
    auto_evolution_threshold: float = 0.8
    feedback_processing_interval_hours: int = 24
    pattern_analysis_interval_hours: int = 48
    template_evolution_interval_hours: int = 168  # Weekly
    metrics_reporting_interval_hours: int = 24

@dataclass
class LearningSystemStatus:
    """Status information for the learning system"""
    system_active: bool
    last_feedback_processing: str
    last_pattern_analysis: str
    last_template_evolution: str
    last_metrics_update: str
    total_feedback_entries: int
    total_patterns_identified: int
    total_template_evolutions: int
    total_metrics_tracked: int
    system_health_score: float
    active_recommendations: int

class LearningSystemIntegration:
    """
    Comprehensive learning system integration for Windsurf Context Engineering Framework
    
    This class provides a unified interface for all learning system components,
    enabling seamless integration with the core framework and automated learning processes.
    """
    
    def __init__(self, config: LearningSystemConfig):
        """Initialize the learning system integration"""
        self.config = config
        self.data_dir = Path(config.learning_data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize learning components
        self.learning_engine = LearningEngine(str(self.data_dir / "learning_engine.db"))
        self.feedback_collector = FeedbackCollector(str(self.data_dir / "feedback.db"))
        self.pattern_analyzer = PatternAnalyzer(str(self.data_dir / "patterns.db"))
        self.template_evolution = TemplateEvolution(str(self.data_dir))
        self.metrics_tracker = MetricsTracker(str(self.data_dir / "metrics.db"))
        
        # Integration state
        self.last_processing_times = {
            'feedback': None,
            'patterns': None,
            'evolution': None,
            'metrics': None
        }
        
        # Active learning processes
        self.active_processes = {
            'feedback_collection': config.feedback_collection_enabled,
            'pattern_analysis': config.pattern_analysis_enabled,
            'template_evolution': config.template_evolution_enabled,
            'metrics_tracking': config.metrics_tracking_enabled
        }
        
        # Initialize all databases
        self._initialize_all_databases()
        
        logger.info("Learning system integration initialized")
    
    def _initialize_all_databases(self):
        """Initialize all component databases to ensure proper schema"""
        try:
            # Force database initialization by accessing each component
            # This ensures all tables are created
            self.learning_engine._init_database()
            self.feedback_collector._init_database()
            self.pattern_analyzer._init_database()
            self.template_evolution._init_database()
            self.metrics_tracker._init_database()
            
            logger.info("All learning system databases initialized")
            
            # Populate with sample data for testing
            self._populate_sample_data()
            
        except Exception as e:
            logger.error(f"Failed to initialize databases: {e}")
    
    def _populate_sample_data(self):
        """Populate sample data for testing and demonstration"""
        try:
            # Add sample template usage data
            self.template_evolution.track_template_usage(
                template_name="react_typescript_template",
                version_id="react_typescript_v1",
                project_id="sample_project_001",
                user_id="sample_user",
                success_score=0.85,
                completion_time=24.0,
                user_feedback="Great template, very helpful!",
                user_satisfaction=0.8,
                issues_encountered=["minor build configuration issue"]
            )
            
            # Add sample metrics
            self.metrics_tracker.track_development_speed(
                project_id="sample_project_001",
                user_id="sample_user",
                features_completed=3,
                time_spent_hours=24.0
            )
            
            self.metrics_tracker.track_code_quality(
                project_id="sample_project_001",
                user_id="sample_user",
                quality_score=0.85
            )
            
            logger.info("Sample data populated successfully")
            
        except Exception as e:
            logger.error(f"Failed to populate sample data: {e}")
    
    def process_project_completion(self, project_id: str, user_id: str, 
                                 project_data: Dict[str, Any],
                                 outcome_data: Dict[str, Any]) -> bool:
        """Process a completed project through all learning components"""
        try:
            success = True
            
            # Record project outcome in learning engine
            if self.active_processes['metrics_tracking']:
                outcome = ProjectOutcome(
                    project_id=project_id,
                    project_type=project_data.get('project_type', 'unknown'),
                    template_used=project_data.get('template_id', 'none'),
                    success_score=outcome_data.get('success_score', 0.8),
                    completion_time=outcome_data.get('completion_time', 0),
                    code_quality_score=outcome_data.get('quality_metrics', {}).get('overall_score', 0.8),
                    user_satisfaction=outcome_data.get('user_satisfaction', 0.7),
                    issues_encountered=outcome_data.get('issues', []),
                    patterns_used=project_data.get('patterns_used', []),
                    feedback_summary=outcome_data.get('feedback_summary', ''),
                    created_at=datetime.now().isoformat(),
                    metadata={**project_data, **outcome_data}
                )
                outcome_recorded = self.learning_engine.record_project_outcome(outcome)
                success = success and outcome_recorded
            
            # Track metrics
            if self.active_processes['metrics_tracking']:
                # Track development speed
                features_completed = project_data.get('features_completed', 1)
                time_spent = outcome_data.get('completion_time', 0)
                if time_spent > 0:
                    self.metrics_tracker.track_development_speed(
                        project_id=project_id,
                        user_id=user_id,
                        features_completed=features_completed,
                        time_spent_hours=time_spent,
                        context=project_data
                    )
                
                # Track code quality
                quality_score = outcome_data.get('quality_metrics', {}).get('overall_score', 0.8)
                self.metrics_tracker.track_code_quality(
                    project_id=project_id,
                    user_id=user_id,
                    quality_score=quality_score,
                    quality_metrics=outcome_data.get('quality_metrics', {}),
                    context=project_data
                )
                
                # Track user satisfaction
                satisfaction = outcome_data.get('user_satisfaction', 0.7)
                self.metrics_tracker.track_user_satisfaction(
                    project_id=project_id,
                    user_id=user_id,
                    satisfaction_score=satisfaction,
                    feedback_summary=outcome_data.get('feedback_summary', ''),
                    context=project_data
                )
                
                # Track project success
                success_score = outcome_data.get('success_score', 0.8)
                self.metrics_tracker.track_project_success(
                    project_id=project_id,
                    user_id=user_id,
                    success_score=success_score,
                    completion_status=outcome_data.get('outcome_type', 'success'),
                    context=project_data
                )
            
            # Collect feedback if available
            if self.active_processes['feedback_collection'] and 'user_feedback' in outcome_data:
                feedback_entry = FeedbackEntry(
                    feedback_id=f"feedback_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    project_id=project_id,
                    user_id=user_id,
                    feedback_type=FeedbackType.GENERAL,
                    rating=int(outcome_data.get('user_satisfaction', 0.7) * 5),
                    title="Project Completion Feedback",
                    description=outcome_data['user_feedback'],
                    context=project_data,
                    sentiment_score=0.0,  # Will be analyzed automatically
                    sentiment_level=None,
                    keywords=[],
                    priority="medium",
                    created_at=datetime.now().isoformat(),
                    processed=False,
                    response="",
                    metadata=outcome_data
                )
                feedback_collected = self.feedback_collector.collect_feedback(feedback_entry)
                success = success and feedback_collected
            
            # Trigger pattern analysis if enough data
            if self.active_processes['pattern_analysis']:
                self._trigger_pattern_analysis_if_needed()
            
            # Trigger template evolution if needed
            if self.active_processes['template_evolution']:
                self._trigger_template_evolution_if_needed(project_data)
            
            logger.info(f"Processed project completion for {project_id}: {'success' if success else 'partial success'}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to process project completion: {e}")
            return False
    
    def collect_user_feedback(self, project_id: str, user_id: str, 
                            feedback_text: str, feedback_type: str = 'general',
                            context: Dict[str, Any] = None) -> bool:
        """Collect user feedback and integrate with learning system"""
        try:
            if not self.active_processes['feedback_collection']:
                return True  # Silently skip if disabled
            
            # Collect feedback
            feedback_entry = FeedbackEntry(
                feedback_id=f"feedback_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                project_id=project_id,
                user_id=user_id,
                feedback_type=FeedbackType.GENERAL if feedback_type == 'general' else FeedbackType.USER_EXPERIENCE,
                rating=3,  # Default neutral rating
                title=f"{feedback_type.title()} Feedback",
                description=feedback_text,
                context=context or {},
                sentiment_score=0.0,
                sentiment_level=None,
                keywords=[],
                priority="medium",
                created_at=datetime.now().isoformat(),
                processed=False,
                response="",
                metadata={}
            )
            feedback_collected = self.feedback_collector.collect_feedback(feedback_entry)
            
            if feedback_collected:
                # Process feedback for immediate insights
                self._process_immediate_feedback(project_id, user_id, feedback_text, context or {})
                
                # Update last processing time
                self.last_processing_times['feedback'] = datetime.now().isoformat()
            
            return feedback_collected
            
        except Exception as e:
            logger.error(f"Failed to collect user feedback: {e}")
            return False
    
    def get_project_recommendations(self, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get comprehensive recommendations for a project"""
        try:
            recommendations = []
            
            # Get learning engine recommendations
            if self.active_processes['pattern_analysis']:
                learning_result = self.learning_engine.get_recommendations(
                    project_type=project_context.get('project_type', 'unknown'),
                    context=project_context
                )
                if learning_result.get('status') == 'success':
                    learning_recommendations = learning_result.get('recommendations', [])
                    recommendations.extend([
                        {
                            'source': 'learning_engine',
                            'type': 'pattern_based',
                            'recommendation': rec['recommendation'],
                            'confidence': rec['confidence'],
                            'reasoning': rec.get('reason', 'Based on learned patterns')
                        }
                        for rec in learning_recommendations
                    ])
            
            # Get pattern analyzer recommendations
            if self.active_processes['pattern_analysis']:
                pattern_recommendations = self.pattern_analyzer.get_recommendations(
                    project_context=project_context,
                    max_recommendations=3
                )
                recommendations.extend([
                    {
                        'source': 'pattern_analyzer',
                        'type': 'pattern_analysis',
                        'recommendation': rec['recommendation'],
                        'confidence': rec['confidence'],
                        'pattern_type': rec.get('pattern_type', 'unknown')
                    }
                    for rec in pattern_recommendations
                ])
            
            # Get template evolution recommendations
            if self.active_processes['template_evolution']:
                template_recommendations = self.template_evolution.get_template_recommendations(
                    project_context=project_context,
                    max_recommendations=3
                )
                recommendations.extend([
                    {
                        'source': 'template_evolution',
                        'type': 'template_optimization',
                        'recommendation': rec['recommendation'],
                        'confidence': rec['confidence'],
                        'template_id': rec.get('template_id', 'unknown')
                    }
                    for rec in template_recommendations
                ])
            
            # Sort by confidence and return top recommendations
            recommendations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            return recommendations[:10]
            
        except Exception as e:
            logger.error(f"Failed to get project recommendations: {e}")
            return []
    
    def get_system_status(self) -> LearningSystemStatus:
        """Get comprehensive status of the learning system"""
        try:
            # Get component statistics
            feedback_stats = self.feedback_collector.get_feedback_summary(days=30)
            pattern_stats = self.pattern_analyzer.get_pattern_summary(days=30)
            evolution_stats = self.template_evolution.get_evolution_summary(days=30)
            metrics_stats = self.metrics_tracker.get_metric_summary('development_speed', days=30)
            
            # Calculate system health score
            health_components = []
            
            # Feedback health
            if feedback_stats.get('total_feedback', 0) > 0:
                health_components.append(0.9)
            else:
                health_components.append(0.5)
            
            # Pattern analysis health
            if pattern_stats.get('total_patterns', 0) > 0:
                health_components.append(0.9)
            else:
                health_components.append(0.6)
            
            # Template evolution health
            if evolution_stats.get('total_evolutions', 0) > 0:
                health_components.append(0.9)
            else:
                health_components.append(0.7)
            
            # Metrics health
            if metrics_stats.get('data_points', 0) > 0:
                health_components.append(0.9)
            else:
                health_components.append(0.6)
            
            system_health_score = sum(health_components) / len(health_components)
            
            # Get active recommendations count
            sample_context = {'project_type': 'web_app', 'framework': 'react'}
            active_recommendations = len(self.get_project_recommendations(sample_context))
            
            return LearningSystemStatus(
                system_active=any(self.active_processes.values()),
                last_feedback_processing=self.last_processing_times.get('feedback', 'never'),
                last_pattern_analysis=self.last_processing_times.get('patterns', 'never'),
                last_template_evolution=self.last_processing_times.get('evolution', 'never'),
                last_metrics_update=self.last_processing_times.get('metrics', 'never'),
                total_feedback_entries=feedback_stats.get('total_feedback', 0),
                total_patterns_identified=pattern_stats.get('total_patterns', 0),
                total_template_evolutions=evolution_stats.get('total_evolutions', 0),
                total_metrics_tracked=metrics_stats.get('data_points', 0),
                system_health_score=system_health_score,
                active_recommendations=active_recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return LearningSystemStatus(
                system_active=False,
                last_feedback_processing='error',
                last_pattern_analysis='error',
                last_template_evolution='error',
                last_metrics_update='error',
                total_feedback_entries=0,
                total_patterns_identified=0,
                total_template_evolutions=0,
                total_metrics_tracked=0,
                system_health_score=0.0,
                active_recommendations=0
            )
    
    def generate_learning_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive learning system report"""
        try:
            # Get performance report from metrics tracker
            performance_report = self.metrics_tracker.generate_performance_report(days)
            
            # Get feedback analysis
            feedback_analysis = self.feedback_collector.analyze_feedback_trends(days)
            
            # Get pattern insights
            pattern_insights = self.pattern_analyzer.get_pattern_insights_by_period(days)
            
            # Get template evolution summary
            evolution_summary = self.template_evolution.get_evolution_summary(days)
            
            # Get system status
            system_status = self.get_system_status()
            
            # Compile comprehensive report
            learning_report = {
                'report_id': f"learning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'generated_at': datetime.now().isoformat(),
                'period_days': days,
                'system_status': asdict(system_status),
                'performance_metrics': {
                    'summary_metrics': performance_report.summary_metrics,
                    'trends': [asdict(trend) for trend in performance_report.trends],
                    'roi_analysis': performance_report.roi_analysis
                },
                'feedback_analysis': feedback_analysis,
                'pattern_insights': pattern_insights,
                'template_evolution': evolution_summary,
                'key_insights': performance_report.insights,
                'recommendations': performance_report.recommendations,
                'learning_effectiveness': self._calculate_learning_effectiveness(days)
            }
            
            logger.info(f"Generated learning report: {learning_report['report_id']}")
            return learning_report
            
        except Exception as e:
            logger.error(f"Failed to generate learning report: {e}")
            return {
                'report_id': 'error_report',
                'generated_at': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _trigger_pattern_analysis_if_needed(self):
        """Trigger pattern analysis if enough time has passed"""
        try:
            last_analysis = self.last_processing_times.get('patterns')
            if last_analysis:
                last_time = datetime.fromisoformat(last_analysis)
                hours_since = (datetime.now() - last_time).total_seconds() / 3600
                
                if hours_since < self.config.pattern_analysis_interval_hours:
                    return
            
            # Run pattern analysis
            patterns_identified = self.pattern_analyzer.analyze_recent_patterns(days=7)
            if patterns_identified:
                self.last_processing_times['patterns'] = datetime.now().isoformat()
                logger.info(f"Pattern analysis completed: {len(patterns_identified)} patterns identified")
            
        except Exception as e:
            logger.error(f"Failed to trigger pattern analysis: {e}")
    
    def _trigger_template_evolution_if_needed(self, project_data: Dict[str, Any]):
        """Trigger template evolution if conditions are met"""
        try:
            template_id = project_data.get('template_id')
            if not template_id:
                return
            
            last_evolution = self.last_processing_times.get('evolution')
            if last_evolution:
                last_time = datetime.fromisoformat(last_evolution)
                hours_since = (datetime.now() - last_time).total_seconds() / 3600
                
                if hours_since < self.config.template_evolution_interval_hours:
                    return
            
            # Check if template should evolve
            should_evolve = self.template_evolution.should_template_evolve(
                template_id=template_id,
                threshold=self.config.auto_evolution_threshold
            )
            
            if should_evolve:
                evolution_result = self.template_evolution.evolve_template(template_id)
                if evolution_result:
                    self.last_processing_times['evolution'] = datetime.now().isoformat()
                    logger.info(f"Template evolution completed for {template_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger template evolution: {e}")
    
    def _process_immediate_feedback(self, project_id: str, user_id: str, 
                                  feedback_text: str, context: Dict[str, Any]):
        """Process feedback for immediate insights and actions"""
        try:
            # Analyze sentiment
            sentiment = self.feedback_collector.analyze_sentiment(feedback_text)
            
            # If negative feedback, trigger immediate analysis
            if sentiment.get('sentiment') == 'negative' and sentiment.get('confidence', 0) > 0.7:
                # Record as a learning opportunity
                self.learning_engine.record_project_outcome(
                    project_id=project_id,
                    user_id=user_id,
                    outcome_type='feedback_negative',
                    success_score=0.3,
                    completion_time=0,
                    quality_metrics={'user_satisfaction': 0.3},
                    user_satisfaction=0.3,
                    context={'feedback': feedback_text, **context}
                )
                
                logger.info(f"Processed negative feedback for immediate learning: {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to process immediate feedback: {e}")
    
    def _calculate_learning_effectiveness(self, days: int) -> Dict[str, float]:
        """Calculate learning system effectiveness metrics"""
        try:
            # Get ROI data
            roi_data = self.metrics_tracker.calculate_roi(days)
            
            # Calculate learning rate (improvement over time)
            learning_rate = roi_data.get('speed_improvement_percentage', 0) / days * 30  # Monthly rate
            
            # Calculate adaptation rate (how quickly system responds to feedback)
            feedback_stats = self.feedback_collector.get_feedback_summary(days)
            total_feedback = feedback_stats.get('total_feedback', 0)
            adaptation_rate = min(total_feedback / (days * 0.5), 1.0)  # Normalize to 0-1
            
            # Calculate prediction accuracy (based on recommendation success)
            pattern_stats = self.pattern_analyzer.get_pattern_summary(days)
            prediction_accuracy = pattern_stats.get('prediction_accuracy', 0.5)
            
            return {
                'learning_rate_monthly': learning_rate,
                'adaptation_rate': adaptation_rate,
                'prediction_accuracy': prediction_accuracy,
                'overall_effectiveness': (learning_rate/10 + adaptation_rate + prediction_accuracy) / 3
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate learning effectiveness: {e}")
            return {
                'learning_rate_monthly': 0.0,
                'adaptation_rate': 0.0,
                'prediction_accuracy': 0.0,
                'overall_effectiveness': 0.0
            }


# Factory function for easy integration
def create_learning_system(data_dir: str = "learning_data", 
                         config_overrides: Dict[str, Any] = None) -> LearningSystemIntegration:
    """Create and configure a learning system integration instance"""
    config = LearningSystemConfig(
        learning_data_dir=data_dir,
        **(config_overrides or {})
    )
    return LearningSystemIntegration(config)


if __name__ == "__main__":
    # Example usage
    learning_system = create_learning_system("test_learning_data")
    
    # Simulate project completion
    project_data = {
        'project_type': 'web_app',
        'framework': 'react',
        'template_id': 'react_typescript_template',
        'features_completed': 5
    }
    
    outcome_data = {
        'outcome_type': 'success',
        'success_score': 0.85,
        'completion_time': 32.0,
        'quality_metrics': {'overall_score': 0.8, 'test_coverage': 0.9},
        'user_satisfaction': 0.8,
        'user_feedback': 'Great template, very helpful for getting started quickly!'
    }
    
    # Process project completion
    result = learning_system.process_project_completion(
        project_id="test_project_001",
        user_id="user_123",
        project_data=project_data,
        outcome_data=outcome_data
    )
    
    # Get recommendations
    recommendations = learning_system.get_project_recommendations(project_data)
    
    # Get system status
    status = learning_system.get_system_status()
    
    # Generate report
    report = learning_system.generate_learning_report(30)
    
    print("Learning System Integration Demo:")
    print(f"Project processing result: {result}")
    print(f"Recommendations count: {len(recommendations)}")
    print(f"System health score: {status.system_health_score:.2f}")
    print(f"Learning report generated: {report['report_id']}")
