from fastapi import APIRouter

from backend.app.api.routes import dsetkit, file_tree


api_router = APIRouter(prefix="/api")
api_router.include_router(file_tree.router)
api_router.include_router(dsetkit.router)
