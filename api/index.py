"""
Vercel Serverless Function Entrypoint
Exposes the FastAPI application instance for Vercel's Python runtime.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path so all internal modules (core, bifrost, benchmarking) resolve
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from api.main import app
