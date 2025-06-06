"""
FastAPI application for the Voice Cloning Web App.

This module initializes the FastAPI application and includes all routes.
"""
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse

from app.api import webhooks
from app.main import create_ui

# Create FastAPI app
app = FastAPI(
    title="Voice Cloning API",
    description="API for voice cloning using Resemble AI's Chatterbox",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(webhooks.router)

# Templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def root(request: Request):
    """Root endpoint.
    
    Args:
        request: FastAPI request
        
    Returns:
        TemplateResponse: Rendered template with proper app access instructions
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Voice Cloning Web App"}
    )

@app.get("/app")
async def app_redirect():
    """Redirect to the Gradio UI.
    
    Returns:
        RedirectResponse: Redirect to the Gradio UI
    """
    from fastapi.responses import RedirectResponse
    # In production, this should be the actual URL where Gradio is mounted
    return RedirectResponse(url="/gradio")

@app.get("/gradio")
async def serve_gradio(request: Request):
    """Serve the Gradio UI.
    
    Args:
        request: FastAPI request
        
    Returns:
        HTMLResponse: HTML response with embedded Gradio UI
    """
    from fastapi.responses import HTMLResponse
    
    # Create a simple HTML page that embeds the Gradio interface
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Voice Cloning App - Gradio Interface</title>
        <style>
            body, html {
                margin: 0;
                padding: 0;
                height: 100%;
                overflow: hidden;
            }
            .gradio-container {
                width: 100%;
                height: 100vh;
                border: none;
            }
            .loading {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                font-family: Arial, sans-serif;
                font-size: 1.5rem;
                color: #6f42c1;
            }
        </style>
    </head>
    <body>
        <div class="loading" id="loading">Loading Voice Cloning Interface...</div>
        <iframe src="/gradio-app" class="gradio-container" id="gradio-iframe" style="display:none;"></iframe>
        
        <script>
            // Show the iframe once it's loaded
            document.getElementById('gradio-iframe').onload = function() {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('gradio-iframe').style.display = 'block';
            };
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@app.get("/app")
async def launch_app(request: Request):
    """Launch the Gradio application.
    
    Args:
        request: FastAPI request
        
    Returns:
        HTMLResponse: HTML content for the Gradio UI
    """
    # Create a simple HTML page that embeds the Gradio interface
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Voice Cloning App - Gradio Interface</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: #f8f9fa;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                margin-bottom: 20px;
                padding-bottom: 20px;
                border-bottom: 1px solid #dee2e6;
            }
            .btn-back {
                margin-bottom: 20px;
            }
            iframe {
                width: 100%;
                height: 800px;
                border: none;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Voice Cloning Application</h1>
                <p class="lead">Upload audio samples and generate text-to-speech with your cloned voice</p>
            </div>
            
            <a href="/" class="btn btn-outline-secondary btn-back">← Back to Home</a>
            
            <div class="gradio-container">
                <iframe src="/gradio" allow="microphone"></iframe>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": "voice-cloning-api",
        "version": "0.1.0"
    }
