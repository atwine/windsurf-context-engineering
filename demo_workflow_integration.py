#!/usr/bin/env python3
"""
Windsurf Workflow Integration Demo

This script demonstrates the integration between Windsurf workflows and the
Advanced Learning System. It shows how workflows can be enhanced with
intelligent learning, recommendations, and performance tracking.

Usage:
    python demo_workflow_integration.py
"""

import time
import json
from datetime import datetime
from learning_workflow_integration import workflow_learning

def demo_execute_plan_workflow():
    """Demonstrate execute-plan workflow with learning integration"""
    
    print("🎯 Demo: Execute Plan Workflow with Learning Integration")
    print("=" * 60)
    
    # Simulate plan execution with learning integration
    plan_context = {
        "plan_file": "demo-web-app-plan.md",
        "project_type": "web_app",
        "technologies": ["React", "Node.js", "PostgreSQL"],
        "complexity": "medium",
        "estimated_duration": 3600  # 1 hour
    }
    
    # Start workflow tracking
    workflow_learning.start_workflow_tracking("execute-plan", plan_context)
    
    # Simulate workflow phases
    phases = [
        ("project_setup", 5, "Setting up project structure"),
        ("dependency_installation", 10, "Installing dependencies"),
        ("core_implementation", 30, "Implementing core features"),
        ("testing", 15, "Running tests"),
        ("documentation", 8, "Generating documentation"),
        ("validation", 5, "Final validation")
    ]
    
    total_duration = 0
    
    for phase, duration, description in phases:
        print(f"\n📋 Phase: {phase}")
        print(f"   {description}...")
        
        # Update progress
        workflow_learning.update_workflow_progress(phase, {
            "phase_duration": duration,
            "description": description
        })
        
        # Simulate work
        time.sleep(1)  # Reduced for demo
        total_duration += duration
        
        print(f"   ✅ Completed in {duration}s")
    
    # Complete workflow tracking
    workflow_learning.complete_workflow_tracking(
        success=True,
        results={
            "total_phases": len(phases),
            "total_duration": total_duration,
            "project_type": "web_app",
            "technologies_used": plan_context["technologies"]
        }
    )
    
    print(f"\n🎉 Execute Plan workflow completed successfully!")
    print(f"   Total duration: {total_duration}s")

def demo_generate_plan_workflow():
    """Demonstrate generate-plan workflow with learning integration"""
    
    print("\n🎯 Demo: Generate Plan Workflow with Learning Integration")
    print("=" * 60)
    
    # Simulate plan generation with learning integration
    project_context = {
        "project_name": "E-commerce Platform",
        "project_type": "web_app",
        "technologies": ["React", "TypeScript", "Node.js", "MongoDB"],
        "complexity": "high",
        "team_size": 3,
        "timeline": "4_weeks"
    }
    
    # Start workflow tracking
    workflow_learning.start_workflow_tracking("generate-plan", project_context)
    
    # Simulate plan generation phases
    phases = [
        ("requirements_analysis", 8, "Analyzing project requirements"),
        ("architecture_design", 12, "Designing system architecture"),
        ("task_breakdown", 10, "Breaking down tasks"),
        ("timeline_estimation", 5, "Estimating timelines"),
        ("plan_optimization", 7, "Optimizing plan with learning insights")
    ]
    
    total_duration = 0
    
    for phase, duration, description in phases:
        print(f"\n📋 Phase: {phase}")
        print(f"   {description}...")
        
        # Update progress
        workflow_learning.update_workflow_progress(phase, {
            "phase_duration": duration,
            "description": description
        })
        
        # Simulate work
        time.sleep(0.5)  # Reduced for demo
        total_duration += duration
        
        print(f"   ✅ Completed in {duration}s")
    
    # Complete workflow tracking
    workflow_learning.complete_workflow_tracking(
        success=True,
        results={
            "plan_generated": True,
            "total_tasks": 25,
            "estimated_project_duration": "4_weeks",
            "technologies_recommended": project_context["technologies"]
        }
    )
    
    print(f"\n🎉 Generate Plan workflow completed successfully!")
    print(f"   Total duration: {total_duration}s")

def demo_workflow_analytics():
    """Demonstrate workflow analytics and insights"""
    
    print("\n📊 Demo: Workflow Analytics and Insights")
    print("=" * 60)
    
    # Get comprehensive analytics
    analytics = workflow_learning.get_workflow_analytics()
    
    print("🏥 System Health:")
    health = analytics["system_health"]
    print(f"   Health Score: {health['workflow_health_score']:.2f}/1.0")
    print(f"   System Active: {health['system_active']}")
    
    print("\n📈 Performance Metrics:")
    performance = analytics["workflow_performance"]
    print(f"   Total Feedback Entries: {performance['total_feedback_entries']}")
    print(f"   Total Patterns Identified: {performance['total_patterns_identified']}")
    print(f"   Total Metrics Tracked: {performance['total_metrics_tracked']}")
    print(f"   Active Recommendations: {performance['active_recommendations']}")
    
    print("\n📋 Recent Execution History:")
    history = analytics["execution_history"]
    if history:
        for i, execution in enumerate(history[-3:], 1):  # Last 3 executions
            status = "✅" if execution["success"] else "❌"
            print(f"   {i}. {status} {execution['workflow']} - {execution['duration']:.1f}s")
    else:
        print("   No execution history available yet")

def demo_workflow_recommendations():
    """Demonstrate intelligent workflow recommendations"""
    
    print("\n🤖 Demo: Intelligent Workflow Recommendations")
    print("=" * 60)
    
    # Get recommendations for different workflow types
    workflow_types = ["execute-plan", "generate-plan", "init-context"]
    
    for workflow_type in workflow_types:
        print(f"\n💡 Recommendations for {workflow_type}:")
        recommendations = workflow_learning.get_workflow_recommendations(workflow_type)
        
        if recommendations:
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec['recommendation']}")
                print(f"      Confidence: {rec['confidence']:.2f}")
                print(f"      Source: {rec['source']}")
                if 'reasoning' in rec:
                    print(f"      Reasoning: {rec['reasoning']}")
        else:
            print("   No recommendations available yet")

def demo_workflow_insights():
    """Demonstrate workflow-specific insights"""
    
    print("\n🔍 Demo: Workflow-Specific Insights")
    print("=" * 60)
    
    # Get insights for executed workflows
    executed_workflows = ["execute-plan", "generate-plan"]
    
    for workflow_name in executed_workflows:
        print(f"\n📊 Insights for {workflow_name}:")
        insights = workflow_learning.get_workflow_insights(workflow_name)
        
        if "error" not in insights:
            metrics = insights["performance_metrics"]
            print(f"   Success Rate: {metrics['success_rate']:.1%}")
            print(f"   Average Duration: {metrics['average_duration']:.1f}s")
            print(f"   Total Executions: {metrics['total_executions']}")
            
            patterns = insights.get("common_patterns", [])
            if patterns:
                print("   Common Patterns:")
                for pattern in patterns[:2]:
                    print(f"     • {pattern.get('description', 'Pattern identified')}")
        else:
            print(f"   Error getting insights: {insights['error']}")

def main():
    """Main demo function"""
    
    print("🌟 Windsurf Workflow Learning Integration Demo")
    print("=" * 80)
    print("This demo shows how Windsurf workflows are enhanced with AI learning")
    print("=" * 80)
    
    try:
        # Demo 1: Execute Plan Workflow
        demo_execute_plan_workflow()
        
        # Demo 2: Generate Plan Workflow  
        demo_generate_plan_workflow()
        
        # Demo 3: Analytics
        demo_workflow_analytics()
        
        # Demo 4: Recommendations
        demo_workflow_recommendations()
        
        # Demo 5: Insights
        demo_workflow_insights()
        
        print("\n" + "=" * 80)
        print("🎉 Demo completed successfully!")
        print("=" * 80)
        
        print("\n📚 What you've seen:")
        print("✅ Automatic workflow tracking and performance monitoring")
        print("✅ Real-time progress updates during workflow execution")
        print("✅ Intelligent recommendations based on learning patterns")
        print("✅ Comprehensive analytics and system health monitoring")
        print("✅ Workflow-specific insights and pattern recognition")
        print("✅ Cross-workflow learning and optimization")
        
        print("\n🚀 Next Steps:")
        print("1. Integrate with your existing Windsurf workflows")
        print("2. Start collecting real workflow execution data")
        print("3. Review and act on learning system recommendations")
        print("4. Monitor workflow performance improvements over time")
        print("5. Customize the learning system for your specific needs")
        
        print("\n📖 Documentation:")
        print("• Integration Guide: docs/integration-guide.md")
        print("• Training Guide: docs/training-guide.md")
        print("• API Reference: docs/api-reference.md")
        print("• Examples: examples/")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Please check the learning system setup and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
