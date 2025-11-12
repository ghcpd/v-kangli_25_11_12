# Dockerfile for Computer Vision Detection System
# Build: docker build -t cv-detection:latest .
# Run: docker run --rm -v $(pwd)/images:/app/images -v $(pwd)/output:/app/output cv-detection:latest

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libopenblas-dev \
    libgomp1 \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY detect.py .
COPY test_detection.py .

# Create output directories
RUN mkdir -p images output output_images

# Default command
CMD ["python", "detect.py"]
