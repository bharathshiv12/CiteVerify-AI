"""
Vercel Serverless Function Entry Point for CiteVerify FastAPI Backend.
Exposes the FastAPI ASGI application for Vercel's Python Serverless Runtime.
"""
import os
import sys

# Ensure backend directory is in sys.path for module resolution
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
