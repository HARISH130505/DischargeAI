"""
server/app.py — OpenEnv multi-mode deployment entry point.
Provides a main() callable referenced by [project.scripts] server = "server.app:main"
"""
import uvicorn
import sys
import os

# Make sure the root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # re-export the FastAPI app


def main():
    """Entry point for openenv multi-mode deployment."""
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 7860)),
        reload=False,
    )


if __name__ == "__main__":
    main()
