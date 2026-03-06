#!/usr/bin/env python3
"""
Islamic TikTok Stories — Pipeline Orchestrator

This is the main entry point that coordinates all agents in sequence.
Each agent is a separate module with a standard interface:
  agent.run(input_json) -> output_json

Usage:
  python orchestrator.py --story-topic "patience" --language en
  python orchestrator.py --batch --count 7 --language en
  python orchestrator.py --story-id "prophet_ayyub_001" --resume-from visual
"""

import argparse
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

# -- Agent imports (implement these as your actual agent wrappers) --
# from agents.story_agent import StoryAgent
# from agents.script_agent import ScriptAgent
# from agents.visual_agent import VisualAgent
# from agents.voice_agent import VoiceAgent
# from agents.assembly_agent import AssemblyAgent
# from agents.publishing_agent import PublishingAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log"),
    ],
)
logger = logging.getLogger("orchestrator")


class PipelineStage(Enum):
    STORY = "story"
    SCRIPT = "script"
    VISUAL = "visual"
    VOICE = "voice"
    ASSEMBLY = "assembly"
    PUBLISHING = "publishing"


@dataclass
class PipelineState:
    """Tracks the state of a single video through the pipeline."""

    story_id: str
    stage: PipelineStage = PipelineStage.STORY
    story_output: Optional[dict] = None
    script_output: Optional[dict] = None
    visual_output: Optional[dict] = None
    voice_output: Optional[dict] = None
    assembly_output: Optional[dict] = None
    publishing_output: Optional[dict] = None
    errors: list = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def save(self, output_dir: Path):
        """Persist state to disk for resume capability."""
        state_file = output_dir / f"{self.story_id}_state.json"
        with open(state_file, "w") as f:
            json.dump(self.__dict__, f, indent=2, default=str)

    @classmethod
    def load(cls, state_file: Path) -> "PipelineState":
        with open(state_file) as f:
            data = json.load(f)
        state = cls(story_id=data["story_id"])
        state.stage = PipelineStage(data["stage"])
        for key in [
            "story_output", "script_output", "visual_output",
            "voice_output", "assembly_output", "publishing_output",
            "errors", "started_at", "completed_at",
        ]:
            setattr(state, key, data.get(key))
        return state


class PipelineOrchestrator:
    """
    Coordinates the full video creation pipeline.

    Architecture decisions:
    - Sequential by default with parallel visual+voice generation
    - Each agent is stateless — all context passed via JSON
    - State persisted to disk after each stage for resume capability
    - Face detection is a hard gate — pipeline stops if faces detected
    """

    def __init__(self, config_path: str = "config/global_config.json"):
        self.config = self._load_config(config_path)
        self.output_dir = Path("output") / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize agents — replace with your actual implementations
        # self.story_agent = StoryAgent(self.config)
        # self.script_agent = ScriptAgent(self.config)
        # self.visual_agent = VisualAgent(self.config)
        # self.voice_agent = VoiceAgent(self.config)
        # self.assembly_agent = AssemblyAgent(self.config)
        # self.publishing_agent = PublishingAgent(self.config)

        logger.info(f"Pipeline initialized. Output: {self.output_dir}")

    def _load_config(self, path: str) -> dict:
        config_file = Path(path)
        if not config_file.exists():
            logger.warning(f"Config not found at {path}, using defaults")
            return self._default_config()
        with open(config_file) as f:
            return json.load(f)

    def _default_config(self) -> dict:
        return {
            "brand": {
                "channel_name": "IslamicStories",
                "character_description": (
                    "A faceless man wearing traditional white thobe and "
                    "red-checkered keffiyeh. Never show face."
                ),
                "visual_style": "Cinematic digital concept art, painterly, warm golden palette",
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
            },
            "voice": {
                "provider": "elevenlabs",
                "voice_id": "CONFIGURE_ME",
            },
            "image_gen": {
                "provider": "flux",
                "model": "flux-dev",
                "max_retries_on_face_detected": 3,
            },
            "video": {
                "fps": 30,
                "transition_duration_seconds": 0.3,
                "transition_type": "crossfade",
                "subtitle_font": "Montserrat-Bold",
                "subtitle_size": 56,
            },
            "target_languages": ["en"],
            "default_language": "en",
        }

    def run_single(
        self,
        topic: Optional[str] = None,
        story_id: Optional[str] = None,
        language: str = "en",
        resume_from: Optional[str] = None,
    ) -> PipelineState:
        """Run the full pipeline for a single video."""

        state = PipelineState(
            story_id=story_id or f"story_{int(time.time())}",
            started_at=datetime.now().isoformat(),
        )

        try:
            # ── Stage 1: Story Research ──
            if not resume_from or resume_from == "story":
                logger.info("▶ Stage 1/6: Story Research")
                state.stage = PipelineStage.STORY
                story_input = {
                    "request_type": "topic" if topic else "random",
                    "topic": topic,
                    "previously_covered": self._get_covered_stories(),
                    "target_duration_seconds": 60,
                }
                # state.story_output = self.story_agent.run(story_input)
                state.story_output = self._placeholder("story", story_input)
                state.story_id = state.story_output.get("story_id", state.story_id)
                state.save(self.output_dir)
                logger.info(f"  ✓ Story: {state.story_output.get('title', 'untitled')}")

            # ── Stage 2: Script Writing ──
            if not resume_from or resume_from in ("story", "script"):
                logger.info("▶ Stage 2/6: Script Writing")
                state.stage = PipelineStage.SCRIPT
                # state.script_output = self.script_agent.run(state.story_output)
                state.script_output = self._placeholder("script", state.story_output)
                state.save(self.output_dir)
                scene_count = len(state.script_output.get("scenes", []))
                logger.info(f"  ✓ Script: {scene_count} scenes")

            # ── Stage 3 & 4: Visual + Voice (PARALLEL) ──
            if not resume_from or resume_from in ("story", "script", "visual", "voice"):
                logger.info("▶ Stage 3+4/6: Visual Generation + Voice Narration (parallel)")

                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = {}

                    if not resume_from or resume_from != "voice":
                        state.stage = PipelineStage.VISUAL
                        futures["visual"] = executor.submit(
                            # self.visual_agent.run, state.script_output
                            self._placeholder, "visual", state.script_output
                        )

                    if not resume_from or resume_from != "visual":
                        futures["voice"] = executor.submit(
                            # self.voice_agent.run,
                            # {"script": state.script_output, "language": language}
                            self._placeholder, "voice", state.script_output
                        )

                    for name, future in futures.items():
                        try:
                            result = future.result(timeout=1800)  # 30 min timeout
                            if name == "visual":
                                state.visual_output = result
                                # Validate no faces
                                self._validate_no_faces(result)
                                logger.info("  ✓ Visual: all scenes generated")
                            elif name == "voice":
                                state.voice_output = result
                                logger.info("  ✓ Voice: narration generated")
                        except FaceDetectedError as e:
                            state.errors.append(str(e))
                            logger.error(f"  ✗ FACE DETECTED — pipeline stopped: {e}")
                            state.save(self.output_dir)
                            raise
                        except Exception as e:
                            state.errors.append(f"{name} failed: {str(e)}")
                            logger.error(f"  ✗ {name} failed: {e}")
                            raise

                state.save(self.output_dir)

            # ── Stage 5: Video Assembly ──
            if not resume_from or resume_from in (
                "story", "script", "visual", "voice", "assembly"
            ):
                logger.info("▶ Stage 5/6: Video Assembly")
                state.stage = PipelineStage.ASSEMBLY
                assembly_input = {
                    "script": state.script_output,
                    "visual": state.visual_output,
                    "voice": state.voice_output,
                    "config": self.config["video"],
                }
                # state.assembly_output = self.assembly_agent.run(assembly_input)
                state.assembly_output = self._placeholder("assembly", assembly_input)
                state.save(self.output_dir)
                logger.info(
                    f"  ✓ Video: {state.assembly_output.get('video_path', 'unknown')}"
                )

            # ── Stage 6: Publishing Metadata ──
            logger.info("▶ Stage 6/6: Publishing Metadata")
            state.stage = PipelineStage.PUBLISHING
            publish_input = {
                "video": state.assembly_output,
                "story": state.story_output,
                "language": language,
            }
            # state.publishing_output = self.publishing_agent.run(publish_input)
            state.publishing_output = self._placeholder("publishing", publish_input)

            state.completed_at = datetime.now().isoformat()
            state.save(self.output_dir)
            logger.info("═══════════════════════════════════════")
            logger.info(f"✅ Pipeline complete: {state.story_id}")
            logger.info(f"   Output: {self.output_dir}")
            logger.info("═══════════════════════════════════════")

        except Exception as e:
            state.errors.append(str(e))
            state.save(self.output_dir)
            logger.error(f"Pipeline failed at stage {state.stage.value}: {e}")
            raise

        return state

    def run_batch(self, count: int = 7, language: str = "en"):
        """Generate a batch of videos (e.g., a week's worth)."""
        logger.info(f"Starting batch run: {count} videos")
        results = []

        for i in range(count):
            logger.info(f"\n{'='*50}")
            logger.info(f"Video {i+1}/{count}")
            logger.info(f"{'='*50}")
            try:
                state = self.run_single(language=language)
                results.append({"story_id": state.story_id, "status": "success"})
            except Exception as e:
                results.append({"story_id": f"failed_{i}", "status": "error", "error": str(e)})
                logger.error(f"Video {i+1} failed, continuing batch...")

        # Summary
        success = sum(1 for r in results if r["status"] == "success")
        logger.info(f"\nBatch complete: {success}/{count} succeeded")

        summary_path = self.output_dir / "batch_summary.json"
        with open(summary_path, "w") as f:
            json.dump(results, f, indent=2)

        return results

    def _validate_no_faces(self, visual_output: dict):
        """
        Post-generation face detection check.
        Uses a face detection model to verify no faces are visible.
        This is a HARD GATE — if faces detected, the pipeline stops.
        """
        # TODO: Implement with your face detection tool
        # Options:
        #   - OpenCV Haar cascades (fast, less accurate)
        #   - MTCNN or RetinaFace (more accurate)
        #   - Cloud API (Google Vision, AWS Rekognition)
        #
        # for scene in visual_output.get("scenes", []):
        #     image_path = scene["image_path"]
        #     if detect_face(image_path):
        #         raise FaceDetectedError(f"Face detected in {image_path}")
        pass

    def _get_covered_stories(self) -> list:
        """Load list of previously published story IDs to avoid repeats."""
        history_file = Path("data/published_stories.json")
        if history_file.exists():
            with open(history_file) as f:
                return json.load(f)
        return []

    def _placeholder(self, agent_name: str, input_data: dict) -> dict:
        """
        Placeholder for actual agent calls during development.
        Replace each with your real agent implementation.
        """
        logger.info(f"  [PLACEHOLDER] {agent_name} agent called")
        return {
            "agent": agent_name,
            "status": "placeholder",
            "message": f"Replace with actual {agent_name} agent implementation",
            "input_keys": list(input_data.keys()) if isinstance(input_data, dict) else [],
        }


class FaceDetectedError(Exception):
    """Raised when a face is detected in a generated image."""
    pass


def main():
    parser = argparse.ArgumentParser(description="Islamic TikTok Stories Pipeline")
    parser.add_argument("--story-topic", type=str, help="Topic for the story")
    parser.add_argument("--story-id", type=str, help="Specific story ID to produce")
    parser.add_argument("--language", type=str, default="en", help="Target language")
    parser.add_argument("--batch", action="store_true", help="Run in batch mode")
    parser.add_argument("--count", type=int, default=7, help="Number of videos in batch")
    parser.add_argument(
        "--resume-from",
        type=str,
        choices=["story", "script", "visual", "voice", "assembly"],
        help="Resume pipeline from a specific stage",
    )
    parser.add_argument("--config", type=str, default="config/global_config.json")

    args = parser.parse_args()
    pipeline = PipelineOrchestrator(config_path=args.config)

    if args.batch:
        pipeline.run_batch(count=args.count, language=args.language)
    else:
        pipeline.run_single(
            topic=args.story_topic,
            story_id=args.story_id,
            language=args.language,
            resume_from=args.resume_from,
        )


if __name__ == "__main__":
    main()
