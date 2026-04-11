"""
server/app.py — OpenEnv multi-mode deployment entry point.
This re-exports the main FastAPI app and provides a start() callable
referenced by [project.scripts] server = "server.app:start"
"""
import uvicorn
import sys
import os

# Make sure the root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # re-export the FastAPI app

def start():
    """Entry point for openenv multi-mode deployment."""
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 7860)),
        reload=False,
    )

if __name__ == "__main__":
    start()
