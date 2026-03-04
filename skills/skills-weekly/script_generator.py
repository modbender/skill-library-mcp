"""
script_generator.py — LLM Script Generator (v7 — GitHubAwesome Format)

Generates YouTube segments for top ClawHub skills.
Format cloned from GitHubAwesome's GitHub Trending Weekly (episodes 24-25):
  - ONE hook sentence (problem-first / absurdist / provocateur / punchy)
  - ONE-TWO sentences of what it does with exact technical details
  - 30-50 words per segment, no transitions, no filler
  - Dry, slightly sardonic — a knowledgeable friend reporting back

Supports two tracks: MOVERS (established) and ROCKETS (new <30 days).
Uses Anthropic SDK (claude-haiku-4-5 by default).
"""

import re

import anthropic
import community_signals
from datetime import datetime, timezone


# --- GitHubAwesome-style system prompt ---
# Calibrated from verbatim analysis of GitHubAwesome episodes 24 and 25
SYSTEM_PROMPT = (
    "You write YouTube video segments about AI agent skills. "
    "Your tone is dry, precise, and slightly sardonic — a knowledgeable friend "
    "who has already seen everything, reporting back with deadpan efficiency. "
    "The wit is in the framing, not in adjectives."
    "\n\n"
    "FORMAT — exactly this structure, nothing else:\n"
    "1. ONE hook sentence. Use one of these patterns:\n"
    "   - Problem-first: a specific scenario the listener recognises\n"
    "   - Absurdist-specific: a weird real detail that grabs attention\n"
    "   - Provocateur: a statement that makes the listener lean in\n"
    "   - Punchy tagline: a short declarative that frames the whole project\n"
    "2. ONE to TWO sentences of what it does. Name exact technologies, "
    "CLI commands, file formats, languages, or integrations. "
    "Describe active behaviour, not capability.\n"
    "3. STOP. No closer, no call to action, no summary sentence.\n"
    "\n"
    "BANNED:\n"
    "- Markdown, headers, bold, bullets, formatting of any kind\n"
    "- Download counts, install counts, star counts, popularity metrics\n"
    "- 'allows you to', 'enables you to', 'lets you' — use active voice instead\n"
    "- 'check it out', 'game changer', 'Welcome back', 'worth noting'\n"
    "- Superlatives: 'incredible', 'amazing', 'revolutionary', 'powerful', 'robust'\n"
    "- Generic problem framing like 'managing X is hard' — be specific\n"
    "- Transitional phrases, enthusiasm injection, filler of any kind\n"
    "\n"
    "HARD LIMIT: 30-50 words. Count them. Single paragraph. No line breaks.\n"
    "\n"
    "EXAMPLES of the exact style (from GitHub Trending Weekly):\n"
    "\n"
    "\"One thousand job applications in two days. Fully autonomous. "
    "JobBot fills forms, uploads resumes, and tracks responses across "
    "LinkedIn, Indeed, and Glassdoor via headless Chromium.\"\n"
    "\n"
    "\"A dad got tired of walking past his kid's tablet hearing gaming YouTubers. "
    "BrainRotGuard is a self-hosted YouTube approval system — sends Telegram "
    "notifications with Approve and Deny buttons. No YouTube account needed.\"\n"
    "\n"
    "\"Surge is a download manager built in Go for the terminal. "
    "Simultaneous connections, intelligent worker optimisation, three modes: "
    "interactive TUI, headless server, and CLI client.\""
)

USER_TEMPLATE_VELOCITY = """Skill: {display_name}
Author: {author}
Track: {track}

Summary: {summary}

Documentation:
{content}

Write one segment in the exact style shown. Hook sentence, then what it does. 30-50 words. Stop after that."""

USER_TEMPLATE_COLD = """Skill: {display_name} (brand new)
Author: {author}
Track: {track}

Summary: {summary}

Documentation:
{content}

Write one segment in the exact style shown. Hook sentence, then what it does — emphasise what's novel. 30-50 words. Stop after that."""


def _strip_markdown(text: str) -> str:
    """Remove any markdown formatting from LLM output for voice-ready text."""
    text = re.sub(r"^#+\s+.*\n?", "", text, flags=re.MULTILINE)  # headers
    text = re.sub(r"\*\*\[?[A-Z ]+\]?\*\*\n?", "", text)  # **[HOOK]** style labels
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # **bold**
    text = re.sub(r"\*(.+?)\*", r"\1", text)  # *italic*
    text = re.sub(r"^[-*]\s+", "", text, flags=re.MULTILINE)  # bullet points
    text = re.sub(r"\n{2,}", " ", text)  # collapse multiple newlines
    return text.strip()


def _build_prompt(skill: dict) -> str:
    track = skill.get("_track", "mover")
    track_label = "NEW THIS WEEK" if track == "rocket" else "TOP MOVER"
    cold = skill.get("_cold_start", False)
    template = USER_TEMPLATE_COLD if cold else USER_TEMPLATE_VELOCITY

    return template.format(
        display_name=skill.get("display_name", "Unknown"),
        author=skill.get("author", "Unknown"),
        summary=skill.get("summary") or "No description.",
        content=(skill.get("content") or "No documentation available.")[:3000],
        track=track_label,
    )


def generate_scripts(
    harvested: list[dict],
    api_key: str,
    model: str = "claude-haiku-4-5-20251001",
) -> list[dict]:
    """
    Generate YouTube segment for each harvested skill.
    Returns list with 'script' field added.
    """
    client = anthropic.Anthropic(api_key=api_key)
    results = []

    for i, skill in enumerate(harvested, 1):
        name = skill.get("display_name", skill.get("slug", "?"))
        print(f"[SCRIPT] {i}/{len(harvested)} Generating segment for {name}...")

        try:
            message = client.messages.create(
                model=model,
                max_tokens=150,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": _build_prompt(skill)}],
            )
            script = _strip_markdown(message.content[0].text)
        except anthropic.APIError as e:
            print(f"  [WARN] API error for {name}: {e}")
            script = f"[Script generation failed: {e}]"

        skill["script"] = script
        results.append(skill)
        print(f"  Script: {script[:80]}...")

    return results


def render_markdown(
    movers: list[dict],
    rockets: list[dict] | None = None,
    week_label: str = "",
) -> str:
    """Render the final report with MOVERS and ROCKETS sections."""
    rockets = rockets or []

    # Determine if any movers have real velocity data
    has_velocity = any(r.get("_snapshots_used", 0) > 1 for r in movers)

    lines = [
        f"# OpenClaw Skills Weekly{' — ' + week_label if week_label else ''}",
        "",
    ]

    # --- MOVERS section ---
    if has_velocity:
        ranking_desc = "*Ranked by 7-day install velocity (installs_all_time delta).*"
    else:
        ranking_desc = "*Ranked by estimated weekly velocity (age-normalized from lifetime data — building daily history for true 7-day deltas).*"

    lines += [
        f"## Top {len(movers)} Trending Skills",
        "",
        ranking_desc,
        "",
    ]

    for i, r in enumerate(movers, 1):
        snaps = r.get("_snapshots_used", 0)
        cold = r.get("_cold_start", snaps <= 1)
        author = r.get("author", "")
        author_str = f"**Author:** {author} | " if author else ""

        if cold:
            hist = "estimated"
            pct_str = "est."
            growth_label = "Est. weekly"
        else:
            hist = f"{snaps}d data"
            pct_str = f"{r.get('_pct_increase', 0.0):.1f}%"
            growth_label = "7d Growth"

        lines += [
            f"### #{i} [{r.get('display_name', r.get('slug', '?'))}]({r.get('clawhub_url', '')})",
            "",
            (
                f"{author_str}"
                f"**Downloads:** {r.get('downloads', 0):,} | "
                f"**Installs:** {r.get('installs_current', 0):,} (all-time: {r.get('installs_all_time', 0):,}) | "
                f"**Stars:** {r.get('stars', 0)} | "
                f"**{growth_label}:** +{r.get('_installs_delta', 0):,} ({pct_str}) | "
                f"**Score:** {r.get('_score', 0.0):.4f} | "
                f"*{hist}*"
            ),
            "",
            f"> {r.get('summary', '')}" if r.get("summary") else "",
            "",
            "**YouTube Script**",
            "",
            f"_{r.get('script', '')}_",
            "",
            "---",
            "",
        ]

    # --- ROCKETS section (new skills) ---
    if rockets:
        lines += [
            "## New This Week",
            "",
            "*Brand new skills (<30 days old) showing early traction.*",
            "",
        ]
        for i, r in enumerate(rockets, 1):
            age = ""
            if r.get("created_at"):
                age_d = (datetime.now(timezone.utc) - datetime.fromtimestamp(r["created_at"] / 1000, tz=timezone.utc)).days
                age = f" | *{age_d} days old*"
            author = r.get("author", "")
            author_str = f"**Author:** {author} | " if author else ""
            lines += [
                f"### [{r.get('display_name', r.get('slug', '?'))}]({r.get('clawhub_url', '')})",
                "",
                (
                    f"{author_str}"
                    f"**Downloads:** {r.get('downloads', 0):,} | "
                    f"**Installs:** {r.get('installs_current', 0):,} | "
                    f"**Stars:** {r.get('stars', 0)} | "
                    f"**Score:** {r.get('_score', 0.0):.4f}"
                    f"{age}"
                ),
                "",
                f"> {r.get('summary', '')}" if r.get("summary") else "",
                "",
                "**YouTube Script**",
                "",
                f"_{r.get('script', '')}_",
                "",
                "---",
                "",
            ]

    # --- Community signals section ---
    signals = community_signals.load_signals()
    if signals:
        lines.append(community_signals.render_community_section(signals))

    return "\n".join(lines)


def render_video_script(
    movers: list[dict],
    rockets: list[dict] | None = None,
    episode_num: int = 1,
    week_label: str = "",
) -> str:
    """
    Render a voice-ready video script in GitHubAwesome style.

    Plain text, no markdown. Ready to read aloud or feed to TTS.
    Structure: cold open → movers → rockets → hard stop (no outro).
    """
    rockets = rockets or []
    total_skills = len(movers) + len(rockets)

    lines = []

    # --- Cold open (GitHubAwesome style) ---
    lines += [
        f"[COLD OPEN]",
        "",
        f"It is time for OpenClaw Skills Weekly, episode number {episode_num}, "
        f"featuring {total_skills} of the AI agent skills trending on ClawHub right now.",
        "",
        "",
    ]

    # --- Movers section ---
    if movers:
        lines += [
            "[TOP MOVERS]",
            "",
        ]
        for i, r in enumerate(movers, 1):
            name = r.get("display_name", r.get("slug", "?"))
            script = r.get("script", "")
            lines += [
                f"[{i}] {name}",
                "",
                script,
                "",
                "",
            ]

    # --- Rockets section ---
    if rockets:
        lines += [
            "[NEW THIS WEEK]",
            "",
        ]
        for i, r in enumerate(rockets, 1):
            name = r.get("display_name", r.get("slug", "?"))
            script = r.get("script", "")
            lines += [
                f"[NEW {i}] {name}",
                "",
                script,
                "",
                "",
            ]

    # --- No outro — last item ends the episode (GitHubAwesome style) ---
    lines += [
        "[END]",
    ]

    return "\n".join(lines)
