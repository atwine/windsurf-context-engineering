#!/usr/bin/env python3
"""
Docker Integration Example for Windsurf Learning System

This example demonstrates how to integrate the Windsurf Learning System
into a containerized application with proper lifecycle management,
health checks, and container-aware logging.

Features:
    - Container lifecycle tracking
    - Health check integration
    - Environment-aware configuration
    - Docker-specific metrics
    - Graceful shutdown handling
"""

import os
import sys
import time
import signal
import threading
from datetime import datetime
from flask import Flask, jsonify, request
import logging

# Add learning system to path
sys.path.append('/app/learning_system')

from learning.learning_integration import LearningSystemIntegration, LearningSystemConfig

# Configure logging for container environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DockerLearningIntegration:
    """Docker-aware learning system integration"""
    
    def __init__(self):
        self.container_id = os.getenv('HOSTNAME', 'unknown')
        self.app_name = os.getenv('APP_NAME', 'docker_app')
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        # Initialize learning system
        self.config = LearningSystemConfig(
            learning_data_dir=os.getenv('LEARNING_DATA_DIR', '/app/learning_data')
        )
        self.learning_system = LearningSystemIntegration(self.config)
        
        # Container metrics
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        
        logger.info(f"🐳 Docker Learning Integration initialized")
        logger.info(f"📦 Container ID: {self.container_id}")
        logger.info(f"🏷️  App Name: {self.app_name}")
        logger.info(f"🌍 Environment: {self.environment}")
    
    def record_container_startup(self):
        """Record container startup event"""
        try:
            self.learning_system.process_project_completion(
                project_id=f"container_startup_{self.container_id}_{int(time.time())}",
                user_id="docker_system",
                project_data={
                    "name": f"Container Startup - {self.app_name}",
                    "type": "container_startup",
                    "container_id": self.container_id,
                    "app_name": self.app_name,
                    "environment": self.environment,
                    "timestamp": datetime.now().isoformat()
                },
                outcome_data={
                    "success": True,
                    "completion_time": 0,
                    "event": "startup",
                    "container_metrics": self._get_container_metrics()
                }
            )
            logger.info("✅ Container startup recorded in learning system")
        except Exception as e:
            logger.error(f"❌ Failed to record container startup: {e}")
    
    def record_container_shutdown(self):
        """Record container shutdown event"""
        try:
            uptime = time.time() - self.start_time
            self.learning_system.process_project_completion(
                project_id=f"container_shutdown_{self.container_id}_{int(time.time())}",
                user_id="docker_system",
                project_data={
                    "name": f"Container Shutdown - {self.app_name}",
                    "type": "container_shutdown",
                    "container_id": self.container_id,
                    "app_name": self.app_name,
                    "environment": self.environment,
                    "timestamp": datetime.now().isoformat()
                },
                outcome_data={
                    "success": True,
                    "completion_time": uptime,
                    "event": "shutdown",
                    "uptime": uptime,
                    "total_requests": self.request_count,
                    "total_errors": self.error_count,
                    "container_metrics": self._get_container_metrics()
                }
            )
            logger.info("✅ Container shutdown recorded in learning system")
        except Exception as e:
            logger.error(f"❌ Failed to record container shutdown: {e}")
    
    def record_request(self, path: str, method: str, status_code: int, duration: float):
        """Record HTTP request"""
        self.request_count += 1
        if status_code >= 400:
            self.error_count += 1
        
        try:
            self.learning_system.process_project_completion(
                project_id=f"http_request_{int(time.time() * 1000)}",
                user_id=request.remote_addr if request else "unknown",
                project_data={
                    "name": f"HTTP Request - {method} {path}",
                    "type": "http_request",
                    "container_id": self.container_id,
                    "app_name": self.app_name,
                    "method": method,
                    "path": path,
                    "timestamp": datetime.now().isoformat()
                },
                outcome_data={
                    "success": status_code < 400,
                    "completion_time": duration,
                    "status_code": status_code,
                    "container_metrics": self._get_container_metrics()
                }
            )
        except Exception as e:
            logger.error(f"❌ Failed to record request: {e}")
    
    def get_health_status(self) -> dict:
        """Get application and learning system health"""
        try:
            learning_health = self.learning_system.get_system_status()
            uptime = time.time() - self.start_time
            
            return {
                "status": "healthy",
                "uptime": uptime,
                "container_id": self.container_id,
                "app_name": self.app_name,
                "environment": self.environment,
                "request_count": self.request_count,
                "error_count": self.error_count,
                "error_rate": self.error_count / max(self.request_count, 1),
                "learning_system": {
                    "health_score": learning_health.system_health_score,
                    "active_recommendations": learning_health.active_recommendations,
                    "total_projects": learning_health.total_projects,
                    "success_rate": learning_health.success_rate
                },
                "container_metrics": self._get_container_metrics(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_container_metrics(self) -> dict:
        """Get basic container metrics"""
        try:
            # Read memory usage from cgroup (if available)
            memory_usage = None
            try:
                with open('/sys/fs/cgroup/memory/memory.usage_in_bytes', 'r') as f:
                    memory_usage = int(f.read().strip())
            except:
                pass
            
            # Read CPU usage from cgroup (if available)
            cpu_usage = None
            try:
                with open('/sys/fs/cgroup/cpu/cpuacct.usage', 'r') as f:
                    cpu_usage = int(f.read().strip())
            except:
                pass
            
            return {
                "uptime": time.time() - self.start_time,
                "memory_usage": memory_usage,
                "cpu_usage": cpu_usage,
                "request_count": self.request_count,
                "error_count": self.error_count
            }
        except Exception as e:
            logger.error(f"❌ Failed to get container metrics: {e}")
            return {}

# Initialize Docker learning integration
docker_integration = DockerLearningIntegration()

# Initialize Flask app
app = Flask(__name__)

# Request tracking middleware
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        docker_integration.record_request(
            path=request.path,
            method=request.method,
            status_code=response.status_code,
            duration=duration
        )
    return response

# Routes
@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        "message": "Docker Learning System Integration Example",
        "container_id": docker_integration.container_id,
        "app_name": docker_integration.app_name,
        "environment": docker_integration.environment,
        "uptime": time.time() - docker_integration.start_time
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    health_status = docker_integration.get_health_status()
    status_code = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), status_code

@app.route('/metrics')
def metrics():
    """Metrics endpoint"""
    try:
        learning_health = docker_integration.learning_system.get_system_status()
        
        metrics = {
            "container": {
                "id": docker_integration.container_id,
                "uptime": time.time() - docker_integration.start_time,
                "requests_total": docker_integration.request_count,
                "errors_total": docker_integration.error_count,
                "error_rate": docker_integration.error_count / max(docker_integration.request_count, 1)
            },
            "learning_system": {
                "health_score": learning_health.system_health_score,
                "active_recommendations": learning_health.active_recommendations,
                "total_projects": learning_health.total_projects,
                "success_rate": learning_health.success_rate,
                "avg_completion_time": learning_health.avg_completion_time
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recommendations')
def recommendations():
    """Get learning system recommendations"""
    try:
        recs = docker_integration.learning_system.get_project_recommendations({
            "project_type": "http_request",
            "container_id": docker_integration.container_id,
            "app_name": docker_integration.app_name
        })
        
        return jsonify({
            "recommendations": recs,
            "count": len(recs),
            "container_id": docker_integration.container_id,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data', methods=['GET', 'POST'])
def data_endpoint():
    """Sample data endpoint"""
    if request.method == 'POST':
        data = request.get_json()
        # Simulate processing
        time.sleep(0.1)
        return jsonify({
            "message": "Data processed successfully",
            "received": data,
            "processed_at": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "data": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"},
                {"id": 3, "name": "Item 3"}
            ],
            "count": 3
        })

@app.route('/api/simulate-error')
def simulate_error():
    """Simulate an error for testing"""
    raise Exception("This is a simulated error for testing purposes")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500

# Health check function for Docker
def health_check() -> bool:
    """Health check function for Docker HEALTHCHECK"""
    try:
        health_status = docker_integration.get_health_status()
        return health_status["status"] == "healthy"
    except:
        return False

# Graceful shutdown handling
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
    docker_integration.record_container_shutdown()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    # Record container startup
    docker_integration.record_container_startup()
    
    # Start background health monitoring
    def health_monitor():
        """Background health monitoring"""
        while True:
            try:
                time.sleep(60)  # Check every minute
                health_status = docker_integration.get_health_status()
                logger.info(f"📊 Health: {health_status['status']}, "
                           f"Requests: {health_status['request_count']}, "
                           f"Errors: {health_status['error_count']}")
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
    
    health_thread = threading.Thread(target=health_monitor, daemon=True)
    health_thread.start()
    
    # Start Flask app
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"🚀 Starting Docker app on {host}:{port}")
    logger.info(f"🔗 Health check: http://{host}:{port}/health")
    logger.info(f"📊 Metrics: http://{host}:{port}/metrics")
    logger.info(f"🤖 Recommendations: http://{host}:{port}/recommendations")
    
    try:
        app.run(host=host, port=port, debug=False)
    except KeyboardInterrupt:
        logger.info("🛑 Received keyboard interrupt")
    finally:
        docker_integration.record_container_shutdown()
