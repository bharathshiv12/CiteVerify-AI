# Windows Troubleshooting & Developer Guide

This guide documents Windows-specific development considerations, known pitfalls, and recommended workarounds for CiteVerify AI.

---

## 1. Virtual Environment Activation

Depending on your shell, activate the backend virtual environment as follows:

### PowerShell
```powershell
backend\.venv\Scripts\Activate.ps1
```
*Note on Execution Policy:* If PowerShell displays `cannot be loaded because running scripts is disabled on this system`, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
Then rerun the activation command. Alternatively, invoke Python directly from the venv:
```powershell
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### Git Bash / WSL
```bash
source backend/.venv/Scripts/activate
```

---

## 2. Line Endings (CRLF vs LF)

Windows text editors typically default to CRLF line endings (`\r\n`), which can introduce git churn and break shell scripts or POSIX tools.
- We have committed `.gitattributes` enforcing:
  ```gitattributes
  * text=auto eol=lf
  *.py text eol=lf
  *.ts text eol=lf
  *.tsx text eol=lf
  *.json text eol=lf
  *.yaml text eol=lf
  *.yml text eol=lf
  *.md text eol=lf
  ```
- Configure Git locally if needed:
  ```bash
  git config core.autocrlf input
  ```

---

## 3. Windows Long Path Limitations

By default, the Windows API limits maximum path lengths to 260 characters (`MAX_PATH`). Deep `node_modules` or nested Python virtual environment trees can occasionally hit this limit.
- **Fix:** Keep the repository path reasonably short (e.g., `%USERPROFILE%\Desktop\CiteVerify-AI`).
- To enable long paths system-wide (requires Admin PowerShell):
  ```powershell
  New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
  ```

---

## 4. Port Conflicts (8000 & 3000)

- **Backend default:** `http://localhost:8000`
- **Frontend default:** `http://localhost:3000`

If port 8000 or 3000 is occupied by another local service:
- Check what process is using the port:
  ```powershell
  Get-NetTCPConnection -LocalPort 8000
  ```
- Override ports using environment variables:
  - Backend: set `BACKEND_PORT=8080` in `backend/.env`
  - Frontend: `npm run dev -- -p 3001` or set `PORT=3001`

---

## 5. Windows Defender & File I/O Slowdown

Windows Defender real-time scanning can significantly slow down `npm install`, Next.js builds, and Python package installations due to inspecting thousands of small files inside `node_modules/` and `.venv/`.
- **Recommendation:** If builds feel sluggish, add an exclusion in Windows Security for the project directory:
  - Settings -> Windows Security -> Virus & threat protection -> Manage settings -> Exclusions -> Add folder -> `%USERPROFILE%\Desktop\CiteVerify-AI`.

---

## 6. Python 3.13 Binary Wheels

Some third-party C/C++ compiled packages may not yet have pre-built binary wheels for Python 3.13 on Windows.
- If a package like `torch` or `pymupdf` fails to compile from source (missing Visual C++ Build Tools):
  1. For text extraction, pure-Python fallbacks (`pypdf`, `pdfplumber`) or PyMuPDF wheel-verified versions can be used.
  2. For embeddings and verification, our AI Engine architecture is abstracted to support zero-shot cloud LLMs (Gemini / OpenAI API) and remote embeddings so local compilation is not a blocker.
