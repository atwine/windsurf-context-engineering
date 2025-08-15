#!/usr/bin/env python3
"""
System Status Check for Windsurf Context Engineering Framework
==============================================================

Comprehensive validation of all system components and capabilities.
"""

import os
import sys
import importlib.util
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json

class SystemStatusChecker:
    """Comprehensive system status validation."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.status_report = {
            "overall_status": "unknown",
            "components": {},
            "capabilities": {},
            "issues": [],
            "recommendations": []
        }
    
    def check_all_components(self) -> Dict[str, Any]:
        """Run comprehensive system check."""
        print("🔍 Windsurf Context Engineering Framework - System Status Check")
        print("=" * 70)
        
        # Check core components
        self._check_directory_structure()
        self._check_workflows()
        self._check_mcp_system()
        self._check_utilities()
        self._check_templates()
        self._check_dependencies()
        
        # Determine overall status
        self._determine_overall_status()
        
        # Print summary
        self._print_status_summary()
        
        return self.status_report
    
    def _check_directory_structure(self):
        """Validate directory structure."""
        print("\n📁 Checking Directory Structure...")
        
        required_dirs = [
            ".windsurf/workflows",
            "mcp",
            "mcp/servers", 
            "utilities",
            "templates",
            "examples",
            "plans"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                print(f"  ✅ {dir_path}")
            else:
                print(f"  ❌ {dir_path} - MISSING")
                missing_dirs.append(dir_path)
        
        self.status_report["components"]["directory_structure"] = {
            "status": "complete" if not missing_dirs else "incomplete",
            "missing_directories": missing_dirs
        }
    
    def _check_workflows(self):
        """Validate workflow files."""
        print("\n🔄 Checking Workflows...")
        
        # Updated: legacy execute-plan workflow is deprecated → use enhanced variant
        required_workflows = [
            "init-context.md",
            "generate-plan.md", 
            "execute-plan-enhanced.md",
            "validate-result.md",
            "research-automation.md",
            "adaptive-template.md",
            "mcp-integration.md"
        ]
        
        workflow_dir = self.project_root / ".windsurf" / "workflows"
        missing_workflows = []
        
        for workflow in required_workflows:
            workflow_path = workflow_dir / workflow
            if workflow_path.exists():
                print(f"  ✅ {workflow}")
            else:
                print(f"  ❌ {workflow} - MISSING")
                missing_workflows.append(workflow)
        
        self.status_report["components"]["workflows"] = {
            "status": "complete" if not missing_workflows else "incomplete",
            "missing_workflows": missing_workflows
        }
    
    def _check_mcp_system(self):
        """Validate MCP system components."""
        print("\n🧠 Checking MCP System...")
        
        mcp_components = [
            "mcp/__init__.py",
            "mcp/server.py",
            "mcp/client.py", 
            "mcp/registry.py",
            "mcp/knowledge_base.py",
            "mcp/semantic_search.py",
            "mcp/servers/react_docs_server.py",
            "mcp/servers/stackoverflow_server.py"
        ]
        
        missing_components = []
        for component in mcp_components:
            component_path = self.project_root / component
            if component_path.exists():
                print(f"  ✅ {component}")
            else:
                print(f"  ❌ {component} - MISSING")
                missing_components.append(component)
        
        # Test MCP imports
        import_status = self._test_mcp_imports()
        
        self.status_report["components"]["mcp_system"] = {
            "status": "complete" if not missing_components and import_status else "incomplete",
            "missing_components": missing_components,
            "import_status": import_status
        }
    
    def _test_mcp_imports(self) -> bool:
        """Test MCP system imports."""
        try:
            # Add project root to path
            sys.path.insert(0, str(self.project_root))
            
            # Test core MCP imports
            from mcp.client import MCPClient
            from mcp.server import MCPServer
            from mcp.registry import MCPRegistry
            from mcp.knowledge_base import KnowledgeBase
            from mcp.semantic_search import SemanticSearch
            
            print("  ✅ MCP imports successful")
            return True
        except Exception as e:
            print(f"  ❌ MCP import failed: {e}")
            return False
    
    def _check_utilities(self):
        """Validate utility components."""
        print("\n🛠️ Checking Utilities...")
        
        utilities = [
            "security-scanner.py",
            "code-quality-analyzer.py",
            "test-coverage-validator.py", 
            "dependency-tracker.py",
            "project-type-detector.py",
            "adaptive-template-engine.py"
        ]
        
        utility_dir = self.project_root / "utilities"
        missing_utilities = []
        
        for utility in utilities:
            utility_path = utility_dir / utility
            if utility_path.exists():
                print(f"  ✅ {utility}")
            else:
                print(f"  ❌ {utility} - MISSING")
                missing_utilities.append(utility)
        
        self.status_report["components"]["utilities"] = {
            "status": "complete" if not missing_utilities else "incomplete",
            "missing_utilities": missing_utilities
        }
    
    def _check_templates(self):
        """Validate template system."""
        print("\n🎨 Checking Templates...")
        
        templates = [
            "web_application_simple.md",
            "rest_api_simple.md",
            "ml_project_simple.md"
        ]
        
        template_dir = self.project_root / "templates"
        missing_templates = []
        
        for template in templates:
            template_path = template_dir / template
            if template_path.exists():
                print(f"  ✅ {template}")
            else:
                print(f"  ❌ {template} - MISSING")
                missing_templates.append(template)
        
        self.status_report["components"]["templates"] = {
            "status": "complete" if not missing_templates else "incomplete",
            "missing_templates": missing_templates
        }
    
    def _check_dependencies(self):
        """Validate dependency files."""
        print("\n📦 Checking Dependencies...")
        
        dependency_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "setup.py",
            "INSTALL.md"
        ]
        
        missing_files = []
        for file_name in dependency_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name} - MISSING")
                missing_files.append(file_name)
        
        self.status_report["components"]["dependencies"] = {
            "status": "complete" if not missing_files else "incomplete",
            "missing_files": missing_files
        }
    
    def _determine_overall_status(self):
        """Determine overall system status."""
        incomplete_components = []
        
        for component, status in self.status_report["components"].items():
            if status["status"] != "complete":
                incomplete_components.append(component)
        
        if not incomplete_components:
            self.status_report["overall_status"] = "excellent"
        elif len(incomplete_components) <= 2:
            self.status_report["overall_status"] = "good"
        else:
            self.status_report["overall_status"] = "needs_attention"
        
        # Set capabilities based on component status
        self._assess_capabilities()
    
    def _assess_capabilities(self):
        """Assess system capabilities."""
        capabilities = {
            "context_engineering": True,
            "mcp_integration": self.status_report["components"]["mcp_system"]["status"] == "complete",
            "quality_guardrails": self.status_report["components"]["utilities"]["status"] == "complete",
            "adaptive_templates": self.status_report["components"]["templates"]["status"] == "complete",
            "workflow_automation": self.status_report["components"]["workflows"]["status"] == "complete"
        }
        
        self.status_report["capabilities"] = capabilities
    
    def _print_status_summary(self):
        """Print comprehensive status summary."""
        print("\n" + "=" * 70)
        print("📊 SYSTEM STATUS SUMMARY")
        print("=" * 70)
        
        # Overall status
        status_emoji = {
            "excellent": "🟢",
            "good": "🟡", 
            "needs_attention": "🔴"
        }
        
        overall = self.status_report["overall_status"]
        print(f"\n🎯 Overall Status: {status_emoji[overall]} {overall.upper()}")
        
        # Component status
        print(f"\n📋 Component Status:")
        for component, status in self.status_report["components"].items():
            status_icon = "✅" if status["status"] == "complete" else "⚠️"
            print(f"  {status_icon} {component.replace('_', ' ').title()}: {status['status']}")
        
        # Capabilities
        print(f"\n🚀 Available Capabilities:")
        for capability, available in self.status_report["capabilities"].items():
            cap_icon = "✅" if available else "❌"
            print(f"  {cap_icon} {capability.replace('_', ' ').title()}")
        
        # Recommendations
        if overall != "excellent":
            print(f"\n💡 Recommendations:")
            if self.status_report["components"]["mcp_system"]["status"] != "complete":
                print("  • Run MCP integration tests to validate system")
            if self.status_report["components"]["utilities"]["status"] != "complete":
                print("  • Install missing utility components")
            if self.status_report["components"]["templates"]["status"] != "complete":
                print("  • Add missing template files")
            print("  • Review missing components and install as needed")
        
        print(f"\n🎉 System Ready: {'YES' if overall in ['excellent', 'good'] else 'NEEDS WORK'}")
        print("=" * 70)

def main():
    """Main execution function."""
    checker = SystemStatusChecker()
    status_report = checker.check_all_components()
    
    # Save report to file
    report_path = Path("system_status_report.json")
    with open(report_path, 'w') as f:
        json.dump(status_report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    return status_report["overall_status"] in ["excellent", "good"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
