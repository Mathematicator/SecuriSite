# Dockerfile for SecuriSite-IA Multi-Agent Construction Risk Analysis System
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY assets/ ./assets/
COPY rapport.md ./

# Set environment variables
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# Create directories for reports and logs
RUN mkdir -p /app/reports /app/logs

# Switch to non-root user
RUN useradd -m -u 1000 securisite && \
    chown -R securisite:securisite /app

USER securisite

# Run the application
CMD ["python", "src/main.py"]