# Dockerfile for Windsurf Learning System Integration Example
# This demonstrates how to integrate the learning system into a containerized application

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash appuser

# Copy learning system
COPY windsurf-context-engineering/ /app/learning_system/
WORKDIR /app/learning_system
RUN pip install -r requirements.txt

# Copy application code
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set up learning system integration
ENV PYTHONPATH="/app/learning_system:$PYTHONPATH"
ENV LEARNING_DATA_DIR="/app/learning_data"
ENV LEARNING_ENABLED="true"

# Create learning data directory
RUN mkdir -p /app/learning_data && chown -R appuser:appuser /app/learning_data

# Switch to app user
USER appuser

# Health check with learning system integration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "from docker_app import health_check; exit(0 if health_check() else 1)"

# Expose port
EXPOSE 8080

# Start application with learning integration
CMD ["python", "docker_app.py"]
