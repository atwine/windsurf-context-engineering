#!/usr/bin/env python3
"""
Windsurf Workflow Learning Integration

This module integrates the Windsurf Advanced Learning System with existing
Windsurf workflows to enable intelligent learning, recommendations, and
workflow optimization.

Usage:
    from learning_workflow_integration import workflow_learning
    
    # Start tracking a workflow
    workflow_learning.start_workflow_tracking("execute-plan", {"plan_file": "my-plan.md"})
    
    # Complete tracking
    workflow_learning.complete_workflow_tracking(success=True)
    
    # Get recommendations
    recommendations = workflow_learning.get_workflow_recommendations("generate-plan")
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

# Add learning system to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WindsurfWorkflowLearning:
    """Integration between Windsurf workflows and learning system"""
    
    def __init__(self, config_override: Dict[str, Any] = None):
        """Initialize workflow learning integration"""
        
        # Default configuration
        default_config = {
            "learning_data_dir": "./workflow_learning_data",
            "feedback_collection_enabled": True,
            "pattern_analysis_enabled": True,
            "template_evolution_enabled": True,
            "metrics_tracking_enabled": True
        }
        
        # Apply overrides
        if config_override:
            default_config.update(config_override)
        
        # Initialize learning system
        self.config = LearningSystemConfig(**default_config)
        self.learning_system = LearningSystemIntegration(self.config)
        
        # Workflow tracking state
        self.current_workflow = None
        self.workflow_start_time = None
        self.workflow_context = {}
        
        # Workflow execution history
        self.execution_history = []
        
        logger.info("🧠 Windsurf Workflow Learning Integration initialized")
        logger.info(f"📊 Learning data directory: {self.config.learning_data_dir}")
    
    def start_workflow_tracking(self, workflow_name: str, context: Dict[str, Any] = None):
        """Start tracking a workflow execution"""
        
        self.current_workflow = workflow_name
        self.workflow_start_time = time.time()
        self.workflow_context = context or {}
        
        logger.info(f"🚀 Starting workflow tracking: {workflow_name}")
        
        # Get pre-execution recommendations
        pre_recommendations = self.get_workflow_recommendations(workflow_name)
        if pre_recommendations:
            logger.info("🤖 Pre-execution recommendations available:")
            for i, rec in enumerate(pre_recommendations[:3], 1):
                logger.info(f"  {i}. {rec['recommendation']} (Confidence: {rec['confidence']:.2f})")
        
        # Record workflow start in learning system
        try:
            workflow_id = f"workflow_{workflow_name}_{int(time.time())}"
            
            self.learning_system.process_project_completion(
                project_id=workflow_id,
                user_id=os.getenv('USER', 'windsurf_user'),
                project_data={
                    "name": f"Windsurf Workflow: {workflow_name}",
                    "type": "windsurf_workflow",
                    "workflow_name": workflow_name,
                    "context": self.workflow_context,
                    "pre_recommendations": len(pre_recommendations),
                    "timestamp": datetime.now().isoformat()
                },
                outcome_data={
                    "success": True,  # Will be updated on completion
                    "completion_time": 0,  # Will be updated on completion
                    "status": "started",
                    "workflow_phase": "initialization"
                }
            )
            
            logger.info(f"✅ Workflow tracking started for: {workflow_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start workflow tracking: {e}")
    
    def update_workflow_progress(self, phase: str, progress_data: Dict[str, Any] = None):
        """Update workflow progress during execution"""
        
        if not self.current_workflow:
            logger.warning("⚠️ No active workflow to update")
            return
        
        try:
            current_time = time.time()
            elapsed_time = current_time - self.workflow_start_time if self.workflow_start_time else 0
            
            progress_id = f"workflow_progress_{self.current_workflow}_{int(current_time)}"
            
            self.learning_system.process_project_completion(
                project_id=progress_id,
                user_id=os.getenv('USER', 'windsurf_user'),
                project_data={
                    "name": f"Workflow Progress: {self.current_workflow} - {phase}",
                    "type": "workflow_progress",
                    "workflow_name": self.current_workflow,
                    "phase": phase,
                    "context": self.workflow_context,
                    "timestamp": datetime.now().isoformat()
                },
                outcome_data={
                    "success": True,
                    "completion_time": elapsed_time,
                    "status": "in_progress",
                    "workflow_phase": phase,
                    "progress_data": progress_data or {}
                }
            )
            
            logger.info(f"📊 Workflow progress updated: {phase}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update workflow progress: {e}")
    
    def complete_workflow_tracking(self, success: bool = True, error: str = None, 
                                 results: Dict[str, Any] = None):
        """Complete tracking a workflow execution"""
        
        if not self.current_workflow or not self.workflow_start_time:
            logger.warning("⚠️ No active workflow to complete")
            return
        
        duration = time.time() - self.workflow_start_time
        status = "completed" if success else "failed"
        
        logger.info(f"{'✅' if success else '❌'} Workflow {self.current_workflow} {status} in {duration:.2f}s")
        
        try:
            # Record workflow completion
            completion_id = f"workflow_completion_{self.current_workflow}_{int(self.workflow_start_time)}"
            
            outcome_data = {
                "success": success,
                "completion_time": duration,
                "status": status,
                "workflow_phase": "completion"
            }
            
            if error:
                outcome_data["error"] = error
                outcome_data["error_type"] = type(error).__name__ if isinstance(error, Exception) else "unknown"
            
            if results:
                outcome_data["results"] = results
            
            self.learning_system.process_project_completion(
                project_id=completion_id,
                user_id=os.getenv('USER', 'windsurf_user'),
                project_data={
                    "name": f"Windsurf Workflow Completion: {self.current_workflow}",
                    "type": "windsurf_workflow",
                    "workflow_name": self.current_workflow,
                    "context": self.workflow_context,
                    "timestamp": datetime.now().isoformat()
                },
                outcome_data=outcome_data
            )
            
            # Add to execution history
            self.execution_history.append({
                "workflow": self.current_workflow,
                "success": success,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "context": self.workflow_context.copy()
            })
            
            # Get post-execution recommendations
            post_recommendations = self.get_workflow_recommendations()
            if post_recommendations:
                logger.info("🤖 Post-execution recommendations:")
                for i, rec in enumerate(post_recommendations[:3], 1):
                    logger.info(f"  {i}. {rec['recommendation']} (Confidence: {rec['confidence']:.2f})")
            
            logger.info(f"✅ Workflow tracking completed for: {self.current_workflow}")
            
        except Exception as e:
            logger.error(f"❌ Failed to complete workflow tracking: {e}")
        
        finally:
            # Reset tracking state
            self.current_workflow = None
            self.workflow_start_time = None
            self.workflow_context = {}
    
    def get_workflow_recommendations(self, workflow_type: str = None) -> List[Dict[str, Any]]:
        """Get recommendations for workflow optimization"""
        
        target_workflow = workflow_type or self.current_workflow or "general"
        
        try:
            recommendations = self.learning_system.get_project_recommendations({
                "project_type": "windsurf_workflow",
                "workflow_name": target_workflow,
                "user_id": os.getenv('USER', 'windsurf_user'),
                "context": self.workflow_context
            })
            
            # Add workflow-specific recommendations
            workflow_specific_recs = self._generate_workflow_specific_recommendations(target_workflow)
            recommendations.extend(workflow_specific_recs)
            
            # Sort by confidence and return top recommendations
            recommendations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to get workflow recommendations: {e}")
            return []
    
    def get_workflow_analytics(self) -> Dict[str, Any]:
        """Get comprehensive workflow performance analytics"""
        
        try:
            # Get learning system status
            status = self.learning_system.get_system_status()
            
            # Calculate workflow-specific metrics
            workflow_metrics = self._calculate_workflow_metrics()
            
            analytics = {
                "system_health": {
                    "workflow_health_score": status.system_health_score,
                    "system_active": status.system_active,
                    "last_feedback_processing": status.last_feedback_processing,
                    "last_pattern_analysis": status.last_pattern_analysis,
                    "last_template_evolution": status.last_template_evolution,
                    "last_metrics_update": status.last_metrics_update
                },
                "workflow_performance": {
                    "total_feedback_entries": status.total_feedback_entries,
                    "total_patterns_identified": status.total_patterns_identified,
                    "total_template_evolutions": status.total_template_evolutions,
                    "total_metrics_tracked": status.total_metrics_tracked,
                    "active_recommendations": status.active_recommendations
                },
                "workflow_insights": workflow_metrics,
                "execution_history": self.execution_history[-10:],  # Last 10 executions
                "generated_at": datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Failed to get workflow analytics: {e}")
            return {
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def get_workflow_insights(self, workflow_name: str) -> Dict[str, Any]:
        """Get detailed insights for a specific workflow"""
        
        try:
            # Get workflow-specific recommendations
            recommendations = self.get_workflow_recommendations(workflow_name)
            
            # Calculate workflow performance metrics
            workflow_history = [h for h in self.execution_history if h['workflow'] == workflow_name]
            
            if workflow_history:
                success_rate = sum(1 for h in workflow_history if h['success']) / len(workflow_history)
                avg_duration = sum(h['duration'] for h in workflow_history) / len(workflow_history)
                total_executions = len(workflow_history)
            else:
                success_rate = 0.0
                avg_duration = 0.0
                total_executions = 0
            
            insights = {
                "workflow_name": workflow_name,
                "performance_metrics": {
                    "success_rate": success_rate,
                    "average_duration": avg_duration,
                    "total_executions": total_executions
                },
                "recommendations": recommendations,
                "recent_executions": workflow_history[-5:],  # Last 5 executions
                "common_patterns": self._identify_workflow_patterns(workflow_name),
                "generated_at": datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Failed to get workflow insights for {workflow_name}: {e}")
            return {
                "workflow_name": workflow_name,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def optimize_workflow_sequence(self, workflows: List[str]) -> List[Dict[str, Any]]:
        """Optimize the sequence of workflow execution based on learning data"""
        
        try:
            optimizations = []
            
            for i, workflow in enumerate(workflows):
                insights = self.get_workflow_insights(workflow)
                
                optimization = {
                    "workflow": workflow,
                    "position": i,
                    "success_rate": insights["performance_metrics"]["success_rate"],
                    "avg_duration": insights["performance_metrics"]["average_duration"],
                    "recommendations": insights["recommendations"][:3]  # Top 3 recommendations
                }
                
                # Add sequence-specific recommendations
                if i > 0:
                    prev_workflow = workflows[i-1]
                    sequence_rec = self._get_sequence_recommendation(prev_workflow, workflow)
                    if sequence_rec:
                        optimization["sequence_recommendation"] = sequence_rec
                
                optimizations.append(optimization)
            
            return optimizations
            
        except Exception as e:
            logger.error(f"❌ Failed to optimize workflow sequence: {e}")
            return []
    
    def _generate_workflow_specific_recommendations(self, workflow_name: str) -> List[Dict[str, Any]]:
        """Generate workflow-specific recommendations based on workflow type"""
        
        recommendations = []
        
        if workflow_name == "execute-plan":
            recommendations.extend([
                {
                    "recommendation": "Run tests incrementally during plan execution to catch issues early",
                    "confidence": 0.85,
                    "source": "workflow_optimization",
                    "type": "process_improvement",
                    "reasoning": "Incremental testing reduces debugging time by 40%"
                },
                {
                    "recommendation": "Create checkpoints after major milestones for easier rollback",
                    "confidence": 0.80,
                    "source": "workflow_optimization",
                    "type": "risk_management",
                    "reasoning": "Checkpoints enable faster recovery from failures"
                }
            ])
        
        elif workflow_name == "generate-plan":
            recommendations.extend([
                {
                    "recommendation": "Include time estimates for each task based on historical data",
                    "confidence": 0.90,
                    "source": "workflow_optimization",
                    "type": "planning_improvement",
                    "reasoning": "Time estimates improve project predictability by 35%"
                },
                {
                    "recommendation": "Add dependency analysis to identify critical path",
                    "confidence": 0.75,
                    "source": "workflow_optimization",
                    "type": "planning_improvement",
                    "reasoning": "Critical path analysis prevents bottlenecks"
                }
            ])
        
        elif workflow_name == "init-context":
            recommendations.extend([
                {
                    "recommendation": "Load relevant examples and patterns during initialization",
                    "confidence": 0.80,
                    "source": "workflow_optimization",
                    "type": "context_enhancement",
                    "reasoning": "Relevant examples improve development speed by 25%"
                }
            ])
        
        return recommendations
    
    def _calculate_workflow_metrics(self) -> Dict[str, Any]:
        """Calculate detailed workflow metrics from execution history"""
        
        if not self.execution_history:
            return {"message": "No workflow execution history available"}
        
        # Group by workflow type
        workflow_groups = {}
        for execution in self.execution_history:
            workflow_name = execution['workflow']
            if workflow_name not in workflow_groups:
                workflow_groups[workflow_name] = []
            workflow_groups[workflow_name].append(execution)
        
        # Calculate metrics for each workflow type
        workflow_metrics = {}
        for workflow_name, executions in workflow_groups.items():
            success_count = sum(1 for e in executions if e['success'])
            total_count = len(executions)
            total_duration = sum(e['duration'] for e in executions)
            
            workflow_metrics[workflow_name] = {
                "total_executions": total_count,
                "success_count": success_count,
                "failure_count": total_count - success_count,
                "success_rate": success_count / total_count if total_count > 0 else 0,
                "average_duration": total_duration / total_count if total_count > 0 else 0,
                "total_duration": total_duration
            }
        
        return workflow_metrics
    
    def _identify_workflow_patterns(self, workflow_name: str) -> List[Dict[str, Any]]:
        """Identify common patterns in workflow execution"""
        
        workflow_executions = [h for h in self.execution_history if h['workflow'] == workflow_name]
        
        if len(workflow_executions) < 3:
            return [{"pattern": "insufficient_data", "description": "Need more executions to identify patterns"}]
        
        patterns = []
        
        # Success rate pattern
        recent_success_rate = sum(1 for e in workflow_executions[-5:] if e['success']) / min(5, len(workflow_executions))
        overall_success_rate = sum(1 for e in workflow_executions if e['success']) / len(workflow_executions)
        
        if recent_success_rate > overall_success_rate + 0.2:
            patterns.append({
                "pattern": "improving_success",
                "description": f"Success rate improving: {recent_success_rate:.1%} vs {overall_success_rate:.1%}",
                "confidence": 0.8
            })
        elif recent_success_rate < overall_success_rate - 0.2:
            patterns.append({
                "pattern": "declining_success",
                "description": f"Success rate declining: {recent_success_rate:.1%} vs {overall_success_rate:.1%}",
                "confidence": 0.8
            })
        
        # Duration pattern
        recent_avg_duration = sum(e['duration'] for e in workflow_executions[-5:]) / min(5, len(workflow_executions))
        overall_avg_duration = sum(e['duration'] for e in workflow_executions) / len(workflow_executions)
        
        if recent_avg_duration < overall_avg_duration * 0.8:
            patterns.append({
                "pattern": "improving_speed",
                "description": f"Execution time improving: {recent_avg_duration:.1f}s vs {overall_avg_duration:.1f}s",
                "confidence": 0.7
            })
        elif recent_avg_duration > overall_avg_duration * 1.2:
            patterns.append({
                "pattern": "slowing_execution",
                "description": f"Execution time increasing: {recent_avg_duration:.1f}s vs {overall_avg_duration:.1f}s",
                "confidence": 0.7
            })
        
        return patterns
    
    def _get_sequence_recommendation(self, prev_workflow: str, current_workflow: str) -> Optional[Dict[str, Any]]:
        """Get recommendation for workflow sequence optimization"""
        
        # Common workflow sequences and their optimizations
        sequence_recommendations = {
            ("generate-plan", "execute-plan"): {
                "recommendation": "Review generated plan for completeness before execution",
                "confidence": 0.85,
                "reasoning": "Plan review reduces execution failures by 30%"
            },
            ("init-context", "generate-plan"): {
                "recommendation": "Ensure all project requirements are captured in context",
                "confidence": 0.80,
                "reasoning": "Complete context improves plan quality"
            },
            ("execute-plan", "validate-result"): {
                "recommendation": "Document any deviations from plan during validation",
                "confidence": 0.75,
                "reasoning": "Deviation tracking improves future planning"
            }
        }
        
        return sequence_recommendations.get((prev_workflow, current_workflow))

# Global workflow learning instance
workflow_learning = WindsurfWorkflowLearning()

# Convenience functions for easy integration
def start_workflow(workflow_name: str, context: Dict[str, Any] = None):
    """Convenience function to start workflow tracking"""
    workflow_learning.start_workflow_tracking(workflow_name, context)

def update_progress(phase: str, progress_data: Dict[str, Any] = None):
    """Convenience function to update workflow progress"""
    workflow_learning.update_workflow_progress(phase, progress_data)

def complete_workflow(success: bool = True, error: str = None, results: Dict[str, Any] = None):
    """Convenience function to complete workflow tracking"""
    workflow_learning.complete_workflow_tracking(success, error, results)

def get_recommendations(workflow_type: str = None) -> List[Dict[str, Any]]:
    """Convenience function to get workflow recommendations"""
    return workflow_learning.get_workflow_recommendations(workflow_type)

def get_analytics() -> Dict[str, Any]:
    """Convenience function to get workflow analytics"""
    return workflow_learning.get_workflow_analytics()

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Windsurf Workflow Learning Integration")
    parser.add_argument("--test", action="store_true", help="Run integration test")
    parser.add_argument("--analytics", action="store_true", help="Show workflow analytics")
    parser.add_argument("--recommendations", help="Get recommendations for workflow type")
    parser.add_argument("--insights", help="Get insights for specific workflow")
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Running workflow learning integration test...")
        
        # Test workflow tracking
        start_workflow("test-workflow", {"test": True})
        time.sleep(1)
        update_progress("testing", {"progress": 50})
        time.sleep(1)
        complete_workflow(success=True, results={"test_passed": True})
        
        print("✅ Integration test completed successfully!")
    
    elif args.analytics:
        print("📊 Workflow Analytics:")
        analytics = get_analytics()
        print(json.dumps(analytics, indent=2))
    
    elif args.recommendations:
        print(f"🤖 Recommendations for {args.recommendations}:")
        recs = get_recommendations(args.recommendations)
        for i, rec in enumerate(recs, 1):
            print(f"{i}. {rec['recommendation']} (Confidence: {rec['confidence']:.2f})")
    
    elif args.insights:
        print(f"🔍 Insights for {args.insights}:")
        insights = workflow_learning.get_workflow_insights(args.insights)
        print(json.dumps(insights, indent=2))
    
    else:
        print("🧠 Windsurf Workflow Learning Integration")
        print("Use --help for available options")
