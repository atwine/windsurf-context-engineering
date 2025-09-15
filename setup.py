#!/usr/bin/env python3
"""
Setup script for Windsurf Context Engineering Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    requirements_path = Path(__file__).parent / filename
    if requirements_path.exists():
        with open(requirements_path, 'r') as f:
            lines = f.readlines()
        
        # Filter out comments and empty lines
        requirements = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove inline comments
                if '#' in line:
                    line = line.split('#')[0].strip()
                requirements.append(line)
        
        return requirements
    return []

# Core requirements
install_requires = read_requirements("requirements.txt")

# Development requirements
dev_requires = read_requirements("requirements-dev.txt")

setup(
    name="windsurf-context-engineering",
    version="1.0.0",
    author="Windsurf Team",
    author_email="team@windsurf.ai",
    description="Enhanced context engineering framework for AI-assisted software development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atwine/windsurf-context-engineering",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        "all": install_requires + dev_requires,
    },
    entry_points={
        "console_scripts": [
            "windsurf-context=utilities.dependency_tracker:main",
            "windsurf-security=utilities.security_scanner:main",
            "windsurf-quality=utilities.code_quality_analyzer:main",
            "windsurf-coverage=utilities.test_coverage_validator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
        "workflows": ["*.md"],
        "templates": ["*.md", "*.txt"],
        "examples": ["*.md", "*.py"],
    },
    project_urls={
        "Bug Reports": "https://github.com/atwine/windsurf-context-engineering/issues",
        "Source": "https://github.com/atwine/windsurf-context-engineering",
        "Documentation": "https://windsurf-context-engineering.readthedocs.io/",
    },
)
