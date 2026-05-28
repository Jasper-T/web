from pathlib import Path

from fastapi import HTTPException

from backend.app.core.config import WORKSPACE_ROOT
from backend.app.schemas.file_tree import FileNode, TreeResponse


def resolve_workspace_path(raw_path: str | None) -> Path:
    path = Path(raw_path or str(WORKSPACE_ROOT))
    resolved = path.resolve(strict=False)

    try:
        resolved.relative_to(WORKSPACE_ROOT)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Path is outside /workspace") from exc

    if not resolved.exists():
        raise HTTPException(status_code=404, detail="Path does not exist")

    return resolved


def directory_has_children(path: Path) -> bool:
    if not path.is_dir():
        return False

    try:
        next(path.iterdir())
    except StopIteration:
        return False
    except OSError:
        return False

    return True


def to_file_node(path: Path) -> FileNode:
    is_directory = path.is_dir()
    return FileNode(
        name=path.name or str(path),
        path=str(path),
        type="directory" if is_directory else "file",
        hasChildren=directory_has_children(path) if is_directory else False,
    )


def read_directory_tree(raw_path: str | None) -> TreeResponse:
    target = resolve_workspace_path(raw_path)
    if not target.is_dir():
        return TreeResponse(path=str(target), children=[])

    try:
        children = [to_file_node(child) for child in target.iterdir()]
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail="Permission denied") from exc

    children.sort(key=lambda item: (item.type != "directory", item.name.lower()))
    return TreeResponse(path=str(target), children=children)
