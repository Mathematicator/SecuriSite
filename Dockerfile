# SecuriSite-IA Production Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/src/securisite/static/css \
    && mkdir -p /app/src/securisite/templates \
    && mkdir -p /app/assets

# Set environment variables for production
ENV FLASK_ENV=production
ENV FLASK_DEBUG=False
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=8080
ENV PYTHONPATH=/app/src:/app

# Expose port for Cloud Run
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/login || exit 1

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash securisite
RUN chown -R securisite:securisite /app
USER securisite

# Start the application
CMD ["python", "src/run_web_app.py"]