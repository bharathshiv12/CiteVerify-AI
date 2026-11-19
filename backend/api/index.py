"""
Vercel Serverless Function Entry Point for CiteVerify FastAPI Backend.
Exposes the FastAPI ASGI application for Vercel's Python Serverless Runtime.
Includes VercelPathRewriteMiddleware to restore client request paths rewritten by Vercel.
"""
import os
import sys
import urllib.parse

# Ensure backend directory is in sys.path for module resolution
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app as fastapi_app


class VercelPathRewriteMiddleware:
    """
    ASGI middleware for Vercel Python Serverless Runtime.

    When Vercel processes rewrites to /api/index.py/$1:
    The ASGI scope['path'] arrives with prefix '/api/index.py' (or '/api/index').
    This middleware strips the entrypoint prefix so FastAPI routers match
    the intended target routes (/health, /api/health, /api/documents, etc.) accurately.
    """

    def __init__(self, inner_app):
        self.inner_app = inner_app

    def __getattr__(self, name):
        return getattr(self.inner_app, name)

    async def __call__(self, scope, receive, send):
        if scope.get("type") in ("http", "websocket"):
            path = scope.get("path", "")
            for prefix in ("/api/index.py", "/api/index"):
                if path == prefix or path == prefix + "/":
                    scope["path"] = "/"
                    break
                elif path.startswith(prefix + "/"):
                    scope["path"] = path[len(prefix):]
                    break
            if "raw_path" in scope:
                scope["raw_path"] = scope["path"].encode("latin-1")

        await self.inner_app(scope, receive, send)


app = VercelPathRewriteMiddleware(fastapi_app)
