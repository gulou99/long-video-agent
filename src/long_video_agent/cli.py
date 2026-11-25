from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from pathlib import Path

from long_video_agent.models import ProjectBrief
from long_video_agent.storage.project_store import ProjectStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lva", description="Long-form AI video agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a resumable video project")
    init_parser.add_argument("--title", required=True)
    init_parser.add_argument("--premise", required=True)
    init_parser.add_argument("--duration", type=int, default=600)
    init_parser.add_argument("--language", default="zh-CN")
    init_parser.add_argument("--aspect-ratio", default="16:9")
    init_parser.add_argument("--root", default=os.getenv("STORAGE_ROOT", "./projects"))

    status_parser = subparsers.add_parser("status", help="Show project and pipeline state")
    status_parser.add_argument("project_path", type=Path)

    subparsers.add_parser("doctor", help="Check local runtime and provider configuration")
    return parser


def _doctor() -> dict[str, object]:
    return {
        "python": platform.python_version(),
        "python_supported": sys.version_info >= (3, 11),
        "ffmpeg": shutil.which("ffmpeg"),
        "node": shutil.which("node"),
        "providers": {
            name: bool(os.getenv(variable))
            for name, variable in {
                "llm": "LLM_API_KEY",
                "image": "IMAGE_API_KEY",
                "video": "VIDEO_API_KEY",
                "speech": "TTS_API_KEY",
            }.items()
        },
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            brief = ProjectBrief(
                title=args.title,
                premise=args.premise,
                target_duration_seconds=args.duration,
                language=args.language,
                aspect_ratio=args.aspect_ratio,
            )
            project, path = ProjectStore(args.root).create(brief)
            print(
                json.dumps(
                    {"project_id": project.id, "project_path": str(path)},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "status":
            store = ProjectStore(args.project_path.parent.parent)
            project = store.load_project(args.project_path)
            state = store.load_state(args.project_path)
            print(
                json.dumps(
                    {
                        "project": project.model_dump(mode="json"),
                        "pipeline": state.model_dump(mode="json"),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "doctor":
            print(json.dumps(_doctor(), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
