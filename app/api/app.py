"""
FastAPI application for the Voice Cloning Web App.

This module initializes the FastAPI application and includes all routes.
"""
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.api import webhooks

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
        TemplateResponse: Rendered template
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Voice Cloning Web App"}
    )


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
