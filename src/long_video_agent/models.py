from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    PLANNING = "planning"
    PRODUCTION = "production"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineStage(StrEnum):
    INGEST = "ingest"
    STORY = "story"
    CHARACTER_BIBLE = "character_bible"
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    VISUAL_ASSETS = "visual_assets"
    SHOT_GENERATION = "shot_generation"
    AUDIO = "audio"
    TIMELINE = "timeline"
    QUALITY_CONTROL = "quality_control"
    RENDER = "render"
    DELIVERY = "delivery"


class ShotStatus(StrEnum):
    PENDING = "pending"
    GENERATING = "generating"
    REVIEW = "review"
    APPROVED = "approved"
    FAILED = "failed"


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProjectBrief(ContractModel):
    title: str = Field(min_length=1, max_length=200)
    premise: str = Field(min_length=1)
    target_duration_seconds: int = Field(default=600, ge=30, le=7200)
    language: str = "zh-CN"
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:3"] = "16:9"
    genre: str = "剧情"
    visual_style: str = "电影感、统一色彩、角色外观一致"
    audience: str = "大众"
    source_text: str | None = None


class Character(ContractModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    biography: str = ""
    visual_identity: str = Field(min_length=1)
    voice_profile: str = ""
    reference_assets: list[str] = Field(default_factory=list)


class DialogueLine(ContractModel):
    character_id: str
    text: str = Field(min_length=1)
    emotion: str = "neutral"


class Shot(ContractModel):
    id: str = Field(min_length=1)
    index: int = Field(ge=1)
    duration_seconds: float = Field(default=8.0, gt=0, le=30)
    purpose: str = ""
    visual_prompt: str = Field(min_length=1)
    negative_prompt: str = ""
    camera: str = "中景，固定机位"
    action: str = ""
    narration: str = ""
    dialogue: list[DialogueLine] = Field(default_factory=list)
    character_ids: list[str] = Field(default_factory=list)
    reference_assets: list[str] = Field(default_factory=list)
    status: ShotStatus = ShotStatus.PENDING
    generation_attempts: int = Field(default=0, ge=0)


class Scene(ContractModel):
    id: str = Field(min_length=1)
    index: int = Field(ge=1)
    title: str = Field(min_length=1)
    summary: str = ""
    location: str = ""
    story_goal: str = ""
    shots: list[Shot] = Field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        return sum(shot.duration_seconds for shot in self.shots)


class Storyboard(ContractModel):
    logline: str = ""
    characters: list[Character] = Field(default_factory=list)
    scenes: list[Scene] = Field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        return sum(scene.duration_seconds for scene in self.scenes)


class ProductionProject(ContractModel):
    id: str = Field(min_length=1)
    brief: ProjectBrief
    status: ProjectStatus = ProjectStatus.DRAFT
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    storyboard: Storyboard | None = None


class PipelineState(ContractModel):
    completed_stages: list[PipelineStage] = Field(default_factory=list)
    artifacts: dict[str, str] = Field(default_factory=dict)
    attempts: dict[str, int] = Field(default_factory=dict)
    last_error: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
