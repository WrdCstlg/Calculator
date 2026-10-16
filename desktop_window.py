"""
QuantumCalc - Native Desktop Window
Launches the full QuantumCalc Web Studio as a dedicated native Windows Desktop application
using PyWebView (Edge Chromium / WebView2 engine) without browser chrome, tabs, or address bars.
"""

import sys
import os
import subprocess
import time
import urllib.request
import webview

def ensure_services_running():
    """Ensure both FastAPI backend and Next.js frontend are running."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")

    # Add Node to PATH if in LocalAppData
    local_node = os.path.expandvars(r"%LOCALAPPDATA%\Programs\nodejs")
    if os.path.exists(local_node):
        os.environ["PATH"] = local_node + os.pathsep + os.environ.get("PATH", "")

    # Check if backend (port 8000) is running
    backend_up = False
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=2) as resp:
            if resp.status == 200:
                backend_up = True
    except Exception:
        backend_up = False

    if not backend_up:
        print("[*] Starting Python FastAPI backend on port 8000...")
        backend_cmd = ["py", "-m", "uvicorn", "backend.server:app", "--host", "127.0.0.1", "--port", "8000"]
        subprocess.Popen(backend_cmd, cwd=base_dir, shell=True)

    # Check if frontend (port 3000) is running
    frontend_up = False
    try:
        with urllib.request.urlopen("http://localhost:3000", timeout=2) as resp:
            if resp.status == 200:
                frontend_up = True
    except Exception:
        frontend_up = False

    if not frontend_up:
        print("[*] Starting Next.js frontend on port 3000...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        subprocess.Popen([npm_cmd, "run", "dev"], cwd=frontend_dir, shell=True)
        # Wait up to 10 seconds for server to be responsive
        for _ in range(20):
            time.sleep(0.5)
            try:
                with urllib.request.urlopen("http://localhost:3000", timeout=1) as resp:
                    if resp.status == 200:
                        break
            except Exception:
                pass


def main():
    ensure_services_running()

    print("[+] Launching QuantumCalc Native Desktop Window...")
    # Create native desktop window
    window = webview.create_window(
        title="QuantumCalc - Scientific Desktop Studio",
        url="http://localhost:3000",
        width=1280,
        height=880,
        min_size=(960, 680),
        background_color="#0b0f19",
        text_select=True,
        zoomable=True
    )

    webview.start(private_mode=False)


if __name__ == "__main__":
    main()
