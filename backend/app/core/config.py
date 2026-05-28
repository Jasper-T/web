from pathlib import Path


WORKSPACE_ROOT = Path("/workspace").resolve()
FRONTEND_DIST = Path(__file__).resolve().parents[3] / "frontend" / "dist"

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
