#!/usr/bin/env python3
"""
Flask Integration Example for Windsurf Learning System

This example demonstrates how to integrate the Windsurf Learning System
with a Flask web application to automatically track API performance,
user interactions, and deployment outcomes.

Usage:
    python flask_integration_example.py

Features:
    - Automatic API performance tracking
    - User interaction recording
    - Deployment outcome tracking
    - Real-time recommendations
    - Health monitoring endpoint
"""

import os
import sys
import time
from datetime import datetime
from flask import Flask, request, jsonify, g
from functools import wraps

# Add learning system to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize Learning System
learning_config = LearningSystemConfig(
    learning_data_dir="./flask_learning_data"
)
learning_system = LearningSystemIntegration(learning_config)

# Track request performance
@app.before_request
def before_request():
    """Record request start time"""
    g.start_time = time.time()
    g.request_id = f"flask_request_{int(time.time() * 1000)}"

@app.after_request
def after_request(response):
    """Record request completion and performance"""
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        
        # Record API performance in learning system
        try:
            learning_system.process_project_completion(
                project_id=g.request_id,
                user_id=request.remote_addr or 'unknown',
                project_data={
                    "name": f"API Request {request.path}",
                    "type": "api_request",
                    "method": request.method,
                    "path": request.path,
                    "endpoint": request.endpoint,
                    "timestamp": datetime.now().isoformat()
                },
                outcome_data={
                    "success": 200 <= response.status_code < 400,
                    "completion_time": duration,
                    "status_code": response.status_code,
                    "response_size": len(response.get_data())
                }
            )
        except Exception as e:
            app.logger.error(f"Failed to record request in learning system: {e}")
    
    return response

# Decorator for tracking specific operations
def track_operation(operation_type):
    """Decorator to track specific operations"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            operation_id = f"{operation_type}_{int(time.time() * 1000)}"
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record successful operation
                learning_system.process_project_completion(
                    project_id=operation_id,
                    user_id=request.remote_addr or 'system',
                    project_data={
                        "name": f"{operation_type.title()} Operation",
                        "type": operation_type,
                        "function": f.__name__,
                        "timestamp": datetime.now().isoformat()
                    },
                    outcome_data={
                        "success": True,
                        "completion_time": duration,
                        "result_type": type(result).__name__
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record failed operation
                learning_system.process_project_completion(
                    project_id=operation_id,
                    user_id=request.remote_addr or 'system',
                    project_data={
                        "name": f"{operation_type.title()} Operation",
                        "type": operation_type,
                        "function": f.__name__,
                        "timestamp": datetime.now().isoformat()
                    },
                    outcome_data={
                        "success": False,
                        "completion_time": duration,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )
                
                raise
        
        return decorated_function
    return decorator

# API Routes
@app.route('/')
def index():
    """Home page"""
    return jsonify({
        "message": "Flask Learning System Integration Example",
        "version": "1.0.0",
        "learning_system": "active"
    })

@app.route('/api/users', methods=['GET'])
@track_operation('user_list')
def get_users():
    """Get all users - tracked operation"""
    # Simulate some processing time
    time.sleep(0.1)
    
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
    ]
    
    return jsonify({"users": users, "count": len(users)})

@app.route('/api/users', methods=['POST'])
@track_operation('user_create')
def create_user():
    """Create a new user - tracked operation"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email are required"}), 400
    
    # Simulate processing time
    time.sleep(0.2)
    
    new_user = {
        "id": 4,
        "name": data['name'],
        "email": data['email'],
        "created_at": datetime.now().isoformat()
    }
    
    return jsonify({"user": new_user, "message": "User created successfully"}), 201

@app.route('/api/users/<int:user_id>', methods=['GET'])
@track_operation('user_get')
def get_user(user_id):
    """Get specific user - tracked operation"""
    # Simulate database lookup time
    time.sleep(0.05)
    
    if user_id > 3:
        return jsonify({"error": "User not found"}), 404
    
    user = {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    }
    
    return jsonify({"user": user})

@app.route('/api/process-data', methods=['POST'])
@track_operation('data_processing')
def process_data():
    """Process data - tracked operation that might fail"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Simulate processing time
    processing_time = data.get('processing_time', 0.3)
    time.sleep(processing_time)
    
    # Simulate occasional failures
    if data.get('simulate_failure', False):
        raise Exception("Simulated processing failure")
    
    result = {
        "processed_items": len(data.get('items', [])),
        "processing_time": processing_time,
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify({"result": result})

# Learning System Integration Endpoints
@app.route('/api/learning/recommendations')
def get_recommendations():
    """Get learning system recommendations"""
    try:
        recommendations = learning_system.get_project_recommendations({
            "project_type": "api_request",
            "user_id": request.remote_addr or 'unknown',
            "context": "flask_app"
        })
        
        return jsonify({
            "recommendations": recommendations,
            "count": len(recommendations),
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get recommendations: {e}"}), 500

@app.route('/api/learning/health')
def get_learning_health():
    """Get learning system health status"""
    try:
        status = learning_system.get_system_status()
        
        return jsonify({
            "system_health_score": status.system_health_score,
            "active_recommendations": status.active_recommendations,
            "total_projects": status.total_projects,
            "success_rate": status.success_rate,
            "avg_completion_time": status.avg_completion_time,
            "component_health": status.component_health,
            "last_updated": status.last_updated.isoformat() if status.last_updated else None
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get health status: {e}"}), 500

@app.route('/api/learning/record-deployment', methods=['POST'])
def record_deployment():
    """Record deployment outcome"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No deployment data provided"}), 400
    
    required_fields = ['deployment_id', 'success', 'duration', 'environment']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400
    
    try:
        result = learning_system.process_project_completion(
            project_id=f"flask_deployment_{data['deployment_id']}",
            user_id=data.get('user_id', 'system'),
            project_data={
                "name": f"Flask App Deployment {data['deployment_id']}",
                "type": "deployment",
                "environment": data['environment'],
                "timestamp": datetime.now().isoformat()
            },
            outcome_data={
                "success": data['success'],
                "completion_time": data['duration'],
                "environment": data['environment'],
                "deployment_id": data['deployment_id']
            }
        )
        
        return jsonify({
            "message": "Deployment recorded successfully",
            "result": result,
            "recorded_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to record deployment: {e}"}), 500

# Error handlers with learning integration
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    # Record 404 errors for learning
    try:
        learning_system.process_project_completion(
            project_id=f"404_error_{int(time.time() * 1000)}",
            user_id=request.remote_addr or 'unknown',
            project_data={
                "name": f"404 Error - {request.path}",
                "type": "error",
                "error_type": "404",
                "path": request.path,
                "timestamp": datetime.now().isoformat()
            },
            outcome_data={
                "success": False,
                "completion_time": 0,
                "error": "Not Found",
                "status_code": 404
            }
        )
    except Exception as e:
        app.logger.error(f"Failed to record 404 error: {e}")
    
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    # Record 500 errors for learning
    try:
        learning_system.process_project_completion(
            project_id=f"500_error_{int(time.time() * 1000)}",
            user_id=request.remote_addr or 'unknown',
            project_data={
                "name": f"500 Error - {request.path}",
                "type": "error",
                "error_type": "500",
                "path": request.path,
                "timestamp": datetime.now().isoformat()
            },
            outcome_data={
                "success": False,
                "completion_time": 0,
                "error": str(error),
                "status_code": 500
            }
        )
    except Exception as e:
        app.logger.error(f"Failed to record 500 error: {e}")
    
    return jsonify({"error": "Internal server error"}), 500

# Startup and shutdown hooks
@app.before_first_request
def startup():
    """Application startup"""
    print("🚀 Flask app starting with Learning System integration")
    print(f"📊 Learning data directory: {learning_config.learning_data_dir}")
    
    # Record application startup
    try:
        learning_system.process_project_completion(
            project_id=f"flask_startup_{int(time.time())}",
            user_id="system",
            project_data={
                "name": "Flask Application Startup",
                "type": "startup",
                "timestamp": datetime.now().isoformat()
            },
            outcome_data={
                "success": True,
                "completion_time": 0,
                "event": "application_startup"
            }
        )
    except Exception as e:
        app.logger.error(f"Failed to record startup: {e}")

def shutdown():
    """Application shutdown"""
    print("🛑 Flask app shutting down")
    
    # Record application shutdown
    try:
        learning_system.process_project_completion(
            project_id=f"flask_shutdown_{int(time.time())}",
            user_id="system",
            project_data={
                "name": "Flask Application Shutdown",
                "type": "shutdown",
                "timestamp": datetime.now().isoformat()
            },
            outcome_data={
                "success": True,
                "completion_time": 0,
                "event": "application_shutdown"
            }
        )
    except Exception as e:
        app.logger.error(f"Failed to record shutdown: {e}")

# CLI Commands for testing
def test_integration():
    """Test the learning system integration"""
    print("🧪 Testing Flask Learning System Integration...")
    
    # Test recording a sample project
    try:
        result = learning_system.process_project_completion(
            project_id="test_integration",
            user_id="test_user",
            project_data={
                "name": "Integration Test",
                "type": "test",
                "timestamp": datetime.now().isoformat()
            },
            outcome_data={
                "success": True,
                "completion_time": 1.5,
                "test": True
            }
        )
        print(f"✅ Test recording successful: {result}")
        
        # Test getting recommendations
        recommendations = learning_system.get_project_recommendations({
            "project_type": "test",
            "user_id": "test_user"
        })
        print(f"✅ Got {len(recommendations)} recommendations")
        
        # Test system health
        health = learning_system.get_system_status()
        print(f"✅ System health score: {health.system_health_score:.2f}")
        
        print("🎉 Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Flask Learning System Integration Example')
    parser.add_argument('--test', action='store_true', help='Run integration test')
    parser.add_argument('--host', default='127.0.0.1', help='Host to run on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.test:
        success = test_integration()
        sys.exit(0 if success else 1)
    else:
        print("🌟 Starting Flask Learning System Integration Example")
        print(f"📡 Server will run on http://{args.host}:{args.port}")
        print("\n🔗 Available endpoints:")
        print("  GET  /                              - Home page")
        print("  GET  /api/users                     - Get all users")
        print("  POST /api/users                     - Create user")
        print("  GET  /api/users/<id>                - Get specific user")
        print("  POST /api/process-data              - Process data")
        print("  GET  /api/learning/recommendations  - Get recommendations")
        print("  GET  /api/learning/health           - Get system health")
        print("  POST /api/learning/record-deployment - Record deployment")
        print("\n🧪 Test the integration:")
        print(f"  curl http://{args.host}:{args.port}/api/learning/health")
        print(f"  curl http://{args.host}:{args.port}/api/learning/recommendations")
        print()
        
        try:
            app.run(host=args.host, port=args.port, debug=args.debug)
        except KeyboardInterrupt:
            shutdown()
