"""
Top-level entrypoint for Vercel Python serverless runtime and local runners.
Exposes the ASGI app instance from api.index.
"""
import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from api.index import app
