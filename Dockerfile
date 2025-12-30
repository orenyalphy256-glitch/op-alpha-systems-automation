# ============================================================================
# RUNTIME STAGE (Single Stage Build using Local Cache)
# ============================================================================

# Use locally verified image to bypass network registry blocks
FROM autom8:20251223_024601

# Set labels
LABEL maintainer="Autom8 Engineering"
LABEL description="Autom8 Systems Automation Platform"
LABEL version="1.0.1+restored"

# Switch to root to perform updates
USER root

# Set working directory
WORKDIR /app

# Ensure we are using the venv from the base image
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and try to install (PyPI might work even if Docker Hub fails)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (Overwrites old version)
COPY . .

# Create directories with correct permissions if they don't exist
RUN mkdir -p /app/data /app/logs && \
    chown -R autom8:autom8 /app

# Security: Remove unnecessary files
RUN find . -type f -name "*.pyc" -delete && \
    find . -type d -name "__pycache__" -delete

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_NAME=Autom8 \
    ENVIRONMENT=production \
    DEBUG=False

# Health check - Using absolute path to venv python
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /opt/venv/bin/python -c "import requests; requests.get('http://localhost:5000/api/v1/health', timeout=5).raise_for_status()" || exit 1

# Switch to non-root user
USER autom8

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "-m", "autom8.api"]