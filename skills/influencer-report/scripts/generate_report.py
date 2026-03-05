#!/usr/bin/env python3
"""
Generate a formatted markdown influencer vetting report from analysis data.
"""

from datetime import datetime, timezone


def _fmt_number(n) -> str:
    if not n or not isinstance(n, (int, float)):
        return "N/A"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(int(n))


def generate_report(handle: str, platform: str, analyses: list[dict]) -> str:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    num_videos = len(analyses)
    avg_score = sum(a["score"]["total"] for a in analyses) / len(analyses) if analyses else 0

    if avg_score >= 80:
        recommendation = "✅ APPROVED"
    elif avg_score >= 60:
        recommendation = "⚠️ CONDITIONAL — Review concerns below"
    else:
        recommendation = "❌ REJECTED"

    lines = [
        f"# Influencer Vetting Report\n",
        f"**Influencer**: @{handle.lstrip('@')}",
        f"**Platform**: {platform.title()}",
        f"**Date**: {date_str}",
        f"**Videos Analyzed**: {num_videos}\n",
    ]

    # Aggregate engagement stats from metadata
    total_likes = 0
    total_comments = 0
    total_views = 0
    has_stats = False
    for a in analyses:
        md = a.get("metadata") or a["score"].get("metadata") or {}
        if md:
            has_stats = True
            total_likes += md.get("likes", 0) or md.get("likeCount", 0) or 0
            total_comments += md.get("comments", 0) or md.get("commentCount", 0) or 0
            total_views += md.get("views", 0) or md.get("viewCount", 0) or md.get("playCount", 0) or 0

    if has_stats:
        lines.append("## Engagement Overview\n")
        lines.append(f"- **Total Views** (across {num_videos} videos): {_fmt_number(total_views)}")
        lines.append(f"- **Total Likes**: {_fmt_number(total_likes)}")
        lines.append(f"- **Total Comments**: {_fmt_number(total_comments)}")
        if total_views > 0:
            eng_rate = (total_likes + total_comments) / total_views * 100
            lines.append(f"- **Engagement Rate**: {eng_rate:.2f}%")
        lines.append("")

    lines.append("## Video Analysis\n")

    strengths = []
    concerns = []

    for i, a in enumerate(analyses, 1):
        v = a["video"]
        sc = a["score"]
        title = v.get("title", "Untitled") or "Untitled"
        url = v.get("url", "")

        lines.append(f"### Video {i}: [{title}]({url})\n")

        # Metadata line
        md = a.get("metadata") or {}
        if md:
            stats = []
            for key, label in [("views", "Views"), ("viewCount", "Views"), ("playCount", "Views"),
                                ("likes", "Likes"), ("likeCount", "Likes"),
                                ("comments", "Comments"), ("commentCount", "Comments")]:
                val = md.get(key)
                if val and label not in [s.split(":")[0] for s in stats]:
                    stats.append(f"{label}: {_fmt_number(val)}")
            if stats:
                lines.append(f"**Stats**: {' | '.join(stats)}\n")

        lines.append("| Criteria | Score | Notes |")
        lines.append("|----------|-------|-------|")

        label_map = {
            "camera_facing": "Camera-facing",
            "audio_quality": "Audio quality",
            "lighting": "Lighting",
            "content_relevance": "Content relevance",
            "brand_safety": "Brand safety",
        }

        for key, label in label_map.items():
            passed = sc["scores"][key]
            icon = "✅" if passed else "❌"
            note = sc["notes"][key]
            lines.append(f"| {label} | {icon} | {note} |")
            if passed and key in ("camera_facing", "brand_safety"):
                strengths.append(f"{label} in Video {i}")
            if not passed:
                concerns.append(f"{label} issue in Video {i}: {note}")

        analysis = a.get("analysis", {})
        audio = analysis.get("audio_transcript", "")
        visual = analysis.get("video_transcript", "")

        if audio:
            lines.append(f"\n**AI Transcript Summary**: {audio[:300]}{'...' if len(audio) > 300 else ''}")
        if visual:
            lines.append(f"\n**Visual Analysis**: {visual[:300]}{'...' if len(visual) > 300 else ''}")

        lines.append(f"\n**Video Score**: {sc['total']}/100\n")

    lines.append("## Overall Assessment\n")
    lines.append(f"- **Score**: {avg_score:.0f}/100")
    lines.append(f"- **Recommendation**: {recommendation}")
    lines.append(f"- **Key Strengths**: {'; '.join(strengths[:5]) if strengths else 'N/A (insufficient data)'}")
    lines.append(f"- **Concerns**: {'; '.join(concerns[:5]) if concerns else 'None detected'}")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_report("demo_user", "instagram", []))
