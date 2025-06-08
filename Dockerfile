# Dockerfile for Enhanced Voice Cloning Application

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p app/templates

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "8000"]
