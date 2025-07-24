#!/usr/bin/env python3
"""
Tests for Predictive Analytics

This module tests the Phase 3 predictive analytics capabilities including
performance prediction, issue prediction, and trend analysis.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time
from datetime import datetime, timedelta

from tools.predictive_analytics import (
    PredictiveAnalytics,
    PredictionResult,
    PerformanceMetrics,
    TrendAnalysis,
    get_performance_prediction,
    get_issue_prediction,
    get_comprehensive_analytics,
    record_performance_metrics
)

class TestPredictiveAnalytics(unittest.TestCase):
    """Test cases for PredictiveAnalytics class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test project structure
        (self.test_path / "requirements.txt").write_text("pytest==7.0.0\nblack==22.0.0\n")
        (self.test_path / "main.py").write_text("print('Hello, World!')\n")
        
        # Initialize predictive analytics
        self.analytics = PredictiveAnalytics(str(self.test_path))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test predictive analytics initialization."""
        self.assertIsInstance(self.analytics, PredictiveAnalytics)
        self.assertEqual(str(self.analytics.project_path), str(self.test_path))
        
        # Check data structures
        self.assertIsInstance(self.analytics.performance_history, type(self.analytics.performance_history))
        self.assertIsInstance(self.analytics.command_history, type(self.analytics.command_history))
        self.assertIsInstance(self.analytics.workflow_history, type(self.analytics.workflow_history))
        self.assertIsInstance(self.analytics.error_history, type(self.analytics.error_history))
        self.assertIsInstance(self.analytics.prediction_models, dict)
        
        # Check prediction models
        expected_models = ['performance', 'issues', 'resources', 'velocity', 'workflow_optimization']
        for model in expected_models:
            self.assertIn(model, self.analytics.prediction_models)
    
    def test_analyze_trends(self):
        """Test trend analysis functionality."""
        # Add some test performance data
        test_metrics = PerformanceMetrics(
            command_success_rate=0.9,
            average_execution_time=2.5,
            error_frequency=0.1,
            resource_usage={'cpu': 50.0, 'memory': 60.0},
            workflow_efficiency=0.8,
            git_operation_success=0.95,
            environment_health=0.85
        )
        
        self.analytics.record_performance_data(test_metrics)
        
        # Analyze trend
        trend = self.analytics.analyze_trends('command_success_rate', 24)
        
        self.assertIsInstance(trend, TrendAnalysis)
        self.assertEqual(trend.metric_name, 'command_success_rate')
        self.assertIn(trend.trend_direction, ['improving', 'declining', 'stable', 'unknown'])
        self.assertGreaterEqual(trend.trend_strength, 0.0)
        self.assertLessEqual(trend.trend_strength, 1.0)
        self.assertGreaterEqual(trend.confidence, 0.0)
        self.assertLessEqual(trend.confidence, 1.0)
        self.assertIsInstance(trend.time_series_data, list)
    
    def test_predict_performance(self):
        """Test performance prediction."""
        # Add test data
        for i in range(5):
            metrics = PerformanceMetrics(
                command_success_rate=0.9 - i * 0.02,  # Declining trend
                average_execution_time=2.0 + i * 0.5,  # Increasing trend
                error_frequency=0.05 + i * 0.01,
                resource_usage={'cpu': 40.0 + i * 5, 'memory': 50.0 + i * 3},
                workflow_efficiency=0.85 - i * 0.02,
                git_operation_success=0.95,
                environment_health=0.8
            )
            self.analytics.record_performance_data(metrics)
        
        # Test different time horizons
        for horizon in ['short', 'medium', 'long']:
            prediction = self.analytics.predict_performance(horizon)
            
            self.assertIsInstance(prediction, PredictionResult)
            self.assertEqual(prediction.prediction_type, 'performance')
            self.assertIsInstance(prediction.predicted_value, float)
            self.assertGreaterEqual(prediction.confidence, 0.0)
            self.assertLessEqual(prediction.confidence, 1.0)
            self.assertEqual(prediction.time_horizon, horizon)
            self.assertIsInstance(prediction.factors, list)
            self.assertIsInstance(prediction.recommendations, list)
            self.assertGreater(prediction.timestamp, 0)
    
    def test_predict_issues(self):
        """Test issue prediction."""
        for horizon in ['short', 'medium', 'long']:
            prediction = self.analytics.predict_issues(horizon)
            
            self.assertIsInstance(prediction, PredictionResult)
            self.assertEqual(prediction.prediction_type, 'issues')
            self.assertIsInstance(prediction.predicted_value, float)
            self.assertGreaterEqual(prediction.predicted_value, 0.0)
            self.assertLessEqual(prediction.predicted_value, 1.0)
            self.assertGreaterEqual(prediction.confidence, 0.0)
            self.assertLessEqual(prediction.confidence, 1.0)
            self.assertEqual(prediction.time_horizon, horizon)
            self.assertIsInstance(prediction.factors, list)
            self.assertIsInstance(prediction.recommendations, list)
    
    def test_predict_resource_usage(self):
        """Test resource usage prediction."""
        for horizon in ['short', 'medium', 'long']:
            prediction = self.analytics.predict_resource_usage(horizon)
            
            self.assertIsInstance(prediction, PredictionResult)
            self.assertEqual(prediction.prediction_type, 'resources')
            self.assertIsInstance(prediction.predicted_value, float)
            self.assertGreaterEqual(prediction.predicted_value, 0.0)
            self.assertLessEqual(prediction.predicted_value, 1.0)
            self.assertGreaterEqual(prediction.confidence, 0.0)
            self.assertLessEqual(prediction.confidence, 1.0)
            self.assertEqual(prediction.time_horizon, horizon)
            self.assertIsInstance(prediction.factors, list)
            self.assertIsInstance(prediction.recommendations, list)
    
    def test_predict_development_velocity(self):
        """Test development velocity prediction."""
        for horizon in ['short', 'medium', 'long']:
            prediction = self.analytics.predict_development_velocity(horizon)
            
            self.assertIsInstance(prediction, PredictionResult)
            self.assertEqual(prediction.prediction_type, 'velocity')
            self.assertIsInstance(prediction.predicted_value, float)
            self.assertGreaterEqual(prediction.confidence, 0.0)
            self.assertLessEqual(prediction.confidence, 1.0)
            self.assertEqual(prediction.time_horizon, horizon)
            self.assertIsInstance(prediction.factors, list)
            self.assertIsInstance(prediction.recommendations, list)
    
    def test_predict_workflow_optimization(self):
        """Test workflow optimization prediction."""
        prediction = self.analytics.predict_workflow_optimization()
        
        self.assertIsInstance(prediction, PredictionResult)
        self.assertEqual(prediction.prediction_type, 'workflow_optimization')
        self.assertIsInstance(prediction.predicted_value, float)
        self.assertGreaterEqual(prediction.predicted_value, 0.0)
        self.assertLessEqual(prediction.predicted_value, 1.0)
        self.assertGreaterEqual(prediction.confidence, 0.0)
        self.assertLessEqual(prediction.confidence, 1.0)
        self.assertEqual(prediction.time_horizon, 'medium')
        self.assertIsInstance(prediction.factors, list)
        self.assertIsInstance(prediction.recommendations, list)
    
    def test_get_comprehensive_predictions(self):
        """Test comprehensive predictions generation."""
        predictions = self.analytics.get_comprehensive_predictions()
        
        self.assertIsInstance(predictions, dict)
        
        # Check all prediction types are present
        expected_types = ['performance', 'issues', 'resources', 'velocity', 'workflow_optimization']
        for pred_type in expected_types:
            self.assertIn(pred_type, predictions)
            
            pred_data = predictions[pred_type]
            self.assertIsInstance(pred_data, dict)
            self.assertIn('prediction_type', pred_data)
            self.assertIn('predicted_value', pred_data)
            self.assertIn('confidence', pred_data)
            self.assertIn('time_horizon', pred_data)
            self.assertIn('factors', pred_data)
            self.assertIn('recommendations', pred_data)
            self.assertIn('timestamp', pred_data)
        
        # Check summary
        self.assertIn('summary', predictions)
        summary = predictions['summary']
        self.assertIn('overall_health_score', summary)
        self.assertIn('risk_level', summary)
        self.assertIn('optimization_potential', summary)
        self.assertIn('timestamp', summary)
        
        # Validate summary values
        self.assertGreaterEqual(summary['overall_health_score'], 0.0)
        self.assertLessEqual(summary['overall_health_score'], 1.0)
        self.assertIn(summary['risk_level'], ['low', 'medium', 'high'])
        self.assertGreaterEqual(summary['optimization_potential'], 0.0)
        self.assertLessEqual(summary['optimization_potential'], 1.0)
    
    def test_record_performance_data(self):
        """Test performance data recording."""
        metrics = PerformanceMetrics(
            command_success_rate=0.95,
            average_execution_time=1.5,
            error_frequency=0.02,
            resource_usage={'cpu': 30.0, 'memory': 45.0, 'disk': 20.0},
            workflow_efficiency=0.9,
            git_operation_success=0.98,
            environment_health=0.92
        )
        
        initial_count = len(self.analytics.performance_history)
        
        self.analytics.record_performance_data(metrics)
        
        # Check data was recorded
        self.assertEqual(len(self.analytics.performance_history), initial_count + 1)
        
        # Check latest data
        latest_data = self.analytics.performance_history[-1]
        self.assertIn('metrics', latest_data)
        self.assertIn('timestamp', latest_data)
        
        recorded_metrics = latest_data['metrics']
        self.assertEqual(recorded_metrics['command_success_rate'], 0.95)
        self.assertEqual(recorded_metrics['average_execution_time'], 1.5)
        self.assertEqual(recorded_metrics['error_frequency'], 0.02)
    
    def test_get_metric_time_series(self):
        """Test metric time series retrieval."""
        # Add test data with timestamps
        current_time = time.time()
        for i in range(5):
            metrics = PerformanceMetrics(
                command_success_rate=0.8 + i * 0.05,
                average_execution_time=2.0,
                error_frequency=0.1,
                resource_usage={},
                workflow_efficiency=0.8,
                git_operation_success=0.9,
                environment_health=0.8
            )
            
            # Manually add with specific timestamp
            data_point = {
                'metrics': {
                    'command_success_rate': metrics.command_success_rate,
                    'average_execution_time': metrics.average_execution_time,
                    'error_frequency': metrics.error_frequency,
                    'workflow_efficiency': metrics.workflow_efficiency,
                    'git_operation_success': metrics.git_operation_success,
                    'environment_health': metrics.environment_health
                },
                'timestamp': current_time - (4 - i) * 3600  # Spread over 4 hours
            }
            self.analytics.performance_history.append(data_point)
        
        # Get time series
        time_series = self.analytics._get_metric_time_series('command_success_rate', 6)
        
        self.assertIsInstance(time_series, list)
        self.assertGreater(len(time_series), 0)
        
        # Check time series structure
        for timestamp, value in time_series:
            self.assertIsInstance(timestamp, float)
            self.assertIsInstance(value, float)
            self.assertGreaterEqual(value, 0.8)
            self.assertLessEqual(value, 1.0)
    
    def test_calculate_trend_slope(self):
        """Test trend slope calculation."""
        timestamps = [1.0, 2.0, 3.0, 4.0, 5.0]
        values = [0.8, 0.82, 0.84, 0.86, 0.88]  # Positive trend
        
        slope = self.analytics._calculate_trend_slope(timestamps, values)
        
        self.assertIsInstance(slope, float)
        self.assertGreater(slope, 0)  # Should be positive for increasing trend
        
        # Test negative trend
        values_negative = [0.9, 0.85, 0.8, 0.75, 0.7]
        slope_negative = self.analytics._calculate_trend_slope(timestamps, values_negative)
        
        self.assertLess(slope_negative, 0)  # Should be negative for decreasing trend
    
    def test_determine_trend_direction(self):
        """Test trend direction determination."""
        # Test positive slope
        direction = self.analytics._determine_trend_direction(0.1)
        self.assertEqual(direction, 'improving')
        
        # Test negative slope
        direction = self.analytics._determine_trend_direction(-0.1)
        self.assertEqual(direction, 'declining')
        
        # Test near-zero slope
        direction = self.analytics._determine_trend_direction(0.0000001)
        self.assertEqual(direction, 'stable')
    
    def test_calculate_trend_confidence(self):
        """Test trend confidence calculation."""
        # Test consistent values (high confidence)
        consistent_values = [0.9, 0.91, 0.89, 0.9, 0.91]
        confidence = self.analytics._calculate_trend_confidence(consistent_values)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        # Test highly variable values (low confidence)
        variable_values = [0.1, 0.9, 0.2, 0.8, 0.3]
        confidence_low = self.analytics._calculate_trend_confidence(variable_values)
        
        self.assertLess(confidence_low, confidence)
    
    def test_get_time_window_hours(self):
        """Test time window calculation."""
        self.assertEqual(self.analytics._get_time_window_hours('short'), 6)
        self.assertEqual(self.analytics._get_time_window_hours('medium'), 24)
        self.assertEqual(self.analytics._get_time_window_hours('long'), 168)
        self.assertEqual(self.analytics._get_time_window_hours('unknown'), 24)  # Default
    
    def test_create_default_prediction(self):
        """Test default prediction creation."""
        prediction = self.analytics._create_default_prediction('test', 0.7, 0.5)
        
        self.assertIsInstance(prediction, PredictionResult)
        self.assertEqual(prediction.prediction_type, 'test')
        self.assertEqual(prediction.predicted_value, 0.7)
        self.assertEqual(prediction.confidence, 0.5)
        self.assertEqual(prediction.time_horizon, 'medium')
        self.assertIn('Limited historical data', prediction.factors)
    
    def test_data_persistence(self):
        """Test data persistence functionality."""
        # Add test data
        metrics = PerformanceMetrics(
            command_success_rate=0.9,
            average_execution_time=2.0,
            error_frequency=0.05,
            resource_usage={'cpu': 40.0},
            workflow_efficiency=0.85,
            git_operation_success=0.95,
            environment_health=0.8
        )
        
        self.analytics.record_performance_data(metrics)
        
        # Force save
        self.analytics._save_historical_data()
        
        # Check file was created
        data_file = self.analytics.analytics_data_path / "historical_data.json"
        self.assertTrue(data_file.exists())
        
        # Load data in new instance
        new_analytics = PredictiveAnalytics(str(self.test_path))
        
        # Check data was loaded
        self.assertGreater(len(new_analytics.performance_history), 0)


class TestPerformanceMetricsDataClass(unittest.TestCase):
    """Test cases for PerformanceMetrics data class."""
    
    def test_performance_metrics_creation(self):
        """Test performance metrics creation and attributes."""
        metrics = PerformanceMetrics(
            command_success_rate=0.95,
            average_execution_time=1.5,
            error_frequency=0.02,
            resource_usage={'cpu': 30.0, 'memory': 45.0},
            workflow_efficiency=0.9,
            git_operation_success=0.98,
            environment_health=0.92
        )
        
        self.assertEqual(metrics.command_success_rate, 0.95)
        self.assertEqual(metrics.average_execution_time, 1.5)
        self.assertEqual(metrics.error_frequency, 0.02)
        self.assertEqual(metrics.resource_usage, {'cpu': 30.0, 'memory': 45.0})
        self.assertEqual(metrics.workflow_efficiency, 0.9)
        self.assertEqual(metrics.git_operation_success, 0.98)
        self.assertEqual(metrics.environment_health, 0.92)


class TestPredictionResultDataClass(unittest.TestCase):
    """Test cases for PredictionResult data class."""
    
    def test_prediction_result_creation(self):
        """Test prediction result creation and attributes."""
        result = PredictionResult(
            prediction_type='test',
            predicted_value=0.8,
            confidence=0.9,
            time_horizon='medium',
            factors=['factor1', 'factor2'],
            recommendations=['rec1', 'rec2'],
            timestamp=time.time()
        )
        
        self.assertEqual(result.prediction_type, 'test')
        self.assertEqual(result.predicted_value, 0.8)
        self.assertEqual(result.confidence, 0.9)
        self.assertEqual(result.time_horizon, 'medium')
        self.assertEqual(result.factors, ['factor1', 'factor2'])
        self.assertEqual(result.recommendations, ['rec1', 'rec2'])
        self.assertGreater(result.timestamp, 0)


class TestTrendAnalysisDataClass(unittest.TestCase):
    """Test cases for TrendAnalysis data class."""
    
    def test_trend_analysis_creation(self):
        """Test trend analysis creation and attributes."""
        trend = TrendAnalysis(
            metric_name='test_metric',
            trend_direction='improving',
            trend_strength=0.7,
            predicted_future_value=0.85,
            confidence=0.8,
            time_series_data=[(1.0, 0.8), (2.0, 0.82)]
        )
        
        self.assertEqual(trend.metric_name, 'test_metric')
        self.assertEqual(trend.trend_direction, 'improving')
        self.assertEqual(trend.trend_strength, 0.7)
        self.assertEqual(trend.predicted_future_value, 0.85)
        self.assertEqual(trend.confidence, 0.8)
        self.assertEqual(trend.time_series_data, [(1.0, 0.8), (2.0, 0.82)])


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test project
        (self.test_path / "requirements.txt").write_text("pytest==7.0.0\n")
        (self.test_path / "main.py").write_text("print('Hello')\n")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_get_performance_prediction(self):
        """Test get_performance_prediction convenience function."""
        prediction = get_performance_prediction(str(self.test_path), 'medium')
        
        self.assertIsInstance(prediction, dict)
        self.assertIn('prediction_type', prediction)
        self.assertIn('predicted_value', prediction)
        self.assertIn('confidence', prediction)
        self.assertIn('time_horizon', prediction)
        self.assertEqual(prediction['prediction_type'], 'performance')
        self.assertEqual(prediction['time_horizon'], 'medium')
    
    def test_get_issue_prediction(self):
        """Test get_issue_prediction convenience function."""
        prediction = get_issue_prediction(str(self.test_path), 'short')
        
        self.assertIsInstance(prediction, dict)
        self.assertIn('prediction_type', prediction)
        self.assertIn('predicted_value', prediction)
        self.assertIn('confidence', prediction)
        self.assertIn('time_horizon', prediction)
        self.assertEqual(prediction['prediction_type'], 'issues')
        self.assertEqual(prediction['time_horizon'], 'short')
    
    def test_get_comprehensive_analytics(self):
        """Test get_comprehensive_analytics convenience function."""
        analytics = get_comprehensive_analytics(str(self.test_path))
        
        self.assertIsInstance(analytics, dict)
        
        # Check all prediction types
        expected_types = ['performance', 'issues', 'resources', 'velocity', 'workflow_optimization']
        for pred_type in expected_types:
            self.assertIn(pred_type, analytics)
        
        self.assertIn('summary', analytics)
    
    def test_record_performance_metrics(self):
        """Test record_performance_metrics convenience function."""
        metrics_dict = {
            'command_success_rate': 0.9,
            'average_execution_time': 2.0,
            'error_frequency': 0.05,
            'resource_usage': {'cpu': 40.0, 'memory': 50.0},
            'workflow_efficiency': 0.85,
            'git_operation_success': 0.95,
            'environment_health': 0.8
        }
        
        # Should not raise exception
        try:
            record_performance_metrics(metrics_dict, str(self.test_path))
        except Exception as e:
            self.fail(f"record_performance_metrics raised {e} unexpectedly")
    
    def test_error_handling(self):
        """Test error handling in convenience functions."""
        # Test with invalid path
        prediction = get_performance_prediction("/nonexistent/path")
        self.assertIsInstance(prediction, dict)
        self.assertIn('error', prediction)
        
        analytics = get_comprehensive_analytics("/nonexistent/path")
        self.assertIsInstance(analytics, dict)
        self.assertIn('error', analytics)


if __name__ == '__main__':
    unittest.main()
