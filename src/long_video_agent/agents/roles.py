from enum import StrEnum


class AgentRole(StrEnum):
    SHOW_RUNNER = "show_runner"
    SCREENWRITER = "screenwriter"
    SCRIPT_EDITOR = "script_editor"
    CHARACTER_DIRECTOR = "character_director"
    STORYBOARD_ARTIST = "storyboard_artist"
    ART_DIRECTOR = "art_director"
    SHOT_PRODUCER = "shot_producer"
    VOICE_DIRECTOR = "voice_director"
    EDITOR = "editor"
    QUALITY_REVIEWER = "quality_reviewer"


ROLE_ARTIFACTS = {
    AgentRole.SHOW_RUNNER: "artifacts/story/series_plan.json",
    AgentRole.SCREENWRITER: "artifacts/story/script.json",
    AgentRole.SCRIPT_EDITOR: "artifacts/story/script_review.json",
    AgentRole.CHARACTER_DIRECTOR: "artifacts/characters/registry.json",
    AgentRole.STORYBOARD_ARTIST: "artifacts/storyboard/storyboard.json",
    AgentRole.ART_DIRECTOR: "artifacts/characters/style_bible.json",
    AgentRole.SHOT_PRODUCER: "artifacts/shots/manifest.json",
    AgentRole.VOICE_DIRECTOR: "artifacts/audio/manifest.json",
    AgentRole.EDITOR: "artifacts/timeline/timeline.json",
    AgentRole.QUALITY_REVIEWER: "artifacts/qc/report.json",
}
