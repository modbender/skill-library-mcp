#!/usr/bin/env python3
"""
onboard.py - Pull repo context and generate interview prompts for vision/rubric creation.

Usage:
    python3 onboard.py <repo-url> [--output-dir <dir>]

Examples:
    python3 onboard.py https://github.com/openclaw/openclaw
    python3 onboard.py https://github.com/user/repo --output-dir ./triage-config
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def run_gh(args: list[str], ignore_errors: bool = False) -> str:
    """Run a gh CLI command and return stdout."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0 and not ignore_errors:
            return ""
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        if not ignore_errors:
            print(f"Warning: gh command failed: {e}", file=sys.stderr)
        return ""


def parse_repo(url: str) -> str:
    """Extract owner/repo from a GitHub URL."""
    # Handle https://github.com/owner/repo or owner/repo
    url = url.rstrip("/")
    if "github.com" in url:
        parts = url.split("github.com/")[-1]
    else:
        parts = url
    # Remove .git suffix if present
    parts = parts.removesuffix(".git")
    return parts


def fetch_repo_context(repo: str) -> dict:
    """Fetch repo metadata, README, CONTRIBUTING, and recent releases."""
    context = {}

    # Repo description and metadata
    repo_json = run_gh(["repo", "view", repo, "--json",
                        "name,description,homepageUrl,stargazerCount,primaryLanguage,repositoryTopics"])
    if repo_json:
        try:
            context["metadata"] = json.loads(repo_json)
        except json.JSONDecodeError:
            context["metadata"] = {}

    # README
    readme = run_gh(["api", f"repos/{repo}/readme",
                     "--jq", ".content", "-H", "Accept: application/vnd.github.raw+json"],
                    ignore_errors=True)
    if readme:
        context["readme"] = readme[:5000]  # Truncate to keep prompt manageable

    # CONTRIBUTING.md
    contributing = run_gh(["api", f"repos/{repo}/contents/CONTRIBUTING.md",
                           "--jq", ".content", "-H", "Accept: application/vnd.github.raw+json"],
                          ignore_errors=True)
    if contributing:
        context["contributing"] = contributing[:3000]

    # Recent releases (last 5)
    releases = run_gh(["release", "list", "--repo", repo, "--limit", "5"])
    if releases:
        context["releases"] = releases

    # Open issue/PR counts
    issue_count = run_gh(["api", f"repos/{repo}", "--jq", ".open_issues_count"])
    if issue_count:
        context["open_issues"] = issue_count

    return context


def generate_interview_prompt(repo: str, context: dict) -> str:
    """Generate the interview prompt for the agent to ask the repo owner."""
    meta = context.get("metadata", {})
    name = meta.get("name", repo.split("/")[-1])
    desc = meta.get("description", "No description available")
    stars = meta.get("stargazerCount", "unknown")
    lang = meta.get("primaryLanguage", {})
    language = lang.get("name", "unknown") if isinstance(lang, dict) else "unknown"
    topics = meta.get("repositoryTopics", [])
    topic_names = [t.get("name", "") for t in topics] if topics else []

    readme_snippet = context.get("readme", "Not available")[:2000]

    prompt = f"""# Vision Interview for {name}

## Repo Context (auto-gathered)
- **Repo:** {repo}
- **Description:** {desc}
- **Stars:** {stars} | **Language:** {language}
- **Topics:** {', '.join(topic_names) if topic_names else 'none'}
- **Open issues/PRs:** {context.get('open_issues', 'unknown')}

### README excerpt:
```
{readme_snippet}
```

### Recent releases:
{context.get('releases', 'None found')}

---

## Interview Questions

Ask the repo owner these questions to build their vision document and scoring rubric.
Adapt based on the repo context above. Skip questions that are already answered by the README.

### Identity & Mission
1. In one sentence, what is this project and who is it for?
2. What problem does it solve that alternatives do not?
3. What are your 3-5 non-negotiable principles? (e.g., "must stay local-first", "no vendor lock-in")

### Priorities
4. Rank these contribution areas by importance for YOUR project:
   - Security fixes
   - Bug fixes
   - New features
   - Performance improvements
   - Documentation
   - Tests / CI improvements
   - Refactoring / code quality
5. What types of PRs would you auto-reject? (e.g., "anything adding cloud dependencies")
6. What types of PRs would you fast-track for review?

### Red Flags
7. What patterns signal a low-quality or misaligned contribution?
8. Are there areas of the codebase that need extra scrutiny?
9. Any specific anti-patterns you have seen in past PRs?

### Green Flags
10. What makes you excited to review a PR?
11. Are there specific areas where you actively want help?

### Context
12. Is the project in growth mode, maintenance mode, or transitioning?
13. Any upcoming milestones or releases that should affect prioritization?
14. How do you handle breaking changes? Any migration requirements?

---

After gathering answers, generate:
1. A **vision document** (save as `vision.md`) with mission, identity, priorities, and alignment signals
2. A **scoring rubric** (save as `rubric.md`) with base 50, positive/negative modifiers customized to this project

Use `references/rubric-template.md` as the starting template for the rubric.
"""
    return prompt


def main():
    parser = argparse.ArgumentParser(description="Onboard a repo for PR triage")
    parser.add_argument("repo_url", help="GitHub repo URL (e.g., https://github.com/owner/repo)")
    parser.add_argument("--output-dir", default="./triage-config",
                        help="Directory to save vision doc and rubric (default: ./triage-config)")
    args = parser.parse_args()

    repo = parse_repo(args.repo_url)
    print(f"Onboarding repo: {repo}", file=sys.stderr)

    # Fetch context
    context = fetch_repo_context(repo)

    # Generate interview prompt
    prompt = generate_interview_prompt(repo, context)

    # Save interview prompt
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    interview_path = output_dir / "interview-prompt.md"
    interview_path.write_text(prompt)
    print(f"Interview prompt saved to: {interview_path}", file=sys.stderr)

    # Also print to stdout for the agent to use directly
    print(prompt)


if __name__ == "__main__":
    main()
