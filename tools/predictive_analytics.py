#!/usr/bin/env python3
"""
Predictive Analytics for Windsurf Context Engineering Framework

This module provides predictive analytics capabilities for workflow optimization,
performance prediction, and proactive issue prevention.

Phase 3: Predictive Analytics
- Workflow performance prediction
- Issue prevention and early warning
- Resource usage forecasting
- Development velocity prediction
"""

import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
import math

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Result of a predictive analysis."""
    prediction_type: str
    predicted_value: Union[float, str, bool]
    confidence: float  # 0.0 to 1.0
    time_horizon: str  # 'short', 'medium', 'long'
    factors: List[str]
    recommendations: List[str]
    timestamp: float

@dataclass
class PerformanceMetrics:
    """Performance metrics for prediction."""
    command_success_rate: float
    average_execution_time: float
    error_frequency: float
    resource_usage: Dict[str, float]
    workflow_efficiency: float
    git_operation_success: float
    environment_health: float

@dataclass
class TrendAnalysis:
    """Trend analysis result."""
    metric_name: str
    trend_direction: str  # 'improving', 'declining', 'stable'
    trend_strength: float  # 0.0 to 1.0
    predicted_future_value: float
    confidence: float
    time_series_data: List[Tuple[float, float]]  # (timestamp, value)

class PredictiveAnalytics:
    """
    Advanced predictive analytics for workflow optimization.
    
    Provides:
    - Performance prediction based on historical data
    - Issue prevention through pattern analysis
    - Resource usage forecasting
    - Development velocity prediction
    - Workflow optimization recommendations
    """
    
    def __init__(self, project_path: str = "."):
        """Initialize predictive analytics."""
        self.project_path = Path(project_path).resolve()
        
        # Data storage
        self.analytics_data_path = self.project_path / ".windsurf" / "analytics"
        self.analytics_data_path.mkdir(parents=True, exist_ok=True)
        
        # Historical data caches
        self.performance_history: deque = deque(maxlen=1000)
        self.command_history: deque = deque(maxlen=500)
        self.workflow_history: deque = deque(maxlen=200)
        self.error_history: deque = deque(maxlen=300)
        
        # Prediction models (simplified)
        self.prediction_models = {
            'performance': self.predict_performance,
            'issues': self.predict_issues,
            'resources': self.predict_resource_usage,
            'velocity': self.predict_development_velocity,
            'workflow_optimization': self.predict_workflow_optimization
        }
        
        # Load historical data
        self._load_historical_data()
        
        logger.info(f"Predictive analytics initialized for: {self.project_path}")
    
    def analyze_trends(self, metric_name: str, time_window_hours: int = 24) -> TrendAnalysis:
        """Analyze trends for a specific metric."""
        try:
            # Get historical data for the metric
            time_series_data = self._get_metric_time_series(metric_name, time_window_hours)
            
            if len(time_series_data) < 3:
                return TrendAnalysis(
                    metric_name=metric_name,
                    trend_direction='stable',
                    trend_strength=0.0,
                    predicted_future_value=0.0,
                    confidence=0.0,
                    time_series_data=time_series_data
                )
            
            # Calculate trend
            values = [point[1] for point in time_series_data]
            timestamps = [point[0] for point in time_series_data]
            
            # Simple linear regression for trend
            trend_slope = self._calculate_trend_slope(timestamps, values)
            trend_direction = self._determine_trend_direction(trend_slope)
            trend_strength = min(1.0, abs(trend_slope) * 10)  # Normalize
            
            # Predict future value
            latest_value = values[-1]
            time_delta = 3600  # 1 hour ahead
            predicted_value = latest_value + (trend_slope * time_delta)
            
            # Calculate confidence based on data consistency
            confidence = self._calculate_trend_confidence(values)
            
            return TrendAnalysis(
                metric_name=metric_name,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                predicted_future_value=predicted_value,
                confidence=confidence,
                time_series_data=time_series_data
            )
            
        except Exception as e:
            logger.error(f"Error analyzing trends for {metric_name}: {e}")
            return TrendAnalysis(
                metric_name=metric_name,
                trend_direction='unknown',
                trend_strength=0.0,
                predicted_future_value=0.0,
                confidence=0.0,
                time_series_data=[]
            )
    
    def predict_performance(self, time_horizon: str = 'short') -> PredictionResult:
        """Predict future performance metrics."""
        try:
            # Analyze historical performance data
            recent_performance = self._get_recent_performance_metrics()
            
            if not recent_performance:
                return self._create_default_prediction('performance', 0.8, 0.3)
            
            # Calculate prediction based on trends
            success_rate_trend = self.analyze_trends('command_success_rate', 
                                                   self._get_time_window_hours(time_horizon))
            execution_time_trend = self.analyze_trends('average_execution_time',
                                                     self._get_time_window_hours(time_horizon))
            
            # Combine trends for overall performance prediction
            predicted_success_rate = max(0.0, min(1.0, success_rate_trend.predicted_future_value))
            predicted_execution_time = max(0.1, execution_time_trend.predicted_future_value)
            
            # Calculate overall performance score
            performance_score = predicted_success_rate * (1.0 / (1.0 + predicted_execution_time / 10.0))
            
            # Calculate confidence
            confidence = (success_rate_trend.confidence + execution_time_trend.confidence) / 2
            
            # Generate factors and recommendations
            factors = self._identify_performance_factors(recent_performance)
            recommendations = self._generate_performance_recommendations(
                predicted_success_rate, predicted_execution_time
            )
            
            return PredictionResult(
                prediction_type='performance',
                predicted_value=performance_score,
                confidence=confidence,
                time_horizon=time_horizon,
                factors=factors,
                recommendations=recommendations,
                timestamp=datetime.now().timestamp()
            )
            
        except Exception as e:
            logger.error(f"Error predicting performance: {e}")
            return self._create_default_prediction('performance', 0.8, 0.3)
    
    def predict_issues(self, time_horizon: str = 'short') -> PredictionResult:
        """Predict potential issues based on patterns."""
        try:
            # Analyze error patterns
            error_patterns = self._analyze_error_patterns()
            
            # Calculate issue probability
            issue_probability = self._calculate_issue_probability(error_patterns, time_horizon)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(error_patterns)
            
            # Generate prevention recommendations
            prevention_recommendations = self._generate_prevention_recommendations(risk_factors)
            
            # Calculate confidence based on pattern consistency
            confidence = self._calculate_pattern_confidence(error_patterns)
            
            return PredictionResult(
                prediction_type='issues',
                predicted_value=issue_probability,
                confidence=confidence,
                time_horizon=time_horizon,
                factors=risk_factors,
                recommendations=prevention_recommendations,
                timestamp=datetime.now().timestamp()
            )
            
        except Exception as e:
            logger.error(f"Error predicting issues: {e}")
            return self._create_default_prediction('issues', 0.2, 0.4)
    
    def predict_resource_usage(self, time_horizon: str = 'medium') -> PredictionResult:
        """Predict future resource usage."""
        try:
            # Analyze resource usage trends
            cpu_trend = self.analyze_trends('cpu_usage', self._get_time_window_hours(time_horizon))
            memory_trend = self.analyze_trends('memory_usage', self._get_time_window_hours(time_horizon))
            disk_trend = self.analyze_trends('disk_usage', self._get_time_window_hours(time_horizon))
            
            # Predict peak resource usage
            predicted_cpu = max(0.0, min(100.0, cpu_trend.predicted_future_value))
            predicted_memory = max(0.0, min(100.0, memory_trend.predicted_future_value))
            predicted_disk = max(0.0, min(100.0, disk_trend.predicted_future_value))
            
            # Calculate overall resource stress
            resource_stress = (predicted_cpu + predicted_memory + predicted_disk) / 300.0
            
            # Generate factors and recommendations
            factors = [
                f"CPU trend: {cpu_trend.trend_direction}",
                f"Memory trend: {memory_trend.trend_direction}",
                f"Disk trend: {disk_trend.trend_direction}"
            ]
            
            recommendations = self._generate_resource_recommendations(
                predicted_cpu, predicted_memory, predicted_disk
            )
            
            # Calculate confidence
            confidence = (cpu_trend.confidence + memory_trend.confidence + disk_trend.confidence) / 3
            
            return PredictionResult(
                prediction_type='resources',
                predicted_value=resource_stress,
                confidence=confidence,
                time_horizon=time_horizon,
                factors=factors,
                recommendations=recommendations,
                timestamp=datetime.now().timestamp()
            )
            
        except Exception as e:
            logger.error(f"Error predicting resource usage: {e}")
            return self._create_default_prediction('resources', 0.3, 0.5)
    
    def predict_development_velocity(self, time_horizon: str = 'medium') -> PredictionResult:
        """Predict development velocity based on historical data."""
        try:
            # Analyze workflow completion trends
            workflow_trend = self.analyze_trends('workflow_completion_rate',
                                                self._get_time_window_hours(time_horizon))
            
            # Analyze command execution efficiency
            efficiency_trend = self.analyze_trends('command_efficiency',
                                                 self._get_time_window_hours(time_horizon))
            
            # Calculate predicted velocity
            base_velocity = workflow_trend.predicted_future_value
            efficiency_multiplier = 1.0 + (efficiency_trend.predicted_future_value - 1.0) * 0.5
            predicted_velocity = base_velocity * efficiency_multiplier
            
            # Generate factors
            factors = [
                f"Workflow completion trend: {workflow_trend.trend_direction}",
                f"Command efficiency trend: {efficiency_trend.trend_direction}",
                f"Historical velocity patterns"
            ]
            
            # Generate recommendations
            recommendations = self._generate_velocity_recommendations(predicted_velocity)
            
            # Calculate confidence
            confidence = (workflow_trend.confidence + efficiency_trend.confidence) / 2
            
            return PredictionResult(
                prediction_type='velocity',
                predicted_value=predicted_velocity,
                confidence=confidence,
                time_horizon=time_horizon,
                factors=factors,
                recommendations=recommendations,
                timestamp=datetime.now().timestamp()
            )
            
        except Exception as e:
            logger.error(f"Error predicting development velocity: {e}")
            return self._create_default_prediction('velocity', 1.0, 0.4)
    
    def predict_workflow_optimization(self) -> PredictionResult:
        """Predict workflow optimization opportunities."""
        try:
            # Analyze workflow patterns
            workflow_patterns = self._analyze_workflow_patterns()
            
            # Calculate optimization potential
            optimization_score = self._calculate_optimization_potential(workflow_patterns)
            
            # Identify optimization opportunities
            opportunities = self._identify_optimization_opportunities(workflow_patterns)
            
            # Generate optimization recommendations
            recommendations = self._generate_optimization_recommendations(opportunities)
            
            # Calculate confidence based on pattern strength
            confidence = self._calculate_optimization_confidence(workflow_patterns)
            
            return PredictionResult(
                prediction_type='workflow_optimization',
                predicted_value=optimization_score,
                confidence=confidence,
                time_horizon='medium',
                factors=opportunities,
                recommendations=recommendations,
                timestamp=datetime.now().timestamp()
            )
            
        except Exception as e:
            logger.error(f"Error predicting workflow optimization: {e}")
            return self._create_default_prediction('workflow_optimization', 0.6, 0.5)
    
    def get_comprehensive_predictions(self) -> Dict[str, Any]:
        """Get comprehensive predictions for all areas."""
        try:
            predictions = {}
            
            for prediction_type, prediction_func in self.prediction_models.items():
                try:
                    if prediction_type == 'workflow_optimization':
                        prediction = prediction_func()
                    else:
                        prediction = prediction_func('medium')
                    
                    predictions[prediction_type] = asdict(prediction)
                    
                except Exception as e:
                    logger.warning(f"Error getting {prediction_type} prediction: {e}")
                    predictions[prediction_type] = asdict(
                        self._create_default_prediction(prediction_type, 0.5, 0.3)
                    )
            
            # Add summary metrics
            predictions['summary'] = {
                'overall_health_score': self._calculate_overall_health_score(predictions),
                'risk_level': self._calculate_risk_level(predictions),
                'optimization_potential': predictions.get('workflow_optimization', {}).get('predicted_value', 0.5),
                'timestamp': datetime.now().timestamp()
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error getting comprehensive predictions: {e}")
            return {'error': str(e)}
    
    def record_performance_data(self, metrics: PerformanceMetrics):
        """Record performance data for future predictions."""
        try:
            performance_data = {
                'metrics': asdict(metrics),
                'timestamp': datetime.now().timestamp()
            }
            
            self.performance_history.append(performance_data)
            
            # Persist data periodically
            if len(self.performance_history) % 10 == 0:
                self._save_historical_data()
            
            logger.debug("Recorded performance data for predictions")
            
        except Exception as e:
            logger.warning(f"Error recording performance data: {e}")
    
    # Helper methods
    
    def _get_metric_time_series(self, metric_name: str, time_window_hours: int) -> List[Tuple[float, float]]:
        """Get time series data for a specific metric."""
        try:
            cutoff_time = datetime.now().timestamp() - (time_window_hours * 3600)
            time_series = []
            
            for data_point in self.performance_history:
                if data_point['timestamp'] >= cutoff_time:
                    metrics = data_point['metrics']
                    if metric_name in metrics:
                        time_series.append((data_point['timestamp'], metrics[metric_name]))
            
            return sorted(time_series, key=lambda x: x[0])
            
        except Exception as e:
            logger.warning(f"Error getting time series for {metric_name}: {e}")
            return []
    
    def _calculate_trend_slope(self, timestamps: List[float], values: List[float]) -> float:
        """Calculate trend slope using simple linear regression."""
        try:
            if len(timestamps) < 2:
                return 0.0
            
            n = len(timestamps)
            sum_x = sum(timestamps)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(timestamps, values))
            sum_x2 = sum(x * x for x in timestamps)
            
            denominator = n * sum_x2 - sum_x * sum_x
            if abs(denominator) < 1e-10:
                return 0.0
            
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            return slope
            
        except Exception as e:
            logger.warning(f"Error calculating trend slope: {e}")
            return 0.0
    
    def _determine_trend_direction(self, slope: float) -> str:
        """Determine trend direction from slope."""
        if abs(slope) < 1e-6:
            return 'stable'
        elif slope > 0:
            return 'improving'
        else:
            return 'declining'
    
    def _calculate_trend_confidence(self, values: List[float]) -> float:
        """Calculate confidence in trend analysis."""
        try:
            if len(values) < 3:
                return 0.0
            
            # Calculate coefficient of variation
            mean_val = statistics.mean(values)
            if mean_val == 0:
                return 0.5
            
            std_val = statistics.stdev(values)
            cv = std_val / abs(mean_val)
            
            # Convert to confidence (lower variation = higher confidence)
            confidence = max(0.0, min(1.0, 1.0 - cv))
            return confidence
            
        except Exception as e:
            logger.warning(f"Error calculating trend confidence: {e}")
            return 0.5
    
    def _get_time_window_hours(self, time_horizon: str) -> int:
        """Get time window in hours for different horizons."""
        horizons = {
            'short': 6,
            'medium': 24,
            'long': 168  # 1 week
        }
        return horizons.get(time_horizon, 24)
    
    def _get_recent_performance_metrics(self) -> Optional[PerformanceMetrics]:
        """Get most recent performance metrics."""
        try:
            if not self.performance_history:
                return None
            
            latest_data = self.performance_history[-1]
            metrics_dict = latest_data['metrics']
            
            return PerformanceMetrics(**metrics_dict)
            
        except Exception as e:
            logger.warning(f"Error getting recent performance metrics: {e}")
            return None
    
    def _create_default_prediction(self, prediction_type: str, value: float, confidence: float) -> PredictionResult:
        """Create a default prediction when analysis fails."""
        return PredictionResult(
            prediction_type=prediction_type,
            predicted_value=value,
            confidence=confidence,
            time_horizon='medium',
            factors=['Limited historical data'],
            recommendations=['Collect more performance data for better predictions'],
            timestamp=datetime.now().timestamp()
        )
    
    def _identify_performance_factors(self, metrics: PerformanceMetrics) -> List[str]:
        """Identify factors affecting performance."""
        factors = []
        
        if metrics.command_success_rate < 0.8:
            factors.append('Low command success rate')
        
        if metrics.average_execution_time > 10.0:
            factors.append('High average execution time')
        
        if metrics.error_frequency > 0.1:
            factors.append('High error frequency')
        
        if metrics.environment_health < 0.7:
            factors.append('Poor environment health')
        
        return factors if factors else ['Performance within normal range']
    
    def _generate_performance_recommendations(self, success_rate: float, execution_time: float) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        if success_rate < 0.8:
            recommendations.append('Review and fix failing commands')
        
        if execution_time > 10.0:
            recommendations.append('Optimize slow-running commands')
        
        if success_rate > 0.9 and execution_time < 5.0:
            recommendations.append('Performance is excellent - maintain current practices')
        
        return recommendations if recommendations else ['Continue monitoring performance']
    
    def _analyze_error_patterns(self) -> Dict[str, Any]:
        """Analyze error patterns for issue prediction."""
        # Simplified error pattern analysis
        return {
            'error_frequency': 0.1,
            'common_errors': ['timeout', 'permission_denied'],
            'error_trend': 'stable',
            'critical_errors': 0
        }
    
    def _calculate_issue_probability(self, error_patterns: Dict[str, Any], time_horizon: str) -> float:
        """Calculate probability of issues occurring."""
        base_probability = error_patterns.get('error_frequency', 0.1)
        
        # Adjust based on time horizon
        horizon_multiplier = {
            'short': 0.5,
            'medium': 1.0,
            'long': 2.0
        }.get(time_horizon, 1.0)
        
        return min(1.0, base_probability * horizon_multiplier)
    
    def _identify_risk_factors(self, error_patterns: Dict[str, Any]) -> List[str]:
        """Identify risk factors for potential issues."""
        factors = []
        
        if error_patterns.get('error_frequency', 0) > 0.2:
            factors.append('High error frequency')
        
        if 'timeout' in error_patterns.get('common_errors', []):
            factors.append('Timeout errors detected')
        
        if error_patterns.get('critical_errors', 0) > 0:
            factors.append('Critical errors present')
        
        return factors if factors else ['Low risk factors detected']
    
    def _generate_prevention_recommendations(self, risk_factors: List[str]) -> List[str]:
        """Generate recommendations for issue prevention."""
        recommendations = []
        
        for factor in risk_factors:
            if 'timeout' in factor.lower():
                recommendations.append('Increase timeout values for long-running operations')
            elif 'error frequency' in factor.lower():
                recommendations.append('Review and fix common error patterns')
            elif 'critical' in factor.lower():
                recommendations.append('Address critical errors immediately')
        
        return recommendations if recommendations else ['Continue monitoring for issues']
    
    def _calculate_pattern_confidence(self, patterns: Dict[str, Any]) -> float:
        """Calculate confidence in pattern analysis."""
        # Simplified confidence calculation
        return 0.7
    
    def _generate_resource_recommendations(self, cpu: float, memory: float, disk: float) -> List[str]:
        """Generate resource usage recommendations."""
        recommendations = []
        
        if cpu > 80:
            recommendations.append('Consider optimizing CPU-intensive operations')
        
        if memory > 80:
            recommendations.append('Monitor memory usage and consider cleanup')
        
        if disk > 90:
            recommendations.append('Clean up disk space or expand storage')
        
        return recommendations if recommendations else ['Resource usage within normal limits']
    
    def _generate_velocity_recommendations(self, velocity: float) -> List[str]:
        """Generate development velocity recommendations."""
        recommendations = []
        
        if velocity < 0.7:
            recommendations.append('Consider workflow optimization to improve velocity')
        elif velocity > 1.3:
            recommendations.append('Excellent velocity - maintain current practices')
        else:
            recommendations.append('Velocity is stable - monitor for improvements')
        
        return recommendations
    
    def _analyze_workflow_patterns(self) -> Dict[str, Any]:
        """Analyze workflow patterns for optimization."""
        # Simplified workflow pattern analysis
        return {
            'repetitive_commands': 0.3,
            'workflow_efficiency': 0.8,
            'optimization_opportunities': ['command_batching', 'parallel_execution']
        }
    
    def _calculate_optimization_potential(self, patterns: Dict[str, Any]) -> float:
        """Calculate workflow optimization potential."""
        return 1.0 - patterns.get('workflow_efficiency', 0.8)
    
    def _identify_optimization_opportunities(self, patterns: Dict[str, Any]) -> List[str]:
        """Identify workflow optimization opportunities."""
        return patterns.get('optimization_opportunities', ['No specific opportunities identified'])
    
    def _generate_optimization_recommendations(self, opportunities: List[str]) -> List[str]:
        """Generate workflow optimization recommendations."""
        recommendations = []
        
        for opportunity in opportunities:
            if 'batching' in opportunity:
                recommendations.append('Implement command batching for related operations')
            elif 'parallel' in opportunity:
                recommendations.append('Consider parallel execution for independent tasks')
        
        return recommendations if recommendations else ['Continue monitoring for optimization opportunities']
    
    def _calculate_optimization_confidence(self, patterns: Dict[str, Any]) -> float:
        """Calculate confidence in optimization predictions."""
        return 0.75  # Simplified
    
    def _calculate_overall_health_score(self, predictions: Dict[str, Any]) -> float:
        """Calculate overall system health score."""
        try:
            performance_score = predictions.get('performance', {}).get('predicted_value', 0.5)
            issue_risk = 1.0 - predictions.get('issues', {}).get('predicted_value', 0.5)
            resource_health = 1.0 - predictions.get('resources', {}).get('predicted_value', 0.5)
            
            return (performance_score + issue_risk + resource_health) / 3
            
        except Exception as e:
            logger.warning(f"Error calculating health score: {e}")
            return 0.5
    
    def _calculate_risk_level(self, predictions: Dict[str, Any]) -> str:
        """Calculate overall risk level."""
        try:
            issue_probability = predictions.get('issues', {}).get('predicted_value', 0.5)
            resource_stress = predictions.get('resources', {}).get('predicted_value', 0.5)
            
            risk_score = (issue_probability + resource_stress) / 2
            
            if risk_score > 0.7:
                return 'high'
            elif risk_score > 0.4:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.warning(f"Error calculating risk level: {e}")
            return 'medium'
    
    def _load_historical_data(self):
        """Load historical data from disk."""
        try:
            data_file = self.analytics_data_path / "historical_data.json"
            if data_file.exists():
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                # Load performance history
                for item in data.get('performance_history', []):
                    self.performance_history.append(item)
                
                logger.info(f"Loaded {len(self.performance_history)} historical data points")
            
        except Exception as e:
            logger.warning(f"Error loading historical data: {e}")
    
    def _save_historical_data(self):
        """Save historical data to disk."""
        try:
            data_file = self.analytics_data_path / "historical_data.json"
            
            data = {
                'performance_history': list(self.performance_history),
                'timestamp': datetime.now().timestamp()
            }
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Saved historical data to disk")
            
        except Exception as e:
            logger.warning(f"Error saving historical data: {e}")


# Convenience functions for easy integration

def get_performance_prediction(project_path: str = ".", time_horizon: str = 'medium') -> Dict[str, Any]:
    """Get performance prediction for the project."""
    try:
        analytics = PredictiveAnalytics(project_path)
        prediction = analytics.predict_performance(time_horizon)
        return asdict(prediction)
    except Exception as e:
        logger.error(f"Error getting performance prediction: {e}")
        return {'error': str(e)}

def get_issue_prediction(project_path: str = ".", time_horizon: str = 'short') -> Dict[str, Any]:
    """Get issue prediction for the project."""
    try:
        analytics = PredictiveAnalytics(project_path)
        prediction = analytics.predict_issues(time_horizon)
        return asdict(prediction)
    except Exception as e:
        logger.error(f"Error getting issue prediction: {e}")
        return {'error': str(e)}

def get_comprehensive_analytics(project_path: str = ".") -> Dict[str, Any]:
    """Get comprehensive predictive analytics for the project."""
    try:
        analytics = PredictiveAnalytics(project_path)
        return analytics.get_comprehensive_predictions()
    except Exception as e:
        logger.error(f"Error getting comprehensive analytics: {e}")
        return {'error': str(e)}

def record_performance_metrics(metrics: Dict[str, Any], project_path: str = "."):
    """Record performance metrics for future predictions."""
    try:
        analytics = PredictiveAnalytics(project_path)
        performance_metrics = PerformanceMetrics(
            command_success_rate=metrics.get('command_success_rate', 1.0),
            average_execution_time=metrics.get('average_execution_time', 0.0),
            error_frequency=metrics.get('error_frequency', 0.0),
            resource_usage=metrics.get('resource_usage', {}),
            workflow_efficiency=metrics.get('workflow_efficiency', 1.0),
            git_operation_success=metrics.get('git_operation_success', 1.0),
            environment_health=metrics.get('environment_health', 1.0)
        )
        analytics.record_performance_data(performance_metrics)
    except Exception as e:
        logger.error(f"Error recording performance metrics: {e}")
