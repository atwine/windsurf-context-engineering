#!/usr/bin/env python3
"""
CLI Integration Example for Windsurf Learning System

This example demonstrates how to integrate the Windsurf Learning System
with command-line tools and scripts to automatically track command
execution, performance, and outcomes.

Usage:
    python cli_integration_example.py --help
    python cli_integration_example.py build --project myapp
    python cli_integration_example.py deploy --project myapp --env production
    python cli_integration_example.py test --project myapp --suite unit

Features:
    - Command execution tracking
    - Performance monitoring
    - Error handling and recording
    - Intelligent recommendations
    - Project context awareness
"""

import os
import sys
import time
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Add learning system to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig

class CLILearningIntegration:
    """CLI integration wrapper for learning system"""
    
    def __init__(self, project_name: str = "cli_project"):
        self.project_name = project_name
        self.config = LearningSystemConfig(
            learning_data_dir=f"./cli_learning_data_{project_name}"
        )
        self.learning_system = LearningSystemIntegration(self.config)
        
    def execute_and_learn(self, 
                         command: str, 
                         command_type: str,
                         context: Dict[str, Any] = None,
                         cwd: str = None) -> Dict[str, Any]:
        """Execute command and record outcome in learning system"""
        
        start_time = time.time()
        command_id = f"{command_type}_{int(time.time() * 1000)}"
        
        print(f"🚀 Executing {command_type}: {command}")
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            # Prepare outcome data
            outcome_data = {
                "success": success,
                "completion_time": duration,
                "return_code": result.returncode,
                "command": command,
                "stdout_length": len(result.stdout),
                "stderr_length": len(result.stderr)
            }
            
            # Add context if provided
            if context:
                outcome_data.update(context)
            
            # Add error details if failed
            if not success:
                outcome_data["error"] = result.stderr[:500]  # Limit error message length
            
            # Record in learning system
            learning_result = self.learning_system.process_project_completion(
                project_id=command_id,
                user_id=os.getenv('USER', 'cli_user'),
                project_data={
                    "name": f"{command_type.title()} Command",
                    "type": command_type,
                    "project": self.project_name,
                    "command": command,
                    "timestamp": datetime.now().isoformat()
                },
                outcome_data=outcome_data
            )
            
            # Print results
            if success:
                print(f"✅ {command_type.title()} completed successfully in {duration:.2f}s")
                if result.stdout.strip():
                    print("📄 Output:")
                    print(result.stdout)
            else:
                print(f"❌ {command_type.title()} failed after {duration:.2f}s")
                print(f"💥 Error (code {result.returncode}):")
                print(result.stderr)
            
            return {
                "success": success,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "learning_recorded": learning_result
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"⏰ {command_type.title()} timed out after {duration:.2f}s")
            
            # Record timeout
            self.learning_system.process_project_completion(
                project_id=command_id,
                user_id=os.getenv('USER', 'cli_user'),
                project_data={
                    "name": f"{command_type.title()} Command",
                    "type": command_type,
                    "project": self.project_name,
                    "command": command,
                    "timestamp": datetime.now().isoformat()
                },
                outcome_data={
                    "success": False,
                    "completion_time": duration,
                    "error": "Command timed out",
                    "timeout": True
                }
            )
            
            return {
                "success": False,
                "duration": duration,
                "error": "timeout",
                "learning_recorded": True
            }
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {command_type.title()} failed with exception: {e}")
            
            # Record exception
            self.learning_system.process_project_completion(
                project_id=command_id,
                user_id=os.getenv('USER', 'cli_user'),
                project_data={
                    "name": f"{command_type.title()} Command",
                    "type": command_type,
                    "project": self.project_name,
                    "command": command,
                    "timestamp": datetime.now().isoformat()
                },
                outcome_data={
                    "success": False,
                    "completion_time": duration,
                    "error": str(e),
                    "exception": True
                }
            )
            
            return {
                "success": False,
                "duration": duration,
                "error": str(e),
                "learning_recorded": True
            }
    
    def get_recommendations(self, command_type: str) -> List[Dict[str, Any]]:
        """Get learning system recommendations for command type"""
        return self.learning_system.get_project_recommendations({
            "project_type": command_type,
            "project": self.project_name,
            "user_id": os.getenv('USER', 'cli_user')
        })
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get learning system health status"""
        status = self.learning_system.get_system_status()
        return {
            "system_health_score": status.system_health_score,
            "active_recommendations": status.active_recommendations,
            "total_projects": status.total_projects,
            "success_rate": status.success_rate,
            "avg_completion_time": status.avg_completion_time,
            "component_health": status.component_health
        }

def build_command(args, cli_integration: CLILearningIntegration):
    """Handle build command"""
    print(f"🏗️  Building project: {args.project}")
    
    # Get recommendations first
    recommendations = cli_integration.get_recommendations("build")
    if recommendations:
        print("🤖 Learning System Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec['recommendation']} (Confidence: {rec['confidence']:.2f})")
        print()
    
    # Determine build command based on project type
    if args.type == "node":
        command = "npm run build"
    elif args.type == "python":
        command = "python setup.py build"
    elif args.type == "docker":
        command = f"docker build -t {args.project} ."
    else:
        command = args.command or "make build"
    
    # Add build context
    context = {
        "build_type": args.type,
        "project_type": args.type,
        "environment": args.env or "development"
    }
    
    # Execute build
    result = cli_integration.execute_and_learn(
        command=command,
        command_type="build",
        context=context,
        cwd=args.cwd
    )
    
    if result["success"]:
        print(f"🎉 Build completed successfully!")
        
        # Get post-build recommendations
        post_recommendations = cli_integration.get_recommendations("build")
        if post_recommendations and len(post_recommendations) > len(recommendations):
            print("\n🔄 Updated recommendations based on this build:")
            for i, rec in enumerate(post_recommendations[len(recommendations):len(recommendations)+2], 1):
                print(f"  {i}. {rec['recommendation']} (Confidence: {rec['confidence']:.2f})")
    else:
        print(f"💥 Build failed!")
        return False
    
    return True

def deploy_command(args, cli_integration: CLILearningIntegration):
    """Handle deploy command"""
    print(f"🚀 Deploying project: {args.project} to {args.env}")
    
    # Get recommendations first
    recommendations = cli_integration.get_recommendations("deploy")
    if recommendations:
        print("🤖 Deployment Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec['recommendation']} (Confidence: {rec['confidence']:.2f})")
        print()
    
    # Determine deployment command
    if args.platform == "heroku":
        command = f"git push heroku main"
    elif args.platform == "docker":
        command = f"docker run -d --name {args.project} {args.project}"
    elif args.platform == "k8s":
        command = f"kubectl apply -f k8s/"
    else:
        command = args.command or f"deploy.sh {args.env}"
    
    # Add deployment context
    context = {
        "environment": args.env,
        "platform": args.platform,
        "project_type": "deployment"
    }
    
    # Execute deployment
    result = cli_integration.execute_and_learn(
        command=command,
        command_type="deploy",
        context=context,
        cwd=args.cwd
    )
    
    if result["success"]:
        print(f"🎉 Deployment to {args.env} completed successfully!")
    else:
        print(f"💥 Deployment to {args.env} failed!")
        return False
    
    return True

def test_command(args, cli_integration: CLILearningIntegration):
    """Handle test command"""
    print(f"🧪 Running {args.suite} tests for project: {args.project}")
    
    # Get recommendations first
    recommendations = cli_integration.get_recommendations("test")
    if recommendations:
        print("🤖 Testing Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec['recommendation']} (Confidence: {rec['confidence']:.2f})")
        print()
    
    # Determine test command
    if args.suite == "unit":
        if args.type == "node":
            command = "npm test"
        elif args.type == "python":
            command = "python -m pytest tests/unit/"
        else:
            command = "make test-unit"
    elif args.suite == "integration":
        if args.type == "node":
            command = "npm run test:integration"
        elif args.type == "python":
            command = "python -m pytest tests/integration/"
        else:
            command = "make test-integration"
    elif args.suite == "e2e":
        command = "npm run test:e2e" if args.type == "node" else "make test-e2e"
    else:
        command = args.command or "make test"
    
    # Add test context
    context = {
        "test_suite": args.suite,
        "test_type": args.type,
        "project_type": "test"
    }
    
    # Execute tests
    result = cli_integration.execute_and_learn(
        command=command,
        command_type="test",
        context=context,
        cwd=args.cwd
    )
    
    if result["success"]:
        print(f"🎉 {args.suite.title()} tests passed!")
    else:
        print(f"💥 {args.suite.title()} tests failed!")
        return False
    
    return True

def status_command(args, cli_integration: CLILearningIntegration):
    """Handle status command"""
    print(f"📊 Learning System Status for project: {args.project}")
    print("=" * 50)
    
    try:
        health = cli_integration.get_system_health()
        
        print(f"🏥 System Health Score: {health['system_health_score']:.2f}/1.0")
        print(f"📈 Active Recommendations: {health['active_recommendations']}")
        print(f"📊 Total Projects Tracked: {health['total_projects']}")
        print(f"✅ Success Rate: {health['success_rate']:.1%}")
        print(f"⏱️  Average Completion Time: {health['avg_completion_time']:.2f}s")
        
        print("\n🔧 Component Health:")
        for component, status in health['component_health'].items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {component}")
        
        # Get recent recommendations
        recommendations = cli_integration.get_recommendations("general")
        if recommendations:
            print(f"\n🤖 Recent Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec['recommendation']}")
                print(f"     Confidence: {rec['confidence']:.2f} | Source: {rec['source']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to get status: {e}")
        return False

def recommendations_command(args, cli_integration: CLILearningIntegration):
    """Handle recommendations command"""
    print(f"🤖 Learning System Recommendations for: {args.type or 'general'}")
    print("=" * 50)
    
    try:
        recommendations = cli_integration.get_recommendations(args.type or "general")
        
        if not recommendations:
            print("📭 No recommendations available yet.")
            print("💡 Try running some commands first to generate recommendations!")
            return True
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['recommendation']}")
            print(f"   🎯 Confidence: {rec['confidence']:.2f}")
            print(f"   📊 Source: {rec['source']}")
            print(f"   🔍 Type: {rec['type']}")
            if 'reasoning' in rec:
                print(f"   💭 Reasoning: {rec['reasoning']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to get recommendations: {e}")
        return False

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="CLI Learning System Integration Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s build --project myapp --type node
  %(prog)s deploy --project myapp --env production --platform heroku
  %(prog)s test --project myapp --suite unit --type python
  %(prog)s status --project myapp
  %(prog)s recommendations --project myapp --type build
        """
    )
    
    parser.add_argument('--project', default='default', help='Project name')
    parser.add_argument('--cwd', help='Working directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build project')
    build_parser.add_argument('--type', choices=['node', 'python', 'docker', 'custom'], 
                             default='custom', help='Build type')
    build_parser.add_argument('--env', help='Environment')
    build_parser.add_argument('--command', help='Custom build command')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy project')
    deploy_parser.add_argument('--env', required=True, help='Deployment environment')
    deploy_parser.add_argument('--platform', choices=['heroku', 'docker', 'k8s', 'custom'],
                              default='custom', help='Deployment platform')
    deploy_parser.add_argument('--command', help='Custom deployment command')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--suite', choices=['unit', 'integration', 'e2e', 'all'],
                            default='all', help='Test suite to run')
    test_parser.add_argument('--type', choices=['node', 'python', 'custom'],
                            default='custom', help='Test type')
    test_parser.add_argument('--command', help='Custom test command')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show learning system status')
    
    # Recommendations command
    rec_parser = subparsers.add_parser('recommendations', help='Get recommendations')
    rec_parser.add_argument('--type', help='Recommendation type (build, deploy, test, etc.)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize CLI integration
    cli_integration = CLILearningIntegration(args.project)
    
    # Route to appropriate command handler
    try:
        if args.command == 'build':
            success = build_command(args, cli_integration)
        elif args.command == 'deploy':
            success = deploy_command(args, cli_integration)
        elif args.command == 'test':
            success = test_command(args, cli_integration)
        elif args.command == 'status':
            success = status_command(args, cli_integration)
        elif args.command == 'recommendations':
            success = recommendations_command(args, cli_integration)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Command interrupted by user")
        return 130
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
