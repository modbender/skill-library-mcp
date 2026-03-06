#!/usr/bin/env python3
"""
Video Analyzer CLI Entry Point
"""
import argparse
import json
import sys
from pathlib import Path

# Add skill directory to import path for script-mode execution.
SKILL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_DIR))

try:
    from main import skill_main
    from models import SummaryStyle
except ImportError as exc:
    raise ImportError(f"Failed to import video-analyzer modules: {exc}") from exc


STYLE_MAP = {
    # Canonical CLI values.
    "concise": SummaryStyle.BRIEF_POINTS,
    "deep": SummaryStyle.DEEP_LONGFORM,
    "social": SummaryStyle.SOCIAL_MEDIA,
    "study": SummaryStyle.STUDY_NOTES,
    # Backward-compatible values used in skill.yaml/history.
    "brief_points": SummaryStyle.BRIEF_POINTS,
    "deep_longform": SummaryStyle.DEEP_LONGFORM,
    "social_media": SummaryStyle.SOCIAL_MEDIA,
    "study_notes": SummaryStyle.STUDY_NOTES,
}


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Bilibili/YouTube/local videos and generate transcript/evaluation/summary."
    )
    parser.add_argument("--url", required=True, help="Video URL or local media path.")
    parser.add_argument(
        "--whisper-model",
        default="large-v2",
        help="tiny/base/small/medium/large-v2/large-v3/turbo/distil-large-v2/distil-large-v3/distil-large-v3.5",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Whisper language code (e.g. zh/en/ja). Default: auto-detect.",
    )
    parser.add_argument(
        "--analysis-types",
        default="evaluation,summary",
        help="Comma-separated: evaluation,summary,format",
    )
    parser.add_argument("--output-dir", default="./video-analysis", help="Output directory")
    parser.add_argument(
        "--save-transcript",
        type=lambda x: str(x).lower() in ["true", "1", "yes"],
        default=True,
        help="Whether to save raw transcript.",
    )
    parser.add_argument("--config", help="Path to config.json")
    parser.add_argument(
        "--summary-style",
        help="Summary style: concise/deep/social/study (also supports brief_points/deep_longform/social_media/study_notes).",
    )
    parser.add_argument(
        "--enable-screenshots",
        action="store_true",
        default=True,
        help="Enable keyframe screenshot extraction (default enabled; use --no-screenshots to disable).",
    )
    parser.add_argument(
        "--no-screenshots",
        action="store_true",
        help="Disable keyframe screenshot extraction.",
    )
    parser.add_argument(
        "--publish-to-feishu",
        dest="publish_to_feishu",
        action="store_true",
        default=True,
        help="Publish generated content to Feishu wiki (default enabled).",
    )
    parser.add_argument(
        "--no-publish-feishu",
        dest="publish_to_feishu",
        action="store_false",
        help="Disable Feishu wiki publishing.",
    )
    parser.add_argument(
        "--feishu-space-id",
        help="Target Feishu wiki space id (required when publishing is enabled).",
    )
    parser.add_argument(
        "--feishu-parent-node-token",
        help="Target Feishu wiki parent node token (required when publishing is enabled).",
    )

    args = parser.parse_args()

    analysis_types = [t.strip() for t in args.analysis_types.split(",") if t.strip()]
    style_key = args.summary_style.strip().lower() if args.summary_style else None
    summary_style = STYLE_MAP.get(style_key) if style_key else None

    if style_key and summary_style is None:
        valid_values = ", ".join(sorted(STYLE_MAP.keys()))
        print(f"Invalid --summary-style '{args.summary_style}'. Valid values: {valid_values}")
        sys.exit(2)

    enable_screenshots = args.enable_screenshots and not args.no_screenshots

    result = skill_main(
        url=args.url,
        whisper_model=args.whisper_model,
        transcribe_language=args.language,
        analysis_types=analysis_types,
        output_dir=args.output_dir,
        save_transcript=args.save_transcript,
        config_path=args.config,
        summary_style=summary_style,
        enable_screenshots=enable_screenshots,
        publish_to_feishu=args.publish_to_feishu,
        feishu_space_id=args.feishu_space_id,
        feishu_parent_node_token=args.feishu_parent_node_token,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
