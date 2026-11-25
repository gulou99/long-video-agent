from __future__ import annotations

from typing import Literal, Protocol, TypeVar

from pydantic import BaseModel, Field

from long_video_agent.models import ContractModel

ModelT = TypeVar("ModelT", bound=BaseModel)
ProviderT = TypeVar("ProviderT")


class GenerationRequest(ContractModel):
    prompt: str = Field(min_length=1)
    negative_prompt: str = ""
    width: int = Field(default=1920, gt=0)
    height: int = Field(default=1080, gt=0)
    duration_seconds: float | None = Field(default=None, gt=0, le=30)
    seed: int | None = None
    reference_assets: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class GeneratedAsset(ContractModel):
    kind: Literal["image", "video", "audio", "subtitle"]
    uri: str
    provider: str
    provider_job_id: str | None = None
    cost_usd: float | None = Field(default=None, ge=0)
    metadata: dict[str, str] = Field(default_factory=dict)


class TextProvider(Protocol):
    async def generate_structured(
        self, instructions: str, schema: type[ModelT]
    ) -> ModelT: ...


class MediaProvider(Protocol):
    async def generate(self, request: GenerationRequest) -> GeneratedAsset: ...


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, object] = {}

    def register(self, capability: str, provider: object) -> None:
        if capability in self._providers:
            raise ValueError(f"Provider already registered: {capability}")
        self._providers[capability] = provider

    def get(self, capability: str) -> ProviderT:
        try:
            return self._providers[capability]  # type: ignore[return-value]
        except KeyError as error:
            raise KeyError(f"No provider registered for: {capability}") from error

    @property
    def capabilities(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))
