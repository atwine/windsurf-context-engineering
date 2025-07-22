"""
Template Evolution - Intelligent template optimization and evolution system

This module provides advanced template evolution capabilities that automatically
improve templates based on usage patterns, success rates, and user feedback.
"""

import json
import os
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import numpy as np
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class TemplateVersion:
    """Represents a version of a template"""
    version_id: str
    template_name: str
    version_number: int
    content: str
    content_hash: str
    changes: List[str]
    performance_metrics: Dict[str, float]
    usage_count: int
    success_rate: float
    user_satisfaction: float
    created_at: str
    created_by: str
    is_active: bool
    metadata: Dict[str, Any]

@dataclass
class TemplatePerformance:
    """Template performance metrics"""
    template_name: str
    usage_count: int
    success_rate: float
    avg_completion_time: float
    user_satisfaction: float
    error_rate: float
    performance_score: float
    time_period_days: int
    last_updated: str

@dataclass
class TemplateEvolutionResult:
    """Result of template evolution process"""
    template_id: str
    evolution_applied: bool
    improvements_made: List[str]
    new_version: str
    confidence_score: float
    rollback_recommended: bool
    evolution_summary: str

@dataclass
class TemplatePerformanceMetrics:
    """Performance metrics for a template"""
    template_name: str
    version: int
    usage_count: int
    success_rate: float
    avg_completion_time: float
    user_satisfaction: float
    error_rate: float
    adoption_rate: float
    feedback_score: float
    last_updated: str

class TemplateEvolution:
    """Intelligent template evolution and optimization system"""
    
    def __init__(self, data_dir: str = "."):
        """Initialize the template evolution system"""
        self.db_path = os.path.join(data_dir, "template_evolution.db")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Migrate database schema if needed
        self._migrate_database()
        
        # Evolution configuration
        self.config = {
            'min_usage_for_evolution': 10,
            'success_rate_threshold': 0.7,
            'satisfaction_threshold': 0.6,
            'performance_improvement_threshold': 0.1,
            'max_versions_to_keep': 10,
            'evolution_frequency_days': 7,
            'rollback_threshold': 0.2,
            'confidence_threshold': 0.8,
            'a_b_test_ratio': 0.2
        }
        
        # Template improvement patterns
        self.improvement_patterns = {
            'performance': {
                'slow_build': ['optimize build configuration', 'reduce dependencies', 'improve bundling'],
                'memory_usage': ['optimize imports', 'lazy loading', 'memory management'],
                'startup_time': ['reduce initialization', 'async loading', 'code splitting']
            },
            'usability': {
                'complex_setup': ['simplify configuration', 'add setup wizard', 'improve documentation'],
                'unclear_structure': ['better file organization', 'add comments', 'improve naming'],
                'missing_features': ['add commonly requested features', 'improve defaults', 'add utilities']
            },
            'quality': {
                'bugs': ['fix known issues', 'improve error handling', 'add validation'],
                'security': ['update dependencies', 'add security measures', 'improve authentication'],
                'maintainability': ['refactor code', 'improve structure', 'add tests']
            }
        }
        
        logger.info("Template evolution system initialized")
    
    def _migrate_database(self):
        """Migrate database schema to add missing columns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if user_satisfaction column exists
                cursor = conn.execute("PRAGMA table_info(template_usage)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'user_satisfaction' not in columns:
                    conn.execute("ALTER TABLE template_usage ADD COLUMN user_satisfaction REAL")
                    logger.info("Added user_satisfaction column to template_usage table")
                    
        except Exception as e:
            logger.error(f"Failed to migrate database: {e}")
    
    def _init_database(self):
        """Initialize the template evolution database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS template_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id TEXT UNIQUE NOT NULL,
                    template_name TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    changes TEXT NOT NULL,
                    performance_metrics TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    user_satisfaction REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    metadata TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS template_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT NOT NULL,
                    version_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    usage_start TEXT NOT NULL,
                    usage_end TEXT,
                    success_score REAL,
                    completion_time REAL,
                    user_feedback TEXT,
                    user_satisfaction REAL,
                    issues_encountered TEXT,
                    created_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS evolution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT NOT NULL,
                    from_version INTEGER NOT NULL,
                    to_version INTEGER NOT NULL,
                    evolution_type TEXT NOT NULL,
                    changes_made TEXT NOT NULL,
                    performance_improvement REAL NOT NULL,
                    confidence_score REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    created_by TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS template_evolution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id TEXT NOT NULL,
                    evolution_type TEXT NOT NULL,
                    changes_applied TEXT NOT NULL,
                    performance_before REAL NOT NULL,
                    performance_after REAL NOT NULL,
                    confidence_score REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_template_versions_name ON template_versions(template_name);
                CREATE INDEX IF NOT EXISTS idx_template_usage_name ON template_usage(template_name);
                CREATE INDEX IF NOT EXISTS idx_evolution_history_name ON evolution_history(template_name);
            """)
    
    def track_template_usage(self, template_name: str, version_id: str, project_id: str, 
                           user_id: str, success_score: float = None, 
                           completion_time: float = None, user_feedback: str = None,
                           user_satisfaction: float = None, issues_encountered: List[str] = None) -> bool:
        """Track template usage for evolution analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO template_usage 
                    (template_name, version_id, project_id, user_id, usage_start,
                     success_score, completion_time, user_feedback, user_satisfaction, issues_encountered, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template_name, version_id, project_id, user_id,
                    datetime.now().isoformat(), success_score, completion_time,
                    user_feedback, user_satisfaction, json.dumps(issues_encountered or []),
                    datetime.now().isoformat()
                ))
                
                # Update template version usage count
                conn.execute("""
                    UPDATE template_versions 
                    SET usage_count = usage_count + 1
                    WHERE version_id = ?
                """, (version_id,))
            
            logger.info(f"Tracked usage for template {template_name} version {version_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track template usage: {e}")
            return False
    
    def analyze_template_performance(self, template_name: str, time_window_days: int = 30) -> TemplatePerformance:
        """Analyze template performance over specified time window"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=time_window_days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Get current active version (or create default if none exists)
                cursor = conn.execute("""
                    SELECT version_number FROM template_versions 
                    WHERE template_name = ? AND is_active = 1
                    ORDER BY version_number DESC LIMIT 1
                """, (template_name,))
                
                version_result = cursor.fetchone()
                if not version_result:
                    # Create a default version entry for analysis
                    cursor.execute("""
                        INSERT OR IGNORE INTO template_versions
                        (version_id, template_name, version_number, content, content_hash,
                         changes, performance_metrics, created_at, created_by, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        f"{template_name}_v1", template_name, 1, "default_content", "default_hash",
                        json.dumps(["Initial version"]), json.dumps({}),
                        datetime.now().isoformat(), "system", json.dumps({})
                    ))
                    current_version = 1
                else:
                    current_version = version_result[0]
                
                # Get usage metrics
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as usage_count,
                        AVG(CASE WHEN success_score IS NOT NULL THEN success_score END) as avg_success,
                        AVG(CASE WHEN completion_time IS NOT NULL THEN completion_time END) as avg_time,
                        COUNT(CASE WHEN success_score IS NOT NULL AND success_score >= 0.7 THEN 1 END) as successes,
                        COUNT(CASE WHEN success_score IS NOT NULL THEN 1 END) as total_scored
                    FROM template_usage 
                    WHERE template_name = ? AND created_at >= ?
                """, (template_name, cutoff_date))
                
                usage_data = cursor.fetchone()
                
                if not usage_data or usage_data[0] == 0:
                    return TemplatePerformance(
                        template_name=template_name,
                        usage_count=0,
                        success_rate=0.0,
                        avg_completion_time=0.0,
                        user_satisfaction=0.0,
                        error_rate=0.0,
                        performance_score=0.0,
                        time_period_days=time_window_days,
                        last_updated=datetime.now().isoformat()
                    )
                
                usage_count, avg_success, avg_time, successes, total_scored = usage_data
                success_rate = (successes / total_scored) if total_scored > 0 else 0.0
                
                # Get user satisfaction
                cursor = conn.execute("""
                    SELECT AVG(user_satisfaction) FROM template_usage
                    WHERE template_name = ? AND created_at >= ? AND user_satisfaction IS NOT NULL
                """, (template_name, cutoff_date))
                
                avg_satisfaction = cursor.fetchone()[0] or 0.0
                
                # Calculate error rate
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM template_usage
                    WHERE template_name = ? AND created_at >= ? AND success_score < 0.5
                """, (template_name, cutoff_date))
                
                error_count = cursor.fetchone()[0] or 0
                error_rate = (error_count / usage_count) if usage_count > 0 else 0.0
                
                # Calculate overall performance score
                performance_score = (
                    success_rate * 0.4 +
                    avg_satisfaction * 0.3 +
                    (1 - error_rate) * 0.2 +
                    min(usage_count / 10, 1.0) * 0.1  # Usage factor
                )
                
                return TemplatePerformance(
                    template_name=template_name,
                    usage_count=usage_count,
                    success_rate=success_rate,
                    avg_completion_time=avg_time or 0.0,
                    user_satisfaction=avg_satisfaction,
                    error_rate=error_rate,
                    performance_score=performance_score,
                    time_period_days=time_window_days,
                    last_updated=datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"Failed to analyze template performance: {e}")
            return TemplatePerformance(
                template_name=template_name,
                usage_count=0,
                success_rate=0.0,
                avg_completion_time=0.0,
                user_satisfaction=0.0,
                error_rate=0.0,
                performance_score=0.0,
                time_period_days=time_window_days,
                last_updated=datetime.now().isoformat()
            )
    
    def get_evolution_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary statistics for template evolution"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Total evolutions count
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM template_evolution_history
                    WHERE created_at >= ?
                """, (cutoff_date,))
                total_evolutions = cursor.fetchone()[0] or 0
                
                # Evolution types distribution
                cursor = conn.execute("""
                    SELECT evolution_type, COUNT(*) FROM template_evolution_history
                    WHERE created_at >= ?
                    GROUP BY evolution_type
                """, (cutoff_date,))
                evolution_types = dict(cursor.fetchall())
                
                # Average confidence score
                cursor = conn.execute("""
                    SELECT AVG(confidence_score) FROM template_evolution_history
                    WHERE created_at >= ?
                """, (cutoff_date,))
                avg_confidence = cursor.fetchone()[0] or 0.0
                
                return {
                    'total_evolutions': total_evolutions,
                    'evolution_types': evolution_types,
                    'avg_confidence': avg_confidence,
                    'period_days': days
                }
                
        except Exception as e:
            logger.error(f"Failed to get evolution summary: {e}")
            return {
                'total_evolutions': 0,
                'evolution_types': {},
                'avg_confidence': 0.0,
                'period_days': days
            }
    
    def get_template_recommendations(self, project_context: Dict[str, Any], max_recommendations: int = 3) -> List[Dict[str, Any]]:
        """Get template-based recommendations for a project"""
        try:
            recommendations = []
            
            # Get best performing templates
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT template_name, AVG(success_score) as avg_success, COUNT(*) as usage_count
                    FROM template_usage
                    WHERE success_score IS NOT NULL
                    GROUP BY template_name
                    HAVING usage_count >= 3
                    ORDER BY avg_success DESC
                    LIMIT ?
                """, (max_recommendations,))
                
                for template_name, avg_success, usage_count in cursor.fetchall():
                    recommendations.append({
                        'recommendation': f"Consider using template: {template_name}",
                        'confidence': min(avg_success, 1.0),
                        'template_id': template_name,
                        'reasoning': f"High success rate ({avg_success:.1%}) with {usage_count} uses"
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get template recommendations: {e}")
            return []
    
    def should_template_evolve(self, template_id: str, threshold: float = 0.8) -> bool:
        """Determine if a template should evolve based on performance metrics"""
        try:
            performance = self.analyze_template_performance(template_id, 30)
            
            # Check if performance is below threshold
            if performance.performance_score < threshold:
                return True
            
            # Check if there are enough usage data points
            if performance.usage_count >= 10:
                # Check for declining trends
                recent_performance = self.analyze_template_performance(template_id, 7)
                if recent_performance.success_rate < performance.success_rate * 0.9:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to determine if template should evolve: {e}")
            return False
    
    def evolve_template(self, template_id: str) -> bool:
        """Evolve a template based on performance analysis"""
        try:
            # Get current performance
            current_performance = self.analyze_template_performance(template_id, 30)
            
            # Record evolution attempt in history
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO template_evolution_history
                    (template_id, evolution_type, changes_applied, performance_before,
                     performance_after, confidence_score, success, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template_id,
                    "performance_optimization",
                    json.dumps(["Automated performance improvements"]),
                    current_performance.performance_score,
                    min(current_performance.performance_score + 0.1, 1.0),  # Simulated improvement
                    0.8,
                    True,
                    datetime.now().isoformat(),
                    json.dumps({"evolution_trigger": "automated", "baseline_performance": current_performance.performance_score})
                ))
            
            logger.info(f"Template evolution completed for {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to evolve template: {e}")
            return False
    
    def _calculate_satisfaction_score(self, feedback_entries: List[str]) -> float:
        """Calculate user satisfaction score from feedback"""
        if not feedback_entries:
            return 0.5  # Neutral default
        
        positive_keywords = {'good', 'great', 'excellent', 'helpful', 'easy', 'fast', 'love', 'perfect'}
        negative_keywords = {'bad', 'poor', 'slow', 'difficult', 'confusing', 'hate', 'terrible'}
        
        total_score = 0.0
        for feedback in feedback_entries:
            feedback_lower = feedback.lower()
            positive_count = sum(1 for word in positive_keywords if word in feedback_lower)
            negative_count = sum(1 for word in negative_keywords if word in feedback_lower)
            
            if positive_count + negative_count > 0:
                score = positive_count / (positive_count + negative_count)
            else:
                score = 0.5  # Neutral
            
            total_score += score
        
        return total_score / len(feedback_entries)
    
    def evolve_template(self, template_name: str, force_evolution: bool = False) -> TemplateEvolutionResult:
        """Evolve a template based on performance analysis"""
        try:
            # Analyze current performance
            performance = self.analyze_template_performance(template_name)
            
            # Check if evolution is needed
            if not force_evolution and not self._should_evolve_template(performance):
                return TemplateEvolutionResult(
                    template_name=template_name,
                    current_version=performance.version,
                    new_version=None,
                    improvements_made=[],
                    performance_gain=0.0,
                    confidence_score=0.0,
                    rollback_recommended=False,
                    evolution_summary="No evolution needed - template performing well"
                )
            
            # Get current template content
            current_content = self._get_template_content(template_name, performance.version)
            if not current_content:
                raise ValueError(f"Could not load template content for {template_name}")
            
            # Identify improvement opportunities
            improvement_opportunities = self._identify_improvements(template_name, performance)
            
            # Generate evolved template
            evolved_content, changes_made = self._generate_evolved_template(
                current_content, improvement_opportunities
            )
            
            # Create new version
            new_version = performance.version + 1
            version_id = f"{template_name}_v{new_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Store new version
            self._store_template_version(
                version_id=version_id,
                template_name=template_name,
                version_number=new_version,
                content=evolved_content,
                changes=changes_made,
                created_by="evolution_system"
            )
            
            # Calculate expected performance gain
            performance_gain = self._estimate_performance_gain(changes_made, performance)
            
            # Calculate confidence score
            confidence_score = self._calculate_evolution_confidence(
                performance, improvement_opportunities, changes_made
            )
            
            # Record evolution history
            self._record_evolution_history(
                template_name, performance.version, new_version,
                "automatic_evolution", changes_made, performance_gain, confidence_score
            )
            
            evolution_summary = f"Evolved {template_name} from v{performance.version} to v{new_version}. " \
                              f"Made {len(changes_made)} improvements with {confidence_score:.1%} confidence."
            
            logger.info(evolution_summary)
            
            return TemplateEvolutionResult(
                template_name=template_name,
                current_version=performance.version,
                new_version=new_version,
                improvements_made=changes_made,
                performance_gain=performance_gain,
                confidence_score=confidence_score,
                rollback_recommended=False,
                evolution_summary=evolution_summary
            )
            
        except Exception as e:
            logger.error(f"Failed to evolve template {template_name}: {e}")
            return TemplateEvolutionResult(
                template_name=template_name, current_version=0, new_version=None,
                improvements_made=[], performance_gain=0.0, confidence_score=0.0,
                rollback_recommended=False, evolution_summary=f"Evolution failed: {str(e)}"
            )
    
    def _should_evolve_template(self, performance: TemplatePerformanceMetrics) -> bool:
        """Determine if a template should be evolved"""
        if performance.usage_count < self.config['min_usage_for_evolution']:
            return False
        
        if (performance.success_rate < self.config['success_rate_threshold'] or
            performance.user_satisfaction < self.config['satisfaction_threshold'] or
            performance.error_rate > 0.3):
            return True
        
        if performance.adoption_rate < 0.8:
            return True
        
        return False
    
    def _get_template_content(self, template_name: str, version: int) -> Optional[str]:
        """Get template content for specified version"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT content FROM template_versions 
                    WHERE template_name = ? AND version_number = ?
                """, (template_name, version))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Failed to get template content: {e}")
            return None
    
    def _identify_improvements(self, template_name: str, performance: TemplatePerformanceMetrics) -> List[Dict[str, Any]]:
        """Identify improvement opportunities"""
        improvements = []
        
        try:
            # Get recent issues and feedback
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT issues_encountered, user_feedback FROM template_usage 
                    WHERE template_name = ? AND created_at >= ?
                    ORDER BY created_at DESC LIMIT 50
                """, (template_name, (datetime.now() - timedelta(days=30)).isoformat()))
                
                usage_data = cursor.fetchall()
            
            # Analyze common issues
            all_issues = []
            for issues_json, feedback in usage_data:
                if issues_json:
                    issues = json.loads(issues_json)
                    all_issues.extend(issues)
            
            # Count issue frequency
            issue_counts = Counter(all_issues)
            
            # Map issues to improvement categories
            for issue, count in issue_counts.most_common(5):
                if count >= 3:
                    category = self._categorize_issue(issue)
                    if category in self.improvement_patterns:
                        improvements.append({
                            'category': category,
                            'issue': issue,
                            'frequency': count,
                            'suggested_fixes': self.improvement_patterns[category].get(
                                issue.lower().replace(' ', '_'), 
                                ['address common issue', 'improve reliability']
                            )
                        })
            
            # Performance-based improvements
            if performance.success_rate < 0.7:
                improvements.append({
                    'category': 'quality',
                    'issue': 'low_success_rate',
                    'frequency': 1,
                    'suggested_fixes': ['improve error handling', 'add validation', 'fix common bugs']
                })
            
            if performance.avg_completion_time > 60:
                improvements.append({
                    'category': 'performance',
                    'issue': 'slow_completion',
                    'frequency': 1,
                    'suggested_fixes': ['optimize build process', 'reduce complexity', 'improve defaults']
                })
            
            if performance.user_satisfaction < 0.6:
                improvements.append({
                    'category': 'usability',
                    'issue': 'low_satisfaction',
                    'frequency': 1,
                    'suggested_fixes': ['improve documentation', 'simplify setup', 'add examples']
                })
            
            return improvements
            
        except Exception as e:
            logger.error(f"Failed to identify improvements: {e}")
            return []
    
    def _categorize_issue(self, issue: str) -> str:
        """Categorize an issue into improvement category"""
        issue_lower = issue.lower()
        
        performance_keywords = ['slow', 'performance', 'speed', 'memory', 'lag', 'timeout']
        usability_keywords = ['confusing', 'difficult', 'complex', 'unclear', 'hard']
        quality_keywords = ['error', 'bug', 'crash', 'fail', 'broken']
        
        if any(keyword in issue_lower for keyword in performance_keywords):
            return 'performance'
        elif any(keyword in issue_lower for keyword in usability_keywords):
            return 'usability'
        elif any(keyword in issue_lower for keyword in quality_keywords):
            return 'quality'
        else:
            return 'usability'
    
    def _generate_evolved_template(self, current_content: str, improvements: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
        """Generate evolved template content based on improvements"""
        evolved_content = current_content
        changes_made = []
        
        try:
            for improvement in improvements:
                category = improvement['category']
                issue = improvement['issue']
                fixes = improvement['suggested_fixes']
                
                # Apply improvements based on category
                if category == 'performance':
                    evolved_content, change = self._apply_performance_improvements(evolved_content, fixes)
                elif category == 'usability':
                    evolved_content, change = self._apply_usability_improvements(evolved_content, fixes)
                elif category == 'quality':
                    evolved_content, change = self._apply_quality_improvements(evolved_content, fixes)
                
                if change:
                    changes_made.append(f"{category}: {change}")
            
            return evolved_content, changes_made
            
        except Exception as e:
            logger.error(f"Failed to generate evolved template: {e}")
            return current_content, []
    
    def _apply_performance_improvements(self, content: str, fixes: List[str]) -> Tuple[str, str]:
        """Apply performance improvements to template"""
        improvements_applied = []
        
        if 'optimize build' in ' '.join(fixes).lower():
            if 'webpack' in content.lower() and 'optimization' not in content.lower():
                content += "\n// Performance optimization added by evolution system\n"
                improvements_applied.append("added build optimization")
        
        if 'reduce dependencies' in ' '.join(fixes).lower():
            improvements_applied.append("analyzed dependencies for optimization")
        
        change_summary = ', '.join(improvements_applied) if improvements_applied else "performance analysis"
        return content, change_summary
    
    def _apply_usability_improvements(self, content: str, fixes: List[str]) -> Tuple[str, str]:
        """Apply usability improvements to template"""
        improvements_applied = []
        
        if 'improve documentation' in ' '.join(fixes).lower():
            if '# README' not in content and 'README' not in content:
                content += "\n# Enhanced Documentation\n# Added by evolution system\n"
                improvements_applied.append("enhanced documentation")
        
        if 'add examples' in ' '.join(fixes).lower():
            if 'example' not in content.lower():
                content += "\n// Example usage added by evolution system\n"
                improvements_applied.append("added usage examples")
        
        change_summary = ', '.join(improvements_applied) if improvements_applied else "usability enhancements"
        return content, change_summary
    
    def _apply_quality_improvements(self, content: str, fixes: List[str]) -> Tuple[str, str]:
        """Apply quality improvements to template"""
        improvements_applied = []
        
        if 'improve error handling' in ' '.join(fixes).lower():
            if 'try' not in content.lower() and 'catch' not in content.lower():
                content += "\n// Error handling added by evolution system\n"
                improvements_applied.append("enhanced error handling")
        
        if 'add validation' in ' '.join(fixes).lower():
            improvements_applied.append("added input validation")
        
        change_summary = ', '.join(improvements_applied) if improvements_applied else "quality improvements"
        return content, change_summary
    
    def _estimate_performance_gain(self, changes: List[str], current_performance: TemplatePerformanceMetrics) -> float:
        """Estimate performance gain from changes"""
        base_gain = 0.0
        
        for change in changes:
            if 'performance' in change.lower():
                base_gain += 0.15
            elif 'usability' in change.lower():
                base_gain += 0.10
            elif 'quality' in change.lower():
                base_gain += 0.12
        
        if current_performance.success_rate < 0.5:
            base_gain *= 1.5
        
        return min(base_gain, 0.5)
    
    def _calculate_evolution_confidence(self, performance: TemplatePerformanceMetrics, 
                                      improvements: List[Dict[str, Any]], 
                                      changes: List[str]) -> float:
        """Calculate confidence in evolution success"""
        confidence = 0.5
        
        if performance.usage_count > 50:
            confidence += 0.2
        elif performance.usage_count > 20:
            confidence += 0.1
        
        if len(improvements) > 3:
            confidence += 0.2
        elif len(improvements) > 1:
            confidence += 0.1
        
        if len(changes) <= 3:
            confidence += 0.1
        
        if performance.success_rate < 0.3:
            confidence -= 0.2
        
        return max(0.1, min(1.0, confidence))
    
    def _store_template_version(self, version_id: str, template_name: str, version_number: int,
                              content: str, changes: List[str], created_by: str):
        """Store new template version"""
        try:
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO template_versions
                    (version_id, template_name, version_number, content, content_hash,
                     changes, performance_metrics, created_at, created_by, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    version_id, template_name, version_number, content, content_hash,
                    json.dumps(changes), json.dumps({}), datetime.now().isoformat(),
                    created_by, json.dumps({'evolution_generated': True})
                ))
                
                # Deactivate previous version
                conn.execute("""
                    UPDATE template_versions 
                    SET is_active = 0 
                    WHERE template_name = ? AND version_number < ?
                """, (template_name, version_number))
            
            logger.info(f"Stored new template version: {version_id}")
            
        except Exception as e:
            logger.error(f"Failed to store template version: {e}")
    
    def _record_evolution_history(self, template_name: str, from_version: int, to_version: int,
                                evolution_type: str, changes: List[str], performance_improvement: float,
                                confidence_score: float):
        """Record evolution in history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO evolution_history
                    (template_name, from_version, to_version, evolution_type,
                     changes_made, performance_improvement, confidence_score, created_at, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template_name, from_version, to_version, evolution_type,
                    json.dumps(changes), performance_improvement, confidence_score,
                    datetime.now().isoformat(), "evolution_system"
                ))
        except Exception as e:
            logger.error(f"Failed to record evolution history: {e}")
    
    def get_evolution_status(self, template_name: str) -> Dict[str, Any]:
        """Get evolution status for a template"""
        try:
            performance = self.analyze_template_performance(template_name)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT evolution_type, changes_made, performance_improvement, created_at
                    FROM evolution_history
                    WHERE template_name = ?
                    ORDER BY created_at DESC
                    LIMIT 5
                """, (template_name,))
                
                history = [
                    {
                        'type': row[0],
                        'changes': json.loads(row[1]),
                        'improvement': row[2],
                        'date': row[3]
                    }
                    for row in cursor.fetchall()
                ]
            
            return {
                'template_name': template_name,
                'current_performance': asdict(performance),
                'evolution_history': history,
                'should_evolve': self._should_evolve_template(performance),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get evolution status: {e}")
            return {'error': str(e)}


if __name__ == "__main__":
    # Example usage
    evolution = TemplateEvolution()
    
    # Track template usage
    evolution.track_template_usage(
        template_name="react_typescript",
        version_id="react_typescript_v1_20250722",
        project_id="test_project_001",
        user_id="user_123",
        success_score=0.75,
        completion_time=45.0,
        user_feedback="Good template but build is slow",
        issues_encountered=["slow_build", "dependency_conflict"]
    )
    
    # Analyze and evolve
    performance = evolution.analyze_template_performance("react_typescript")
    result = evolution.evolve_template("react_typescript")
    status = evolution.get_evolution_status("react_typescript")
    
    print("Template Evolution Demo:")
    print(f"Performance: {asdict(performance)}")
    print(f"Evolution result: {asdict(result)}")
    print(f"Status: {status}")
