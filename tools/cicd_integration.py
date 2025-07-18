#!/usr/bin/env python3
"""
CI/CD Pipeline Integration
==========================

Creates CI/CD pipeline configurations for popular platforms:
- GitHub Actions
- GitLab CI
- Docker deployment
- AWS deployment
- Vercel deployment
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class CICDIntegration:
    """Manages CI/CD pipeline generation and configuration."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.pipeline_configs = {}
        
    def detect_deployment_needs(self) -> Dict[str, Any]:
        """Detect deployment requirements based on project structure."""
        needs = {
            'platform': 'web',  # web, api, desktop, mobile
            'runtime': [],       # node, python, docker
            'database': None,    # postgres, mysql, mongodb
            'static_assets': False,
            'environment_vars': [],
            'deployment_targets': []
        }
        
        # Detect runtime
        if (self.project_root / 'package.json').exists():
            needs['runtime'].append('node')
        if (self.project_root / 'requirements.txt').exists():
            needs['runtime'].append('python')
        if (self.project_root / 'Dockerfile').exists():
            needs['runtime'].append('docker')
        
        # Detect platform type
        if (self.project_root / 'public').exists():
            needs['platform'] = 'web'
            needs['static_assets'] = True
        elif any((self.project_root / 'src').rglob('*.py')):
            needs['platform'] = 'api'
        
        # Suggest deployment targets
        if 'node' in needs['runtime'] and needs['static_assets']:
            needs['deployment_targets'].extend(['vercel', 'netlify'])
        if 'python' in needs['runtime']:
            needs['deployment_targets'].extend(['heroku', 'aws'])
        if 'docker' in needs['runtime']:
            needs['deployment_targets'].extend(['aws', 'gcp', 'azure'])
        
        return needs
    
    def create_github_actions(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Create GitHub Actions workflow."""
        workflows = {}
        
        # Main CI workflow
        ci_workflow = self._create_github_ci_workflow(config)
        workflows['ci.yml'] = ci_workflow
        
        # Deployment workflow
        if config.get('deployment_targets'):
            deploy_workflow = self._create_github_deploy_workflow(config)
            workflows['deploy.yml'] = deploy_workflow
        
        # Create .github/workflows directory
        workflows_dir = self.project_root / '.github' / 'workflows'
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Write workflow files
        created_files = []
        for filename, content in workflows.items():
            file_path = workflows_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)
            created_files.append(str(file_path))
            logger.info(f"Created GitHub Actions workflow: {file_path}")
        
        return {
            'workflows_created': created_files,
            'directory': str(workflows_dir)
        }
    
    def _create_github_ci_workflow(self, config: Dict[str, Any]) -> str:
        """Create GitHub Actions CI workflow."""
        workflow = {
            'name': 'CI',
            'on': {
                'push': {
                    'branches': ['main', 'develop']
                },
                'pull_request': {
                    'branches': ['main']
                }
            },
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v4'
                        }
                    ]
                }
            }
        }
        
        # Add Node.js steps
        if 'node' in config.get('runtime', []):
            workflow['jobs']['test']['steps'].extend([
                {
                    'name': 'Setup Node.js',
                    'uses': 'actions/setup-node@v4',
                    'with': {
                        'node-version': '18',
                        'cache': 'npm'
                    }
                },
                {
                    'name': 'Install dependencies',
                    'run': 'npm ci'
                },
                {
                    'name': 'Run linting',
                    'run': 'npm run lint'
                },
                {
                    'name': 'Run tests',
                    'run': 'npm test'
                },
                {
                    'name': 'Build project',
                    'run': 'npm run build'
                }
            ])
        
        # Add Python steps
        if 'python' in config.get('runtime', []):
            workflow['jobs']['test']['steps'].extend([
                {
                    'name': 'Setup Python',
                    'uses': 'actions/setup-python@v4',
                    'with': {
                        'python-version': '3.9'
                    }
                },
                {
                    'name': 'Install dependencies',
                    'run': 'pip install -r requirements.txt'
                },
                {
                    'name': 'Run linting',
                    'run': 'flake8 .'
                },
                {
                    'name': 'Run tests',
                    'run': 'pytest --cov=src'
                }
            ])
        
        return yaml.dump(workflow, default_flow_style=False)
    
    def _create_github_deploy_workflow(self, config: Dict[str, Any]) -> str:
        """Create GitHub Actions deployment workflow."""
        workflow = {
            'name': 'Deploy',
            'on': {
                'push': {
                    'branches': ['main']
                }
            },
            'jobs': {
                'deploy': {
                    'runs-on': 'ubuntu-latest',
                    'needs': 'test',
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v4'
                        }
                    ]
                }
            }
        }
        
        # Add deployment steps based on targets
        deployment_targets = config.get('deployment_targets', [])
        
        if 'vercel' in deployment_targets:
            workflow['jobs']['deploy']['steps'].extend([
                {
                    'name': 'Deploy to Vercel',
                    'uses': 'amondnet/vercel-action@v25',
                    'with': {
                        'vercel-token': '${{ secrets.VERCEL_TOKEN }}',
                        'vercel-org-id': '${{ secrets.ORG_ID }}',
                        'vercel-project-id': '${{ secrets.PROJECT_ID }}',
                        'vercel-args': '--prod'
                    }
                }
            ])
        
        if 'aws' in deployment_targets:
            workflow['jobs']['deploy']['steps'].extend([
                {
                    'name': 'Configure AWS credentials',
                    'uses': 'aws-actions/configure-aws-credentials@v4',
                    'with': {
                        'aws-access-key-id': '${{ secrets.AWS_ACCESS_KEY_ID }}',
                        'aws-secret-access-key': '${{ secrets.AWS_SECRET_ACCESS_KEY }}',
                        'aws-region': 'us-east-1'
                    }
                },
                {
                    'name': 'Deploy to AWS',
                    'run': 'aws s3 sync ./build s3://${{ secrets.S3_BUCKET }}'
                }
            ])
        
        return yaml.dump(workflow, default_flow_style=False)
    
    def create_gitlab_ci(self, config: Dict[str, Any]) -> str:
        """Create GitLab CI configuration."""
        gitlab_ci = {
            'stages': ['test', 'build', 'deploy'],
            'variables': {
                'NODE_VERSION': '18',
                'PYTHON_VERSION': '3.9'
            }
        }
        
        # Test stage
        if 'node' in config.get('runtime', []):
            gitlab_ci['test:node'] = {
                'stage': 'test',
                'image': 'node:18',
                'script': [
                    'npm ci',
                    'npm run lint',
                    'npm test',
                    'npm run build'
                ],
                'artifacts': {
                    'paths': ['build/'],
                    'expire_in': '1 hour'
                }
            }
        
        if 'python' in config.get('runtime', []):
            gitlab_ci['test:python'] = {
                'stage': 'test',
                'image': 'python:3.9',
                'script': [
                    'pip install -r requirements.txt',
                    'flake8 .',
                    'pytest --cov=src'
                ]
            }
        
        # Deploy stage
        if 'vercel' in config.get('deployment_targets', []):
            gitlab_ci['deploy:vercel'] = {
                'stage': 'deploy',
                'image': 'node:18',
                'script': [
                    'npm install -g vercel',
                    'vercel --token $VERCEL_TOKEN --prod'
                ],
                'only': ['main']
            }
        
        # Write .gitlab-ci.yml
        config_path = self.project_root / '.gitlab-ci.yml'
        with open(config_path, 'w') as f:
            yaml.dump(gitlab_ci, f, default_flow_style=False)
        
        logger.info(f"Created GitLab CI configuration: {config_path}")
        return str(config_path)
    
    def create_docker_config(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Create Docker configuration files."""
        files_created = {}
        
        # Create Dockerfile
        dockerfile_content = self._generate_dockerfile(config)
        dockerfile_path = self.project_root / 'Dockerfile'
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        files_created['Dockerfile'] = str(dockerfile_path)
        
        # Create .dockerignore
        dockerignore_content = """
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.nyc_output
coverage
.coverage
__pycache__
*.pyc
.pytest_cache
"""
        
        dockerignore_path = self.project_root / '.dockerignore'
        with open(dockerignore_path, 'w') as f:
            f.write(dockerignore_content.strip())
        files_created['.dockerignore'] = str(dockerignore_path)
        
        # Create docker-compose.yml for development
        if config.get('database'):
            compose_content = self._generate_docker_compose(config)
            compose_path = self.project_root / 'docker-compose.yml'
            with open(compose_path, 'w') as f:
                f.write(compose_content)
            files_created['docker-compose.yml'] = str(compose_path)
        
        logger.info(f"Created Docker configuration files: {list(files_created.keys())}")
        return files_created
    
    def _generate_dockerfile(self, config: Dict[str, Any]) -> str:
        """Generate Dockerfile based on project configuration."""
        if 'node' in config.get('runtime', []):
            return """
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
"""
        elif 'python' in config.get('runtime', []):
            return """
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
"""
        else:
            return """
FROM alpine:latest

WORKDIR /app
COPY . .

EXPOSE 8080

CMD ["echo", "Configure your application"]
"""
    
    def _generate_docker_compose(self, config: Dict[str, Any]) -> str:
        """Generate docker-compose.yml for development."""
        compose = {
            'version': '3.8',
            'services': {
                'app': {
                    'build': '.',
                    'ports': ['3000:3000'],
                    'environment': [
                        'NODE_ENV=development'
                    ],
                    'volumes': [
                        '.:/app',
                        '/app/node_modules'
                    ]
                }
            }
        }
        
        # Add database service if needed
        database = config.get('database')
        if database == 'postgres':
            compose['services']['db'] = {
                'image': 'postgres:15',
                'environment': [
                    'POSTGRES_DB=myapp',
                    'POSTGRES_USER=user',
                    'POSTGRES_PASSWORD=password'
                ],
                'ports': ['5432:5432'],
                'volumes': ['postgres_data:/var/lib/postgresql/data']
            }
            compose['volumes'] = {'postgres_data': None}
        
        elif database == 'mysql':
            compose['services']['db'] = {
                'image': 'mysql:8',
                'environment': [
                    'MYSQL_DATABASE=myapp',
                    'MYSQL_USER=user',
                    'MYSQL_PASSWORD=password',
                    'MYSQL_ROOT_PASSWORD=rootpassword'
                ],
                'ports': ['3306:3306'],
                'volumes': ['mysql_data:/var/lib/mysql']
            }
            compose['volumes'] = {'mysql_data': None}
        
        return yaml.dump(compose, default_flow_style=False)
    
    def create_deployment_scripts(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Create deployment scripts for various platforms."""
        scripts = {}
        
        # Vercel deployment
        if 'vercel' in config.get('deployment_targets', []):
            vercel_config = {
                "version": 2,
                "builds": [
                    {
                        "src": "package.json",
                        "use": "@vercel/static-build",
                        "config": {
                            "distDir": "build"
                        }
                    }
                ],
                "routes": [
                    {
                        "src": "/(.*)",
                        "dest": "/$1"
                    }
                ]
            }
            
            vercel_path = self.project_root / 'vercel.json'
            with open(vercel_path, 'w') as f:
                json.dump(vercel_config, f, indent=2)
            scripts['vercel.json'] = str(vercel_path)
        
        # AWS deployment script
        if 'aws' in config.get('deployment_targets', []):
            aws_script = """#!/bin/bash
set -e

echo "Building application..."
npm run build

echo "Deploying to AWS S3..."
aws s3 sync ./build s3://$S3_BUCKET --delete

echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"

echo "Deployment complete!"
"""
            
            aws_path = self.project_root / 'deploy-aws.sh'
            with open(aws_path, 'w') as f:
                f.write(aws_script.strip())
            scripts['deploy-aws.sh'] = str(aws_path)
        
        logger.info(f"Created deployment scripts: {list(scripts.keys())}")
        return scripts
    
    def setup_cicd_for_project(self, platform: str = 'github') -> Dict[str, Any]:
        """Set up complete CI/CD pipeline for the project."""
        config = self.detect_deployment_needs()
        
        setup_results = {
            'platform': platform,
            'config': config,
            'files_created': [],
            'recommendations': []
        }
        
        try:
            if platform == 'github':
                github_files = self.create_github_actions(config)
                setup_results['files_created'].extend(github_files['workflows_created'])
            
            elif platform == 'gitlab':
                gitlab_file = self.create_gitlab_ci(config)
                setup_results['files_created'].append(gitlab_file)
            
            # Create Docker configuration
            docker_files = self.create_docker_config(config)
            setup_results['files_created'].extend(docker_files.values())
            
            # Create deployment scripts
            deploy_scripts = self.create_deployment_scripts(config)
            setup_results['files_created'].extend(deploy_scripts.values())
            
            # Add recommendations
            setup_results['recommendations'] = self._generate_recommendations(config)
            
        except Exception as e:
            logger.error(f"CI/CD setup failed: {e}")
            setup_results['error'] = str(e)
        
        return setup_results
    
    def _generate_recommendations(self, config: Dict[str, Any]) -> List[str]:
        """Generate setup recommendations."""
        recommendations = []
        
        if 'node' in config.get('runtime', []):
            recommendations.append("Set up Node.js version in .nvmrc file")
            recommendations.append("Configure npm scripts for build and test")
        
        if 'python' in config.get('runtime', []):
            recommendations.append("Pin Python version in runtime.txt or Dockerfile")
            recommendations.append("Use virtual environments for dependency isolation")
        
        if config.get('deployment_targets'):
            recommendations.append("Set up environment variables and secrets in CI/CD platform")
            recommendations.append("Configure deployment environments (staging, production)")
        
        if config.get('database'):
            recommendations.append("Set up database migrations in CI/CD pipeline")
            recommendations.append("Configure database connection strings as environment variables")
        
        return recommendations

# Example usage
if __name__ == "__main__":
    cicd = CICDIntegration()
    
    # Detect deployment needs
    needs = cicd.detect_deployment_needs()
    print(f"Deployment needs: {needs}")
    
    # Set up CI/CD
    setup_results = cicd.setup_cicd_for_project('github')
    print(f"CI/CD setup results: {setup_results}")
