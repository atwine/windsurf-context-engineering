"""
Metrics Tracker - Comprehensive performance metrics tracking and analysis system

This module provides advanced metrics tracking capabilities for monitoring
development speed, code quality trends, user satisfaction, ROI calculation,
and comparative analysis across projects and time periods.
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import numpy as np
import statistics
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics that can be tracked"""
    DEVELOPMENT_SPEED = "development_speed"
    CODE_QUALITY = "code_quality"
    USER_SATISFACTION = "user_satisfaction"
    PROJECT_SUCCESS = "project_success"
    TEMPLATE_PERFORMANCE = "template_performance"
    LEARNING_EFFECTIVENESS = "learning_effectiveness"
    ROI = "roi"
    PRODUCTIVITY = "productivity"

@dataclass
class MetricEntry:
    """Represents a single metric measurement"""
    metric_id: str
    metric_type: MetricType
    project_id: str
    user_id: str
    metric_name: str
    metric_value: float
    unit: str
    context: Dict[str, Any]
    timestamp: str
    tags: List[str]
    metadata: Dict[str, Any]

@dataclass
class MetricTrend:
    """Represents a trend analysis for a metric"""
    metric_name: str
    period_days: int
    trend_direction: str  # improving, declining, stable
    trend_strength: float  # 0.0 to 1.0
    current_value: float
    previous_value: float
    change_percentage: float
    confidence_level: float
    data_points: int

@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    report_id: str
    generated_at: str
    period_start: str
    period_end: str
    summary_metrics: Dict[str, float]
    trends: List[MetricTrend]
    insights: List[str]
    recommendations: List[str]
    comparative_analysis: Dict[str, Any]
    roi_analysis: Dict[str, float]

class MetricsTracker:
    """
    Comprehensive performance metrics tracking and analysis system
    """
    
    def __init__(self, db_path: str = "metrics_tracking.db"):
        """Initialize the metrics tracker"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Tracking configuration
        self.config = {
            'trend_analysis_min_points': 5,
            'trend_confidence_threshold': 0.7,
            'roi_calculation_period_days': 90,
            'performance_baseline_days': 30,
            'metric_retention_days': 365,
            'outlier_threshold': 2.0,  # Standard deviations
            'trend_sensitivity': 0.1,  # Minimum change to detect trend
            'aggregation_intervals': ['daily', 'weekly', 'monthly']
        }
        
        # Metric definitions and benchmarks
        self.metric_definitions = {
            'development_speed': {
                'unit': 'hours_per_feature',
                'lower_is_better': True,
                'benchmark_excellent': 8.0,
                'benchmark_good': 16.0,
                'benchmark_poor': 32.0
            },
            'code_quality_score': {
                'unit': 'score_0_to_1',
                'lower_is_better': False,
                'benchmark_excellent': 0.9,
                'benchmark_good': 0.7,
                'benchmark_poor': 0.5
            },
            'user_satisfaction': {
                'unit': 'score_0_to_1',
                'lower_is_better': False,
                'benchmark_excellent': 0.8,
                'benchmark_good': 0.6,
                'benchmark_poor': 0.4
            },
            'project_success_rate': {
                'unit': 'percentage',
                'lower_is_better': False,
                'benchmark_excellent': 0.9,
                'benchmark_good': 0.7,
                'benchmark_poor': 0.5
            },
            'template_adoption_rate': {
                'unit': 'percentage',
                'lower_is_better': False,
                'benchmark_excellent': 0.8,
                'benchmark_good': 0.6,
                'benchmark_poor': 0.3
            },
            'learning_improvement_rate': {
                'unit': 'percentage_per_month',
                'lower_is_better': False,
                'benchmark_excellent': 0.2,
                'benchmark_good': 0.1,
                'benchmark_poor': 0.05
            }
        }
        
        logger.info("Metrics tracker initialized")
    
    def _init_database(self):
        """Initialize the metrics tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS metric_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id TEXT UNIQUE NOT NULL,
                    metric_type TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    context TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    metadata TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS metric_aggregations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    aggregation_type TEXT NOT NULL,
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    aggregated_value REAL NOT NULL,
                    data_points INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS performance_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id TEXT UNIQUE NOT NULL,
                    generated_at TEXT NOT NULL,
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    report_data TEXT NOT NULL,
                    report_type TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS metric_baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT UNIQUE NOT NULL,
                    baseline_value REAL NOT NULL,
                    baseline_date TEXT NOT NULL,
                    confidence_level REAL NOT NULL,
                    data_points INTEGER NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_metric_entries_name ON metric_entries(metric_name);
                CREATE INDEX IF NOT EXISTS idx_metric_entries_timestamp ON metric_entries(timestamp);
                CREATE INDEX IF NOT EXISTS idx_metric_entries_project ON metric_entries(project_id);
                CREATE INDEX IF NOT EXISTS idx_metric_aggregations_name ON metric_aggregations(metric_name);
                CREATE INDEX IF NOT EXISTS idx_performance_reports_generated ON performance_reports(generated_at);
            """)
    
    def track_metric(self, metric: MetricEntry) -> bool:
        """Track a single metric measurement"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO metric_entries
                    (metric_id, metric_type, project_id, user_id, metric_name,
                     metric_value, unit, context, timestamp, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric.metric_id,
                    metric.metric_type.value,
                    metric.project_id,
                    metric.user_id,
                    metric.metric_name,
                    metric.metric_value,
                    metric.unit,
                    json.dumps(metric.context),
                    metric.timestamp,
                    json.dumps(metric.tags),
                    json.dumps(metric.metadata)
                ))
            
            logger.info(f"Tracked metric: {metric.metric_name} = {metric.metric_value} {metric.unit}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track metric: {e}")
            return False
    
    def track_development_speed(self, project_id: str, user_id: str, 
                              features_completed: int, time_spent_hours: float,
                              context: Dict[str, Any] = None) -> bool:
        """Track development speed metrics"""
        try:
            hours_per_feature = time_spent_hours / features_completed if features_completed > 0 else 0
            
            metric = MetricEntry(
                metric_id=f"dev_speed_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                metric_type=MetricType.DEVELOPMENT_SPEED,
                project_id=project_id,
                user_id=user_id,
                metric_name="development_speed",
                metric_value=hours_per_feature,
                unit="hours_per_feature",
                context=context or {},
                timestamp=datetime.now().isoformat(),
                tags=["productivity", "speed"],
                metadata={"features_completed": features_completed, "time_spent_hours": time_spent_hours}
            )
            
            return self.track_metric(metric)
            
        except Exception as e:
            logger.error(f"Failed to track development speed: {e}")
            return False
    
    def track_code_quality(self, project_id: str, user_id: str, quality_score: float,
                          quality_metrics: Dict[str, float] = None,
                          context: Dict[str, Any] = None) -> bool:
        """Track code quality metrics"""
        try:
            metric = MetricEntry(
                metric_id=f"code_quality_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                metric_type=MetricType.CODE_QUALITY,
                project_id=project_id,
                user_id=user_id,
                metric_name="code_quality_score",
                metric_value=quality_score,
                unit="score_0_to_1",
                context=context or {},
                timestamp=datetime.now().isoformat(),
                tags=["quality", "code"],
                metadata=quality_metrics or {}
            )
            
            return self.track_metric(metric)
            
        except Exception as e:
            logger.error(f"Failed to track code quality: {e}")
            return False
    
    def track_user_satisfaction(self, project_id: str, user_id: str, satisfaction_score: float,
                              feedback_summary: str = None, context: Dict[str, Any] = None) -> bool:
        """Track user satisfaction metrics"""
        try:
            metric = MetricEntry(
                metric_id=f"user_satisfaction_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                metric_type=MetricType.USER_SATISFACTION,
                project_id=project_id,
                user_id=user_id,
                metric_name="user_satisfaction",
                metric_value=satisfaction_score,
                unit="score_0_to_1",
                context=context or {},
                timestamp=datetime.now().isoformat(),
                tags=["satisfaction", "user_experience"],
                metadata={"feedback_summary": feedback_summary or ""}
            )
            
            return self.track_metric(metric)
            
        except Exception as e:
            logger.error(f"Failed to track user satisfaction: {e}")
            return False
    
    def track_project_success(self, project_id: str, user_id: str, success_score: float,
                            completion_status: str, context: Dict[str, Any] = None) -> bool:
        """Track project success metrics"""
        try:
            metric = MetricEntry(
                metric_id=f"project_success_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                metric_type=MetricType.PROJECT_SUCCESS,
                project_id=project_id,
                user_id=user_id,
                metric_name="project_success_rate",
                metric_value=success_score,
                unit="score_0_to_1",
                context=context or {},
                timestamp=datetime.now().isoformat(),
                tags=["success", "project"],
                metadata={"completion_status": completion_status}
            )
            
            return self.track_metric(metric)
            
        except Exception as e:
            logger.error(f"Failed to track project success: {e}")
            return False
    
    def analyze_metric_trends(self, metric_name: str, days: int = 30) -> MetricTrend:
        """Analyze trends for a specific metric"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT metric_value, timestamp FROM metric_entries
                    WHERE metric_name = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                """, (metric_name, cutoff_date))
                
                data_points = cursor.fetchall()
            
            if len(data_points) < self.config['trend_analysis_min_points']:
                return MetricTrend(
                    metric_name=metric_name,
                    period_days=days,
                    trend_direction="insufficient_data",
                    trend_strength=0.0,
                    current_value=0.0,
                    previous_value=0.0,
                    change_percentage=0.0,
                    confidence_level=0.0,
                    data_points=len(data_points)
                )
            
            # Extract values and calculate trend
            values = [point[0] for point in data_points]
            timestamps = [point[1] for point in data_points]
            
            # Calculate trend using linear regression
            x_values = list(range(len(values)))
            slope, intercept = np.polyfit(x_values, values, 1)
            
            # Determine trend direction and strength
            current_value = values[-1]
            previous_value = values[0]
            change_percentage = ((current_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
            
            # Determine trend direction
            if abs(slope) < self.config['trend_sensitivity']:
                trend_direction = "stable"
            elif slope > 0:
                trend_direction = "improving" if not self.metric_definitions.get(metric_name, {}).get('lower_is_better', False) else "declining"
            else:
                trend_direction = "declining" if not self.metric_definitions.get(metric_name, {}).get('lower_is_better', False) else "improving"
            
            # Calculate trend strength (correlation coefficient)
            correlation = np.corrcoef(x_values, values)[0, 1] if len(values) > 1 else 0
            trend_strength = abs(correlation)
            
            # Calculate confidence level based on data consistency
            value_std = np.std(values)
            value_mean = np.mean(values)
            coefficient_of_variation = value_std / value_mean if value_mean != 0 else 1
            confidence_level = max(0, 1 - coefficient_of_variation)
            
            return MetricTrend(
                metric_name=metric_name,
                period_days=days,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                current_value=current_value,
                previous_value=previous_value,
                change_percentage=change_percentage,
                confidence_level=confidence_level,
                data_points=len(data_points)
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze metric trends: {e}")
            return MetricTrend(
                metric_name=metric_name, period_days=days, trend_direction="error",
                trend_strength=0.0, current_value=0.0, previous_value=0.0,
                change_percentage=0.0, confidence_level=0.0, data_points=0
            )
    
    def calculate_roi(self, period_days: int = 90) -> Dict[str, float]:
        """Calculate ROI metrics for the learning system"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Calculate average development speed improvement
                cursor = conn.execute("""
                    SELECT AVG(metric_value) FROM metric_entries
                    WHERE metric_name = 'development_speed' AND timestamp >= ?
                """, (cutoff_date,))
                current_dev_speed = cursor.fetchone()[0] or 0
                
                # Get baseline development speed
                baseline_date = (datetime.now() - timedelta(days=period_days*2)).isoformat()
                cursor = conn.execute("""
                    SELECT AVG(metric_value) FROM metric_entries
                    WHERE metric_name = 'development_speed' AND timestamp < ? AND timestamp >= ?
                """, (cutoff_date, baseline_date))
                baseline_dev_speed = cursor.fetchone()[0] or current_dev_speed
                
                # Calculate speed improvement (lower is better for dev speed)
                speed_improvement = ((baseline_dev_speed - current_dev_speed) / baseline_dev_speed * 100) if baseline_dev_speed > 0 else 0
                
                # Calculate quality improvement
                cursor = conn.execute("""
                    SELECT AVG(metric_value) FROM metric_entries
                    WHERE metric_name = 'code_quality_score' AND timestamp >= ?
                """, (cutoff_date,))
                current_quality = cursor.fetchone()[0] or 0
                
                cursor = conn.execute("""
                    SELECT AVG(metric_value) FROM metric_entries
                    WHERE metric_name = 'code_quality_score' AND timestamp < ? AND timestamp >= ?
                """, (cutoff_date, baseline_date))
                baseline_quality = cursor.fetchone()[0] or current_quality
                
                quality_improvement = ((current_quality - baseline_quality) / baseline_quality * 100) if baseline_quality > 0 else 0
                
                # Calculate satisfaction improvement
                cursor = conn.execute("""
                    SELECT AVG(metric_value) FROM metric_entries
                    WHERE metric_name = 'user_satisfaction' AND timestamp >= ?
                """, (cutoff_date,))
                current_satisfaction = cursor.fetchone()[0] or 0
                
                cursor = conn.execute("""
                    SELECT AVG(metric_value) FROM metric_entries
                    WHERE metric_name = 'user_satisfaction' AND timestamp < ? AND timestamp >= ?
                """, (cutoff_date, baseline_date))
                baseline_satisfaction = cursor.fetchone()[0] or current_satisfaction
                
                satisfaction_improvement = ((current_satisfaction - baseline_satisfaction) / baseline_satisfaction * 100) if baseline_satisfaction > 0 else 0
                
                # Calculate overall ROI score
                roi_score = (speed_improvement + quality_improvement + satisfaction_improvement) / 3
                
                # Calculate productivity gain (estimated time saved)
                projects_count = conn.execute("""
                    SELECT COUNT(DISTINCT project_id) FROM metric_entries
                    WHERE timestamp >= ?
                """, (cutoff_date,)).fetchone()[0] or 1
                
                estimated_time_saved_hours = (speed_improvement / 100) * 40 * projects_count  # Assuming 40 hours per project baseline
                
                return {
                    'roi_score': roi_score,
                    'speed_improvement_percentage': speed_improvement,
                    'quality_improvement_percentage': quality_improvement,
                    'satisfaction_improvement_percentage': satisfaction_improvement,
                    'estimated_time_saved_hours': estimated_time_saved_hours,
                    'projects_analyzed': projects_count,
                    'analysis_period_days': period_days
                }
                
        except Exception as e:
            logger.error(f"Failed to calculate ROI: {e}")
            return {
                'roi_score': 0.0,
                'speed_improvement_percentage': 0.0,
                'quality_improvement_percentage': 0.0,
                'satisfaction_improvement_percentage': 0.0,
                'estimated_time_saved_hours': 0.0,
                'projects_analyzed': 0,
                'analysis_period_days': period_days
            }
    
    def generate_performance_report(self, period_days: int = 30) -> PerformanceReport:
        """Generate comprehensive performance report"""
        try:
            report_id = f"perf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            period_start = (datetime.now() - timedelta(days=period_days)).isoformat()
            period_end = datetime.now().isoformat()
            
            # Calculate summary metrics
            summary_metrics = {}
            key_metrics = ['development_speed', 'code_quality_score', 'user_satisfaction', 'project_success_rate']
            
            with sqlite3.connect(self.db_path) as conn:
                for metric in key_metrics:
                    cursor = conn.execute("""
                        SELECT AVG(metric_value), COUNT(*) FROM metric_entries
                        WHERE metric_name = ? AND timestamp >= ?
                    """, (metric, period_start))
                    
                    avg_value, count = cursor.fetchone()
                    summary_metrics[metric] = {
                        'average': avg_value or 0.0,
                        'data_points': count or 0
                    }
            
            # Analyze trends for each metric
            trends = []
            for metric in key_metrics:
                trend = self.analyze_metric_trends(metric, period_days)
                if trend.data_points >= self.config['trend_analysis_min_points']:
                    trends.append(trend)
            
            # Generate insights
            insights = self._generate_performance_insights(summary_metrics, trends)
            
            # Generate recommendations
            recommendations = self._generate_performance_recommendations(summary_metrics, trends)
            
            # Comparative analysis
            comparative_analysis = self._perform_comparative_analysis(period_days)
            
            # ROI analysis
            roi_analysis = self.calculate_roi(period_days)
            
            report = PerformanceReport(
                report_id=report_id,
                generated_at=datetime.now().isoformat(),
                period_start=period_start,
                period_end=period_end,
                summary_metrics=summary_metrics,
                trends=trends,
                insights=insights,
                recommendations=recommendations,
                comparative_analysis=comparative_analysis,
                roi_analysis=roi_analysis
            )
            
            # Store report in database
            self._store_performance_report(report)
            
            logger.info(f"Generated performance report: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return PerformanceReport(
                report_id="error_report",
                generated_at=datetime.now().isoformat(),
                period_start="",
                period_end="",
                summary_metrics={},
                trends=[],
                insights=[f"Report generation failed: {str(e)}"],
                recommendations=[],
                comparative_analysis={},
                roi_analysis={}
            )
    
    def _generate_performance_insights(self, summary_metrics: Dict[str, Any], trends: List[MetricTrend]) -> List[str]:
        """Generate performance insights from metrics and trends"""
        insights = []
        
        try:
            # Analyze development speed
            if 'development_speed' in summary_metrics:
                speed_data = summary_metrics['development_speed']
                if speed_data['data_points'] > 0:
                    avg_speed = speed_data['average']
                    benchmark = self.metric_definitions['development_speed']
                    
                    if avg_speed <= benchmark['benchmark_excellent']:
                        insights.append(f"Excellent development speed: {avg_speed:.1f} hours per feature (benchmark: {benchmark['benchmark_excellent']})")
                    elif avg_speed <= benchmark['benchmark_good']:
                        insights.append(f"Good development speed: {avg_speed:.1f} hours per feature")
                    else:
                        insights.append(f"Development speed needs improvement: {avg_speed:.1f} hours per feature (target: <{benchmark['benchmark_good']})")
            
            # Analyze code quality
            if 'code_quality_score' in summary_metrics:
                quality_data = summary_metrics['code_quality_score']
                if quality_data['data_points'] > 0:
                    avg_quality = quality_data['average']
                    benchmark = self.metric_definitions['code_quality_score']
                    
                    if avg_quality >= benchmark['benchmark_excellent']:
                        insights.append(f"Excellent code quality: {avg_quality:.2f} score (benchmark: {benchmark['benchmark_excellent']})")
                    elif avg_quality >= benchmark['benchmark_good']:
                        insights.append(f"Good code quality: {avg_quality:.2f} score")
                    else:
                        insights.append(f"Code quality needs improvement: {avg_quality:.2f} score (target: >{benchmark['benchmark_good']})")
            
            # Analyze trends
            for trend in trends:
                if trend.confidence_level >= self.config['trend_confidence_threshold']:
                    if trend.trend_direction == "improving":
                        insights.append(f"{trend.metric_name} is improving: {trend.change_percentage:+.1f}% change over {trend.period_days} days")
                    elif trend.trend_direction == "declining":
                        insights.append(f"{trend.metric_name} is declining: {trend.change_percentage:+.1f}% change over {trend.period_days} days")
                    elif trend.trend_direction == "stable":
                        insights.append(f"{trend.metric_name} is stable with {trend.change_percentage:+.1f}% change")
            
            # Data quality insights
            total_data_points = sum(metric['data_points'] for metric in summary_metrics.values())
            if total_data_points < 10:
                insights.append("Limited data available - consider increasing measurement frequency for more accurate insights")
            elif total_data_points > 100:
                insights.append("Rich dataset available - insights have high confidence level")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate performance insights: {e}")
            return ["Unable to generate insights due to data processing error"]
    
    def _generate_performance_recommendations(self, summary_metrics: Dict[str, Any], trends: List[MetricTrend]) -> List[str]:
        """Generate actionable recommendations based on performance analysis"""
        recommendations = []
        
        try:
            # Development speed recommendations
            if 'development_speed' in summary_metrics:
                speed_data = summary_metrics['development_speed']
                if speed_data['data_points'] > 0:
                    avg_speed = speed_data['average']
                    benchmark = self.metric_definitions['development_speed']
                    
                    if avg_speed > benchmark['benchmark_good']:
                        recommendations.append("Consider template optimization and automation to improve development speed")
                        recommendations.append("Analyze common bottlenecks and implement process improvements")
            
            # Code quality recommendations
            if 'code_quality_score' in summary_metrics:
                quality_data = summary_metrics['code_quality_score']
                if quality_data['data_points'] > 0:
                    avg_quality = quality_data['average']
                    benchmark = self.metric_definitions['code_quality_score']
                    
                    if avg_quality < benchmark['benchmark_good']:
                        recommendations.append("Implement additional code quality checks and linting rules")
                        recommendations.append("Consider code review process improvements")
            
            # User satisfaction recommendations
            if 'user_satisfaction' in summary_metrics:
                satisfaction_data = summary_metrics['user_satisfaction']
                if satisfaction_data['data_points'] > 0:
                    avg_satisfaction = satisfaction_data['average']
                    benchmark = self.metric_definitions['user_satisfaction']
                    
                    if avg_satisfaction < benchmark['benchmark_good']:
                        recommendations.append("Focus on user experience improvements and documentation")
                        recommendations.append("Collect more detailed user feedback to identify pain points")
            
            # Trend-based recommendations
            declining_trends = [t for t in trends if t.trend_direction == "declining" and t.confidence_level >= 0.6]
            if declining_trends:
                recommendations.append(f"Address declining trends in: {', '.join([t.metric_name for t in declining_trends])}")
            
            # Data collection recommendations
            low_data_metrics = [name for name, data in summary_metrics.items() if data['data_points'] < 5]
            if low_data_metrics:
                recommendations.append(f"Increase data collection frequency for: {', '.join(low_data_metrics)}")
            
            return recommendations[:8]  # Limit to top 8 recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate performance recommendations: {e}")
            return ["Unable to generate recommendations due to analysis error"]
    
    def _perform_comparative_analysis(self, period_days: int) -> Dict[str, Any]:
        """Perform comparative analysis across different periods and projects"""
        try:
            current_period_start = (datetime.now() - timedelta(days=period_days)).isoformat()
            previous_period_start = (datetime.now() - timedelta(days=period_days*2)).isoformat()
            previous_period_end = current_period_start
            
            comparative_analysis = {}
            
            with sqlite3.connect(self.db_path) as conn:
                # Compare current vs previous period
                key_metrics = ['development_speed', 'code_quality_score', 'user_satisfaction']
                
                for metric in key_metrics:
                    # Current period
                    cursor = conn.execute("""
                        SELECT AVG(metric_value) FROM metric_entries
                        WHERE metric_name = ? AND timestamp >= ?
                    """, (metric, current_period_start))
                    current_avg = cursor.fetchone()[0] or 0
                    
                    # Previous period
                    cursor = conn.execute("""
                        SELECT AVG(metric_value) FROM metric_entries
                        WHERE metric_name = ? AND timestamp >= ? AND timestamp < ?
                    """, (metric, previous_period_start, previous_period_end))
                    previous_avg = cursor.fetchone()[0] or 0
                    
                    # Calculate change
                    if previous_avg > 0:
                        change_percentage = ((current_avg - previous_avg) / previous_avg) * 100
                    else:
                        change_percentage = 0
                    
                    comparative_analysis[metric] = {
                        'current_period_avg': current_avg,
                        'previous_period_avg': previous_avg,
                        'change_percentage': change_percentage,
                        'improvement': change_percentage > 0 if not self.metric_definitions.get(metric, {}).get('lower_is_better', False) else change_percentage < 0
                    }
                
                # Project-level comparison
                cursor = conn.execute("""
                    SELECT project_id, AVG(metric_value) as avg_success
                    FROM metric_entries
                    WHERE metric_name = 'project_success_rate' AND timestamp >= ?
                    GROUP BY project_id
                    ORDER BY avg_success DESC
                    LIMIT 5
                """, (current_period_start,))
                
                top_projects = cursor.fetchall()
                comparative_analysis['top_performing_projects'] = [
                    {'project_id': row[0], 'success_rate': row[1]}
                    for row in top_projects
                ]
            
            return comparative_analysis
            
        except Exception as e:
            logger.error(f"Failed to perform comparative analysis: {e}")
            return {}
    
    def _store_performance_report(self, report: PerformanceReport):
        """Store performance report in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO performance_reports
                    (report_id, generated_at, period_start, period_end, report_data, report_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    report.report_id,
                    report.generated_at,
                    report.period_start,
                    report.period_end,
                    json.dumps(asdict(report)),
                    "comprehensive"
                ))
        except Exception as e:
            logger.error(f"Failed to store performance report: {e}")
    
    def get_metric_summary(self, metric_name: str, days: int = 30) -> Dict[str, Any]:
        """Get summary statistics for a specific metric"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT metric_value FROM metric_entries
                    WHERE metric_name = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                """, (metric_name, cutoff_date))
                
                values = [row[0] for row in cursor.fetchall()]
            
            if not values:
                return {
                    'metric_name': metric_name,
                    'period_days': days,
                    'data_points': 0,
                    'error': 'No data available'
                }
            
            return {
                'metric_name': metric_name,
                'period_days': days,
                'data_points': len(values),
                'average': statistics.mean(values),
                'median': statistics.median(values),
                'std_deviation': statistics.stdev(values) if len(values) > 1 else 0,
                'min_value': min(values),
                'max_value': max(values),
                'latest_value': values[-1],
                'trend': self.analyze_metric_trends(metric_name, days)
            }
            
        except Exception as e:
            logger.error(f"Failed to get metric summary: {e}")
            return {'metric_name': metric_name, 'error': str(e)}
    
    def export_metrics_data(self, output_path: str, days: int = 90) -> bool:
        """Export metrics data for external analysis"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM metric_entries
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (cutoff_date,))
                
                columns = [desc[0] for desc in cursor.description]
                metrics_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Create export data structure
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'period_days': days,
                'total_metrics': len(metrics_data),
                'metric_definitions': self.metric_definitions,
                'metrics_data': metrics_data
            }
            
            # Write to file
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported metrics data to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export metrics data: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    tracker = MetricsTracker()
    
    # Track some example metrics
    tracker.track_development_speed(
        project_id="test_project_001",
        user_id="user_123",
        features_completed=3,
        time_spent_hours=24.0,
        context={"template_used": "react_typescript"}
    )
    
    tracker.track_code_quality(
        project_id="test_project_001",
        user_id="user_123",
        quality_score=0.85,
        quality_metrics={"test_coverage": 0.9, "complexity_score": 0.8}
    )
    
    tracker.track_user_satisfaction(
        project_id="test_project_001",
        user_id="user_123",
        satisfaction_score=0.8,
        feedback_summary="Good template, minor issues with build process"
    )
    
    # Generate analysis
    trend = tracker.analyze_metric_trends("development_speed", 30)
    roi = tracker.calculate_roi(90)
    report = tracker.generate_performance_report(30)
    summary = tracker.get_metric_summary("code_quality_score", 30)
    
    print("Metrics Tracker Demo:")
    print(f"Trend analysis: {asdict(trend)}")
    print(f"ROI analysis: {roi}")
    print(f"Performance report generated: {report.report_id}")
    print(f"Metric summary: {summary}")
