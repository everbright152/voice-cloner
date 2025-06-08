"""
FastAPI application for the Enhanced Voice Cloning Application
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import gradio as gr
from app.main import demo as gradio_app

# Create FastAPI app
app = FastAPI(title="Enhanced Voice Cloning Application")

# Mount Gradio app at /app path
app = gr.mount_gradio_app(app, gradio_app, path="/app")

# Create a simple landing page
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the landing page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Enhanced Voice Cloning Application"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
