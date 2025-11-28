# Dockerfile - Build instruction for autom8 API

# Base image
FROM python:3.11-slim

# Metadata
LABEL maintainer="Alphonce Liguori Oreny <orenyalphy256@gmail.com>"
LABEL description="Autom8 Systems Automation API"
LABEL version="1.0."

# System Dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Application Setup

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install python Dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Install application in editable mode
RUN pip install -e .

# Create directories for logs and data
RUN mkdir -p /app/data /app/../99-Logs

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV API_HOST=0.0.0.0
ENV API_PORT=5000

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests;requests.get('http://localhost:5000/api/v1/health/detailed')" || exit 1

# Default command
CMD ["python", "run_combined.py"]