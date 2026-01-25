"""
Script to run the Streamlit frontend.
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    print("Starting Adaptive Math Learning Frontend...")
    print("Open in browser: http://localhost:8501")
    print("-" * 50)

    frontend_path = Path(__file__).parent / "frontend" / "app.py"

    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(frontend_path),
        "--server.port", "8501",
        "--server.headless", "true",
    ])
