"""
harvester.py — Content Harvester (v3)

Fetches skill documentation from ClawHub detail page or linked source repo.
Priority order:
  1. ClawHub skill detail page (GET /api/v1/skills/{slug})
  2. Linked GitHub/source repo README
  3. Falls back to summary-only if neither is available
"""

import time
import httpx

CLAWHUB_BASE = "https://clawhub.ai"
GITHUB_RAW = "https://raw.githubusercontent.com"
README_CANDIDATES = ["README.md", "readme.md", "SKILL.md", "README.rst", "README"]
MAX_CONTENT_CHARS = 6000
REQUEST_TIMEOUT = 15


def _fetch_clawhub_detail(slug: str) -> dict:
    """Fetch skill detail via ClawHub API. Returns {content, author} dict."""
    if not slug:
        return {"content": "", "author": ""}
    url = f"{CLAWHUB_BASE}/api/v1/skills/{slug}"
    try:
        resp = httpx.get(url, timeout=REQUEST_TIMEOUT, follow_redirects=True,
                         headers={"Accept": "application/json"})
        if resp.status_code != 200:
            return {"content": "", "author": ""}
        data = resp.json()

        # Extract author from owner field (only available in detail endpoint)
        owner = data.get("owner") or {}
        author = owner.get("handle", "") or owner.get("displayName", "")

        # Build content from skill summary + changelog
        parts = []
        skill_data = data.get("skill") or {}
        summary = skill_data.get("summary") or data.get("summary") or ""
        if summary:
            parts.append(summary)
        if data.get("description"):
            parts.append(data["description"])
        lv = data.get("latestVersion") or {}
        if lv.get("changelog"):
            parts.append(f"Latest changelog: {lv['changelog']}")
        content = "\n\n".join(parts)[:MAX_CONTENT_CHARS]

        return {"content": content, "author": author}
    except Exception:
        return {"content": "", "author": ""}


def _fetch_github_readme(source_url: str, github_token: str) -> str:
    """Fetch README from a GitHub source repo URL."""
    if not source_url or "github.com" not in source_url:
        return ""

    parts = source_url.rstrip("/").replace("https://github.com/", "").split("/")
    if len(parts) < 2:
        return ""
    owner, repo = parts[0], parts[1]

    headers = {"User-Agent": "OpenclawSkillsWeekly/1.0"}
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    # Get default branch
    try:
        api_resp = httpx.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers={**headers, "Accept": "application/vnd.github+json"},
            timeout=REQUEST_TIMEOUT,
        )
        branch = api_resp.json().get("default_branch", "main") if api_resp.status_code == 200 else "main"
    except Exception:
        branch = "main"

    for filename in README_CANDIDATES:
        url = f"{GITHUB_RAW}/{owner}/{repo}/{branch}/{filename}"
        try:
            resp = httpx.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.text[:MAX_CONTENT_CHARS]
        except Exception:
            continue
    return ""


def harvest(skills: list[dict], github_token: str = "") -> list[dict]:
    """
    Fetch documentation for each skill.
    Returns list of enriched skill dicts with added 'content' field.
    """
    results = []

    for i, skill in enumerate(skills, 1):
        name = skill.get("display_name", skill.get("slug", "?"))
        slug = skill.get("slug", "")
        print(f"[HARVEST] {i}/{len(skills)} {name}")

        # 1. Try ClawHub API detail (also extracts author)
        detail = _fetch_clawhub_detail(slug)
        content = detail["content"]
        author = detail["author"]

        if content:
            print(f"  Source: ClawHub API ({len(content)} chars)")
        else:
            # 2. Try GitHub source repo
            content = _fetch_github_readme(skill.get("source_url", ""), github_token)
            if content:
                print(f"  Source: GitHub README ({len(content)} chars)")
            else:
                # 3. Fall back to summary
                content = skill.get("summary", "")
                print(f"  Source: summary only ({len(content)} chars)")

        enriched = {**skill, "content": content}
        # Merge author from detail endpoint if discovery didn't provide one
        if author and not skill.get("author"):
            enriched["author"] = author
            print(f"  Author: {author}")

        results.append(enriched)

        if i < len(skills):
            time.sleep(0.3)

    return results
