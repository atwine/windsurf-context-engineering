"""
Learning Engine - Core orchestrator for all learning and feedback processes

This module provides the central learning engine that coordinates pattern analysis,
feedback collection, template evolution, and performance tracking to create a
self-improving development framework.
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class LearningMetrics:
    """Metrics for learning system performance"""
    projects_analyzed: int = 0
    patterns_identified: int = 0
    templates_evolved: int = 0
    feedback_processed: int = 0
    improvement_score: float = 0.0
    prediction_accuracy: float = 0.0
    user_satisfaction: float = 0.0
    last_updated: str = ""

@dataclass
class ProjectOutcome:
    """Represents the outcome of a project for learning purposes"""
    project_id: str
    project_type: str
    template_used: str
    success_score: float  # 0.0 to 1.0
    completion_time: float  # hours
    code_quality_score: float  # 0.0 to 1.0
    user_satisfaction: float  # 0.0 to 1.0
    issues_encountered: List[str]
    patterns_used: List[str]
    feedback_summary: str
    created_at: str
    metadata: Dict[str, Any]

class LearningEngine:
    """
    Central learning engine that coordinates all learning processes
    """
    
    def __init__(self, db_path: str = "learning_data.db"):
        """Initialize the learning engine"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Learning configuration
        self.config = {
            'min_projects_for_pattern': 5,
            'success_threshold': 0.7,
            'pattern_confidence_threshold': 0.8,
            'template_evolution_threshold': 0.6,
            'feedback_weight': 0.3,
            'outcome_weight': 0.7,
            'learning_rate': 0.1,
            'max_patterns_per_analysis': 50
        }
        
        # Learning state
        self.metrics = LearningMetrics()
        self.active_patterns = {}
        self.template_performance = defaultdict(list)
        self.user_preferences = {}
        
        logger.info("Learning engine initialized")
    
    def _init_database(self):
        """Initialize the learning database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS project_outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT UNIQUE NOT NULL,
                    project_type TEXT NOT NULL,
                    template_used TEXT NOT NULL,
                    success_score REAL NOT NULL,
                    completion_time REAL NOT NULL,
                    code_quality_score REAL NOT NULL,
                    user_satisfaction REAL NOT NULL,
                    issues_encountered TEXT NOT NULL,
                    patterns_used TEXT NOT NULL,
                    feedback_summary TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS template_evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    changes TEXT NOT NULL,
                    performance_improvement REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1
                );
                
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    comments TEXT NOT NULL,
                    sentiment_score REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    processed BOOLEAN DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS learning_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    created_at TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_project_outcomes_type ON project_outcomes(project_type);
                CREATE INDEX IF NOT EXISTS idx_project_outcomes_template ON project_outcomes(template_used);
                CREATE INDEX IF NOT EXISTS idx_learning_patterns_type ON learning_patterns(pattern_type);
                CREATE INDEX IF NOT EXISTS idx_template_evolution_name ON template_evolution(template_name);
                CREATE INDEX IF NOT EXISTS idx_user_feedback_project ON user_feedback(project_id);
            """)
    
    def record_project_outcome(self, outcome: ProjectOutcome) -> bool:
        """Record a project outcome for learning"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO project_outcomes 
                    (project_id, project_type, template_used, success_score, 
                     completion_time, code_quality_score, user_satisfaction,
                     issues_encountered, patterns_used, feedback_summary,
                     created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    outcome.project_id,
                    outcome.project_type,
                    outcome.template_used,
                    outcome.success_score,
                    outcome.completion_time,
                    outcome.code_quality_score,
                    outcome.user_satisfaction,
                    json.dumps(outcome.issues_encountered),
                    json.dumps(outcome.patterns_used),
                    outcome.feedback_summary,
                    outcome.created_at,
                    json.dumps(outcome.metadata)
                ))
            
            self.metrics.projects_analyzed += 1
            logger.info(f"Recorded project outcome: {outcome.project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record project outcome: {e}")
            return False
    
    def analyze_success_patterns(self) -> Dict[str, Any]:
        """Analyze patterns that lead to project success"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get successful projects (success_score >= threshold)
                cursor = conn.execute("""
                    SELECT project_type, template_used, patterns_used, 
                           success_score, code_quality_score, completion_time
                    FROM project_outcomes 
                    WHERE success_score >= ?
                    ORDER BY success_score DESC
                """, (self.config['success_threshold'],))
                
                successful_projects = cursor.fetchall()
                
                if len(successful_projects) < self.config['min_projects_for_pattern']:
                    return {'status': 'insufficient_data', 'patterns': []}
                
                # Analyze patterns
                success_patterns = {
                    'template_performance': defaultdict(list),
                    'project_type_success': defaultdict(list),
                    'pattern_effectiveness': defaultdict(list),
                    'optimal_combinations': []
                }
                
                for project in successful_projects:
                    project_type, template, patterns_json, success, quality, time = project
                    patterns = json.loads(patterns_json) if patterns_json else []
                    
                    success_patterns['template_performance'][template].append({
                        'success_score': success,
                        'quality_score': quality,
                        'completion_time': time
                    })
                    
                    success_patterns['project_type_success'][project_type].append({
                        'template': template,
                        'success_score': success,
                        'patterns': patterns
                    })
                    
                    for pattern in patterns:
                        success_patterns['pattern_effectiveness'][pattern].append({
                            'success_score': success,
                            'quality_score': quality
                        })
                
                # Calculate pattern statistics
                pattern_stats = {}
                for pattern, scores in success_patterns['pattern_effectiveness'].items():
                    if len(scores) >= 3:  # Minimum for statistical significance
                        avg_success = np.mean([s['success_score'] for s in scores])
                        avg_quality = np.mean([s['quality_score'] for s in scores])
                        pattern_stats[pattern] = {
                            'usage_count': len(scores),
                            'avg_success_score': avg_success,
                            'avg_quality_score': avg_quality,
                            'confidence': min(len(scores) / 10.0, 1.0)  # Max confidence at 10+ uses
                        }
                
                # Store patterns in database
                self._store_learning_patterns('success_patterns', pattern_stats)
                
                self.metrics.patterns_identified = len(pattern_stats)
                logger.info(f"Analyzed {len(successful_projects)} successful projects, identified {len(pattern_stats)} patterns")
                
                return {
                    'status': 'success',
                    'patterns': pattern_stats,
                    'projects_analyzed': len(successful_projects),
                    'template_performance': dict(success_patterns['template_performance'])
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze success patterns: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def analyze_failure_patterns(self) -> Dict[str, Any]:
        """Analyze patterns that lead to project failures"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get failed projects (success_score < threshold)
                cursor = conn.execute("""
                    SELECT project_type, template_used, issues_encountered,
                           patterns_used, success_score, completion_time
                    FROM project_outcomes 
                    WHERE success_score < ?
                    ORDER BY success_score ASC
                """, (self.config['success_threshold'],))
                
                failed_projects = cursor.fetchall()
                
                if len(failed_projects) < 3:  # Need minimum failures to analyze
                    return {'status': 'insufficient_data', 'patterns': []}
                
                # Analyze failure patterns
                failure_patterns = {
                    'common_issues': defaultdict(int),
                    'problematic_templates': defaultdict(list),
                    'failure_combinations': defaultdict(int),
                    'time_correlation': []
                }
                
                for project in failed_projects:
                    project_type, template, issues_json, patterns_json, success, time = project
                    issues = json.loads(issues_json) if issues_json else []
                    patterns = json.loads(patterns_json) if patterns_json else []
                    
                    # Count common issues
                    for issue in issues:
                        failure_patterns['common_issues'][issue] += 1
                    
                    # Track problematic templates
                    failure_patterns['problematic_templates'][template].append({
                        'project_type': project_type,
                        'success_score': success,
                        'issues': issues
                    })
                    
                    # Track failure combinations
                    combo_key = f"{project_type}:{template}"
                    failure_patterns['failure_combinations'][combo_key] += 1
                    
                    # Time correlation
                    failure_patterns['time_correlation'].append({
                        'completion_time': time,
                        'success_score': success,
                        'issue_count': len(issues)
                    })
                
                # Calculate failure statistics
                failure_stats = {
                    'most_common_issues': sorted(
                        failure_patterns['common_issues'].items(),
                        key=lambda x: x[1], reverse=True
                    )[:10],
                    'problematic_combinations': sorted(
                        failure_patterns['failure_combinations'].items(),
                        key=lambda x: x[1], reverse=True
                    )[:5],
                    'avg_failure_time': np.mean([p['completion_time'] for p in failure_patterns['time_correlation']])
                }
                
                # Store failure patterns
                self._store_learning_patterns('failure_patterns', failure_stats)
                
                logger.info(f"Analyzed {len(failed_projects)} failed projects")
                
                return {
                    'status': 'success',
                    'patterns': failure_stats,
                    'projects_analyzed': len(failed_projects)
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze failure patterns: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _store_learning_patterns(self, pattern_type: str, patterns: Dict[str, Any]):
        """Store learning patterns in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                timestamp = datetime.now().isoformat()
                
                conn.execute("""
                    INSERT OR REPLACE INTO learning_patterns
                    (pattern_type, pattern_data, confidence_score, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    pattern_type,
                    json.dumps(patterns),
                    0.8,  # Default confidence
                    timestamp,
                    timestamp
                ))
                
        except Exception as e:
            logger.error(f"Failed to store learning patterns: {e}")
    
    def get_recommendations(self, project_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered recommendations based on learned patterns"""
        try:
            # Get relevant patterns
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT pattern_type, pattern_data, confidence_score
                    FROM learning_patterns
                    WHERE confidence_score >= ?
                    ORDER BY confidence_score DESC
                """, (self.config['pattern_confidence_threshold'],))
                
                patterns = cursor.fetchall()
                
                if not patterns:
                    return {'status': 'no_patterns', 'recommendations': []}
                
                recommendations = []
                
                # Analyze patterns for recommendations
                for pattern_type, pattern_data_json, confidence in patterns:
                    pattern_data = json.loads(pattern_data_json)
                    
                    if pattern_type == 'success_patterns':
                        # Recommend successful patterns for this project type
                        for pattern_name, stats in pattern_data.items():
                            if stats.get('avg_success_score', 0) > 0.8:
                                recommendations.append({
                                    'type': 'pattern',
                                    'recommendation': f"Use pattern '{pattern_name}'",
                                    'confidence': confidence * stats.get('confidence', 0.5),
                                    'reason': f"This pattern has {stats['avg_success_score']:.1%} success rate",
                                    'usage_count': stats.get('usage_count', 0)
                                })
                    
                    elif pattern_type == 'failure_patterns':
                        # Warn about common failure patterns
                        common_issues = pattern_data.get('most_common_issues', [])
                        for issue, count in common_issues[:3]:
                            recommendations.append({
                                'type': 'warning',
                                'recommendation': f"Watch out for: {issue}",
                                'confidence': min(count / 10.0, 1.0),
                                'reason': f"This issue occurred in {count} failed projects",
                                'severity': 'high' if count > 5 else 'medium'
                            })
                
                # Sort by confidence
                recommendations.sort(key=lambda x: x['confidence'], reverse=True)
                
                return {
                    'status': 'success',
                    'recommendations': recommendations[:10],  # Top 10
                    'total_patterns': len(patterns)
                }
                
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def update_metrics(self):
        """Update learning metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Count projects analyzed
                cursor = conn.execute("SELECT COUNT(*) FROM project_outcomes")
                self.metrics.projects_analyzed = cursor.fetchone()[0]
                
                # Count patterns identified
                cursor = conn.execute("SELECT COUNT(*) FROM learning_patterns")
                self.metrics.patterns_identified = cursor.fetchone()[0]
                
                # Calculate average success score
                cursor = conn.execute("SELECT AVG(success_score) FROM project_outcomes")
                avg_success = cursor.fetchone()[0] or 0.0
                
                # Calculate user satisfaction
                cursor = conn.execute("SELECT AVG(user_satisfaction) FROM project_outcomes")
                self.metrics.user_satisfaction = cursor.fetchone()[0] or 0.0
                
                # Calculate improvement score (trend analysis)
                cursor = conn.execute("""
                    SELECT success_score, created_at FROM project_outcomes 
                    ORDER BY created_at DESC LIMIT 20
                """)
                recent_scores = [row[0] for row in cursor.fetchall()]
                
                if len(recent_scores) >= 10:
                    recent_avg = np.mean(recent_scores[:10])
                    older_avg = np.mean(recent_scores[10:])
                    self.metrics.improvement_score = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0.0
                
                self.metrics.last_updated = datetime.now().isoformat()
                
                # Store metrics
                timestamp = datetime.now().isoformat()
                for metric_name, value in asdict(self.metrics).items():
                    if isinstance(value, (int, float)):
                        conn.execute("""
                            INSERT INTO learning_metrics (metric_name, metric_value, created_at)
                            VALUES (?, ?, ?)
                        """, (metric_name, value, timestamp))
                
                logger.info("Updated learning metrics")
                
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning system status"""
        self.update_metrics()
        
        return {
            'metrics': asdict(self.metrics),
            'config': self.config,
            'database_path': str(self.db_path),
            'status': 'active'
        }
    
    def export_learning_data(self, output_path: str) -> bool:
        """Export learning data for analysis"""
        try:
            export_data = {
                'metrics': asdict(self.metrics),
                'config': self.config,
                'export_timestamp': datetime.now().isoformat()
            }
            
            # Get all data from database
            with sqlite3.connect(self.db_path) as conn:
                # Project outcomes
                cursor = conn.execute("SELECT * FROM project_outcomes")
                columns = [desc[0] for desc in cursor.description]
                export_data['project_outcomes'] = [
                    dict(zip(columns, row)) for row in cursor.fetchall()
                ]
                
                # Learning patterns
                cursor = conn.execute("SELECT * FROM learning_patterns")
                columns = [desc[0] for desc in cursor.description]
                export_data['learning_patterns'] = [
                    dict(zip(columns, row)) for row in cursor.fetchall()
                ]
                
                # User feedback
                cursor = conn.execute("SELECT * FROM user_feedback")
                columns = [desc[0] for desc in cursor.description]
                export_data['user_feedback'] = [
                    dict(zip(columns, row)) for row in cursor.fetchall()
                ]
            
            # Write to file
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported learning data to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export learning data: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    engine = LearningEngine()
    
    # Example project outcome
    outcome = ProjectOutcome(
        project_id="test_project_001",
        project_type="web_application",
        template_used="react_typescript_template",
        success_score=0.85,
        completion_time=24.5,
        code_quality_score=0.78,
        user_satisfaction=0.90,
        issues_encountered=["dependency_conflict", "build_error"],
        patterns_used=["component_structure", "state_management"],
        feedback_summary="Great template, minor build issues",
        created_at=datetime.now().isoformat(),
        metadata={"team_size": 3, "deadline_met": True}
    )
    
    # Record outcome and analyze
    engine.record_project_outcome(outcome)
    success_patterns = engine.analyze_success_patterns()
    recommendations = engine.get_recommendations("web_application", {})
    status = engine.get_learning_status()
    
    print("Learning Engine Demo:")
    print(f"Status: {status}")
    print(f"Success Patterns: {success_patterns}")
    print(f"Recommendations: {recommendations}")
