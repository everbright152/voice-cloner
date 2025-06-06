"""
Entry point for the Voice Cloning Web App.

This module provides the entry point for running the application.
"""
import os
import argparse
import uvicorn
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Voice Cloning Web App")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["api", "ui", "combined"],
        default="combined",
        help="Run mode: api, ui, or combined"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload"
    )
    return parser.parse_args()


def run_api(host, port, reload):
    """Run the FastAPI application.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Whether to enable auto-reload
    """
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(
        "app.api.app:app",
        host=host,
        port=port,
        reload=reload
    )


def run_ui(host, port):
    """Run the Gradio UI.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    logger.info(f"Starting UI server on {host}:{port}")
    from app.main import create_ui
    app = create_ui()
    app.launch(server_name=host, server_port=port)


def run_combined(host, port, reload):
    """Run both API and UI.
    
    In combined mode, we create a FastAPI app with Gradio mounted at /app.
    This ensures proper integration between FastAPI and Gradio.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Whether to enable auto-reload
    """
    logger.info(f"Starting combined server on {host}:{port}")
    
    # We'll use the app from app.api.app which already has Gradio mounted
    # This ensures proper integration between FastAPI and Gradio
    uvicorn.run(
        "app.api.app:app",
        host=host,
        port=port,
        reload=reload
    )


def main():
    """Main entry point."""
    args = parse_args()
    
    if args.mode == "api":
        run_api(args.host, args.port, args.reload)
    elif args.mode == "ui":
        run_ui(args.host, args.port)
    else:  # combined
        run_combined(args.host, args.port, args.reload)


if __name__ == "__main__":
    main()
