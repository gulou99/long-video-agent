from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from long_video_agent.models import PipelineStage, PipelineState, ProductionProject, ProjectStatus
from long_video_agent.storage.project_store import ProjectStore

PIPELINE_ORDER = tuple(PipelineStage)
StageHandler = Callable[["PipelineContext"], Awaitable[Mapping[str, str]]]


@dataclass(slots=True)
class PipelineContext:
    project_path: Path
    project: ProductionProject
    state: PipelineState
    store: ProjectStore


class PipelineRunner:
    """Runs registered stages, persists after each stage, and resumes completed work."""

    def __init__(self, store: ProjectStore, handlers: Mapping[PipelineStage, StageHandler]):
        self.store = store
        self.handlers = dict(handlers)

    async def run(self, project_path: str | Path) -> PipelineState:
        path = Path(project_path)
        project = self.store.load_project(path)
        state = self.store.load_state(path)
        context = PipelineContext(path, project, state, self.store)
        self.store.set_status(path, ProjectStatus.PRODUCTION)

        for stage in PIPELINE_ORDER:
            if stage in state.completed_stages:
                continue
            handler = self.handlers.get(stage)
            if handler is None:
                break

            state.attempts[stage.value] = state.attempts.get(stage.value, 0) + 1
            state.last_error = None
            self.store.save_state(path, state)
            try:
                artifacts = await handler(context)
            except Exception as error:
                state.last_error = f"{stage.value}: {error}"
                self.store.save_state(path, state)
                self.store.set_status(path, ProjectStatus.FAILED)
                raise

            state.artifacts.update(
                {f"{stage.value}:{name}": str(uri) for name, uri in artifacts.items()}
            )
            state.completed_stages.append(stage)
            self.store.save_state(path, state)

        return state
