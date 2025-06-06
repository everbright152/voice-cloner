"""
FastAPI application for the Voice Cloning Web App.

This module initializes the FastAPI application and includes all routes.
"""
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import gradio as gr

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

# Create Gradio UI and mount it to FastAPI
gradio_app = create_ui()
app = gr.mount_gradio_app(app, gradio_app, path="/app")


@app.get("/")
async def root(request: Request):
    """Root endpoint.
    
    Args:
        request: FastAPI request
        
    Returns:
        TemplateResponse: Rendered template with proper app access instructions
    """
    # For API requests (e.g., from tools or scripts), return JSON
    if request.headers.get("accept") == "application/json":
        return {
            "message": "Voice Cloning API is running",
            "docs_url": "/docs",
            "app_url": "/app"
        }
    
    # For browser requests, render the landing page
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Voice Cloning Web App"}
    )


@app.get("/app/")
async def app_redirect():
    """Redirect /app/ to /app for consistency."""
    return RedirectResponse(url="/app")


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
