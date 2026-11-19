"""
CiteVerify AI - Environment & Setup Sanity Checker
Audits installed runtimes, project virtual environment, dependencies, and configuration files.
"""
import sys
import os
import subprocess
import shutil

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def check_tool(name: str, args: list) -> str:
    target = f"{name}.cmd" if (os.name == "nt" and name in ("npm", "pnpm", "yarn", "npx")) else name
    exe = shutil.which(target) or shutil.which(name)
    if not exe:
        return "NOT FOUND"
    try:
        out = subprocess.check_output([exe] + args, text=True, stderr=subprocess.STDOUT, shell=(os.name == "nt"))
        return out.strip().split("\n")[0]
    except Exception:
        return "ERROR EXECUTING"


def main():
    print("=" * 60)
    print(" CiteVerify AI - System & Environment Audit")
    print("=" * 60)

    # 1. System executables
    tools = {
        "python": ["--version"],
        "git": ["--version"],
        "node": ["--version"],
        "npm": ["--version"],
    }
    for tool, args in tools.items():
        ver = check_tool(tool, args)
        print(f"  {tool:<10}: {ver}")

    # 2. Virtual environment check
    venv_python = (
        os.path.join(REPO_ROOT, "backend", ".venv", "Scripts", "python.exe")
        if os.name == "nt"
        else os.path.join(REPO_ROOT, "backend", ".venv", "bin", "python")
    )
    has_venv = os.path.exists(venv_python)
    print(f"  {'backend/.venv':<10}: {'FOUND' if has_venv else 'MISSING'}")

    # 3. Check critical files
    critical_files = [
        ".env.example",
        "contracts/openapi/openapi.yaml",
        "contracts/schemas/enums.json",
        "backend/app/main.py",
        "frontend/package.json",
    ]
    print("\n  Checking critical project files:")
    all_files_ok = True
    for f in critical_files:
        path = os.path.join(REPO_ROOT, f)
        ok = os.path.exists(path)
        all_files_ok = all_files_ok and ok
        status_str = "OK" if ok else "MISSING"
        print(f"    [{status_str:<7}] {f}")

    print("\n" + "=" * 60)
    if has_venv and all_files_ok:
        print(" Environment status: READY FOR DEVELOPMENT")
    else:
        print(" Environment status: INCOMPLETE (Run setup instructions in README)")
    print("=" * 60)


if __name__ == "__main__":
    main()
