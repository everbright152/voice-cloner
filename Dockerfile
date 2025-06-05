FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install chatterbox-tts directly from GitHub
RUN pip install git+https://github.com/resemble-ai/chatterbox.git

# Copy application code
COPY . .

# Ensure static directories exist
RUN mkdir -p app/static/css app/static/js app/static/uploads

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python", "run.py", "--mode", "combined", "--host", "0.0.0.0", "--port", "8000"]
