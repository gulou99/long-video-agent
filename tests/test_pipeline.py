import tempfile
import unittest
from pathlib import Path

from long_video_agent.models import PipelineStage, ProjectBrief
from long_video_agent.pipeline import PipelineRunner
from long_video_agent.storage.project_store import ProjectStore


class ProjectStoreTests(unittest.TestCase):
    def test_create_and_reload_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = ProjectStore(temporary)
            brief = ProjectBrief(title="测试长片", premise="一名工程师修复城市记忆。")
            created, path = store.create(brief)

            loaded = store.load_project(path)
            state = store.load_state(path)

            self.assertEqual(loaded.id, created.id)
            self.assertEqual(loaded.brief.target_duration_seconds, 600)
            self.assertEqual(state.completed_stages, [])
            self.assertTrue((path / "artifacts/shots").is_dir())
            self.assertTrue((path / "project.json").is_file())


class PipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_pipeline_persists_and_skips_completed_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = ProjectStore(temporary)
            _, path = store.create(ProjectBrief(title="断点续跑", premise="验证阶段缓存。"))
            calls: list[str] = []

            async def ingest(context) -> dict[str, str]:
                calls.append(context.project.id)
                source = Path(context.project_path) / "artifacts/story/source.txt"
                source.write_text("source", encoding="utf-8")
                return {"source": str(source)}

            runner = PipelineRunner(store, {PipelineStage.INGEST: ingest})
            first = await runner.run(path)
            second = await runner.run(path)

            self.assertEqual(first.completed_stages, [PipelineStage.INGEST])
            self.assertEqual(second.completed_stages, [PipelineStage.INGEST])
            self.assertEqual(len(calls), 1)
            self.assertIn("ingest:source", second.artifacts)


if __name__ == "__main__":
    unittest.main()
