# ============================================================================
# AUTOM8 - SECURE DOCKER IMAGE
# Multi-stage build with security hardening
# ============================================================================

# BUILD STAGE
FROM python:3.11-slim AS builder

# Set build arguments
ARG PYTHON_VERSION=3.11

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# RUNTIME STAGE
# ============================================================================

FROM python:3.11-slim

# Set labels
LABEL maintainer="Autom8 Engineering"
LABEL description="Autom8 Systems Automation Platform"
LABEL version="1.0.0"

# Security: Create non-root user
RUN groupadd -r autom8 && \
    useradd -r -g autom8 -s /bin/false autom8

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=autom8:autom8 . .

# Create directories with correct permissions
RUN mkdir -p /app/data /app/logs && \
    chown -R autom8:autom8 /app

# Security: Remove unnecessary files
RUN find . -type f -name "*.pyc" -delete && \
    find . -type d -name "__pycache__" -delete

# Environment variables (defaults, override with .env)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_NAME=Autom8 \
    ENVIRONMENT=production \
    DEBUG=False

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/v1/health', timeout=5).raise_for_status()" || exit 1

# Switch to non-root user
USER autom8

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "-m", "autom8.api"]