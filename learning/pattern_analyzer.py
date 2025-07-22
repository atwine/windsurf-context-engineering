"""
Pattern Analyzer - Advanced pattern recognition and analysis system

This module provides sophisticated pattern analysis capabilities to identify
success and failure patterns, predict project outcomes, and generate
intelligent recommendations based on historical data.
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import numpy as np
import re

logger = logging.getLogger(__name__)

@dataclass
class Pattern:
    """Represents an identified pattern"""
    pattern_id: str
    pattern_type: str  # success, failure, neutral
    name: str
    description: str
    confidence: float  # 0.0 to 1.0
    frequency: int
    success_rate: float
    impact_score: float
    conditions: List[str]
    examples: List[str]
    recommendations: List[str]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]

@dataclass
class PatternAnalysisResult:
    """Result of pattern analysis"""
    total_patterns: int
    success_patterns: List[Pattern]
    failure_patterns: List[Pattern]
    neutral_patterns: List[Pattern]
    correlations: Dict[str, float]
    predictions: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float

class PatternAnalyzer:
    """
    Advanced pattern recognition and analysis system
    """
    
    def __init__(self, db_path: str = "pattern_analysis.db"):
        """Initialize the pattern analyzer"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Analysis configuration
        self.config = {
            'min_pattern_frequency': 3,
            'success_threshold': 0.7,
            'failure_threshold': 0.3,
            'confidence_threshold': 0.6,
            'max_patterns_per_type': 20,
            'similarity_threshold': 0.8,
            'prediction_window_days': 90
        }
        
        logger.info("Pattern analyzer initialized")
    
    def _init_database(self):
        """Initialize the pattern analysis database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS identified_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT UNIQUE NOT NULL,
                    pattern_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    frequency INTEGER NOT NULL,
                    success_rate REAL NOT NULL,
                    impact_score REAL NOT NULL,
                    conditions TEXT NOT NULL,
                    examples TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS pattern_correlations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern1_id TEXT NOT NULL,
                    pattern2_id TEXT NOT NULL,
                    correlation_score REAL NOT NULL,
                    correlation_type TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_patterns_type ON identified_patterns(pattern_type);
                CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON identified_patterns(confidence);
            """)
    
    def analyze_project_patterns(self, project_data: List[Dict[str, Any]]) -> PatternAnalysisResult:
        """Analyze patterns from project data"""
        try:
            if len(project_data) < self.config['min_pattern_frequency']:
                return PatternAnalysisResult(
                    total_patterns=0,
                    success_patterns=[],
                    failure_patterns=[],
                    neutral_patterns=[],
                    correlations={},
                    predictions={},
                    recommendations=[],
                    confidence_score=0.0
                )
            
            # Extract features from project data
            features = self._extract_project_features(project_data)
            
            # Identify patterns
            success_patterns = self._identify_success_patterns(project_data, features)
            failure_patterns = self._identify_failure_patterns(project_data, features)
            neutral_patterns = self._identify_neutral_patterns(project_data, features)
            
            # Calculate correlations
            correlations = self._calculate_pattern_correlations(
                success_patterns + failure_patterns + neutral_patterns
            )
            
            # Generate predictions and recommendations
            predictions = self._generate_pattern_predictions(features)
            recommendations = self._generate_pattern_recommendations(
                success_patterns, failure_patterns, correlations
            )
            
            # Calculate confidence
            all_patterns = success_patterns + failure_patterns + neutral_patterns
            confidence_score = np.mean([p.confidence for p in all_patterns]) if all_patterns else 0.0
            
            # Store patterns
            for pattern in all_patterns:
                self._store_pattern(pattern)
            
            result = PatternAnalysisResult(
                total_patterns=len(all_patterns),
                success_patterns=success_patterns,
                failure_patterns=failure_patterns,
                neutral_patterns=neutral_patterns,
                correlations=correlations,
                predictions=predictions,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
            logger.info(f"Analyzed {len(project_data)} projects, identified {len(all_patterns)} patterns")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze project patterns: {e}")
            return PatternAnalysisResult(
                total_patterns=0,
                success_patterns=[],
                failure_patterns=[],
                neutral_patterns=[],
                correlations={},
                predictions={},
                recommendations=[],
                confidence_score=0.0
            )
    
    def _extract_project_features(self, project_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract features from project data for pattern analysis"""
        features = {
            'technologies': defaultdict(int),
            'project_types': defaultdict(int),
            'team_sizes': [],
            'durations': [],
            'success_scores': [],
            'quality_scores': [],
            'common_issues': defaultdict(int),
            'patterns_used': defaultdict(int)
        }
        
        for project in project_data:
            if 'technologies' in project:
                for tech in project['technologies']:
                    features['technologies'][tech.lower()] += 1
            
            if 'project_type' in project:
                features['project_types'][project['project_type']] += 1
            
            if 'team_size' in project:
                features['team_sizes'].append(project['team_size'])
            
            if 'duration' in project:
                features['durations'].append(project['duration'])
            
            if 'success_score' in project:
                features['success_scores'].append(project['success_score'])
            
            if 'quality_score' in project:
                features['quality_scores'].append(project['quality_score'])
            
            if 'issues' in project:
                for issue in project['issues']:
                    features['common_issues'][issue.lower()] += 1
            
            if 'patterns' in project:
                for pattern in project['patterns']:
                    features['patterns_used'][pattern.lower()] += 1
        
        return features
    
    def _identify_success_patterns(self, project_data: List[Dict[str, Any]], features: Dict[str, Any]) -> List[Pattern]:
        """Identify patterns that correlate with project success"""
        success_patterns = []
        
        try:
            successful_projects = [
                p for p in project_data 
                if p.get('success_score', 0) >= self.config['success_threshold']
            ]
            
            if len(successful_projects) < self.config['min_pattern_frequency']:
                return success_patterns
            
            # Analyze technology patterns
            success_techs = defaultdict(int)
            total_successful = len(successful_projects)
            
            for project in successful_projects:
                if 'technologies' in project:
                    for tech in project['technologies']:
                        success_techs[tech.lower()] += 1
            
            # Create success patterns for high-performing technologies
            for tech, count in success_techs.items():
                if count >= self.config['min_pattern_frequency']:
                    total_tech_usage = features['technologies'][tech]
                    overall_success_rate = count / total_tech_usage if total_tech_usage > 0 else 0
                    
                    if overall_success_rate > 0.6:
                        pattern = Pattern(
                            pattern_id=f"success_tech_{tech}",
                            pattern_type="success",
                            name=f"Successful use of {tech}",
                            description=f"Projects using {tech} have {overall_success_rate:.1%} success rate",
                            confidence=min(count / 10.0, 1.0),
                            frequency=count,
                            success_rate=overall_success_rate,
                            impact_score=overall_success_rate * (count / total_successful),
                            conditions=[f"technology:{tech}"],
                            examples=[p.get('project_id', 'unknown') for p in successful_projects if tech in p.get('technologies', [])][:3],
                            recommendations=[f"Consider using {tech} for similar projects"],
                            created_at=datetime.now().isoformat(),
                            updated_at=datetime.now().isoformat(),
                            metadata={'category': 'technical', 'type': 'technology'}
                        )
                        success_patterns.append(pattern)
            
            return success_patterns[:self.config['max_patterns_per_type']]
            
        except Exception as e:
            logger.error(f"Failed to identify success patterns: {e}")
            return []
    
    def _identify_failure_patterns(self, project_data: List[Dict[str, Any]], features: Dict[str, Any]) -> List[Pattern]:
        """Identify patterns that correlate with project failure"""
        failure_patterns = []
        
        try:
            failed_projects = [
                p for p in project_data 
                if p.get('success_score', 1.0) <= self.config['failure_threshold']
            ]
            
            if len(failed_projects) < self.config['min_pattern_frequency']:
                return failure_patterns
            
            # Analyze failure issues
            failure_issues = defaultdict(int)
            total_failed = len(failed_projects)
            
            for project in failed_projects:
                if 'issues' in project:
                    for issue in project['issues']:
                        failure_issues[issue.lower()] += 1
            
            # Create failure patterns for common issues
            for issue, count in failure_issues.items():
                if count >= self.config['min_pattern_frequency']:
                    total_issue_occurrence = features['common_issues'][issue]
                    overall_failure_rate = count / total_issue_occurrence if total_issue_occurrence > 0 else 0
                    
                    if overall_failure_rate > 0.5:
                        pattern = Pattern(
                            pattern_id=f"failure_issue_{issue.replace(' ', '_')}",
                            pattern_type="failure",
                            name=f"High-risk issue: {issue}",
                            description=f"Projects with {issue} have {overall_failure_rate:.1%} failure rate",
                            confidence=min(count / 8.0, 1.0),
                            frequency=count,
                            success_rate=1.0 - overall_failure_rate,
                            impact_score=overall_failure_rate * (count / total_failed),
                            conditions=[f"issue:{issue}"],
                            examples=[p.get('project_id', 'unknown') for p in failed_projects if issue in p.get('issues', [])][:3],
                            recommendations=[f"Implement preventive measures for {issue}", f"Monitor closely for {issue} symptoms"],
                            created_at=datetime.now().isoformat(),
                            updated_at=datetime.now().isoformat(),
                            metadata={'category': 'quality', 'type': 'issue'}
                        )
                        failure_patterns.append(pattern)
            
            return failure_patterns[:self.config['max_patterns_per_type']]
            
        except Exception as e:
            logger.error(f"Failed to identify failure patterns: {e}")
            return []
    
    def _identify_neutral_patterns(self, project_data: List[Dict[str, Any]], features: Dict[str, Any]) -> List[Pattern]:
        """Identify neutral patterns"""
        neutral_patterns = []
        
        try:
            for tech, count in features['technologies'].items():
                if count >= self.config['min_pattern_frequency']:
                    tech_successes = sum(1 for p in project_data 
                                       if tech in p.get('technologies', []) and 
                                       p.get('success_score', 0) >= self.config['success_threshold'])
                    
                    success_rate = tech_successes / count if count > 0 else 0
                    
                    if 0.4 <= success_rate <= 0.6:
                        pattern = Pattern(
                            pattern_id=f"neutral_tech_{tech}",
                            pattern_type="neutral",
                            name=f"Neutral technology: {tech}",
                            description=f"{tech} has balanced outcomes ({success_rate:.1%} success rate)",
                            confidence=min(count / 15.0, 1.0),
                            frequency=count,
                            success_rate=success_rate,
                            impact_score=0.3,
                            conditions=[f"technology:{tech}"],
                            examples=[],
                            recommendations=[f"{tech} is a stable choice with predictable outcomes"],
                            created_at=datetime.now().isoformat(),
                            updated_at=datetime.now().isoformat(),
                            metadata={'category': 'technical', 'type': 'technology'}
                        )
                        neutral_patterns.append(pattern)
            
            return neutral_patterns[:self.config['max_patterns_per_type'] // 2]
            
        except Exception as e:
            logger.error(f"Failed to identify neutral patterns: {e}")
            return []
    
    def _calculate_pattern_correlations(self, patterns: List[Pattern]) -> Dict[str, float]:
        """Calculate correlations between patterns"""
        correlations = {}
        
        try:
            for i, pattern1 in enumerate(patterns):
                for j, pattern2 in enumerate(patterns[i+1:], i+1):
                    correlation = self._calculate_pattern_similarity(pattern1, pattern2)
                    
                    if abs(correlation) > 0.3:
                        key = f"{pattern1.pattern_id}:{pattern2.pattern_id}"
                        correlations[key] = correlation
                        self._store_pattern_correlation(pattern1.pattern_id, pattern2.pattern_id, correlation)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Failed to calculate pattern correlations: {e}")
            return {}
    
    def _calculate_pattern_similarity(self, pattern1: Pattern, pattern2: Pattern) -> float:
        """Calculate similarity between two patterns"""
        try:
            cat1 = pattern1.metadata.get('category', 'unknown')
            cat2 = pattern2.metadata.get('category', 'unknown')
            category_sim = 1.0 if cat1 == cat2 else 0.0
            
            impact_diff = abs(pattern1.impact_score - pattern2.impact_score)
            impact_sim = 1.0 - impact_diff
            
            type_sim = 1.0 if pattern1.pattern_type == pattern2.pattern_type else -0.5
            
            similarity = (category_sim * 0.4 + impact_sim * 0.3 + type_sim * 0.3)
            return max(-1.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Failed to calculate pattern similarity: {e}")
            return 0.0
    
    def _generate_pattern_predictions(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictions based on patterns"""
        try:
            predictions = {
                'success_probability': 0.5,
                'risk_factors': [],
                'recommended_actions': [],
                'confidence': 0.0
            }
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT pattern_type, name, confidence, success_rate, conditions, recommendations
                    FROM identified_patterns
                    WHERE confidence >= ?
                    ORDER BY confidence DESC
                """, (self.config['confidence_threshold'],))
                
                stored_patterns = cursor.fetchall()
            
            if stored_patterns:
                success_factors = []
                risk_factors = []
                
                for pattern_type, name, confidence, success_rate, conditions_json, recommendations_json in stored_patterns:
                    if pattern_type == 'success':
                        success_factors.append(success_rate * confidence)
                        predictions['recommended_actions'].extend(json.loads(recommendations_json)[:2])
                    elif pattern_type == 'failure':
                        risk_factors.append((1.0 - success_rate) * confidence)
                        predictions['risk_factors'].append(name)
                
                if success_factors or risk_factors:
                    success_boost = sum(success_factors) / len(success_factors) if success_factors else 0
                    risk_penalty = sum(risk_factors) / len(risk_factors) if risk_factors else 0
                    
                    predictions['success_probability'] = max(0.1, min(0.9, 0.5 + success_boost - risk_penalty))
                    predictions['confidence'] = min(len(success_factors + risk_factors) / 10.0, 1.0)
                
                predictions['recommended_actions'] = list(set(predictions['recommended_actions']))[:5]
                predictions['risk_factors'] = list(set(predictions['risk_factors']))[:5]
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to generate predictions: {e}")
            return {'success_probability': 0.5, 'risk_factors': [], 'recommended_actions': [], 'confidence': 0.0}
    
    def _generate_pattern_recommendations(self, success_patterns: List[Pattern], 
                                        failure_patterns: List[Pattern], 
                                        correlations: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            for pattern in success_patterns[:5]:
                if pattern.confidence > 0.7:
                    recommendations.extend(pattern.recommendations[:2])
            
            for pattern in failure_patterns[:3]:
                if pattern.confidence > 0.6:
                    recommendations.append(f"Avoid: {pattern.name}")
            
            return list(set(recommendations))[:10]
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def _store_pattern(self, pattern: Pattern):
        """Store pattern in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO identified_patterns
                    (pattern_id, pattern_type, name, description, confidence,
                     frequency, success_rate, impact_score, conditions,
                     examples, recommendations, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_id, pattern.pattern_type, pattern.name, pattern.description,
                    pattern.confidence, pattern.frequency, pattern.success_rate, pattern.impact_score,
                    json.dumps(pattern.conditions), json.dumps(pattern.examples),
                    json.dumps(pattern.recommendations), pattern.created_at, pattern.updated_at,
                    json.dumps(pattern.metadata)
                ))
        except Exception as e:
            logger.error(f"Failed to store pattern: {e}")
    
    def _store_pattern_correlation(self, pattern1_id: str, pattern2_id: str, correlation: float):
        """Store pattern correlation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO pattern_correlations
                    (pattern1_id, pattern2_id, correlation_score, correlation_type, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    pattern1_id, pattern2_id, correlation,
                    "positive" if correlation > 0 else "negative",
                    datetime.now().isoformat()
                ))
        except Exception as e:
            logger.error(f"Failed to store correlation: {e}")
    
    def get_pattern_insights(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get pattern-based insights for a project context"""
        try:
            features = {
                'technologies': {tech: 1 for tech in project_context.get('technologies', [])},
                'project_types': {project_context.get('project_type', 'unknown'): 1},
                'team_sizes': [project_context.get('team_size', 5)],
                'patterns_used': {pattern: 1 for pattern in project_context.get('patterns', [])}
            }
            
            predictions = self._generate_pattern_predictions(features)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT pattern_type, name, description, confidence, recommendations
                    FROM identified_patterns
                    WHERE confidence >= ?
                    ORDER BY confidence DESC
                    LIMIT 10
                """, (self.config['confidence_threshold'],))
                
                relevant_patterns = [
                    {
                        'type': row[0],
                        'name': row[1],
                        'description': row[2],
                        'confidence': row[3],
                        'recommendations': json.loads(row[4])
                    }
                    for row in cursor.fetchall()
                ]
            
            return {
                'predictions': predictions,
                'relevant_patterns': relevant_patterns,
                'insights_generated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get pattern insights: {e}")
            return {'predictions': {}, 'relevant_patterns': [], 'error': str(e)}
    
    def get_pattern_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary statistics for pattern analysis"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Total patterns count
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM identified_patterns
                    WHERE created_at >= ?
                """, (cutoff_date,))
                total_patterns = cursor.fetchone()[0] or 0
                
                # Pattern types distribution
                cursor = conn.execute("""
                    SELECT pattern_type, COUNT(*) FROM identified_patterns
                    WHERE created_at >= ?
                    GROUP BY pattern_type
                """, (cutoff_date,))
                pattern_types = dict(cursor.fetchall())
                
                # Average confidence
                cursor = conn.execute("""
                    SELECT AVG(confidence) FROM identified_patterns
                    WHERE created_at >= ?
                """, (cutoff_date,))
                avg_confidence = cursor.fetchone()[0] or 0.0
                
                return {
                    'total_patterns': total_patterns,
                    'pattern_types': pattern_types,
                    'avg_confidence': avg_confidence,
                    'period_days': days
                }
                
        except Exception as e:
            logger.error(f"Failed to get pattern summary: {e}")
            return {
                'total_patterns': 0,
                'pattern_types': {},
                'avg_confidence': 0.0,
                'period_days': days
            }
    
    def get_recommendations(self, project_context: Dict[str, Any], max_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get pattern-based recommendations for a project"""
        try:
            insights = self.get_pattern_insights(project_context)
            recommendations = []
            
            # Extract recommendations from relevant patterns
            for pattern in insights.get('relevant_patterns', []):
                pattern_recs = pattern.get('recommendations', [])
                for rec in pattern_recs[:2]:  # Top 2 from each pattern
                    recommendations.append({
                        'recommendation': rec,
                        'confidence': pattern['confidence'],
                        'pattern_type': pattern['type'],
                        'source_pattern': pattern['name']
                    })
            
            # Sort by confidence and return top recommendations
            recommendations.sort(key=lambda x: x['confidence'], reverse=True)
            return recommendations[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []
    
    def analyze_recent_patterns(self, days: int = 7) -> List[Dict[str, Any]]:
        """Analyze patterns from recent project data"""
        try:
            # This would typically analyze recent project outcomes
            # For now, return existing patterns as a placeholder
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT pattern_id, pattern_type, name, confidence
                    FROM identified_patterns
                    WHERE created_at >= ?
                    ORDER BY created_at DESC
                """, ((datetime.now() - timedelta(days=days)).isoformat(),))
                
                patterns = [
                    {
                        'pattern_id': row[0],
                        'pattern_type': row[1],
                        'name': row[2],
                        'confidence': row[3]
                    }
                    for row in cursor.fetchall()
                ]
                
                return patterns
                
        except Exception as e:
            logger.error(f"Failed to analyze recent patterns: {e}")
            return []
    
    def get_pattern_insights_by_period(self, days: int) -> Dict[str, Any]:
        """Get pattern insights for a specific time period"""
        try:
            # Create a context for the time period analysis
            context = {
                'analysis_type': 'temporal',
                'period_days': days,
                'analysis_date': datetime.now().isoformat()
            }
            
            return self.get_pattern_insights(context)
            
        except Exception as e:
            logger.error(f"Failed to get pattern insights by period: {e}")
            return {'predictions': {}, 'relevant_patterns': [], 'error': str(e)}


if __name__ == "__main__":
    # Example usage
    analyzer = PatternAnalyzer()
    
    project_data = [
        {
            'project_id': 'proj_001',
            'project_type': 'web_application',
            'technologies': ['react', 'typescript', 'node.js'],
            'team_size': 4,
            'duration': 12,
            'success_score': 0.85,
            'quality_score': 0.78,
            'issues': ['build_error'],
            'patterns': ['component_structure', 'state_management']
        }
    ]
    
    result = analyzer.analyze_project_patterns(project_data)
    print(f"Pattern analysis complete: {result.total_patterns} patterns identified")
