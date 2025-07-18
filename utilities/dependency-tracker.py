#!/usr/bin/env python3
"""
Dependency Tracker
Automatically tracks and manages project dependencies across all utilities and components.
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DependencyTracker:
    """Tracks and manages project dependencies."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.dependencies = {
            'core': set(),           # Required for basic functionality
            'optional': set(),       # Optional enhancements
            'development': set(),    # Development and testing
            'future': set()          # Planned future dependencies
        }
        self.import_map = {}         # Maps imports to package names
        self.usage_stats = defaultdict(int)  # Track usage frequency
        
    def scan_all_dependencies(self) -> Dict[str, Set[str]]:
        """Scan all Python files for dependencies."""
        logger.info(f"Scanning dependencies in {self.project_path}")
        
        # Scan all Python files
        python_files = list(self.project_path.rglob('*.py'))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                self._scan_file_dependencies(file_path)
            except Exception as e:
                logger.warning(f"Could not scan {file_path}: {e}")
        
        # Categorize dependencies
        self._categorize_dependencies()
        
        return {
            category: sorted(deps) for category, deps in self.dependencies.items()
        }
    
    def update_requirements_files(self) -> None:
        """Update requirements.txt and requirements-dev.txt files."""
        logger.info("Updating requirements files...")
        
        # Update main requirements.txt
        self._update_main_requirements()
        
        # Update development requirements
        self._update_dev_requirements()
        
        logger.info("Requirements files updated successfully")
    
    def generate_dependency_report(self) -> Dict[str, any]:
        """Generate comprehensive dependency report."""
        report = {
            'summary': {
                'total_dependencies': sum(len(deps) for deps in self.dependencies.values()),
                'core_dependencies': len(self.dependencies['core']),
                'optional_dependencies': len(self.dependencies['optional']),
                'development_dependencies': len(self.dependencies['development']),
                'scan_timestamp': self._get_timestamp()
            },
            'dependencies_by_category': {
                category: sorted(list(deps)) for category, deps in self.dependencies.items()
            },
            'usage_statistics': dict(sorted(self.usage_stats.items(), key=lambda x: x[1], reverse=True)),
            'import_mapping': self.import_map,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _scan_file_dependencies(self, file_path: Path) -> None:
        """Scan a single file for dependencies."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._process_import(alias.name, file_path)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._process_import(node.module, file_path)
                        
        except Exception as e:
            logger.warning(f"Could not parse {file_path}: {e}")
    
    def _process_import(self, import_name: str, file_path: Path) -> None:
        """Process a single import statement."""
        # Get the top-level package name
        package_name = import_name.split('.')[0]
        
        # Skip built-in modules
        if self._is_builtin_module(package_name):
            return
        
        # Skip relative imports
        if package_name.startswith('.'):
            return
        
        # Skip local project modules
        if self._is_local_module(package_name):
            return
        
        # Map import to package name
        mapped_package = self._map_import_to_package(package_name)
        
        if mapped_package:
            self.usage_stats[mapped_package] += 1
            self.import_map[import_name] = mapped_package
    
    def _categorize_dependencies(self) -> None:
        """Categorize dependencies based on usage and purpose."""
        # Core dependencies (used in multiple files or critical functionality)
        core_packages = {
            'requests', 'urllib3', 'pathlib', 'typing', 'json', 'logging',
            'os', 'sys', 're', 'ast', 'hashlib', 'subprocess', 'tempfile',
            'collections', 'datetime', 'importlib'
        }
        
        # Development dependencies
        dev_packages = {
            'pytest', 'coverage', 'pytest-cov', 'black', 'isort', 'flake8',
            'pylint', 'mypy', 'bandit', 'safety', 'sphinx', 'mkdocs'
        }
        
        # Optional enhancement packages
        optional_packages = {
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'rich', 'colorama',
            'cryptography', 'pycryptodome', 'beautifulsoup4', 'lxml'
        }
        
        # Future planned packages
        future_packages = {
            'openai', 'anthropic', 'transformers', 'fastapi', 'uvicorn',
            'sqlalchemy', 'redis', 'websockets', 'mcp'
        }
        
        # Categorize based on usage and predefined categories
        for package, count in self.usage_stats.items():
            if package in core_packages or count >= 3:
                self.dependencies['core'].add(package)
            elif package in dev_packages:
                self.dependencies['development'].add(package)
            elif package in optional_packages:
                self.dependencies['optional'].add(package)
            elif package in future_packages:
                self.dependencies['future'].add(package)
            else:
                # Default to optional for unknown packages
                self.dependencies['optional'].add(package)
    
    def _update_main_requirements(self) -> None:
        """Update the main requirements.txt file."""
        requirements_path = self.project_path / 'requirements.txt'
        
        # Read current requirements
        current_content = ""
        if requirements_path.exists():
            with open(requirements_path, 'r') as f:
                current_content = f.read()
        
        # Extract version specifications from current file
        version_specs = self._extract_version_specs(current_content)
        
        # Generate new requirements content
        new_content = self._generate_requirements_content(
            self.dependencies['core'] | self.dependencies['optional'],
            version_specs,
            "Main Requirements"
        )
        
        # Write updated requirements
        with open(requirements_path, 'w') as f:
            f.write(new_content)
    
    def _update_dev_requirements(self) -> None:
        """Update the development requirements file."""
        dev_requirements_path = self.project_path / 'requirements-dev.txt'
        
        # Read current dev requirements
        current_content = ""
        if dev_requirements_path.exists():
            with open(dev_requirements_path, 'r') as f:
                current_content = f.read()
        
        # Extract version specifications
        version_specs = self._extract_version_specs(current_content)
        
        # Generate new dev requirements content
        new_content = self._generate_requirements_content(
            self.dependencies['development'],
            version_specs,
            "Development Requirements"
        )
        
        # Write updated dev requirements
        with open(dev_requirements_path, 'w') as f:
            f.write(new_content)
    
    def _extract_version_specs(self, content: str) -> Dict[str, str]:
        """Extract version specifications from requirements content."""
        version_specs = {}
        
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Parse package==version or package>=version
                match = re.match(r'([a-zA-Z0-9_-]+)([>=<!=]+.+)', line)
                if match:
                    package, version = match.groups()
                    version_specs[package] = version
        
        return version_specs
    
    def _generate_requirements_content(self, packages: Set[str], version_specs: Dict[str, str], title: str) -> str:
        """Generate requirements file content."""
        content = f"""# {title}
# {'=' * len(title)}
# Auto-generated by dependency-tracker.py
# Last updated: {self._get_timestamp()}

"""
        
        # Sort packages alphabetically
        sorted_packages = sorted(packages)
        
        for package in sorted_packages:
            if package in version_specs:
                content += f"{package}{version_specs[package]}\n"
            else:
                # Use default version specification
                default_version = self._get_default_version(package)
                content += f"{package}{default_version}\n"
        
        return content
    
    def _get_default_version(self, package: str) -> str:
        """Get default version specification for a package."""
        # Common version specifications
        default_versions = {
            'requests': '>=2.31.0',
            'urllib3': '>=2.0.0',
            'cryptography': '>=41.0.0',
            'pandas': '>=2.0.0',
            'numpy': '>=1.24.0',
            'pytest': '>=7.4.0',
            'coverage': '>=7.2.0',
            'black': '>=23.0.0',
            'isort': '>=5.12.0',
            'flake8': '>=6.0.0',
            'pylint': '>=2.17.0',
            'mypy': '>=1.4.0',
            'bandit': '>=1.7.5',
            'safety': '>=2.3.0'
        }
        
        return default_versions.get(package, '>=1.0.0')
    
    def _map_import_to_package(self, import_name: str) -> Optional[str]:
        """Map import name to package name."""
        # Common import to package mappings
        import_mappings = {
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'yaml': 'PyYAML',
            'bs4': 'beautifulsoup4',
            'sklearn': 'scikit-learn',
            'skimage': 'scikit-image',
            'dateutil': 'python-dateutil',
            'dotenv': 'python-dotenv',
            'jwt': 'PyJWT',
            'serial': 'pyserial',
            'psycopg2': 'psycopg2-binary',
            'MySQLdb': 'mysqlclient',
            'cx_Oracle': 'cx-Oracle'
        }
        
        return import_mappings.get(import_name, import_name)
    
    def _is_builtin_module(self, module_name: str) -> bool:
        """Check if module is a built-in Python module."""
        builtin_modules = {
            'os', 'sys', 'json', 're', 'ast', 'hashlib', 'subprocess',
            'tempfile', 'pathlib', 'typing', 'collections', 'logging',
            'datetime', 'importlib', 'itertools', 'functools', 'operator',
            'math', 'random', 'string', 'time', 'urllib', 'http', 'email',
            'xml', 'html', 'sqlite3', 'csv', 'configparser', 'argparse',
            'shutil', 'glob', 'fnmatch', 'pickle', 'copy', 'base64',
            'binascii', 'struct', 'array', 'queue', 'threading', 'multiprocessing',
            'concurrent', 'asyncio', 'socket', 'ssl', 'gzip', 'zipfile',
            'tarfile', 'io', 'contextlib', 'warnings', 'traceback', 'inspect',
            'unittest', 'doctest', 'pdb', 'profile', 'cProfile', 'timeit'
        }
        
        return module_name in builtin_modules
    
    def _is_local_module(self, module_name: str) -> bool:
        """Check if module is a local project module."""
        # Check if there's a corresponding .py file in the project
        potential_paths = [
            self.project_path / f"{module_name}.py",
            self.project_path / module_name / "__init__.py",
            self.project_path / "utilities" / f"{module_name}.py",
            self.project_path / "utilities" / f"{module_name.replace('_', '-')}.py"
        ]
        
        return any(path.exists() for path in potential_paths)
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during scanning."""
        skip_patterns = [
            '__pycache__', '.git', '.svn', 'node_modules', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', '.tox', 'build', 'dist'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate dependency management recommendations."""
        recommendations = []
        
        # Check for unused dependencies
        if len(self.dependencies['optional']) > 10:
            recommendations.append("Consider reviewing optional dependencies - you may have unused packages")
        
        # Check for missing core dependencies
        if len(self.dependencies['core']) < 5:
            recommendations.append("Ensure all core dependencies are properly categorized")
        
        # Check for development dependencies
        if len(self.dependencies['development']) < 3:
            recommendations.append("Consider adding more development tools (testing, linting, formatting)")
        
        # General recommendations
        recommendations.extend([
            "Regularly update dependencies to latest secure versions",
            "Use virtual environments for dependency isolation",
            "Pin dependency versions in production deployments",
            "Run security audits on dependencies regularly"
        ])
        
        return recommendations
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


# Utility functions
def scan_project_dependencies(project_path: str) -> Dict[str, any]:
    """Scan project for dependencies and generate report."""
    tracker = DependencyTracker(project_path)
    dependencies = tracker.scan_all_dependencies()
    report = tracker.generate_dependency_report()
    return report

def update_project_requirements(project_path: str) -> None:
    """Update project requirements files based on current usage."""
    tracker = DependencyTracker(project_path)
    tracker.scan_all_dependencies()
    tracker.update_requirements_files()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dependency-tracker.py <project_path> [--update]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    update_files = '--update' in sys.argv
    
    print(f"📦 Dependency Tracker")
    print(f"Scanning project: {project_path}")
    print("=" * 50)
    
    try:
        if update_files:
            print("🔄 Updating requirements files...")
            update_project_requirements(project_path)
            print("✅ Requirements files updated")
        else:
            print("📊 Generating dependency report...")
            report = scan_project_dependencies(project_path)
            
            # Print summary
            summary = report['summary']
            print(f"\n📈 Dependency Summary:")
            print(f"  Total Dependencies: {summary['total_dependencies']}")
            print(f"  Core: {summary['core_dependencies']}")
            print(f"  Optional: {summary['optional_dependencies']}")
            print(f"  Development: {summary['development_dependencies']}")
            
            # Print top used packages
            usage_stats = report['usage_statistics']
            if usage_stats:
                print(f"\n🔥 Most Used Packages:")
                for package, count in list(usage_stats.items())[:10]:
                    print(f"  {package}: {count} imports")
            
            # Print recommendations
            recommendations = report['recommendations']
            if recommendations:
                print(f"\n💡 Recommendations:")
                for rec in recommendations:
                    print(f"  - {rec}")
                    
    except Exception as e:
        print(f"❌ Dependency tracking failed: {e}")
        sys.exit(1)
