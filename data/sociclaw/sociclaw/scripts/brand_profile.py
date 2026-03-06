"""
Brand profile utilities for SociClaw ("Brand Brain").

Stores brand context in a local markdown file so generated content can keep
consistent tone, audience and vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import re


@dataclass
class BrandProfile:
    name: str = ""
    slogan: str = ""
    voice_tone: str = "Professional"
    content_language: str = "en"
    target_audience: str = ""
    value_proposition: str = ""
    key_themes: List[str] = field(default_factory=list)
    do_not_say: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    personality_traits: List[str] = field(default_factory=list)
    visual_style: str = ""
    signature_openers: List[str] = field(default_factory=list)
    content_goals: List[str] = field(default_factory=list)
    cta_style: str = "question"
    has_brand_document: bool = False
    brand_document_path: str = ""


def default_brand_profile_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / ".sociclaw" / "company_profile.md"


def load_brand_profile(path: Optional[Path] = None) -> BrandProfile:
    file_path = path or default_brand_profile_path()
    if not file_path.exists():
        return BrandProfile()

    text = file_path.read_text(encoding="utf-8")
    profile = BrandProfile()
    current_list_key: Optional[str] = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        structured = (
            re.match(r"^- \*\*([^*]+):\*\*\s*(.*)$", line)
            or re.match(r"^- \*\*([^*]+)\*\*:\s*(.*)$", line)
        )
        if structured:
            label = structured.group(1).strip().lower()
            value = structured.group(2).strip()
            current_list_key = None

            if label == "name":
                profile.name = value
            elif label == "slogan":
                profile.slogan = value
            elif label in {"voice/tone", "voice"}:
                profile.voice_tone = value or profile.voice_tone
            elif label == "content language":
                profile.content_language = value or profile.content_language
            elif label == "target audience":
                profile.target_audience = value
            elif label == "value proposition":
                profile.value_proposition = value
            elif label == "key themes":
                profile.key_themes = _parse_inline_list(value)
                current_list_key = "key_themes"
            elif label == "do not say":
                profile.do_not_say = _parse_inline_list(value)
                current_list_key = "do_not_say"
            elif label == "keywords":
                profile.keywords = _parse_inline_list(value)
                current_list_key = "keywords"
            elif label == "personality traits":
                profile.personality_traits = _parse_inline_list(value)
                current_list_key = "personality_traits"
            elif label == "visual style":
                profile.visual_style = value
            elif label == "signature openers":
                profile.signature_openers = _parse_inline_list(value)
                current_list_key = "signature_openers"
            elif label == "content goals":
                profile.content_goals = _parse_inline_list(value)
                current_list_key = "content_goals"
            elif label == "cta style":
                profile.cta_style = value or profile.cta_style
            elif label == "has brand document":
                profile.has_brand_document = value.lower() in {"yes", "true", "1", "y"}
            elif label == "brand document path":
                profile.brand_document_path = value
            continue

        item = re.match(r"^- (.+)$", line)
        if item and current_list_key:
            getattr(profile, current_list_key).append(item.group(1).strip())

    profile.key_themes = _dedupe(profile.key_themes)
    profile.do_not_say = _dedupe(profile.do_not_say)
    profile.keywords = _dedupe(profile.keywords)
    profile.personality_traits = _dedupe(profile.personality_traits)
    profile.signature_openers = _dedupe(profile.signature_openers)
    profile.content_goals = _dedupe(profile.content_goals)
    return profile


def save_brand_profile(profile: BrandProfile, path: Optional[Path] = None) -> Path:
    file_path = path or default_brand_profile_path()
    file_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Brand Profile",
        "",
        "## Identity",
        f"- **Name:** {profile.name}",
        f"- **Slogan:** {profile.slogan}",
        f"- **Voice/Tone:** {profile.voice_tone}",
        f"- **Content Language:** {profile.content_language}",
        "",
        "## Strategic Context",
        f"- **Target Audience:** {profile.target_audience}",
        f"- **Value Proposition:** {profile.value_proposition}",
        f"- **Key Themes:** {', '.join(profile.key_themes)}",
        "",
        "## Constraints",
        f"- **Do Not Say:** {', '.join(profile.do_not_say)}",
        f"- **Keywords:** {', '.join(profile.keywords)}",
        f"- **Personality Traits:** {', '.join(profile.personality_traits)}",
        f"- **Visual Style:** {profile.visual_style}",
        f"- **Signature Openers:** {', '.join(profile.signature_openers)}",
        f"- **Content Goals:** {', '.join(profile.content_goals)}",
        f"- **CTA Style:** {profile.cta_style}",
        f"- **Has Brand Document:** {'yes' if profile.has_brand_document else 'no'}",
        f"- **Brand Document Path:** {profile.brand_document_path}",
        "",
    ]

    file_path.write_text("\n".join(lines), encoding="utf-8")
    return file_path


def _parse_inline_list(value: str) -> List[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


def _dedupe(values: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for value in values:
        key = value.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(value.strip())
    return out
