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

    When Vercel processes rewrites (e.g. {"source": "/(.*)", "destination": "/api/index"}),
    the ASGI scope['path'] is passed as '/api/index'.
    Vercel conveys the client's actual requested URL path in headers such as
    'x-matched-path', 'x-vercel-matched-path', or 'x-forwarded-uri'.

    This middleware detects the client's original path and restores scope['path']
    so FastAPI routers match routes (/health, /api/health, /api/documents, etc.) accurately.
    """

    def __init__(self, inner_app):
        self.inner_app = inner_app

    def __getattr__(self, name):
        return getattr(self.inner_app, name)

    async def __call__(self, scope, receive, send):
        if scope.get("type") in ("http", "websocket"):
            headers = dict(scope.get("headers", []))

            # Check for Vercel's pre-rewrite path headers
            matched_header = (
                headers.get(b"x-matched-path")
                or headers.get(b"x-vercel-matched-path")
                or headers.get(b"x-forwarded-uri")
                or headers.get(b"x-original-url")
                or headers.get(b"x-rewrite-url")
            )

            orig_path = ""
            if matched_header:
                matched_str = matched_header.decode("utf-8", errors="ignore")
                # Split path from query string if present
                if "?" in matched_str:
                    path_part, query_part = matched_str.split("?", 1)
                    if not scope.get("query_string") and query_part:
                        scope["query_string"] = query_part.encode("latin-1")
                else:
                    path_part = matched_str

                orig_path = path_part.strip()

            current_path = scope.get("path", "")

            if orig_path:
                if not orig_path.startswith("/"):
                    orig_path = "/" + orig_path

                # Normalize /api/index (and /api/index/) to root /
                if orig_path == "/api/index" or orig_path == "/api/index/":
                    resolved_path = "/"
                elif orig_path.startswith("/api/index/"):
                    resolved_path = orig_path[len("/api/index"):]
                else:
                    resolved_path = urllib.parse.unquote(orig_path)

                scope["path"] = resolved_path
                if "raw_path" in scope:
                    scope["raw_path"] = resolved_path.encode("latin-1")
            else:
                # Fallback when no header is present
                if current_path == "/api/index" or current_path == "/api/index/":
                    scope["path"] = "/"
                elif current_path.startswith("/api/index/"):
                    scope["path"] = current_path[len("/api/index"):]
                if "raw_path" in scope:
                    scope["raw_path"] = scope["path"].encode("latin-1")

        await self.inner_app(scope, receive, send)


app = VercelPathRewriteMiddleware(fastapi_app)
