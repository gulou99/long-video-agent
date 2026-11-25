from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from long_video_agent.models import PipelineState, ProductionProject, ProjectBrief, ProjectStatus


def _write_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", value, flags=re.UNICODE).strip("-_")
    return (slug[:48] or "video").lower()


class ProjectStore:
    """Portable file-based project storage with atomic JSON checkpoints."""

    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def create(self, brief: ProjectBrief) -> tuple[ProductionProject, Path]:
        project_id = f"{_slugify(brief.title)}-{uuid4().hex[:8]}"
        project_path = self.root / project_id
        project_path.mkdir(parents=False, exist_ok=False)
        for directory in (
            "artifacts/story",
            "artifacts/characters",
            "artifacts/storyboard",
            "artifacts/shots",
            "artifacts/audio",
            "artifacts/timeline",
            "artifacts/qc",
            "renders",
            "logs",
        ):
            (project_path / directory).mkdir(parents=True, exist_ok=True)

        project = ProductionProject(id=project_id, brief=brief)
        self.save_project(project_path, project)
        self.save_state(project_path, PipelineState())
        return project, project_path

    def load_project(self, project_path: str | Path) -> ProductionProject:
        path = self._project_file(project_path)
        return ProductionProject.model_validate_json(path.read_text(encoding="utf-8"))

    def save_project(self, project_path: str | Path, project: ProductionProject) -> None:
        project.updated_at = datetime.now(UTC)
        _write_json(self._project_file(project_path), project.model_dump(mode="json"))

    def load_state(self, project_path: str | Path) -> PipelineState:
        path = Path(project_path) / "state.json"
        return PipelineState.model_validate_json(path.read_text(encoding="utf-8"))

    def save_state(self, project_path: str | Path, state: PipelineState) -> None:
        state.updated_at = datetime.now(UTC)
        _write_json(Path(project_path) / "state.json", state.model_dump(mode="json"))

    def set_status(self, project_path: str | Path, status: ProjectStatus) -> ProductionProject:
        project = self.load_project(project_path)
        project.status = status
        self.save_project(project_path, project)
        return project

    @staticmethod
    def _project_file(project_path: str | Path) -> Path:
        return Path(project_path) / "project.json"
