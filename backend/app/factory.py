from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router
from backend.app.core.config import CORS_ORIGINS
from backend.app.static.frontend import mount_frontend


def create_app() -> FastAPI:
    app = FastAPI(title="Workspace File Browser")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    mount_frontend(app)
    return app
