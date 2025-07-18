#!/usr/bin/env python3
"""
Development Environment Setup
============================

Creates development environment configurations:
- VS Code settings and extensions
- Docker development environments
- Environment variable templates
- Development server configurations
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DevEnvironmentSetup:
    """Manages development environment configuration."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        
    def create_vscode_config(self, languages: List[str]) -> Dict[str, str]:
        """Create VS Code configuration."""
        vscode_dir = self.project_root / '.vscode'
        vscode_dir.mkdir(exist_ok=True)
        
        files_created = {}
        
        # Settings
        settings = self._generate_vscode_settings(languages)
        settings_path = vscode_dir / 'settings.json'
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        files_created['settings.json'] = str(settings_path)
        
        # Extensions
        extensions = self._generate_vscode_extensions(languages)
        extensions_path = vscode_dir / 'extensions.json'
        with open(extensions_path, 'w') as f:
            json.dump(extensions, f, indent=2)
        files_created['extensions.json'] = str(extensions_path)
        
        # Launch configuration
        launch = self._generate_vscode_launch(languages)
        launch_path = vscode_dir / 'launch.json'
        with open(launch_path, 'w') as f:
            json.dump(launch, f, indent=2)
        files_created['launch.json'] = str(launch_path)
        
        # Tasks
        tasks = self._generate_vscode_tasks(languages)
        tasks_path = vscode_dir / 'tasks.json'
        with open(tasks_path, 'w') as f:
            json.dump(tasks, f, indent=2)
        files_created['tasks.json'] = str(tasks_path)
        
        logger.info(f"Created VS Code configuration: {list(files_created.keys())}")
        return files_created
    
    def _generate_vscode_settings(self, languages: List[str]) -> Dict[str, Any]:
        """Generate VS Code settings."""
        settings = {
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.fixAll.eslint": True
            },
            "files.exclude": {
                "**/node_modules": True,
                "**/.git": True,
                "**/.DS_Store": True,
                "**/coverage": True,
                "**/__pycache__": True,
                "**/*.pyc": True
            }
        }
        
        # JavaScript/TypeScript settings
        if 'javascript' in languages or 'typescript' in languages:
            settings.update({
                "javascript.preferences.quoteStyle": "single",
                "typescript.preferences.quoteStyle": "single",
                "eslint.validate": ["javascript", "javascriptreact", "typescript", "typescriptreact"],
                "prettier.singleQuote": True,
                "prettier.semi": True
            })
        
        # Python settings
        if 'python' in languages:
            settings.update({
                "python.defaultInterpreterPath": "./venv/bin/python",
                "python.linting.enabled": True,
                "python.linting.pylintEnabled": True,
                "python.linting.flake8Enabled": True,
                "python.formatting.provider": "black",
                "python.testing.pytestEnabled": True
            })
        
        return settings
    
    def _generate_vscode_extensions(self, languages: List[str]) -> Dict[str, List[str]]:
        """Generate VS Code extensions recommendations."""
        extensions = [
            "ms-vscode.vscode-json",
            "redhat.vscode-yaml",
            "ms-vscode.vscode-eslint",
            "esbenp.prettier-vscode",
            "bradlc.vscode-tailwindcss"
        ]
        
        # JavaScript/TypeScript extensions
        if 'javascript' in languages or 'typescript' in languages:
            extensions.extend([
                "ms-vscode.vscode-typescript-next",
                "dbaeumer.vscode-eslint",
                "esbenp.prettier-vscode",
                "ms-vscode.vscode-jest"
            ])
        
        # Python extensions
        if 'python' in languages:
            extensions.extend([
                "ms-python.python",
                "ms-python.flake8",
                "ms-python.black-formatter",
                "ms-python.pylint"
            ])
        
        # React extensions
        if self._has_react():
            extensions.extend([
                "ms-vscode.vscode-react-native",
                "formulahendry.auto-rename-tag",
                "bradlc.vscode-tailwindcss"
            ])
        
        return {"recommendations": extensions}
    
    def _generate_vscode_launch(self, languages: List[str]) -> Dict[str, Any]:
        """Generate VS Code launch configuration."""
        configurations = []
        
        # Node.js configuration
        if 'javascript' in languages:
            configurations.append({
                "name": "Launch Node.js",
                "type": "node",
                "request": "launch",
                "program": "${workspaceFolder}/src/index.js",
                "console": "integratedTerminal"
            })
        
        # Python configuration
        if 'python' in languages:
            configurations.append({
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal"
            })
        
        return {
            "version": "0.2.0",
            "configurations": configurations
        }
    
    def _generate_vscode_tasks(self, languages: List[str]) -> Dict[str, Any]:
        """Generate VS Code tasks."""
        tasks = []
        
        # JavaScript/TypeScript tasks
        if 'javascript' in languages or 'typescript' in languages:
            tasks.extend([
                {
                    "label": "npm: install",
                    "type": "npm",
                    "script": "install",
                    "group": "build"
                },
                {
                    "label": "npm: test",
                    "type": "npm",
                    "script": "test",
                    "group": "test"
                },
                {
                    "label": "npm: build",
                    "type": "npm",
                    "script": "build",
                    "group": "build"
                }
            ])
        
        # Python tasks
        if 'python' in languages:
            tasks.extend([
                {
                    "label": "Python: Run Tests",
                    "type": "shell",
                    "command": "pytest",
                    "group": "test",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    }
                }
            ])
        
        return {
            "version": "2.0.0",
            "tasks": tasks
        }
    
    def create_env_templates(self) -> Dict[str, str]:
        """Create environment variable templates."""
        files_created = {}
        
        # .env.example
        env_example = """
# Application Configuration
NODE_ENV=development
PORT=3000
API_URL=http://localhost:3000/api

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET=your-secret-key-here
SESSION_SECRET=your-session-secret-here

# External Services
STRIPE_SECRET_KEY=sk_test_...
SENDGRID_API_KEY=SG...
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# Monitoring
SENTRY_DSN=https://...
LOG_LEVEL=info
"""
        
        env_path = self.project_root / '.env.example'
        with open(env_path, 'w') as f:
            f.write(env_example.strip())
        files_created['.env.example'] = str(env_path)
        
        # .env.local (for local development)
        env_local = """
# Local Development Environment
NODE_ENV=development
DEBUG=true
VERBOSE_LOGGING=true

# Local Database
DATABASE_URL=postgresql://localhost:5432/myapp_dev

# Disable external services in development
DISABLE_EMAILS=true
MOCK_PAYMENTS=true
"""
        
        env_local_path = self.project_root / '.env.local'
        with open(env_local_path, 'w') as f:
            f.write(env_local.strip())
        files_created['.env.local'] = str(env_local_path)
        
        logger.info(f"Created environment templates: {list(files_created.keys())}")
        return files_created
    
    def create_dev_scripts(self, languages: List[str]) -> Dict[str, str]:
        """Create development scripts."""
        scripts_dir = self.project_root / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        files_created = {}
        
        # Setup script
        setup_script = self._generate_setup_script(languages)
        setup_path = scripts_dir / 'setup.sh'
        with open(setup_path, 'w') as f:
            f.write(setup_script)
        files_created['setup.sh'] = str(setup_path)
        
        # Development server script
        dev_script = self._generate_dev_script(languages)
        dev_path = scripts_dir / 'dev.sh'
        with open(dev_path, 'w') as f:
            f.write(dev_script)
        files_created['dev.sh'] = str(dev_path)
        
        # Test script
        test_script = self._generate_test_script(languages)
        test_path = scripts_dir / 'test.sh'
        with open(test_path, 'w') as f:
            f.write(test_script)
        files_created['test.sh'] = str(test_path)
        
        logger.info(f"Created development scripts: {list(files_created.keys())}")
        return files_created
    
    def _generate_setup_script(self, languages: List[str]) -> str:
        """Generate setup script."""
        script = "#!/bin/bash\nset -e\n\n"
        script += "echo 'Setting up development environment...'\n\n"
        
        if 'node' in languages:
            script += """
# Node.js setup
if command -v node &> /dev/null; then
    echo "Node.js is installed"
    node --version
else
    echo "Please install Node.js"
    exit 1
fi

echo "Installing npm dependencies..."
npm install

echo "Setting up pre-commit hooks..."
npm install -g pre-commit
pre-commit install
"""
        
        if 'python' in languages:
            script += """
# Python setup
if command -v python3 &> /dev/null; then
    echo "Python is installed"
    python3 --version
else
    echo "Please install Python 3"
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt
"""
        
        script += """
echo "Copying environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please update .env with your configuration"
fi

echo "Setup complete! Run ./scripts/dev.sh to start development server"
"""
        
        return script
    
    def _generate_dev_script(self, languages: List[str]) -> str:
        """Generate development server script."""
        script = "#!/bin/bash\n\n"
        script += "echo 'Starting development server...'\n\n"
        
        if 'node' in languages:
            script += """
# Start Node.js development server
if [ -f package.json ]; then
    npm run dev
fi
"""
        
        if 'python' in languages:
            script += """
# Start Python development server
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

if [ -f app.py ]; then
    python app.py
elif [ -f manage.py ]; then
    python manage.py runserver
fi
"""
        
        return script
    
    def _generate_test_script(self, languages: List[str]) -> str:
        """Generate test script."""
        script = "#!/bin/bash\n\n"
        script += "echo 'Running tests...'\n\n"
        
        if 'node' in languages:
            script += """
# Run JavaScript tests
npm test
"""
        
        if 'python' in languages:
            script += """
# Run Python tests
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

pytest --cov=src --cov-report=html
"""
        
        return script
    
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
        return False
    
    def setup_dev_environment(self, languages: List[str]) -> Dict[str, Any]:
        """Set up complete development environment."""
        setup_results = {
            'languages': languages,
            'files_created': [],
            'recommendations': []
        }
        
        try:
            # VS Code configuration
            vscode_files = self.create_vscode_config(languages)
            setup_results['files_created'].extend(vscode_files.values())
            
            # Environment templates
            env_files = self.create_env_templates()
            setup_results['files_created'].extend(env_files.values())
            
            # Development scripts
            script_files = self.create_dev_scripts(languages)
            setup_results['files_created'].extend(script_files.values())
            
            # Add recommendations
            setup_results['recommendations'] = [
                "Install recommended VS Code extensions",
                "Update .env file with your configuration",
                "Run ./scripts/setup.sh to initialize development environment",
                "Use ./scripts/dev.sh to start development server"
            ]
            
        except Exception as e:
            logger.error(f"Dev environment setup failed: {e}")
            setup_results['error'] = str(e)
        
        return setup_results

# Example usage
if __name__ == "__main__":
    dev_env = DevEnvironmentSetup()
    
    # Set up development environment
    languages = ['javascript', 'python']
    setup_results = dev_env.setup_dev_environment(languages)
    print(f"Dev environment setup: {setup_results}")
