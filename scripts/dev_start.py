"""
CiteVerify AI - Local Development Launcher
Launches backend (FastAPI/uvicorn) and optionally frontend (Next.js) concurrently.
"""
import os
import sys
import subprocess
import time
import signal

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_backend_python():
    if os.name == "nt":
        venv_py = os.path.join(REPO_ROOT, "backend", ".venv", "Scripts", "python.exe")
    else:
        venv_py = os.path.join(REPO_ROOT, "backend", ".venv", "bin", "python")
    return venv_py if os.path.exists(venv_py) else sys.executable


def main():
    include_frontend = "--full" in sys.argv or "--frontend" in sys.argv
    backend_py = get_backend_python()

    print("=" * 60)
    print(" Starting CiteVerify AI Development Server")
    print(f" Backend Python: {backend_py}")
    print("=" * 60)

    processes = []

    try:
        # 1. Start Backend
        backend_cmd = [
            backend_py,
            "-m",
            "uvicorn",
            "app.main:app",
            "--app-dir",
            "backend",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        ]
        print("\n[BACKEND] Starting FastAPI server on http://127.0.0.1:8000 ...")
        p_back = subprocess.Popen(backend_cmd, cwd=REPO_ROOT)
        processes.append(p_back)

        # 2. Optionally start Frontend
        if include_frontend:
            frontend_dir = os.path.join(REPO_ROOT, "frontend")
            print("[FRONTEND] Starting Next.js client on http://localhost:3000 ...")
            npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
            p_front = subprocess.Popen([npm_cmd, "run", "dev"], cwd=frontend_dir)
            processes.append(p_front)

        print("\nAll services launched. Press Ctrl+C to terminate.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down development servers...")
    finally:
        for p in processes:
            p.terminate()
            try:
                p.wait(timeout=3)
            except Exception:
                p.kill()
        print("Shutdown complete.")


if __name__ == "__main__":
    main()

