"""
Run script for the Enhanced Voice Cloning Application
"""

import argparse
import os
import uvicorn
from app.api.app import app as fastapi_app

def parse_args():
    parser = argparse.ArgumentParser(description="Run the Enhanced Voice Cloning Application")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--mode", type=str, choices=["gradio", "fastapi", "combined"], default="combined",
                        help="Run mode: gradio for UI only, fastapi for API only, combined for both")
    return parser.parse_args()

def run_gradio(host, port, reload):
    """Run the Gradio UI server"""
    from app.main import demo
    demo.launch(server_name=host, server_port=port, share=False, reload=reload)

def run_fastapi(host, port, reload):
    """Run the FastAPI server"""
    uvicorn.run("app.api.app:app", host=host, port=port, reload=reload)

def run_combined(host, port, reload):
    """Run the combined FastAPI + Gradio server"""
    uvicorn.run(
        fastapi_app,
        host=host,
        port=port,
        reload=reload
    )

def main():
    args = parse_args()
    
    # Set environment variables
    os.environ["HOST"] = args.host
    os.environ["PORT"] = str(args.port)
    
    # Run in the specified mode
    if args.mode == "gradio":
        run_gradio(args.host, args.port, args.reload)
    elif args.mode == "fastapi":
        run_fastapi(args.host, args.port, args.reload)
    else:  # combined
        run_combined(args.host, args.port, args.reload)

if __name__ == "__main__":
    main()
