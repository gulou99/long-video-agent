from typing import Literal

from pydantic import Field

from long_video_agent.models import ContractModel, ProjectBrief, Storyboard


class QualityIssue(ContractModel):
    severity: Literal["info", "warning", "error"]
    code: str
    message: str
    shot_id: str | None = None
    repair_stage: str | None = None


class QualityReport(ContractModel):
    issues: list[QualityIssue] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def inspect_storyboard(
    storyboard: Storyboard,
    brief: ProjectBrief,
    duration_tolerance_seconds: float = 1.0,
) -> QualityReport:
    issues: list[QualityIssue] = []
    duration_delta = abs(storyboard.duration_seconds - brief.target_duration_seconds)
    if duration_delta > duration_tolerance_seconds:
        issues.append(
            QualityIssue(
                severity="error",
                code="duration_mismatch",
                message=(
                    f"Storyboard duration {storyboard.duration_seconds:.2f}s differs from "
                    f"target {brief.target_duration_seconds}s"
                ),
                repair_stage="storyboard",
            )
        )

    character_ids = {character.id for character in storyboard.characters}
    for scene in storyboard.scenes:
        for shot in scene.shots:
            unknown = set(shot.character_ids) - character_ids
            if unknown:
                issues.append(
                    QualityIssue(
                        severity="error",
                        code="unknown_character",
                        message=f"Unknown characters: {', '.join(sorted(unknown))}",
                        shot_id=shot.id,
                        repair_stage="character_bible",
                    )
                )
            if shot.character_ids and not shot.reference_assets:
                issues.append(
                    QualityIssue(
                        severity="warning",
                        code="missing_shot_references",
                        message="Shot has characters but no visual reference assets",
                        shot_id=shot.id,
                        repair_stage="visual_assets",
                    )
                )
    return QualityReport(issues=issues)
