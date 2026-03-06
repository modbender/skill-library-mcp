"""
Video Analyzer Skill - Main Entry Point

智能分析 Bilibili/YouTube/本地视频，生成转写、评估和总结。
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import shutil

from core import VideoAnalyzer
from dependency_manager import check_and_install_dependencies
from models import SummaryStyle

SKILL_DIR = Path(__file__).resolve().parent


def _resolve_from_skill_dir(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (SKILL_DIR / path).resolve()


def skill_main(
    url: str,
    whisper_model: str = "large-v2",
    transcribe_language: Optional[str] = None,
    analysis_types: Optional[List[str]] = None,
    output_dir: str = "./video-analysis",
    save_transcript: bool = True,
    config_path: Optional[str] = None,
    summary_style: Optional[SummaryStyle] = None,
    enable_screenshots: bool = True,
    publish_to_feishu: bool = True,
    feishu_space_id: Optional[str] = None,
    feishu_parent_node_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze video and generate transcript/evaluation/summary.

    Args:
        url: Video URL or local file path
        whisper_model: tiny/base/small/medium/large-v2/large-v3/turbo/distil-large-v2/distil-large-v3/distil-large-v3.5 (default: large-v2)
        transcribe_language: Whisper language code (e.g. zh/en/ja). None means auto-detect (default).
        analysis_types: List of analysis types [evaluation, summary, format] (default: [evaluation, summary])
        output_dir: Output directory for results (default: ./video-analysis)
        save_transcript: Whether to save raw transcript (default: True)
        config_path: Path to config.json (default: None)
        summary_style: Summary style (brief_points, deep_longform, social_media, study_notes) (default: None -> deep_longform)
        enable_screenshots: Enable screenshot extraction from video key moments (default: True)
        publish_to_feishu: Publish final content to Feishu wiki doc (default: True)
        feishu_space_id: Feishu wiki space id (required when publish_to_feishu=True)
        feishu_parent_node_token: Feishu parent node token (required when publish_to_feishu=True)

    Returns:
        dict with success status, video info, and output files:
        {
            "success": True/False,
            "video_title": str,
            "duration_seconds": float,  # original video duration
            "processing_seconds": float,  # pipeline elapsed time
            "transcript_length": int,
            "output_files": {
                "transcript": str,
                "evaluation": str,
                "summary": str
            },
            "feishu_publish": dict,
            "summary": str,
            "error": str (if failed)
        }
    """
    # Keep runtime paths stable regardless of current working directory.
    (SKILL_DIR / "models" / "whisper").mkdir(parents=True, exist_ok=True)
    (SKILL_DIR / "output").mkdir(parents=True, exist_ok=True)
    (SKILL_DIR / "data").mkdir(parents=True, exist_ok=True)
    (SKILL_DIR / "logs").mkdir(parents=True, exist_ok=True)

    # Ensure config exists (best effort)
    resolved_config_path = _resolve_from_skill_dir(config_path) if config_path else None
    if resolved_config_path is None:
        default_cfg = SKILL_DIR / "config.json"
        example_cfg = SKILL_DIR / "config.example.json"
        if not default_cfg.exists():
            if example_cfg.exists():
                shutil.copy(example_cfg, default_cfg)
                print(
                    "[INFO] config.json not found. Copied from skill config.example.json"
                )
            else:
                print(
                    "[WARN] config.json not found and no config.example.json available"
                )
        resolved_config_path = default_cfg

    resolved_output_dir = _resolve_from_skill_dir(output_dir)

    # Check dependencies
    if not check_and_install_dependencies():
        return {
            "success": False,
            "error": "Dependency installation failed. Please install manually.",
            "hint": "pip install -r requirements.txt && install ffmpeg",
        }

    # Initialize analyzer
    effective_analysis_types = (
        ["evaluation", "summary"] if analysis_types is None else analysis_types
    )

    analyzer = VideoAnalyzer(
        whisper_model=whisper_model,
        transcribe_language=transcribe_language,
        analysis_types=effective_analysis_types,
        output_dir=str(resolved_output_dir),
        save_transcript=save_transcript,
        config_path=str(resolved_config_path) if resolved_config_path else None,
        summary_style=summary_style,
        enable_screenshots=enable_screenshots,
        publish_to_feishu=publish_to_feishu,
        feishu_space_id=feishu_space_id,
        feishu_parent_node_token=feishu_parent_node_token,
    )

    # Run analysis
    return analyzer.analyze(url)
