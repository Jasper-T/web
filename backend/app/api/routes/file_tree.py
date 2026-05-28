from fastapi import APIRouter, Query

from backend.app.core.config import WORKSPACE_ROOT
from backend.app.schemas.file_tree import TreeResponse
from backend.app.services.file_tree import read_directory_tree


router = APIRouter()


@router.get("/tree", response_model=TreeResponse)
def read_tree(
    path: str = Query(default=str(WORKSPACE_ROOT), description="Absolute path under /workspace"),
) -> TreeResponse:
    return read_directory_tree(path)
