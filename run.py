#!/usr/bin/env python
"""
PolicyLens AI — Unified Startup Script
Runs both backend (FastAPI) and frontend (Vite) together
"""
import subprocess
import sys
import os
import time
from pathlib import Path
from shutil import which

# Change to project directory
PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)


def _resolve_python() -> str:
    candidates = [
        PROJECT_DIR / "venv" / "Scripts" / "python.exe",
        PROJECT_DIR.parent / "venv" / "Scripts" / "python.exe",
        PROJECT_DIR / "venv" / "bin" / "python",
        PROJECT_DIR.parent / "venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def _resolve_npm() -> str:
    if os.name == "nt":
        return which("npm.cmd") or which("npm") or "npm.cmd"
    return which("npm") or "npm"


python_exec = _resolve_python()
npm_exec = _resolve_npm()

def main() -> int:
    print("""
╔═══════════════════════════════════════════════════════════╗
║           PolicyLens AI — Starting Both Servers          ║
║                                                           ║
║  Backend:   http://127.0.0.1:8000                        ║
║  Frontend:  http://localhost:3000                        ║
║  API Docs:  http://127.0.0.1:8000/docs                 ║
╚═══════════════════════════════════════════════════════════╝
""")

    # Start backend
    print("🚀 Starting Backend on port 8000...")
    backend_process = subprocess.Popen(
        [python_exec, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"],
        cwd=PROJECT_DIR,
    )

    # Start frontend
    print("🎨 Starting Frontend on port 3000...")
    frontend_process = subprocess.Popen([npm_exec, "run", "dev"], cwd=PROJECT_DIR / "frontend")

    print("""
✅ Both servers are running!
Press Ctrl+C to stop.
""")

    exit_code = 0
    try:
        while True:
            if backend_process.poll() is not None:
                raise RuntimeError("Backend exited unexpectedly.")
            if frontend_process.poll() is not None:
                raise RuntimeError("Frontend exited unexpectedly.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping PolicyLens AI...")
    except RuntimeError as exc:
        print(f"\n{exc}")
        exit_code = 1
    finally:
        for process in (backend_process, frontend_process):
            if process.poll() is None:
                process.terminate()

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
