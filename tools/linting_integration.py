#!/usr/bin/env python3
"""
Linting Tool Integration
=======================

Integrates popular linting and formatting tools for consistent code quality:
- ESLint for JavaScript/TypeScript
- Prettier for code formatting
- Black for Python formatting
- Pylint for Python linting
- Custom rule sets and configurations
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class LintingIntegration:
    """Manages integration with linting and formatting tools."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.supported_tools = {
            'eslint': self._setup_eslint,
            'prettier': self._setup_prettier,
            'black': self._setup_black,
            'pylint': self._setup_pylint,
            'flake8': self._setup_flake8
        }
        
        # Tool configurations
        self.tool_configs = {}
        
    def detect_project_languages(self) -> List[str]:
        """Detect programming languages used in the project."""
        languages = []
        
        # Check for JavaScript/TypeScript
        js_patterns = ['*.js', '*.jsx', '*.ts', '*.tsx', '*.vue']
        for pattern in js_patterns:
            if list(self.project_root.rglob(pattern)):
                if 'javascript' not in languages:
                    languages.append('javascript')
                break
        
        # Check for TypeScript specifically
        ts_patterns = ['*.ts', '*.tsx', 'tsconfig.json']
        for pattern in ts_patterns:
            if list(self.project_root.rglob(pattern)):
                if 'typescript' not in languages:
                    languages.append('typescript')
                break
        
        # Check for Python
        py_patterns = ['*.py', 'requirements.txt', 'setup.py', 'pyproject.toml']
        for pattern in py_patterns:
            if list(self.project_root.rglob(pattern)):
                if 'python' not in languages:
                    languages.append('python')
                break
        
        # Check for other languages
        if list(self.project_root.rglob('*.java')):
            languages.append('java')
        if list(self.project_root.rglob('*.go')):
            languages.append('go')
        if list(self.project_root.rglob('*.rs')):
            languages.append('rust')
        
        return languages
    
    def setup_linting_for_project(self, languages: Optional[List[str]] = None) -> Dict[str, Any]:
        """Set up linting tools for the detected or specified languages."""
        if languages is None:
            languages = self.detect_project_languages()
        
        setup_results = {
            'languages_detected': languages,
            'tools_configured': [],
            'configurations_created': [],
            'errors': []
        }
        
        logger.info(f"Setting up linting for languages: {languages}")
        
        # JavaScript/TypeScript tools
        if 'javascript' in languages or 'typescript' in languages:
            try:
                eslint_config = self._setup_eslint(languages)
                prettier_config = self._setup_prettier()
                
                setup_results['tools_configured'].extend(['eslint', 'prettier'])
                setup_results['configurations_created'].extend([
                    '.eslintrc.json', '.prettierrc.json', '.prettierignore'
                ])
                
                self.tool_configs['eslint'] = eslint_config
                self.tool_configs['prettier'] = prettier_config
                
            except Exception as e:
                setup_results['errors'].append(f"JavaScript/TypeScript setup failed: {e}")
        
        # Python tools
        if 'python' in languages:
            try:
                black_config = self._setup_black()
                pylint_config = self._setup_pylint()
                flake8_config = self._setup_flake8()
                
                setup_results['tools_configured'].extend(['black', 'pylint', 'flake8'])
                setup_results['configurations_created'].extend([
                    'pyproject.toml', '.pylintrc', '.flake8'
                ])
                
                self.tool_configs['black'] = black_config
                self.tool_configs['pylint'] = pylint_config
                self.tool_configs['flake8'] = flake8_config
                
            except Exception as e:
                setup_results['errors'].append(f"Python setup failed: {e}")
        
        # Create package.json scripts for JavaScript projects
        if 'javascript' in languages or 'typescript' in languages:
            self._create_npm_scripts(languages)
            setup_results['configurations_created'].append('package.json (scripts)')
        
        # Create pre-commit hooks
        self._create_precommit_hooks(languages)
        setup_results['configurations_created'].append('.pre-commit-config.yaml')
        
        return setup_results
    
    def _setup_eslint(self, languages: List[str]) -> Dict[str, Any]:
        """Set up ESLint configuration."""
        config = {
            "env": {
                "browser": True,
                "es2021": True,
                "node": True
            },
            "extends": [
                "eslint:recommended"
            ],
            "parserOptions": {
                "ecmaVersion": 12,
                "sourceType": "module"
            },
            "rules": {
                "indent": ["error", 2],
                "linebreak-style": ["error", "unix"],
                "quotes": ["error", "single"],
                "semi": ["error", "always"],
                "no-unused-vars": "warn",
                "no-console": "warn"
            }
        }
        
        # TypeScript specific configuration
        if 'typescript' in languages:
            config["extends"].extend([
                "@typescript-eslint/recommended"
            ])
            config["parser"] = "@typescript-eslint/parser"
            config["plugins"] = ["@typescript-eslint"]
            config["rules"]["@typescript-eslint/no-unused-vars"] = "warn"
        
        # React specific configuration
        if self._has_react():
            config["extends"].extend([
                "plugin:react/recommended",
                "plugin:react-hooks/recommended"
            ])
            config["plugins"] = config.get("plugins", []) + ["react", "react-hooks"]
            config["settings"] = {
                "react": {
                    "version": "detect"
                }
            }
        
        # Write configuration file
        config_path = self.project_root / '.eslintrc.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"ESLint configuration created: {config_path}")
        return config
    
    def _setup_prettier(self) -> Dict[str, Any]:
        """Set up Prettier configuration."""
        config = {
            "semi": True,
            "trailingComma": "es5",
            "singleQuote": True,
            "printWidth": 80,
            "tabWidth": 2,
            "useTabs": False
        }
        
        # Write configuration file
        config_path = self.project_root / '.prettierrc.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create .prettierignore
        ignore_content = """
# Dependencies
node_modules/
dist/
build/

# Logs
*.log

# Runtime data
pids
*.pid
*.seed

# Coverage directory used by tools like istanbul
coverage/

# Generated files
*.min.js
*.min.css
"""
        
        ignore_path = self.project_root / '.prettierignore'
        with open(ignore_path, 'w') as f:
            f.write(ignore_content.strip())
        
        logger.info(f"Prettier configuration created: {config_path}")
        return config
    
    def _setup_black(self) -> Dict[str, Any]:
        """Set up Black configuration."""
        config = {
            "line-length": 88,
            "target-version": ["py38"],
            "include": "\\.pyi?$",
            "exclude": """
            /(
                \\.eggs
              | \\.git
              | \\.hg
              | \\.mypy_cache
              | \\.tox
              | \\.venv
              | _build
              | buck-out
              | build
              | dist
            )/
            """
        }
        
        # Add to pyproject.toml
        pyproject_path = self.project_root / 'pyproject.toml'
        pyproject_content = f"""
[tool.black]
line-length = 88
target-version = ['py38']
include = '\\.pyi?$'
exclude = '''
/(
    \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
"""
        
        if pyproject_path.exists():
            # Append to existing file
            with open(pyproject_path, 'a') as f:
                f.write(pyproject_content)
        else:
            # Create new file
            with open(pyproject_path, 'w') as f:
                f.write(pyproject_content.strip())
        
        logger.info(f"Black configuration added to: {pyproject_path}")
        return config
    
    def _setup_pylint(self) -> Dict[str, Any]:
        """Set up Pylint configuration."""
        config_content = """
[MASTER]
init-hook='import sys; sys.path.append(".")'

[MESSAGES CONTROL]
disable=C0114,C0115,C0116,R0903,R0913,W0613

[FORMAT]
max-line-length=88
indent-string='    '

[DESIGN]
max-args=7
max-locals=15
max-returns=6
max-branches=12
max-statements=50
max-parents=7
max-attributes=7
min-public-methods=2
max-public-methods=20

[SIMILARITIES]
min-similarity-lines=4
ignore-comments=yes
ignore-docstrings=yes
ignore-imports=no
"""
        
        config_path = self.project_root / '.pylintrc'
        with open(config_path, 'w') as f:
            f.write(config_content.strip())
        
        logger.info(f"Pylint configuration created: {config_path}")
        return {"config_file": str(config_path)}
    
    def _setup_flake8(self) -> Dict[str, Any]:
        """Set up Flake8 configuration."""
        config_content = """
[flake8]
max-line-length = 88
extend-ignore = E203, E266, E501, W503
max-complexity = 10
select = B,C,E,F,W,T4,B9
"""
        
        config_path = self.project_root / '.flake8'
        with open(config_path, 'w') as f:
            f.write(config_content.strip())
        
        logger.info(f"Flake8 configuration created: {config_path}")
        return {"config_file": str(config_path)}
    
    def _has_react(self) -> bool:
        """Check if project uses React."""
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    return 'react' in deps
            except:
                pass
        
        # Check for React files
        react_patterns = ['*.jsx', '*.tsx']
        for pattern in react_patterns:
            if list(self.project_root.rglob(pattern)):
                return True
        
        return False
    
    def _create_npm_scripts(self, languages: List[str]):
        """Create or update npm scripts for linting."""
        package_json_path = self.project_root / 'package.json'
        
        scripts = {
            "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
            "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix",
            "format": "prettier --write .",
            "format:check": "prettier --check ."
        }
        
        if package_json_path.exists():
            with open(package_json_path) as f:
                package_data = json.load(f)
        else:
            package_data = {
                "name": self.project_root.name,
                "version": "1.0.0",
                "description": "",
                "main": "index.js"
            }
        
        # Update scripts
        if 'scripts' not in package_data:
            package_data['scripts'] = {}
        
        package_data['scripts'].update(scripts)
        
        # Add dev dependencies
        if 'devDependencies' not in package_data:
            package_data['devDependencies'] = {}
        
        dev_deps = {
            "eslint": "^8.0.0",
            "prettier": "^3.0.0"
        }
        
        if 'typescript' in languages:
            dev_deps.update({
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0"
            })
        
        if self._has_react():
            dev_deps.update({
                "eslint-plugin-react": "^7.33.0",
                "eslint-plugin-react-hooks": "^4.6.0"
            })
        
        package_data['devDependencies'].update(dev_deps)
        
        # Write updated package.json
        with open(package_json_path, 'w') as f:
            json.dump(package_data, f, indent=2)
        
        logger.info(f"Updated package.json with linting scripts: {package_json_path}")
    
    def _create_precommit_hooks(self, languages: List[str]):
        """Create pre-commit hooks configuration."""
        hooks = []
        
        # JavaScript/TypeScript hooks
        if 'javascript' in languages or 'typescript' in languages:
            hooks.extend([
                {
                    "repo": "https://github.com/pre-commit/mirrors-eslint",
                    "rev": "v8.56.0",
                    "hooks": [
                        {
                            "id": "eslint",
                            "files": "\\.(js|jsx|ts|tsx)$",
                            "types": ["file"]
                        }
                    ]
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v3.1.0",
                    "hooks": [
                        {
                            "id": "prettier",
                            "files": "\\.(js|jsx|ts|tsx|json|css|md)$"
                        }
                    ]
                }
            ])
        
        # Python hooks
        if 'python' in languages:
            hooks.extend([
                {
                    "repo": "https://github.com/psf/black",
                    "rev": "23.12.1",
                    "hooks": [
                        {
                            "id": "black",
                            "language_version": "python3"
                        }
                    ]
                },
                {
                    "repo": "https://github.com/pycqa/flake8",
                    "rev": "7.0.0",
                    "hooks": [
                        {
                            "id": "flake8"
                        }
                    ]
                }
            ])
        
        config = {
            "repos": hooks
        }
        
        config_path = self.project_root / '.pre-commit-config.yaml'
        import yaml
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Pre-commit hooks configuration created: {config_path}")
    
    def run_linting(self, tool: str, fix: bool = False) -> Tuple[bool, str]:
        """Run specific linting tool."""
        try:
            if tool == 'eslint':
                cmd = ['npx', 'eslint', '.', '--ext', '.js,.jsx,.ts,.tsx']
                if fix:
                    cmd.append('--fix')
            elif tool == 'prettier':
                cmd = ['npx', 'prettier', '--write' if fix else '--check', '.']
            elif tool == 'black':
                cmd = ['black', '.' if fix else '--check', '.']
            elif tool == 'pylint':
                cmd = ['pylint', '**/*.py']
            elif tool == 'flake8':
                cmd = ['flake8', '.']
            else:
                return False, f"Unknown tool: {tool}"
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0, result.stdout + result.stderr
            
        except Exception as e:
            return False, str(e)
    
    def get_linting_report(self) -> Dict[str, Any]:
        """Generate comprehensive linting report."""
        languages = self.detect_project_languages()
        report = {
            'languages': languages,
            'tools': {},
            'overall_status': 'unknown',
            'issues_found': 0,
            'recommendations': []
        }
        
        # Run applicable tools
        tools_to_run = []
        if 'javascript' in languages or 'typescript' in languages:
            tools_to_run.extend(['eslint', 'prettier'])
        if 'python' in languages:
            tools_to_run.extend(['black', 'flake8'])
        
        issues_count = 0
        for tool in tools_to_run:
            success, output = self.run_linting(tool, fix=False)
            report['tools'][tool] = {
                'status': 'passed' if success else 'failed',
                'output': output
            }
            if not success:
                issues_count += output.count('\n') if output else 1
        
        report['issues_found'] = issues_count
        report['overall_status'] = 'passed' if issues_count == 0 else 'failed'
        
        # Add recommendations
        if issues_count > 0:
            report['recommendations'] = [
                "Run linting tools with --fix flag to auto-fix issues",
                "Review and update linting configurations as needed",
                "Consider adding pre-commit hooks to prevent issues"
            ]
        
        return report

# Example usage
if __name__ == "__main__":
    linting = LintingIntegration()
    
    # Detect languages and set up linting
    languages = linting.detect_project_languages()
    print(f"Detected languages: {languages}")
    
    # Set up linting tools
    setup_results = linting.setup_linting_for_project(languages)
    print(f"Setup results: {setup_results}")
    
    # Generate linting report
    report = linting.get_linting_report()
    print(f"Linting report: {report}")
