import unittest

from pydantic import ValidationError

from long_video_agent.models import Character, ProjectBrief, Scene, Shot, Storyboard
from long_video_agent.quality.checks import inspect_storyboard
from long_video_agent.timeline.model import Timeline, TimelineClip, TimelineTrack


class TimelineTests(unittest.TestCase):
    def test_timeline_duration(self) -> None:
        timeline = Timeline(
            tracks=[
                TimelineTrack(
                    id="v1",
                    kind="video",
                    clips=[
                        TimelineClip(id="a", asset_uri="a.mp4", start_seconds=0, duration_seconds=5),
                        TimelineClip(id="b", asset_uri="b.mp4", start_seconds=5, duration_seconds=5),
                    ],
                )
            ]
        )
        self.assertEqual(timeline.duration_seconds, 10)

    def test_overlap_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Timeline(
                tracks=[
                    TimelineTrack(
                        id="v1",
                        kind="video",
                        clips=[
                            TimelineClip(id="a", asset_uri="a.mp4", start_seconds=0, duration_seconds=6),
                            TimelineClip(id="b", asset_uri="b.mp4", start_seconds=5, duration_seconds=5),
                        ],
                    )
                ]
            )


class QualityTests(unittest.TestCase):
    def test_storyboard_quality_reports_repairable_issues(self) -> None:
        brief = ProjectBrief(title="质检", premise="验证时长与角色引用。", target_duration_seconds=30)
        storyboard = Storyboard(
            characters=[Character(id="hero", name="主角", visual_identity="短黑发，蓝色夹克")],
            scenes=[
                Scene(
                    id="s1",
                    index=1,
                    title="开场",
                    shots=[
                        Shot(
                            id="shot-1",
                            index=1,
                            duration_seconds=8,
                            visual_prompt="主角走进房间",
                            character_ids=["hero", "unknown"],
                        )
                    ],
                )
            ],
        )

        report = inspect_storyboard(storyboard, brief)

        self.assertFalse(report.passed)
        self.assertEqual(
            {issue.code for issue in report.issues},
            {"duration_mismatch", "unknown_character", "missing_shot_references"},
        )


if __name__ == "__main__":
    unittest.main()
