"""
CodeLite AI - FastAPI Server Entrypoint
Serves both the REST API and the futuristic developer frontend dashboard.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes import router as api_router
from bifrost.client import get_bifrost_client

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="CodeLite AI",
    description="Token-Efficient Autonomous Coding Agent Powered by Bifrost LLM Gateway",
    version="1.0.0"
)

# Enable CORS for local development and client integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core API routes
app.include_router(api_router)

# Mount frontend static directory if exists
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/app.js")
    async def serve_app_js():
        return FileResponse(FRONTEND_DIR / "app.js", media_type="text/javascript")

    @app.get("/styles.css")
    async def serve_styles_css():
        return FileResponse(FRONTEND_DIR / "styles.css", media_type="text/css")

    @app.get("/favicon.ico")
    async def favicon():
        return FileResponse(FRONTEND_DIR / "favicon.svg", media_type="image/svg+xml")


@app.get("/ping")
def ping():
    return {"status": "ok", "service": "CodeLite AI"}


def start():
    """CLI launcher for uvicorn server."""
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    start()
