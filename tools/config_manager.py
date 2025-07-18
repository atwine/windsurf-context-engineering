#!/usr/bin/env python3
"""
Configuration Manager
====================

Manages tool configurations across the development ecosystem:
- Configuration templates and validation
- Configuration synchronization
- Configuration versioning
- Migration tools
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigurationManager:
    """Manages development tool configurations."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.config_history = []
        
    def detect_existing_configs(self) -> Dict[str, List[str]]:
        """Detect existing configuration files."""
        config_files = {
            'linting': [],
            'testing': [],
            'build': [],
            'deployment': [],
            'development': []
        }
        
        # Linting configs
        linting_files = [
            '.eslintrc.json', '.eslintrc.js', '.eslintrc.yml',
            '.prettierrc.json', '.prettierrc.js',
            '.pylintrc', '.flake8', 'pyproject.toml'
        ]
        
        for file in linting_files:
            if (self.project_root / file).exists():
                config_files['linting'].append(file)
        
        # Testing configs
        testing_files = [
            'jest.config.js', 'cypress.config.js',
            'pytest.ini', 'tox.ini'
        ]
        
        for file in testing_files:
            if (self.project_root / file).exists():
                config_files['testing'].append(file)
        
        # Build configs
        build_files = [
            'webpack.config.js', 'vite.config.js',
            'tsconfig.json', 'babel.config.js'
        ]
        
        for file in build_files:
            if (self.project_root / file).exists():
                config_files['build'].append(file)
        
        # Deployment configs
        deploy_files = [
            'Dockerfile', 'docker-compose.yml',
            'vercel.json', 'netlify.toml',
            '.github/workflows', '.gitlab-ci.yml'
        ]
        
        for file in deploy_files:
            if (self.project_root / file).exists():
                config_files['deployment'].append(file)
        
        # Development configs
        dev_files = [
            '.vscode/settings.json', '.env.example',
            'package.json', 'requirements.txt'
        ]
        
        for file in dev_files:
            if (self.project_root / file).exists():
                config_files['development'].append(file)
        
        return config_files
    
    def validate_configuration(self, config_type: str, config_file: str) -> Tuple[bool, List[str]]:
        """Validate configuration file."""
        config_path = self.project_root / config_file
        
        if not config_path.exists():
            return False, [f"Configuration file {config_file} does not exist"]
        
        errors = []
        
        try:
            if config_type == 'eslint':
                errors.extend(self._validate_eslint_config(config_path))
            elif config_type == 'prettier':
                errors.extend(self._validate_prettier_config(config_path))
            elif config_type == 'jest':
                errors.extend(self._validate_jest_config(config_path))
            elif config_type == 'package_json':
                errors.extend(self._validate_package_json(config_path))
            elif config_type == 'docker':
                errors.extend(self._validate_dockerfile(config_path))
            
        except Exception as e:
            errors.append(f"Failed to validate {config_file}: {str(e)}")
        
        return len(errors) == 0, errors
    
    def _validate_eslint_config(self, config_path: Path) -> List[str]:
        """Validate ESLint configuration."""
        errors = []
        
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            # Check required fields
            if 'extends' not in config:
                errors.append("ESLint config missing 'extends' field")
            
            if 'rules' not in config:
                errors.append("ESLint config missing 'rules' field")
            
            # Check for common issues
            if 'env' not in config:
                errors.append("ESLint config should specify 'env' for better compatibility")
            
        except json.JSONDecodeError:
            errors.append("ESLint config is not valid JSON")
        
        return errors
    
    def _validate_prettier_config(self, config_path: Path) -> List[str]:
        """Validate Prettier configuration."""
        errors = []
        
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            # Check for conflicting settings
            if config.get('useTabs') and config.get('tabWidth'):
                errors.append("Prettier config has conflicting tab settings")
            
            # Check print width
            if config.get('printWidth', 80) > 120:
                errors.append("Prettier printWidth should be <= 120 for better readability")
            
        except json.JSONDecodeError:
            errors.append("Prettier config is not valid JSON")
        
        return errors
    
    def _validate_jest_config(self, config_path: Path) -> List[str]:
        """Validate Jest configuration."""
        errors = []
        
        try:
            # Handle both .js and .json files
            if config_path.suffix == '.js':
                # For .js files, we can't easily parse without executing
                # Just check if file exists and is readable
                content = config_path.read_text()
                if 'module.exports' not in content:
                    errors.append("Jest config file should export configuration")
            else:
                with open(config_path) as f:
                    config = json.load(f)
                
                # Check coverage thresholds
                if 'coverageThreshold' in config:
                    thresholds = config['coverageThreshold'].get('global', {})
                    for metric, value in thresholds.items():
                        if value < 70:
                            errors.append(f"Coverage threshold for {metric} is below 70%")
        
        except (json.JSONDecodeError, Exception) as e:
            errors.append(f"Jest config validation failed: {str(e)}")
        
        return errors
    
    def _validate_package_json(self, config_path: Path) -> List[str]:
        """Validate package.json."""
        errors = []
        
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            # Check required fields
            required_fields = ['name', 'version']
            for field in required_fields:
                if field not in config:
                    errors.append(f"package.json missing required field: {field}")
            
            # Check scripts
            if 'scripts' in config:
                scripts = config['scripts']
                recommended_scripts = ['test', 'build', 'lint']
                for script in recommended_scripts:
                    if script not in scripts:
                        errors.append(f"package.json missing recommended script: {script}")
            
            # Check for security vulnerabilities in dependencies
            if 'dependencies' in config:
                # This is a simplified check - in practice, you'd use npm audit
                deps = config['dependencies']
                if any('*' in version for version in deps.values()):
                    errors.append("Avoid using '*' in dependency versions")
        
        except json.JSONDecodeError:
            errors.append("package.json is not valid JSON")
        
        return errors
    
    def _validate_dockerfile(self, config_path: Path) -> List[str]:
        """Validate Dockerfile."""
        errors = []
        
        try:
            content = config_path.read_text()
            lines = content.split('\n')
            
            # Check for FROM instruction
            if not any(line.strip().startswith('FROM') for line in lines):
                errors.append("Dockerfile missing FROM instruction")
            
            # Check for WORKDIR
            if not any(line.strip().startswith('WORKDIR') for line in lines):
                errors.append("Dockerfile should specify WORKDIR")
            
            # Check for EXPOSE
            if not any(line.strip().startswith('EXPOSE') for line in lines):
                errors.append("Dockerfile should specify EXPOSE port")
            
            # Check for security best practices
            if any('ADD' in line for line in lines):
                errors.append("Consider using COPY instead of ADD for better security")
            
        except Exception as e:
            errors.append(f"Dockerfile validation failed: {str(e)}")
        
        return errors
    
    def sync_configurations(self, source_config: str, target_configs: List[str]) -> Dict[str, Any]:
        """Synchronize configuration settings across files."""
        sync_results = {
            'source': source_config,
            'targets': target_configs,
            'changes_made': [],
            'errors': []
        }
        
        try:
            # Example: Sync ESLint and Prettier settings
            if source_config == '.eslintrc.json' and '.prettierrc.json' in target_configs:
                self._sync_eslint_prettier()
                sync_results['changes_made'].append('Synchronized ESLint and Prettier quote styles')
            
            # Example: Sync package.json scripts with CI/CD
            if source_config == 'package.json' and any('.github' in target for target in target_configs):
                self._sync_package_json_github_actions()
                sync_results['changes_made'].append('Synchronized package.json scripts with GitHub Actions')
            
        except Exception as e:
            sync_results['errors'].append(str(e))
        
        return sync_results
    
    def _sync_eslint_prettier(self):
        """Sync ESLint and Prettier quote style settings."""
        eslint_path = self.project_root / '.eslintrc.json'
        prettier_path = self.project_root / '.prettierrc.json'
        
        if eslint_path.exists() and prettier_path.exists():
            with open(eslint_path) as f:
                eslint_config = json.load(f)
            
            with open(prettier_path) as f:
                prettier_config = json.load(f)
            
            # Sync quote styles
            if 'rules' in eslint_config and 'quotes' in eslint_config['rules']:
                quote_style = eslint_config['rules']['quotes'][1]  # 'single' or 'double'
                prettier_config['singleQuote'] = quote_style == 'single'
                
                with open(prettier_path, 'w') as f:
                    json.dump(prettier_config, f, indent=2)
    
    def _sync_package_json_github_actions(self):
        """Sync package.json scripts with GitHub Actions."""
        package_path = self.project_root / 'package.json'
        github_dir = self.project_root / '.github' / 'workflows'
        
        if package_path.exists() and github_dir.exists():
            with open(package_path) as f:
                package_data = json.load(f)
            
            scripts = package_data.get('scripts', {})
            
            # Update GitHub Actions workflows to use available scripts
            for workflow_file in github_dir.glob('*.yml'):
                content = workflow_file.read_text()
                
                # Replace generic commands with package.json scripts
                if 'npm test' in content and 'test' in scripts:
                    content = content.replace('npm test', 'npm run test')
                
                if 'npm run build' in content and 'build' in scripts:
                    # Already correct
                    pass
                
                workflow_file.write_text(content)
    
    def create_config_backup(self) -> str:
        """Create backup of all configuration files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.project_root / f'.config_backup_{timestamp}'
        backup_dir.mkdir(exist_ok=True)
        
        config_files = self.detect_existing_configs()
        
        for category, files in config_files.items():
            category_dir = backup_dir / category
            category_dir.mkdir(exist_ok=True)
            
            for file in files:
                source_path = self.project_root / file
                if source_path.exists():
                    if source_path.is_file():
                        target_path = category_dir / source_path.name
                        target_path.write_text(source_path.read_text())
                    elif source_path.is_dir():
                        # Handle directories like .github/workflows
                        import shutil
                        shutil.copytree(source_path, category_dir / source_path.name)
        
        logger.info(f"Configuration backup created: {backup_dir}")
        return str(backup_dir)
    
    def migrate_configurations(self, migration_type: str) -> Dict[str, Any]:
        """Migrate configurations between different versions or formats."""
        migration_results = {
            'type': migration_type,
            'changes_made': [],
            'errors': []
        }
        
        try:
            if migration_type == 'eslint_v8_to_v9':
                self._migrate_eslint_v8_to_v9()
                migration_results['changes_made'].append('Migrated ESLint from v8 to v9')
            
            elif migration_type == 'jest_v28_to_v29':
                self._migrate_jest_v28_to_v29()
                migration_results['changes_made'].append('Migrated Jest from v28 to v29')
            
            elif migration_type == 'prettier_v2_to_v3':
                self._migrate_prettier_v2_to_v3()
                migration_results['changes_made'].append('Migrated Prettier from v2 to v3')
            
        except Exception as e:
            migration_results['errors'].append(str(e))
        
        return migration_results
    
    def _migrate_eslint_v8_to_v9(self):
        """Migrate ESLint configuration from v8 to v9."""
        eslint_path = self.project_root / '.eslintrc.json'
        
        if eslint_path.exists():
            with open(eslint_path) as f:
                config = json.load(f)
            
            # Update deprecated rules
            if 'rules' in config:
                rules = config['rules']
                
                # Example migration: update deprecated rules
                if 'no-return-await' in rules:
                    rules['@typescript-eslint/return-await'] = rules.pop('no-return-await')
            
            with open(eslint_path, 'w') as f:
                json.dump(config, f, indent=2)
    
    def _migrate_jest_v28_to_v29(self):
        """Migrate Jest configuration from v28 to v29."""
        jest_path = self.project_root / 'jest.config.js'
        
        if jest_path.exists():
            content = jest_path.read_text()
            
            # Update deprecated options
            content = content.replace('clearMocks: true', 'restoreMocks: true')
            
            jest_path.write_text(content)
    
    def _migrate_prettier_v2_to_v3(self):
        """Migrate Prettier configuration from v2 to v3."""
        prettier_path = self.project_root / '.prettierrc.json'
        
        if prettier_path.exists():
            with open(prettier_path) as f:
                config = json.load(f)
            
            # Update deprecated options
            if 'trailingComma' in config and config['trailingComma'] == 'es5':
                config['trailingComma'] = 'all'
            
            with open(prettier_path, 'w') as f:
                json.dump(config, f, indent=2)
    
    def generate_config_report(self) -> Dict[str, Any]:
        """Generate comprehensive configuration report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'existing_configs': self.detect_existing_configs(),
            'validation_results': {},
            'recommendations': []
        }
        
        # Validate all configurations
        for category, files in report['existing_configs'].items():
            for file in files:
                config_type = self._get_config_type(file)
                is_valid, errors = self.validate_configuration(config_type, file)
                
                report['validation_results'][file] = {
                    'valid': is_valid,
                    'errors': errors
                }
        
        # Generate recommendations
        report['recommendations'] = self._generate_config_recommendations(report)
        
        return report
    
    def _get_config_type(self, filename: str) -> str:
        """Get configuration type from filename."""
        if 'eslint' in filename:
            return 'eslint'
        elif 'prettier' in filename:
            return 'prettier'
        elif 'jest' in filename:
            return 'jest'
        elif filename == 'package.json':
            return 'package_json'
        elif filename == 'Dockerfile':
            return 'docker'
        else:
            return 'unknown'
    
    def _generate_config_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate configuration recommendations."""
        recommendations = []
        
        # Check for missing configurations
        existing_files = []
        for files in report['existing_configs'].values():
            existing_files.extend(files)
        
        if 'package.json' in existing_files and '.eslintrc.json' not in existing_files:
            recommendations.append("Consider adding ESLint configuration for code quality")
        
        if '.eslintrc.json' in existing_files and '.prettierrc.json' not in existing_files:
            recommendations.append("Add Prettier configuration for consistent formatting")
        
        # Check validation results
        for file, result in report['validation_results'].items():
            if not result['valid']:
                recommendations.append(f"Fix validation errors in {file}")
        
        return recommendations

# Example usage
if __name__ == "__main__":
    config_manager = ConfigurationManager()
    
    # Generate configuration report
    report = config_manager.generate_config_report()
    print(f"Configuration report: {json.dumps(report, indent=2)}")
    
    # Create backup
    backup_path = config_manager.create_config_backup()
    print(f"Backup created: {backup_path}")
