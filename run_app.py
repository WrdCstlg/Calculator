"""
Scientific Calculator - Launcher Script
Runs the Python FastAPI backend server on port 8000 and the Next.js frontend on port 3000.
"""

import subprocess
import sys
import os
import time
import webbrowser

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    backend_dir = os.path.join(base_dir, "backend")

    # Ensure Node is on PATH if in LocalAppData
    local_node = os.path.expandvars(r"%LOCALAPPDATA%\Programs\nodejs")
    if os.path.exists(local_node):
        os.environ["PATH"] = local_node + os.pathsep + os.environ.get("PATH", "")

    print("=" * 60)
    print("   SCIENTIFIC CALCULATOR: NEXT.JS + PYTHON SCIENTIFIC ENGINE   ")
    print("=" * 60)
    print("Starting FastAPI Backend (SymPy + NumPy + SciPy + Pandas)...")

    # Start FastAPI backend
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.server:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    backend_proc = subprocess.Popen(backend_cmd, cwd=base_dir)

    print("Starting Next.js Frontend on http://localhost:3000 ...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen([npm_cmd, "run", "dev"], cwd=frontend_dir)

    time.sleep(3)
    print("\n[+] Services are running!")
    print("    - Web Frontend UI : http://localhost:3000")
    print("    - Python API Docs : http://127.0.0.1:8000/docs")
    print("    - Desktop Native  : py desktop_calculator.py")
    print("    - Desktop Window  : py desktop_window.py")
    print("Press Ctrl+C to stop servers.\n")

    if "--desktop" in sys.argv:
        print("[+] Launching Native Desktop Calculator...")
        subprocess.Popen([sys.executable, "desktop_calculator.py"], cwd=base_dir)
    elif "--window" in sys.argv:
        print("[+] Launching PyWebView Desktop Window...")
        subprocess.Popen([sys.executable, "desktop_window.py"], cwd=base_dir)

    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    main()
