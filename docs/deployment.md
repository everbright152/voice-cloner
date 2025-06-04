# Deployment Guide

This document provides instructions for deploying the Voice Cloning Web Application.

## Local Development Deployment

### Prerequisites
- Python 3.11+
- Virtual environment (venv)
- FFmpeg (for audio processing)

### Setup Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd voice-cloning-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create a .env file with the following variables
CHATTERBOX_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./app.db
```

5. Run the application:
```bash
python run.py --mode combined --host 0.0.0.0 --port 8000
```

6. Access the application:
   - Web UI: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Production Deployment

### Vercel Deployment

For deploying to Vercel:

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Configure the project:
```bash
vercel init
```

3. Deploy:
```bash
vercel --prod
```

### Alternative Deployment Options

#### Docker Deployment

1. Build the Docker image:
```bash
docker build -t voice-cloning-app .
```

2. Run the container:
```bash
docker run -p 8000:8000 -e CHATTERBOX_API_KEY=your_api_key_here voice-cloning-app
```

#### Heroku Deployment

1. Install Heroku CLI and login:
```bash
heroku login
```

2. Create a Heroku app:
```bash
heroku create voice-cloning-app
```

3. Set environment variables:
```bash
heroku config:set CHATTERBOX_API_KEY=your_api_key_here
```

4. Deploy:
```bash
git push heroku main
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| CHATTERBOX_API_KEY | API key for Resemble AI's Chatterbox | Yes |
| DATABASE_URL | Database connection string | Yes |
| PORT | Port to run the application on | No (default: 8000) |
| HOST | Host to bind to | No (default: 0.0.0.0) |
| LOG_LEVEL | Logging level | No (default: INFO) |

## Webhook Configuration

To configure webhooks for Make.com integration:

1. Deploy the application and note the public URL
2. In Make.com, create a webhook trigger pointing to:
   - `https://your-app-url/webhooks/make`
3. In Chatterbox dashboard, configure webhooks to point to:
   - `https://your-app-url/webhooks/chatterbox`

## Scaling Considerations

For production use with multiple users:

1. Migrate from SQLite to PostgreSQL
2. Set up cloud storage for audio files
3. Configure proper authentication and user management
4. Set up a job queue for processing training requests
5. Consider containerization and orchestration for horizontal scaling
