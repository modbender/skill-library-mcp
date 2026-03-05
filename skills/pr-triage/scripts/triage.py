#!/usr/bin/env python3
"""
PR Triage Tool - Detect duplicates and assess PR quality.

Usage:
    python triage.py <owner/repo> [--days N] [--threshold N] [--output FILE]
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any


def run_gh(args: list[str]) -> str:
    """Run gh CLI command with token env cleared."""
    env_prefix = ["env", "-u", "GH_TOKEN", "-u", "GITHUB_TOKEN"]
    result = subprocess.run(
        env_prefix + ["gh"] + args,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def fetch_prs(repo: str, days: int | None = None) -> list[dict]:
    """Fetch open PRs with metadata."""
    args = [
        "pr", "list",
        "--repo", repo,
        "--state", "open",
        "--limit", "500",
        "--json", "number,title,body,author,createdAt,updatedAt,labels,files,additions,deletions,headRefName"
    ]
    data = json.loads(run_gh(args))
    
    if days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        data = [
            pr for pr in data
            if datetime.fromisoformat(pr["updatedAt"].replace("Z", "+00:00")) > cutoff
        ]
    
    return data


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text."""
    if not text:
        return set()
    
    # Lowercase and split
    text = text.lower()
    
    # Remove common words
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "dare",
        "this", "that", "these", "those", "i", "you", "he", "she", "it",
        "we", "they", "what", "which", "who", "whom", "when", "where",
        "why", "how", "all", "each", "every", "both", "few", "more", "most",
        "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "just", "and", "but", "if", "or",
        "because", "as", "until", "while", "of", "at", "by", "for", "with",
        "about", "against", "between", "into", "through", "during", "before",
        "after", "above", "below", "to", "from", "up", "down", "in", "out",
        "on", "off", "over", "under", "again", "further", "then", "once",
        "pr", "fix", "bug", "issue", "add", "update", "change", "remove",
    }
    
    # Extract words (alphanumeric + underscores)
    words = re.findall(r'[a-z][a-z0-9_]*', text)
    
    # Filter
    keywords = {w for w in words if len(w) > 2 and w not in stopwords}
    
    return keywords


def extract_issue_refs(text: str) -> set[int]:
    """Extract issue references from text."""
    if not text:
        return set()
    
    # Match patterns: #123, Fixes #123, Closes #123, Resolves #123
    refs = re.findall(r'(?:fixes|closes|resolves|fix|close|resolve)?\s*#(\d+)', text.lower())
    return {int(r) for r in refs}


def extract_intent(pr: dict) -> dict:
    """Extract searchable intent from PR."""
    files = [f["path"] for f in pr.get("files", [])]
    body = pr.get("body") or ""
    title = pr.get("title", "")
    
    return {
        "number": pr["number"],
        "title": title,
        "files": files,
        "keywords": extract_keywords(title + " " + body),
        "issue_refs": extract_issue_refs(body),
        "additions": pr.get("additions", 0),
        "deletions": pr.get("deletions", 0),
        "labels": [l["name"] for l in pr.get("labels", [])],
        "author": pr.get("author", {}).get("login", "unknown"),
        "created_at": pr.get("createdAt", ""),
        "updated_at": pr.get("updatedAt", ""),
        "body_length": len(body),
        "has_tests": any(
            re.search(r'(test_|_test\.|\.test\.|spec\.|\.spec\.)', f.lower())
            for f in files
        ),
    }


def file_similarity(pr1: dict, pr2: dict) -> float:
    """Jaccard similarity of files changed."""
    files1 = set(pr1["files"])
    files2 = set(pr2["files"])
    if not files1 or not files2:
        return 0.0
    return len(files1 & files2) / len(files1 | files2)


def keyword_similarity(pr1: dict, pr2: dict) -> float:
    """Jaccard similarity of extracted keywords."""
    kw1 = pr1["keywords"]
    kw2 = pr2["keywords"]
    if not kw1 or not kw2:
        return 0.0
    return len(kw1 & kw2) / len(kw1 | kw2)


def same_issue(pr1: dict, pr2: dict) -> bool:
    """Check if both PRs reference the same issue."""
    refs1 = pr1["issue_refs"]
    refs2 = pr2["issue_refs"]
    return bool(refs1 and refs2 and refs1 & refs2)


def similarity_score(pr1: dict, pr2: dict) -> int:
    """Combined similarity (0-100)."""
    if same_issue(pr1, pr2):
        return 100  # Definite duplicate
    
    file_sim = file_similarity(pr1, pr2)
    kw_sim = keyword_similarity(pr1, pr2)
    
    # Weighted combination
    return int((file_sim * 0.6 + kw_sim * 0.4) * 100)


def quality_score(pr: dict) -> int:
    """Calculate quality score for a PR."""
    score = 0
    
    # Has description
    if pr["body_length"] > 50:
        score += 10
    
    # References issue
    if pr["issue_refs"]:
        score += 15
    
    # Has tests
    if pr["has_tests"]:
        score += 20
    
    # Small PR
    if pr["additions"] + pr["deletions"] < 100:
        score += 10
    
    # Has labels
    if pr["labels"]:
        score += 5
    
    # Recent activity
    if pr["updated_at"]:
        updated = datetime.fromisoformat(pr["updated_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) - updated < timedelta(days=7):
            score += 10
    
    return score


def quality_grade(score: int) -> str:
    """Convert score to letter grade."""
    if score >= 60:
        return "A"
    elif score >= 40:
        return "B"
    elif score >= 20:
        return "C"
    else:
        return "D"


def find_duplicates(intents: list[dict], threshold: int) -> list[list[dict]]:
    """Find groups of duplicate PRs."""
    n = len(intents)
    if n == 0:
        return []
    
    # Build adjacency based on similarity
    groups: dict[int, set[int]] = defaultdict(set)
    
    for i in range(n):
        for j in range(i + 1, n):
            score = similarity_score(intents[i], intents[j])
            if score >= threshold:
                groups[i].add(j)
                groups[j].add(i)
    
    # Find connected components (duplicate groups)
    visited = set()
    duplicate_groups = []
    
    for i in range(n):
        if i in visited or i not in groups:
            continue
        
        # BFS to find all connected PRs
        group = []
        queue = [i]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            group.append(intents[node])
            for neighbor in groups[node]:
                if neighbor not in visited:
                    queue.append(neighbor)
        
        if len(group) > 1:
            # Sort by quality score descending
            group.sort(key=lambda x: quality_score(x), reverse=True)
            duplicate_groups.append(group)
    
    return duplicate_groups


def generate_report(
    repo: str,
    intents: list[dict],
    duplicates: list[list[dict]],
    days: int | None,
    top: int | None,
) -> str:
    """Generate Markdown triage report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    lines = [
        "# PR Triage Report",
        "",
        f"**Repository:** {repo}",
        f"**Generated:** {now}",
        f"**PRs Analyzed:** {len(intents)}",
        f"**Duplicates Found:** {len(duplicates)} groups",
        "",
    ]
    
    # Duplicate groups
    if duplicates:
        lines.append("## 🔴 Duplicate Groups (Action Required)")
        lines.append("")
        
        for i, group in enumerate(duplicates, 1):
            # Find common issue reference if any
            refs_with_issues = [pr["issue_refs"] for pr in group if pr["issue_refs"]]
            common_issues = set.intersection(*refs_with_issues) if refs_with_issues else set()
            issue_str = f"Issue: #{list(common_issues)[0]}" if common_issues else "No common issue"
            
            # Infer group topic from first PR
            topic = group[0]["title"][:50]
            
            lines.append(f"### Group {i}: {topic}")
            lines.append(f"**{issue_str}**")
            lines.append("")
            lines.append("| PR | Title | Author | Quality | Recommendation |")
            lines.append("|----|-------|--------|---------|----------------|")
            
            for j, pr in enumerate(group):
                score = quality_score(pr)
                grade = quality_grade(score)
                rec = "✅ Keep" if j == 0 else "❌ Close"
                title = pr["title"][:40] + "..." if len(pr["title"]) > 40 else pr["title"]
                lines.append(f"| #{pr['number']} | {title} | @{pr['author']} | {grade} | {rec} |")
            
            lines.append("")
            lines.append(f"**Recommendation:** Keep #{group[0]['number']} (highest quality score)")
            lines.append("")
    
    # Quality summary
    grades = defaultdict(list)
    for pr in intents:
        grade = quality_grade(quality_score(pr))
        grades[grade].append(pr["number"])
    
    lines.append("## 📊 Quality Summary")
    lines.append("")
    lines.append("| Grade | Count | PRs |")
    lines.append("|-------|-------|-----|")
    for grade in ["A", "B", "C", "D"]:
        prs = grades.get(grade, [])
        pr_list = ", ".join(f"#{n}" for n in prs[:5])
        if len(prs) > 5:
            pr_list += f", ... (+{len(prs) - 5} more)"
        lines.append(f"| {grade} | {len(prs)} | {pr_list} |")
    lines.append("")
    
    # Stale PRs
    stale = []
    for pr in intents:
        if pr["updated_at"]:
            updated = datetime.fromisoformat(pr["updated_at"].replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - updated).days
            if age > 30:
                stale.append((pr, age))
    
    if stale:
        stale.sort(key=lambda x: x[1], reverse=True)
        lines.append("## ⚠️ Stale PRs (>30 days no activity)")
        lines.append("")
        for pr, age in stale[:10]:
            lines.append(f"- #{pr['number']}: \"{pr['title'][:50]}\" ({age} days)")
        lines.append("")
    
    # Ready to merge (high quality, not in duplicates)
    duplicate_numbers = {pr["number"] for group in duplicates for pr in group}
    ready = [
        pr for pr in intents
        if quality_score(pr) >= 60 and pr["number"] not in duplicate_numbers
    ]
    ready.sort(key=lambda x: quality_score(x), reverse=True)
    
    if ready:
        lines.append("## 🚀 Ready to Review (High Quality + No Duplicates)")
        lines.append("")
        for pr in ready[:10]:
            lines.append(f"- #{pr['number']}: \"{pr['title'][:50]}\" (Grade A)")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="PR Triage Tool")
    parser.add_argument("repo", help="Repository (owner/repo)")
    parser.add_argument("--days", type=int, default=7, help="Only PRs updated in last N days")
    parser.add_argument("--all", action="store_true", help="Analyze all open PRs")
    parser.add_argument("--threshold", type=int, default=80, help="Similarity threshold (0-100)")
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument("--top", type=int, help="Only show top N PRs")
    
    args = parser.parse_args()
    
    days = None if args.all else args.days
    
    print(f"Fetching PRs from {args.repo}...", file=sys.stderr)
    prs = fetch_prs(args.repo, days)
    print(f"Found {len(prs)} PRs", file=sys.stderr)
    
    print("Extracting intents...", file=sys.stderr)
    intents = [extract_intent(pr) for pr in prs]
    
    print("Finding duplicates...", file=sys.stderr)
    duplicates = find_duplicates(intents, args.threshold)
    print(f"Found {len(duplicates)} duplicate groups", file=sys.stderr)
    
    print("Generating report...", file=sys.stderr)
    report = generate_report(args.repo, intents, duplicates, days, args.top)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
