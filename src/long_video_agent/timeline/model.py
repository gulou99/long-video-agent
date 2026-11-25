from __future__ import annotations
from typing import Literal

from pydantic import Field, model_validator

from long_video_agent.models import ContractModel


class TimelineClip(ContractModel):
    id: str
    asset_uri: str
    start_seconds: float = Field(ge=0)
    duration_seconds: float = Field(gt=0)
    source_offset_seconds: float = Field(default=0, ge=0)
    volume: float = Field(default=1.0, ge=0, le=2)

    @property
    def end_seconds(self) -> float:
        return self.start_seconds + self.duration_seconds


class TimelineTrack(ContractModel):
    id: str
    kind: Literal["video", "voice", "music", "sound_effect", "subtitle"]
    clips: list[TimelineClip] = Field(default_factory=list)
    muted: bool = False


class Timeline(ContractModel):
    fps: int = Field(default=30, ge=1, le=120)
    width: int = Field(default=1920, gt=0)
    height: int = Field(default=1080, gt=0)
    tracks: list[TimelineTrack] = Field(default_factory=list)

    @model_validator(mode="after")
    def reject_track_overlaps(self) -> "Timeline":
        for track in self.tracks:
            clips = sorted(track.clips, key=lambda clip: clip.start_seconds)
            for previous, current in zip(clips, clips[1:], strict=False):
                if current.start_seconds < previous.end_seconds:
                    raise ValueError(
                        f"Clips overlap on track {track.id}: {previous.id} and {current.id}"
                    )
        return self

    @property
    def duration_seconds(self) -> float:
        return max(
            (clip.end_seconds for track in self.tracks for clip in track.clips),
            default=0.0,
        )
