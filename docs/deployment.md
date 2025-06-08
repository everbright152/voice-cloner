# Deployment Guide for Enhanced Voice Cloning Application

This document provides instructions for deploying the Enhanced Voice Cloning Application to various cloud environments.

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- Access to a cloud provider (DigitalOcean, AWS, GCP, or Azure)
- For GPU acceleration: NVIDIA GPU with CUDA support

## Local Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/voice-cloning-app.git
   cd voice-cloning-app
   ```

2. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Access the application at http://localhost:8000

## Cloud Deployment Options

### DigitalOcean App Platform

1. Create a new app on DigitalOcean App Platform
2. Connect your GitHub repository
3. Configure as a Web Service with the following settings:
   - Source Directory: `/`
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `python run.py --host 0.0.0.0 --port 8080`
4. Add environment variables if needed
5. Deploy the application

### AWS Elastic Beanstalk

1. Initialize Elastic Beanstalk in your project:
   ```bash
   eb init
   ```

2. Create an environment:
   ```bash
   eb create voice-cloning-env
   ```

3. Deploy the application:
   ```bash
   eb deploy
   ```

### Google Cloud Run

1. Build the Docker image:
   ```bash
   docker build -t gcr.io/your-project-id/voice-cloning-app .
   ```

2. Push to Google Container Registry:
   ```bash
   docker push gcr.io/your-project-id/voice-cloning-app
   ```

3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy voice-cloning-app --image gcr.io/your-project-id/voice-cloning-app --platform managed
   ```

## GPU Acceleration

For optimal performance, deploy to a machine with NVIDIA GPU support:

1. Ensure the host has NVIDIA drivers and CUDA installed
2. Use the docker-compose.yml file which includes GPU configuration
3. Run with:
   ```bash
   docker-compose up --build
   ```

## Environment Variables

- `HOST`: Host address (default: 0.0.0.0)
- `PORT`: Port number (default: 8000)

## Troubleshooting

- **Application fails to start**: Check logs with `docker-compose logs`
- **Model loading errors**: Ensure sufficient memory/GPU memory is available
- **Slow performance**: Consider upgrading to a machine with GPU support

## Monitoring

Monitor application health and performance using:
- Cloud provider's built-in monitoring tools
- Prometheus and Grafana for custom metrics
- Application logs for detailed debugging
