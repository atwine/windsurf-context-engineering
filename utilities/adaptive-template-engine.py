#!/usr/bin/env python3
"""
Adaptive Template Engine
Selects and customizes templates based on project analysis and requirements.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdaptiveTemplateEngine:
    """Adaptive template engine for context-aware template selection and customization."""
    
    def __init__(self, templates_dir: str = None):
        self.templates_dir = Path(templates_dir) if templates_dir else Path(__file__).parent.parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize template library
        self._init_template_library()
    
    def _init_template_library(self):
        """Initialize the template library structure."""
        self.template_categories = {
            'base': ['general_application', 'minimal_project'],
            'web': ['web_application_simple', 'web_application_complex', 'spa_application'],
            'api': ['rest_api_simple', 'rest_api_complex', 'graphql_api'],
            'cli': ['cli_tool_simple', 'cli_tool_complex'],
            'ml': ['ml_project_simple', 'ml_project_complex', 'data_science'],
            'mobile': ['mobile_app_simple', 'mobile_app_complex'],
            'desktop': ['desktop_app_simple', 'desktop_app_complex'],
            'data': ['data_processing_simple', 'data_processing_complex'],
            'game': ['game_simple', 'game_complex']
        }
        
        self.template_metadata = {
            'web_application_simple': {
                'description': 'Simple web application template',
                'complexity': 'simple',
                'technologies': ['python', 'flask', 'html', 'css'],
                'features': ['basic_routing', 'templates', 'static_files'],
                'suitable_for': ['prototypes', 'small_projects', 'learning']
            },
            'web_application_complex': {
                'description': 'Complex web application template',
                'complexity': 'complex',
                'technologies': ['python', 'django', 'postgresql', 'redis'],
                'features': ['authentication', 'database', 'api', 'admin_panel', 'caching'],
                'suitable_for': ['production', 'enterprise', 'scalable_apps']
            },
            'rest_api_simple': {
                'description': 'Simple REST API template',
                'complexity': 'simple',
                'technologies': ['python', 'fastapi', 'sqlite'],
                'features': ['crud_operations', 'basic_validation', 'documentation'],
                'suitable_for': ['microservices', 'prototypes', 'small_apis']
            },
            'ml_project_simple': {
                'description': 'Simple ML project template',
                'complexity': 'simple',
                'technologies': ['python', 'scikit-learn', 'pandas', 'jupyter'],
                'features': ['data_loading', 'model_training', 'evaluation'],
                'suitable_for': ['experiments', 'learning', 'proof_of_concept']
            }
        }
    
    def select_template(self, project_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Select the most appropriate template based on project analysis."""
        logger.info("Selecting template based on project analysis")
        
        # Extract key characteristics
        project_type = project_analysis.get('project_type', {}).get('primary', 'general_application')
        complexity = project_analysis.get('complexity_assessment', {}).get('level', 'medium')
        tech_stack = project_analysis.get('technology_stack', {})
        
        # Get template recommendations from analysis
        template_recs = project_analysis.get('template_recommendations', [])
        
        # Score templates based on analysis
        template_scores = self._score_templates(project_type, complexity, tech_stack, template_recs)
        
        # Select best template
        if template_scores:
            best_template = max(template_scores.items(), key=lambda x: x[1])
            selected_template = best_template[0]
            confidence = min(best_template[1] / 10, 1.0)
        else:
            selected_template = 'general_application_medium'
            confidence = 0.5
        
        return {
            'selected_template': selected_template,
            'confidence': confidence,
            'alternatives': sorted(template_scores.items(), key=lambda x: x[1], reverse=True)[1:3],
            'customizations': self._generate_customizations(project_analysis, selected_template)
        }
    
    def _score_templates(self, project_type: str, complexity: str, tech_stack: Dict, template_recs: List) -> Dict[str, float]:
        """Score templates based on project characteristics."""
        scores = {}
        
        # Base scoring from project type
        type_mapping = {
            'web_application': ['web_application_simple', 'web_application_complex'],
            'api_service': ['rest_api_simple', 'rest_api_complex', 'graphql_api'],
            'cli_tool': ['cli_tool_simple', 'cli_tool_complex'],
            'ml_ai_project': ['ml_project_simple', 'ml_project_complex'],
            'mobile_app': ['mobile_app_simple', 'mobile_app_complex'],
            'desktop_app': ['desktop_app_simple', 'desktop_app_complex'],
            'data_processing': ['data_processing_simple', 'data_processing_complex'],
            'game': ['game_simple', 'game_complex']
        }
        
        matching_templates = type_mapping.get(project_type, ['general_application'])
        for template in matching_templates:
            scores[template] = 5.0
        
        # Adjust for complexity
        complexity_suffix = f"_{complexity}" if complexity != 'medium' else ''
        for template in list(scores.keys()):
            if complexity in template or (complexity == 'simple' and 'simple' in template):
                scores[template] += 3.0
            elif complexity == 'complex' and 'complex' in template:
                scores[template] += 3.0
        
        # Boost from template recommendations
        for rec in template_recs:
            template_name = rec['template']
            if template_name in scores:
                scores[template_name] += 2.0
            else:
                scores[template_name] = 2.0
        
        return scores
    
    def _generate_customizations(self, project_analysis: Dict[str, Any], template_name: str) -> Dict[str, Any]:
        """Generate template customizations based on project analysis."""
        customizations = {
            'variables': {},
            'features': [],
            'dependencies': [],
            'structure_modifications': []
        }
        
        # Extract project info
        project_type = project_analysis.get('project_type', {})
        tech_stack = project_analysis.get('technology_stack', {})
        complexity = project_analysis.get('complexity_assessment', {})
        
        # Basic variables
        customizations['variables'] = {
            'project_name': 'my_project',
            'project_type': project_type.get('primary', 'application'),
            'complexity_level': complexity.get('level', 'medium'),
            'primary_language': self._get_primary_language(tech_stack),
            'estimated_team_size': self._estimate_team_size(complexity.get('level', 'medium'))
        }
        
        # Feature customizations
        if 'prompt_analysis' in project_analysis:
            features = project_analysis['prompt_analysis'].get('estimated_features', [])
            customizations['features'] = features
        
        # Technology-specific customizations
        detected_tech = tech_stack.get('detected_technologies', {})
        for tech, tech_info in detected_tech.items():
            if tech_info['confidence'] > 0.7:
                customizations['dependencies'].append(tech)
                
                # Add framework-specific features
                for framework_info in tech_info.get('frameworks', []):
                    if framework_info['confidence'] > 0.7:
                        customizations['dependencies'].append(framework_info['name'])
        
        return customizations
    
    def generate_template_content(self, template_selection: Dict[str, Any], project_prompt: str = None) -> Dict[str, str]:
        """Generate actual template content based on selection and customizations."""
        template_name = template_selection['selected_template']
        customizations = template_selection['customizations']
        
        # Generate different template files
        template_files = {}
        
        # Generate README
        template_files['README.md'] = self._generate_readme(template_name, customizations, project_prompt)
        
        # Generate project structure
        template_files['project_structure.md'] = self._generate_project_structure(template_name, customizations)
        
        # Generate implementation plan
        template_files['implementation_plan.md'] = self._generate_implementation_plan(template_name, customizations)
        
        # Generate requirements/dependencies
        template_files['requirements.txt'] = self._generate_requirements(customizations)
        
        # Generate basic code templates
        if 'python' in customizations.get('dependencies', []):
            template_files['main.py'] = self._generate_python_main(customizations)
        
        return template_files
    
    def _generate_readme(self, template_name: str, customizations: Dict, project_prompt: str = None) -> str:
        """Generate README template."""
        variables = customizations.get('variables', {})
        features = customizations.get('features', [])
        
        readme_content = f"""# {variables.get('project_name', 'My Project').replace('_', ' ').title()}

## Description
{project_prompt or f"A {variables.get('project_type', 'application')} project with {variables.get('complexity_level', 'medium')} complexity."}

## Features
"""
        
        if features:
            for feature in features:
                readme_content += f"- {feature.replace('_', ' ').title()}\n"
        else:
            readme_content += "- Core functionality\n- User interface\n- Data management\n"
        
        readme_content += f"""
## Technology Stack
- **Primary Language**: {variables.get('primary_language', 'Python')}
- **Template**: {template_name}
- **Complexity**: {variables.get('complexity_level', 'Medium')}

## Getting Started

### Prerequisites
- {variables.get('primary_language', 'Python')} 3.8+
- pip (Python package manager)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd {variables.get('project_name', 'my-project')}

# Install dependencies
pip install -r requirements.txt
```

### Usage
```bash
# Run the application
python main.py
```

## Project Structure
See `project_structure.md` for detailed project organization.

## Implementation Plan
See `implementation_plan.md` for development roadmap.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This project is licensed under the MIT License.
"""
        
        return readme_content
    
    def _generate_project_structure(self, template_name: str, customizations: Dict) -> str:
        """Generate project structure template."""
        variables = customizations.get('variables', {})
        complexity = variables.get('complexity_level', 'medium')
        
        if complexity == 'simple':
            structure = """# Project Structure

```
my_project/
├── main.py                 # Main application entry point
├── requirements.txt        # Project dependencies
├── README.md              # Project documentation
├── config.py              # Configuration settings
├── utils.py               # Utility functions
└── tests/                 # Test files
    └── test_main.py
```

## Directory Descriptions

- **main.py**: Entry point for the application
- **config.py**: Configuration and settings
- **utils.py**: Shared utility functions
- **tests/**: Unit tests and test utilities
"""
        elif complexity == 'medium':
            structure = """# Project Structure

```
my_project/
├── src/                   # Source code
│   ├── __init__.py
│   ├── main.py           # Main application
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   └── config/           # Configuration
├── tests/                # Test files
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/                 # Documentation
├── requirements.txt      # Dependencies
├── setup.py             # Package setup
└── README.md            # Project documentation
```
"""
        else:  # complex/enterprise
            structure = """# Project Structure

```
my_project/
├── src/                   # Source code
│   ├── api/              # API layer
│   ├── core/             # Core business logic
│   ├── models/           # Data models
│   ├── services/         # Service layer
│   ├── repositories/     # Data access layer
│   ├── utils/            # Utilities
│   └── config/           # Configuration
├── tests/                # Test suite
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
├── docs/                 # Documentation
├── scripts/              # Build/deployment scripts
├── docker/               # Docker configuration
├── migrations/           # Database migrations
├── requirements/         # Environment-specific requirements
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .github/              # GitHub workflows
├── docker-compose.yml    # Docker services
└── README.md            # Project documentation
```
"""
        
        return structure
    
    def _generate_implementation_plan(self, template_name: str, customizations: Dict) -> str:
        """Generate implementation plan template."""
        variables = customizations.get('variables', {})
        features = customizations.get('features', [])
        complexity = variables.get('complexity_level', 'medium')
        
        plan = f"""# Implementation Plan

## Project Overview
- **Template**: {template_name}
- **Complexity**: {complexity}
- **Estimated Team Size**: {variables.get('estimated_team_size', '1-2 developers')}

## Development Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up project structure
- [ ] Configure development environment
- [ ] Implement basic configuration
- [ ] Set up testing framework
- [ ] Create initial documentation

### Phase 2: Core Features (Week 2-3)
"""
        
        if features:
            for i, feature in enumerate(features[:5], 1):
                plan += f"- [ ] Implement {feature.replace('_', ' ')}\n"
        else:
            plan += """- [ ] Implement core functionality
- [ ] Add data models
- [ ] Create main business logic
- [ ] Implement user interface
"""
        
        plan += """
### Phase 3: Integration & Testing (Week 4)
- [ ] Integration testing
- [ ] Performance optimization
- [ ] Security review
- [ ] Documentation completion
- [ ] Deployment preparation

### Phase 4: Deployment & Monitoring (Week 5)
- [ ] Production deployment
- [ ] Monitoring setup
- [ ] User acceptance testing
- [ ] Performance monitoring
- [ ] Bug fixes and improvements

## Quality Gates
- [ ] Code review for each feature
- [ ] Unit test coverage > 80%
- [ ] Integration tests passing
- [ ] Security scan clean
- [ ] Performance benchmarks met

## Risk Mitigation
- Regular code reviews
- Continuous integration
- Automated testing
- Documentation updates
- Regular stakeholder communication
"""
        
        return plan
    
    def _generate_requirements(self, customizations: Dict) -> str:
        """Generate requirements.txt template."""
        dependencies = customizations.get('dependencies', [])
        
        # Base requirements
        requirements = ["# Core dependencies\n"]
        
        # Add technology-specific requirements
        if 'python' in dependencies:
            requirements.append("# Python core packages are built-in\n")
        
        if 'flask' in dependencies:
            requirements.extend([
                "flask>=2.3.0\n",
                "werkzeug>=2.3.0\n"
            ])
        
        if 'django' in dependencies:
            requirements.extend([
                "django>=4.2.0\n",
                "psycopg2-binary>=2.9.0\n"
            ])
        
        if 'fastapi' in dependencies:
            requirements.extend([
                "fastapi>=0.100.0\n",
                "uvicorn>=0.22.0\n",
                "pydantic>=2.0.0\n"
            ])
        
        if 'pandas' in dependencies:
            requirements.extend([
                "pandas>=2.0.0\n",
                "numpy>=1.24.0\n"
            ])
        
        if 'scikit-learn' in dependencies:
            requirements.extend([
                "scikit-learn>=1.3.0\n",
                "matplotlib>=3.7.0\n",
                "seaborn>=0.12.0\n"
            ])
        
        # Add common development dependencies
        requirements.extend([
            "\n# Development dependencies\n",
            "pytest>=7.4.0\n",
            "black>=23.0.0\n",
            "flake8>=6.0.0\n"
        ])
        
        return "".join(requirements)
    
    def _generate_python_main(self, customizations: Dict) -> str:
        """Generate main.py template."""
        variables = customizations.get('variables', {})
        project_name = variables.get('project_name', 'my_project')
        
        main_content = f'''#!/usr/bin/env python3
"""
{project_name.replace('_', ' ').title()}
Main application entry point.
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main application function."""
    logger.info("Starting {project_name.replace('_', ' ')}")
    
    # TODO: Implement main application logic
    print("Hello, World!")
    
    logger.info("Application completed successfully")

if __name__ == "__main__":
    main()
'''
        
        return main_content
    
    def _get_primary_language(self, tech_stack: Dict) -> str:
        """Get primary programming language from tech stack."""
        detected_tech = tech_stack.get('detected_technologies', {})
        
        if detected_tech:
            primary_tech = max(detected_tech.items(), key=lambda x: x[1]['confidence'])
            return primary_tech[0].title()
        
        return 'Python'
    
    def _estimate_team_size(self, complexity: str) -> str:
        """Estimate team size based on complexity."""
        team_sizes = {
            'simple': '1 developer',
            'medium': '1-2 developers',
            'complex': '2-4 developers',
            'enterprise': '4+ developers'
        }
        
        return team_sizes.get(complexity, '1-2 developers')


# Utility functions
def select_adaptive_template(project_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Select adaptive template based on project analysis."""
    engine = AdaptiveTemplateEngine()
    return engine.select_template(project_analysis)

def generate_project_templates(project_analysis: Dict[str, Any], project_prompt: str = None) -> Dict[str, str]:
    """Generate complete project templates."""
    engine = AdaptiveTemplateEngine()
    template_selection = engine.select_template(project_analysis)
    return engine.generate_template_content(template_selection, project_prompt)

if __name__ == "__main__":
    import sys
    
    print("🎯 Adaptive Template Engine")
    print("=" * 50)
    
    # Example usage
    example_analysis = {
        'project_type': {'primary': 'web_application', 'confidence': 0.8},
        'complexity_assessment': {'level': 'medium', 'score': 2.5},
        'technology_stack': {
            'detected_technologies': {
                'python': {'confidence': 0.9, 'frameworks': [{'name': 'flask', 'confidence': 0.8}]}
            }
        },
        'template_recommendations': [
            {'template': 'web_application_medium', 'priority': 'primary', 'reason': 'Best match'}
        ]
    }
    
    try:
        engine = AdaptiveTemplateEngine()
        
        # Select template
        selection = engine.select_template(example_analysis)
        print(f"Selected Template: {selection['selected_template']}")
        print(f"Confidence: {selection['confidence']:.2f}")
        
        # Generate template content
        templates = engine.generate_template_content(selection, "A web application for task management")
        
        print(f"\nGenerated Templates:")
        for filename, content in templates.items():
            print(f"  - {filename} ({len(content)} characters)")
            
    except Exception as e:
        print(f"❌ Template generation failed: {e}")
        sys.exit(1)
