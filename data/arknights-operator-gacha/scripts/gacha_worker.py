#!/usr/bin/env python3
"""
Arknights Operator Gacha Worker (Simplified)
Outputs JSON with operator info and URLs for manual lore fetching.
"""

import argparse
import json
import random
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

import requests

# Configuration
WORKSPACE_BASE = Path.home() / ".openclaw"
FANDOM_LIST_URL = "https://arknights.fandom.com/wiki/Operator/{star}-star"


def sanitize_agent_name(name: str) -> str:
    """Validate agent name - alphanumeric and hyphens only"""
    if not name or len(name) > 50:
        raise ValueError(f"Invalid name length: {name}")
    normalized = name.lower().replace(" ", "-").replace("_", "-")
    sanitized = re.sub(r'[^a-z0-9\-]', '', normalized)
    if sanitized != normalized or ".." in sanitized:
        raise ValueError(f"Invalid characters in name: {name}")
    return sanitized


def roll_star_rating() -> int:
    """Roll 1-100 and return star rating"""
    roll = random.randint(1, 100)
    if roll <= 2: return 6
    if roll <= 10: return 5
    if roll <= 60: return 4
    return 3


def fetch_operator_list(stars: int) -> dict[str, dict]:
    """Fetch operator list from Fandom and return dict with avatar and detail URLs"""
    url = FANDOM_LIST_URL.format(star=stars)
    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        html = resp.text
        table_match = re.search(
            r'<table[^>]*class="[^"]*mrfz-wtable[^"]*"[^>]*>(.*?)</table>',
            html, re.DOTALL
        )
        if not table_match:
            print("[ERROR] Could not find operator table (mrfz-wtable)", file=sys.stderr)
            return {}
        table_html = table_match.group(1)
        operators = {}
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
        for row in rows:
            if '<th' in row:
                continue
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) < 2:
                continue
            avatar_cell = cells[0]
            avatar_match = re.search(
                r'data-src="(https://static\.wikia\.nocookie\.net/[^"]+)"',
                avatar_cell
            ) or re.search(
                r'src="(https://static\.wikia\.nocookie\.net/[^"]+)"',
                avatar_cell
            )
            avatar_url = avatar_match.group(1) if avatar_match else None
            name_cell = cells[1]
            name_match = re.search(
                r'<a[^>]*href="(/wiki/[^"]+)"[^>]*>([^<]+)</a>',
                name_cell
            )
            if name_match:
                detail_path = name_match.group(1)
                operator_name = name_match.group(2).strip()
                skip_names = ['operator', 'promotion', 'chip', 'skill', 'talent',
                             'class', 'lmd', 'recruitment', 'data supplement']
                if (operator_name and
                    len(operator_name) > 1 and
                    len(operator_name) < 50 and
                    not any(x in operator_name.lower() for x in skip_names)):
                    operators[operator_name] = {
                        "avatar_url": avatar_url,
                        "detail_path": detail_path,
                        "detail_url": f"https://arknights.fandom.com{detail_path}"
                    }
        return operators
    except Exception as e:
        print(f"[ERROR] Failed to fetch operator list: {e}", file=sys.stderr)
        return {}


def select_random_operator(operators: dict[str, dict]) -> tuple[str, dict]:
    if not operators:
        raise RuntimeError("No operators available to select")
    operator_name = random.choice(list(operators.keys()))
    return operator_name, operators[operator_name]


def check_agent_exists(agent_name: str) -> bool:
    """Check if agent workspace or config exists"""
    try:
        sanitized = sanitize_agent_name(agent_name)
        return (
            (WORKSPACE_BASE / "agents" / sanitized).exists() or
            (WORKSPACE_BASE / f"workspace-{sanitized}").exists()
        )
    except ValueError:
        return False


def create_agent(agent_name: str) -> tuple[bool, str]:
    """Create agent via openclaw CLI"""
    try:
        sanitized = sanitize_agent_name(agent_name)
        workspace = WORKSPACE_BASE / f"workspace-{sanitized}"
        result = subprocess.run(
            ["openclaw", "agents", "add", sanitized,
             "--workspace", str(workspace), "--non-interactive"],
            capture_output=True, text=True, timeout=30, shell=False
        )
        return result.returncode == 0, result.stderr if result.returncode != 0 else "OK"
    except Exception as e:
        return False, str(e)


def download_avatar(agent_name: str, avatar_url: str) -> tuple[bool, str]:
    """Download avatar with validation"""
    try:
        sanitized = sanitize_agent_name(agent_name)
        parsed = urllib.parse.urlparse(avatar_url)
        allowed_domains = ["static.wikia.nocookie.net", "media.prts.wiki"]
        if parsed.netloc not in allowed_domains or parsed.scheme != "https":
            return False, "Invalid avatar domain"
        workspace = WORKSPACE_BASE / f"workspace-{sanitized}"
        avatars_dir = workspace / "avatars"
        avatars_dir.mkdir(parents=True, exist_ok=True)
        avatar_path = avatars_dir / f"{sanitized}.png"
        resp = requests.get(avatar_url, timeout=30, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get('content-type', '')
        if not any(ct in content_type for ct in ['image/png', 'image/jpeg', 'image/webp']):
            return False, f"Invalid content type: {content_type}"
        downloaded = 0
        MAX_SIZE = 5 * 1024 * 1024
        with open(avatar_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                downloaded += len(chunk)
                if downloaded > MAX_SIZE:
                    avatar_path.unlink()
                    return False, "File too large"
                f.write(chunk)
        return True, str(avatar_path)
    except Exception as e:
        return False, str(e)


def git_commit(agent_name: str, message: str) -> bool:
    """Git add and commit"""
    try:
        sanitized = sanitize_agent_name(agent_name)
        workspace = WORKSPACE_BASE / f"workspace-{sanitized}"
        subprocess.run(["git", "add", "-A"], cwd=workspace, check=True, timeout=10)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=workspace, capture_output=True, timeout=10
        )
        return result.returncode == 0 or "nothing to commit" in result.stderr.decode().lower()
    except Exception:
        return False


def fetch_chinese_name(english_name: str) -> str:
    """从 Fandom 页面提取中文名 (data-source="cnname")"""
    url = f"https://arknights.fandom.com/wiki/{urllib.parse.quote(english_name)}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        html = resp.text
        m = re.search(
            r'<div[^>]*data-source="cnname"[^>]*>.*?<div[^>]*class="[^"]*pi-data-value[^"]*"[^>]*>([^<]+)</div>',
            html,
            re.DOTALL
        )
        if m:
            return m.group(1).strip()
    except Exception as e:
        print(f"[ERROR] fetch_chinese_name failed for {english_name}: {e}", file=sys.stderr)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--operator", help="Force specific operator (for testing)")
    parser.add_argument("--stars", type=int, choices=[3,4,5,6], help="Force star rating (required when --operator is specified)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run - skip agent creation, identity file, and git commit")
    args = parser.parse_args()
    
    # Validation: if operator is specified, stars must be provided
    if args.operator and args.stars is None:
        print("ERROR: When --operator is specified, --stars is required", file=sys.stderr)
        sys.exit(2)

    result = {
        "success": False,
        "operator": None,
        "error": None
    }

    try:
        # Step 1: Roll
        stars = args.stars or roll_star_rating()
        result["stars"] = stars
        print(f"[ROLL] Star rating: {stars}★", file=sys.stderr)

        # Step 2: Select operator
        operator_info = None
        cn_name = None
        if args.operator:
            op_name = args.operator
            print(f"[SELECT] Forced operator: {op_name}", file=sys.stderr)
            # Even when forcing operator, we need to fetch the list to get detail_url and avatar_url
            print(f"[FETCH] Getting {stars}★ operator list from fandom...", file=sys.stderr)
            operators = fetch_operator_list(stars)
            if operators and op_name in operators:
                operator_info = operators[op_name]
                print(f"[FETCH] Found operator info in {stars}★ list", file=sys.stderr)
            else:
                print(f"[WARN] Operator {op_name} not found in {stars}★ list, using basic URLs", file=sys.stderr)
        else:
            print(f"[FETCH] Getting {stars}★ operator list from fandom...", file=sys.stderr)
            operators = fetch_operator_list(stars)
            if not operators:
                raise RuntimeError(f"Failed to fetch {stars}★ operator list from fandom")
            print(f"[FETCH] Found {len(operators)} operators", file=sys.stderr)
            op_name, operator_info = select_random_operator(operators)
            print(f"[SELECT] Randomly selected: {op_name}", file=sys.stderr)

        # Build operator info - always fetch both English and Chinese
        result["operator"] = {
            "en_name": op_name
        }
        if operator_info:
            result["operator"]["avatar_url"] = operator_info.get("avatar_url")
            result["operator"]["en_detail_url"] = operator_info.get("detail_url")

        # Always fetch Chinese name
        print(f"[LANG] Resolving Chinese name via Fandom...", file=sys.stderr)
        cn_name = fetch_chinese_name(op_name)
        if cn_name:
            result["operator"]["cn_name"] = cn_name
            print(f"[LANG] Chinese name: {cn_name}", file=sys.stderr)
            result["operator"]["cn_detail_url"] = f"https://prts.wiki/w/{urllib.parse.quote(cn_name)}"
        else:
            print(f"[WARN] Could not resolve Chinese name for {op_name}", file=sys.stderr)

        # Step 3: Check duplicates and sanitize
        agent_name = sanitize_agent_name(op_name)
        if check_agent_exists(agent_name):
            result["duplicate"] = True
            print(f"[DUPLICATE] {agent_name} exists, needs re-roll", file=sys.stderr)
            print(json.dumps(result))
            sys.exit(0)

        result["agent_name"] = agent_name
        result["workspace"] = str(WORKSPACE_BASE / f"workspace-{agent_name}")
        result["dialogue_url"] = f"https://arknights.fandom.com/wiki/{urllib.parse.quote(op_name)}/Dialogue"

        # Step 4: Create agent (skip in dry-run)
        if args.dry_run:
            print(f"[DRY-RUN] Skipping agent creation", file=sys.stderr)
        else:
            print(f"[CREATE] Agent: {agent_name}", file=sys.stderr)
            ok, msg = create_agent(agent_name)
            if not ok:
                if "already exists" in msg.lower():
                    result["duplicate"] = True
                    print(json.dumps(result))
                    sys.exit(0)
                raise RuntimeError(f"Create agent failed: {msg}")

        # Step 5: Create IDENTITY.md (skip in dry-run)
        if args.dry_run:
            print(f"[DRY-RUN] Skipping IDENTITY.md creation", file=sys.stderr)
        else:
            identity_path = WORKSPACE_BASE / f"workspace-{agent_name}" / "IDENTITY.md"
            cn_display = cn_name if cn_name else "[TO_BE_FILLED_BY_LLM]"
            identity_content = f"""# IDENTITY.md - Who Am I?

- **Name (EN):** {op_name}
- **Name (CN):** {cn_display}
- **Class:** [TO_BE_FILLED_BY_LLM]
- **Faction:** [TO_BE_FILLED_BY_LLM]
- **Avatar:** avatars/{agent_name}.png
"""
            identity_path.write_text(identity_content, encoding='utf-8')
            print(f"[IDENTITY] Created template", file=sys.stderr)

        # Step 6: Download avatar (always execute, but in dry-run just record the URL)
        avatar_url = result["operator"].get("avatar_url")
        if avatar_url:
            if args.dry_run:
                print(f"[DRY-RUN] Avatar URL: {avatar_url}", file=sys.stderr)
                result["operator"]["avatar_url"] = avatar_url
            else:
                print(f"[AVATAR] Downloading from {avatar_url}...", file=sys.stderr)
                ok, msg = download_avatar(agent_name, avatar_url)
                if ok:
                    print(f"[AVATAR] Downloaded: {msg}", file=sys.stderr)
                else:
                    print(f"[AVATAR] Failed: {msg}", file=sys.stderr)
        else:
            print(f"[AVATAR] No avatar URL available", file=sys.stderr)

        # Step 7: Note lore will be fetched separately by LLM using provided URLs
        # No lore fetching here

        # Step 8: Git commit (skip in dry-run)
        if not args.dry_run:
            print(f"[GIT] Committing...", file=sys.stderr)
            cn_display = cn_name if cn_name else "N/A"
            git_commit(agent_name, f"Initial: {op_name} ({cn_display}) ({stars}★)")

        result["success"] = True
        if args.dry_run:
            print(f"[DONE] Dry run completed", file=sys.stderr)
        else:
            print(f"[DONE] Worker completed", file=sys.stderr)

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        print(f"[FATAL] {e}", file=sys.stderr)

    # Output raw JSON to stdout
    print(json.dumps(result))


if __name__ == "__main__":
    main()
