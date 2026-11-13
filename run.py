#!/usr/bin/env python3
"""
CodeLite AI - Application Entrypoint
Launches the FastAPI backend and futuristic developer dashboard.
"""

import sys
import os
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    print("=================================================================")
    print("[*] CodeLite AI - Token-Efficient Autonomous Coding Agent")
    print("[*] Powered by Bifrost LLM Gateway")
    print(f"[*] Gateway Target: {os.getenv('BIFROST_BASE_URL', 'http://localhost:8080/v1')}")
    print(f"[*] Model: {os.getenv('BIFROST_MODEL', 'openai/gpt-4o-mini')}")
    print(f"[*] Dashboard: http://{host}:{port}")
    print("=================================================================")

    uvicorn.run("api.main:app", host=host, port=port, reload=debug)


if __name__ == "__main__":
    main()
