# Dockerfile - Build instructions for autom8 api service

# Base image
FROM python:3.11-slim

# Metadata
LABEL maintainer="Alphonce Liguori Oreny <orenyalphy256@gmail.com>"
LABEL description="Autom8 Systems Automation Platform API Service"
LABEL version="1.0.0"

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Application setup
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install application in editable mode
RUN pip install -e .

# Runtime configuration
RUN mkdir -p /app/data /app/logs

EXPOSE 5000

# environment variables
ENV FLASK_APP=run_api.py
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/v1/health')" || exit 1

# Default command
CMD ["python", "run_combined.py"]