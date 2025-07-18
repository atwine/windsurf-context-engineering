#!/usr/bin/env python3
"""
Project Type Detector
Analyzes project characteristics to determine type, domain, complexity, and appropriate templates.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectTypeDetector:
    """Detects project type, domain, and complexity characteristics."""
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.analysis_results = {
            'project_type': {},
            'technology_stack': {},
            'domain_classification': {},
            'complexity_assessment': {},
            'template_recommendations': []
        }
        
        # Initialize detection patterns
        self._init_detection_patterns()
    
    def analyze_project(self, project_prompt: str = None) -> Dict[str, any]:
        """Perform comprehensive project analysis."""
        logger.info(f"Analyzing project: {self.project_path}")
        
        # Analyze existing codebase (if any)
        if self.project_path.exists():
            self._analyze_existing_codebase()
        
        # Analyze project prompt
        if project_prompt:
            self._analyze_project_prompt(project_prompt)
        
        # Determine project type
        self._classify_project_type()
        
        # Assess complexity
        self._assess_complexity()
        
        # Generate template recommendations
        self._generate_template_recommendations()
        
        return self.analysis_results
    
    def _init_detection_patterns(self):
        """Initialize patterns for project type detection."""
        
        # Technology stack indicators
        self.tech_patterns = {
            'python': {
                'files': ['*.py', 'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
                'frameworks': {
                    'django': ['django', 'manage.py', 'settings.py', 'urls.py'],
                    'flask': ['flask', 'app.py', 'application.py'],
                    'fastapi': ['fastapi', 'main.py', 'uvicorn'],
                    'streamlit': ['streamlit', 'st.'],
                    'pytorch': ['torch', 'pytorch', 'model.py'],
                    'tensorflow': ['tensorflow', 'tf.', 'keras'],
                    'pandas': ['pandas', 'pd.', 'dataframe'],
                    'numpy': ['numpy', 'np.', 'array']
                }
            },
            'javascript': {
                'files': ['*.js', '*.ts', 'package.json', 'yarn.lock', 'package-lock.json'],
                'frameworks': {
                    'react': ['react', 'jsx', 'tsx', 'create-react-app'],
                    'vue': ['vue', 'vue.js', 'nuxt'],
                    'angular': ['angular', '@angular', 'ng'],
                    'node': ['node', 'express', 'npm', 'yarn'],
                    'next': ['next.js', 'next', 'pages/'],
                    'svelte': ['svelte', 'sveltekit']
                }
            },
            'java': {
                'files': ['*.java', 'pom.xml', 'build.gradle', 'gradle.properties'],
                'frameworks': {
                    'spring': ['spring', 'springframework', '@RestController'],
                    'android': ['android', 'MainActivity', 'AndroidManifest.xml'],
                    'maven': ['pom.xml', 'mvn'],
                    'gradle': ['build.gradle', 'gradle']
                }
            },
            'csharp': {
                'files': ['*.cs', '*.csproj', '*.sln', 'Program.cs'],
                'frameworks': {
                    'dotnet': ['.net', 'dotnet', 'Program.cs'],
                    'aspnet': ['asp.net', 'Controllers/', 'Views/'],
                    'unity': ['unity', 'MonoBehaviour', 'GameObject']
                }
            },
            'go': {
                'files': ['*.go', 'go.mod', 'go.sum'],
                'frameworks': {
                    'gin': ['gin', 'gin-gonic'],
                    'echo': ['echo', 'labstack'],
                    'fiber': ['fiber', 'gofiber']
                }
            },
            'rust': {
                'files': ['*.rs', 'Cargo.toml', 'Cargo.lock'],
                'frameworks': {
                    'actix': ['actix', 'actix-web'],
                    'rocket': ['rocket', 'rocket.rs'],
                    'warp': ['warp', 'tokio']
                }
            }
        }
        
        # Project type indicators
        self.project_type_patterns = {
            'web_application': {
                'keywords': ['web', 'website', 'webapp', 'frontend', 'backend', 'fullstack'],
                'files': ['index.html', 'app.py', 'server.js', 'main.py'],
                'frameworks': ['django', 'flask', 'react', 'vue', 'angular', 'express']
            },
            'api_service': {
                'keywords': ['api', 'rest', 'graphql', 'microservice', 'service', 'endpoint'],
                'files': ['api.py', 'routes.py', 'controllers/', 'endpoints/'],
                'frameworks': ['fastapi', 'flask', 'express', 'spring', 'gin']
            },
            'cli_tool': {
                'keywords': ['cli', 'command', 'tool', 'script', 'automation'],
                'files': ['cli.py', 'main.py', 'bin/', 'scripts/'],
                'frameworks': ['click', 'argparse', 'typer', 'commander']
            },
            'ml_ai_project': {
                'keywords': ['machine learning', 'ai', 'model', 'neural', 'deep learning', 'data science'],
                'files': ['model.py', 'train.py', 'predict.py', 'notebook.ipynb'],
                'frameworks': ['tensorflow', 'pytorch', 'scikit-learn', 'keras']
            },
            'mobile_app': {
                'keywords': ['mobile', 'app', 'ios', 'android', 'react native', 'flutter'],
                'files': ['MainActivity.java', 'AppDelegate.swift', 'pubspec.yaml'],
                'frameworks': ['react-native', 'flutter', 'ionic', 'xamarin']
            },
            'desktop_app': {
                'keywords': ['desktop', 'gui', 'application', 'window'],
                'files': ['main.py', 'app.py', 'MainWindow.xaml'],
                'frameworks': ['tkinter', 'pyqt', 'electron', 'wpf']
            },
            'data_processing': {
                'keywords': ['data', 'etl', 'pipeline', 'processing', 'analytics'],
                'files': ['pipeline.py', 'etl.py', 'process.py'],
                'frameworks': ['pandas', 'spark', 'airflow', 'dask']
            },
            'game': {
                'keywords': ['game', 'gaming', 'unity', 'unreal', 'pygame'],
                'files': ['Game.cs', 'main.py', 'game.py'],
                'frameworks': ['unity', 'pygame', 'godot', 'unreal']
            }
        }
        
        # Domain classification patterns
        self.domain_patterns = {
            'e_commerce': {
                'keywords': ['shop', 'store', 'cart', 'payment', 'order', 'product', 'inventory'],
                'features': ['user authentication', 'payment processing', 'product catalog']
            },
            'social_media': {
                'keywords': ['social', 'chat', 'message', 'post', 'feed', 'follow', 'like'],
                'features': ['user profiles', 'messaging', 'content sharing']
            },
            'finance': {
                'keywords': ['finance', 'bank', 'payment', 'transaction', 'money', 'trading'],
                'features': ['transaction processing', 'security', 'compliance']
            },
            'healthcare': {
                'keywords': ['health', 'medical', 'patient', 'doctor', 'hospital', 'clinic'],
                'features': ['patient management', 'HIPAA compliance', 'medical records']
            },
            'education': {
                'keywords': ['education', 'learning', 'course', 'student', 'teacher', 'school'],
                'features': ['user management', 'content delivery', 'progress tracking']
            },
            'productivity': {
                'keywords': ['productivity', 'task', 'project', 'management', 'todo', 'calendar'],
                'features': ['task management', 'collaboration', 'scheduling']
            },
            'analytics': {
                'keywords': ['analytics', 'dashboard', 'metrics', 'reporting', 'visualization'],
                'features': ['data visualization', 'reporting', 'real-time updates']
            },
            'iot': {
                'keywords': ['iot', 'sensor', 'device', 'monitoring', 'automation', 'smart'],
                'features': ['device management', 'data collection', 'real-time monitoring']
            }
        }
        
        # Complexity indicators
        self.complexity_patterns = {
            'simple': {
                'max_files': 10,
                'max_features': 5,
                'single_user': True,
                'no_external_apis': True
            },
            'medium': {
                'max_files': 50,
                'max_features': 15,
                'multi_user': True,
                'few_external_apis': True
            },
            'complex': {
                'max_files': 200,
                'max_features': 50,
                'enterprise': True,
                'many_external_apis': True
            },
            'enterprise': {
                'unlimited_files': True,
                'unlimited_features': True,
                'scalability_required': True,
                'high_availability': True
            }
        }
    
    def _analyze_existing_codebase(self):
        """Analyze existing codebase for project characteristics."""
        if not self.project_path.exists():
            return
        
        # Count files by type
        file_counts = defaultdict(int)
        total_files = 0
        
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and not self._should_skip_file(file_path):
                total_files += 1
                suffix = file_path.suffix.lower()
                file_counts[suffix] += 1
        
        # Detect technology stack
        tech_stack = self._detect_technology_stack()
        
        # Analyze project structure
        structure_analysis = self._analyze_project_structure()
        
        # Store results
        self.analysis_results['technology_stack'] = {
            'file_counts': dict(file_counts),
            'total_files': total_files,
            'detected_technologies': tech_stack,
            'structure_analysis': structure_analysis
        }
    
    def _analyze_project_prompt(self, prompt: str):
        """Analyze project prompt for type and domain indicators."""
        prompt_lower = prompt.lower()
        
        # Extract keywords
        keywords = re.findall(r'\b\w+\b', prompt_lower)
        keyword_counts = Counter(keywords)
        
        # Detect project type from prompt
        type_scores = {}
        for project_type, patterns in self.project_type_patterns.items():
            score = 0
            for keyword in patterns['keywords']:
                if keyword in prompt_lower:
                    score += 2
            
            # Check for framework mentions
            for framework in patterns.get('frameworks', []):
                if framework in prompt_lower:
                    score += 3
            
            type_scores[project_type] = score
        
        # Detect domain from prompt
        domain_scores = {}
        for domain, patterns in self.domain_patterns.items():
            score = 0
            for keyword in patterns['keywords']:
                if keyword in prompt_lower:
                    score += 1
            domain_scores[domain] = score
        
        # Store prompt analysis
        self.analysis_results['prompt_analysis'] = {
            'keywords': dict(keyword_counts.most_common(20)),
            'type_scores': type_scores,
            'domain_scores': domain_scores,
            'estimated_features': self._extract_features_from_prompt(prompt)
        }
    
    def _detect_technology_stack(self) -> Dict[str, any]:
        """Detect technology stack from codebase."""
        detected_tech = {}
        
        for tech, patterns in self.tech_patterns.items():
            tech_score = 0
            detected_frameworks = []
            
            # Check for technology files
            for file_pattern in patterns['files']:
                matching_files = list(self.project_path.rglob(file_pattern))
                if matching_files:
                    tech_score += len(matching_files)
            
            # Check for framework indicators
            for framework, indicators in patterns.get('frameworks', {}).items():
                framework_score = 0
                for indicator in indicators:
                    # Search in files
                    for file_path in self.project_path.rglob('*'):
                        if file_path.is_file() and not self._should_skip_file(file_path):
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if indicator in content:
                                        framework_score += 1
                            except:
                                continue
                
                if framework_score > 0:
                    detected_frameworks.append({
                        'name': framework,
                        'confidence': min(framework_score / len(indicators), 1.0)
                    })
            
            if tech_score > 0:
                detected_tech[tech] = {
                    'confidence': min(tech_score / 10, 1.0),
                    'frameworks': detected_frameworks
                }
        
        return detected_tech
    
    def _analyze_project_structure(self) -> Dict[str, any]:
        """Analyze project structure patterns."""
        structure = {
            'directories': [],
            'patterns': [],
            'architecture_indicators': []
        }
        
        # Common directory patterns
        common_dirs = {
            'src/': 'source_code',
            'lib/': 'libraries',
            'tests/': 'testing',
            'docs/': 'documentation',
            'config/': 'configuration',
            'static/': 'static_files',
            'templates/': 'templates',
            'migrations/': 'database_migrations',
            'api/': 'api_layer',
            'models/': 'data_models',
            'views/': 'view_layer',
            'controllers/': 'controller_layer',
            'services/': 'service_layer',
            'utils/': 'utilities',
            'components/': 'components'
        }
        
        for dir_pattern, dir_type in common_dirs.items():
            matching_dirs = list(self.project_path.rglob(dir_pattern))
            if matching_dirs:
                structure['directories'].append({
                    'pattern': dir_pattern,
                    'type': dir_type,
                    'count': len(matching_dirs)
                })
        
        # Architecture pattern detection
        mvc_indicators = ['models/', 'views/', 'controllers/']
        if all(list(self.project_path.rglob(pattern)) for pattern in mvc_indicators):
            structure['architecture_indicators'].append('MVC')
        
        microservice_indicators = ['services/', 'api/', 'docker-compose.yml']
        if any(list(self.project_path.rglob(pattern)) for pattern in microservice_indicators):
            structure['architecture_indicators'].append('Microservices')
        
        return structure
    
    def _classify_project_type(self):
        """Classify the overall project type."""
        type_scores = defaultdict(float)
        
        # Score from prompt analysis
        if 'prompt_analysis' in self.analysis_results:
            prompt_scores = self.analysis_results['prompt_analysis']['type_scores']
            for project_type, score in prompt_scores.items():
                type_scores[project_type] += score * 0.6  # 60% weight for prompt
        
        # Score from technology stack
        tech_stack = self.analysis_results.get('technology_stack', {})
        detected_tech = tech_stack.get('detected_technologies', {})
        
        for tech, tech_info in detected_tech.items():
            for framework_info in tech_info.get('frameworks', []):
                framework = framework_info['name']
                confidence = framework_info['confidence']
                
                # Map frameworks to project types
                for project_type, patterns in self.project_type_patterns.items():
                    if framework in patterns.get('frameworks', []):
                        type_scores[project_type] += confidence * 0.4  # 40% weight for tech
        
        # Determine primary project type
        if type_scores:
            primary_type = max(type_scores.items(), key=lambda x: x[1])
            
            self.analysis_results['project_type'] = {
                'primary': primary_type[0],
                'confidence': min(primary_type[1] / 10, 1.0),
                'all_scores': dict(type_scores),
                'secondary_types': sorted(type_scores.items(), key=lambda x: x[1], reverse=True)[1:3]
            }
        else:
            self.analysis_results['project_type'] = {
                'primary': 'general_application',
                'confidence': 0.5,
                'all_scores': {},
                'secondary_types': []
            }
    
    def _assess_complexity(self):
        """Assess project complexity."""
        complexity_factors = {
            'file_count': 0,
            'feature_count': 0,
            'technology_diversity': 0,
            'external_dependencies': 0,
            'architectural_complexity': 0
        }
        
        # File count factor
        total_files = self.analysis_results.get('technology_stack', {}).get('total_files', 0)
        if total_files <= 10:
            complexity_factors['file_count'] = 1
        elif total_files <= 50:
            complexity_factors['file_count'] = 2
        elif total_files <= 200:
            complexity_factors['file_count'] = 3
        else:
            complexity_factors['file_count'] = 4
        
        # Feature count from prompt
        estimated_features = self.analysis_results.get('prompt_analysis', {}).get('estimated_features', [])
        feature_count = len(estimated_features)
        if feature_count <= 5:
            complexity_factors['feature_count'] = 1
        elif feature_count <= 15:
            complexity_factors['feature_count'] = 2
        elif feature_count <= 50:
            complexity_factors['feature_count'] = 3
        else:
            complexity_factors['feature_count'] = 4
        
        # Technology diversity
        tech_count = len(self.analysis_results.get('technology_stack', {}).get('detected_technologies', {}))
        complexity_factors['technology_diversity'] = min(tech_count, 4)
        
        # Calculate overall complexity
        avg_complexity = sum(complexity_factors.values()) / len(complexity_factors)
        
        if avg_complexity <= 1.5:
            complexity_level = 'simple'
        elif avg_complexity <= 2.5:
            complexity_level = 'medium'
        elif avg_complexity <= 3.5:
            complexity_level = 'complex'
        else:
            complexity_level = 'enterprise'
        
        self.analysis_results['complexity_assessment'] = {
            'level': complexity_level,
            'score': round(avg_complexity, 2),
            'factors': complexity_factors,
            'recommendations': self._get_complexity_recommendations(complexity_level)
        }
    
    def _extract_features_from_prompt(self, prompt: str) -> List[str]:
        """Extract likely features from project prompt."""
        features = []
        
        # Common feature patterns
        feature_patterns = [
            r'user\s+(authentication|login|registration)',
            r'(dashboard|admin\s+panel)',
            r'(api|rest|graphql)',
            r'(database|storage|persistence)',
            r'(search|filtering)',
            r'(notification|email|messaging)',
            r'(payment|billing|subscription)',
            r'(file\s+upload|media)',
            r'(real-time|websocket|chat)',
            r'(analytics|reporting|metrics)',
            r'(security|authorization|permissions)',
            r'(mobile\s+app|responsive)',
            r'(testing|unit\s+tests)',
            r'(deployment|ci/cd|docker)'
        ]
        
        prompt_lower = prompt.lower()
        for pattern in feature_patterns:
            matches = re.findall(pattern, prompt_lower)
            if matches:
                features.extend(matches)
        
        return list(set(features))
    
    def _generate_template_recommendations(self):
        """Generate template recommendations based on analysis."""
        recommendations = []
        
        project_type = self.analysis_results.get('project_type', {})
        complexity = self.analysis_results.get('complexity_assessment', {})
        tech_stack = self.analysis_results.get('technology_stack', {})
        
        primary_type = project_type.get('primary', 'general_application')
        complexity_level = complexity.get('level', 'medium')
        
        # Base template recommendation
        base_template = f"{primary_type}_{complexity_level}"
        recommendations.append({
            'template': base_template,
            'priority': 'primary',
            'reason': f"Matches {primary_type} project type with {complexity_level} complexity"
        })
        
        # Technology-specific templates
        detected_tech = tech_stack.get('detected_technologies', {})
        for tech, tech_info in detected_tech.items():
            if tech_info['confidence'] > 0.7:
                for framework_info in tech_info.get('frameworks', []):
                    if framework_info['confidence'] > 0.7:
                        framework_template = f"{tech}_{framework_info['name']}"
                        recommendations.append({
                            'template': framework_template,
                            'priority': 'technology',
                            'reason': f"High confidence {framework_info['name']} framework detection"
                        })
        
        # Domain-specific templates
        if 'prompt_analysis' in self.analysis_results:
            domain_scores = self.analysis_results['prompt_analysis']['domain_scores']
            top_domain = max(domain_scores.items(), key=lambda x: x[1]) if domain_scores else None
            
            if top_domain and top_domain[1] > 2:
                domain_template = f"domain_{top_domain[0]}"
                recommendations.append({
                    'template': domain_template,
                    'priority': 'domain',
                    'reason': f"Strong indicators for {top_domain[0]} domain"
                })
        
        self.analysis_results['template_recommendations'] = recommendations
    
    def _get_complexity_recommendations(self, complexity_level: str) -> List[str]:
        """Get recommendations based on complexity level."""
        recommendations = {
            'simple': [
                "Focus on core functionality first",
                "Use simple, well-established patterns",
                "Minimize external dependencies",
                "Prioritize code clarity over optimization"
            ],
            'medium': [
                "Implement proper separation of concerns",
                "Add comprehensive testing",
                "Consider using established frameworks",
                "Plan for moderate scalability"
            ],
            'complex': [
                "Design for modularity and maintainability",
                "Implement comprehensive error handling",
                "Use design patterns appropriately",
                "Plan for team collaboration",
                "Consider microservices architecture"
            ],
            'enterprise': [
                "Design for high availability and scalability",
                "Implement comprehensive monitoring",
                "Use enterprise-grade security practices",
                "Plan for multi-team development",
                "Consider distributed architecture",
                "Implement comprehensive testing strategy"
            ]
        }
        
        return recommendations.get(complexity_level, [])
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during analysis."""
        skip_patterns = [
            '__pycache__', '.git', '.svn', 'node_modules', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', '.tox', 'build', 'dist',
            '.DS_Store', 'Thumbs.db', '*.log', '*.tmp'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def generate_analysis_report(self) -> Dict[str, any]:
        """Generate comprehensive analysis report."""
        return {
            'summary': {
                'project_type': self.analysis_results.get('project_type', {}).get('primary', 'unknown'),
                'complexity_level': self.analysis_results.get('complexity_assessment', {}).get('level', 'unknown'),
                'primary_technology': self._get_primary_technology(),
                'recommended_templates': len(self.analysis_results.get('template_recommendations', [])),
                'analysis_timestamp': self._get_timestamp()
            },
            'detailed_analysis': self.analysis_results,
            'recommendations': self._generate_overall_recommendations()
        }
    
    def _get_primary_technology(self) -> str:
        """Get the primary technology from analysis."""
        tech_stack = self.analysis_results.get('technology_stack', {})
        detected_tech = tech_stack.get('detected_technologies', {})
        
        if detected_tech:
            primary_tech = max(detected_tech.items(), key=lambda x: x[1]['confidence'])
            return primary_tech[0]
        
        return 'unknown'
    
    def _generate_overall_recommendations(self) -> List[str]:
        """Generate overall project recommendations."""
        recommendations = []
        
        # Add complexity-based recommendations
        complexity = self.analysis_results.get('complexity_assessment', {})
        if complexity:
            recommendations.extend(complexity.get('recommendations', []))
        
        # Add template-based recommendations
        template_recs = self.analysis_results.get('template_recommendations', [])
        if template_recs:
            primary_template = next((rec for rec in template_recs if rec['priority'] == 'primary'), None)
            if primary_template:
                recommendations.append(f"Use {primary_template['template']} template as starting point")
        
        return recommendations
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


# Utility functions
def analyze_project_type(project_path: str = None, project_prompt: str = None) -> Dict[str, any]:
    """Analyze project type and characteristics."""
    detector = ProjectTypeDetector(project_path)
    return detector.analyze_project(project_prompt)

def get_template_recommendations(project_path: str = None, project_prompt: str = None) -> List[Dict[str, str]]:
    """Get template recommendations for a project."""
    detector = ProjectTypeDetector(project_path)
    analysis = detector.analyze_project(project_prompt)
    return analysis.get('template_recommendations', [])

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python project-type-detector.py <project_path> [project_prompt]")
        print("       python project-type-detector.py --prompt 'project description'")
        sys.exit(1)
    
    if sys.argv[1] == '--prompt':
        project_path = None
        project_prompt = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        project_path = sys.argv[1]
        project_prompt = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🔍 Project Type Detector")
    print(f"Analyzing: {project_path or 'prompt only'}")
    print("=" * 50)
    
    try:
        detector = ProjectTypeDetector(project_path)
        analysis = detector.analyze_project(project_prompt)
        report = detector.generate_analysis_report()
        
        # Print summary
        summary = report['summary']
        print(f"\n📊 Analysis Summary:")
        print(f"  Project Type: {summary['project_type']}")
        print(f"  Complexity: {summary['complexity_level']}")
        print(f"  Primary Technology: {summary['primary_technology']}")
        print(f"  Template Recommendations: {summary['recommended_templates']}")
        
        # Print template recommendations
        template_recs = analysis.get('template_recommendations', [])
        if template_recs:
            print(f"\n🎯 Template Recommendations:")
            for rec in template_recs:
                print(f"  {rec['priority'].upper()}: {rec['template']}")
                print(f"    Reason: {rec['reason']}")
        
        # Print overall recommendations
        recommendations = report['recommendations']
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  - {rec}")
                
    except Exception as e:
        print(f"❌ Project analysis failed: {e}")
        sys.exit(1)
