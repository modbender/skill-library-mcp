#!/usr/bin/env python3
"""
Jarvis — GitHub Watch
Récupère :
  1. Repos en tendance cette semaine (GitHub Trending, weekly)
  2. Repos actifs avec topic:sysops et topic:devops (GitHub API)

Sortie : JSON sur stdout (wrapped_listing pour LLM inclus)

Usage: python3 github_watch.py [--token TOKEN]
"""

import requests, json, sys, time, argparse, os
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))
from untrusted import wrap, build_prompt_header

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # override via --token ou GITHUB_TOKEN env

def get_headers(token=None):
    h = {"User-Agent": "Jarvis-GHWatch/1.0"}
    t = token or GITHUB_TOKEN
    if t:
        h["Authorization"] = f"Bearer {t}"
        h["Accept"] = "application/vnd.github.v3+json"
    return h


# ─── Trending ─────────────────────────────────────────────────────────────────

def fetch_trending(since="weekly", token=None):
    url = f"https://github.com/trending?since={since}"
    r = requests.get(url, headers={"User-Agent": "Jarvis-GHWatch/1.0"}, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    repos = []

    for article in soup.select("article.Box-row"):
        h2 = article.select_one("h2 a")
        if not h2:
            continue
        path = h2.get("href", "").strip("/")
        if not path or "/" not in path:
            continue

        desc_el = article.select_one("p")
        description = desc_el.get_text(strip=True) if desc_el else ""

        # Stars gained this week
        gained_el = article.select_one("span.d-inline-block.float-sm-right, [class*='float-sm-right']")
        stars_gained = gained_el.get_text(strip=True).replace(",", "").strip() if gained_el else "?"

        # Total stars (premier lien Link--muted avec compteur)
        muted_links = article.select("a.Link--muted")
        total_stars = muted_links[0].get_text(strip=True).replace(",", "").strip() if muted_links else "?"

        lang_el = article.select_one("span[itemprop='programmingLanguage']")
        language = lang_el.get_text(strip=True) if lang_el else ""

        repos.append({
            "name": path,
            "url": f"https://github.com/{path}",
            "description": description,
            "language": language,
            "stars_total": total_stars,
            "stars_gained": stars_gained,
            "source": "GitHub Trending weekly",
        })

    return repos


# ─── API Topics ───────────────────────────────────────────────────────────────

def fetch_topic_repos(topic, per_page=25, token=None):
    url = (
        f"https://api.github.com/search/repositories"
        f"?q=topic:{topic}&sort=updated&order=desc&per_page={per_page}"
    )
    r = requests.get(url, headers=get_headers(token), timeout=20)
    if r.status_code == 403:
        print(f"[WARN] Rate limit hit pour topic:{topic}", file=sys.stderr)
        return []
    r.raise_for_status()
    data = r.json()
    repos = []
    for item in data.get("items", []):
        repos.append({
            "name": item["full_name"],
            "url": item["html_url"],
            "description": (item.get("description") or "").strip(),
            "language": item.get("language") or "",
            "stars_total": item.get("stargazers_count", 0),
            "stars_gained": None,
            "updated": (item.get("pushed_at") or "")[:10],
            "source": f"GitHub topic:{topic}",
        })
    return repos


# ─── Wrapping LLM-safe ────────────────────────────────────────────────────────

def wrap_repo(repo, idx):
    lines = [
        f"name: {repo['name']}",
        f"url: {repo['url']}",
        f"description: {repo.get('description', '')}",
        f"language: {repo.get('language', '') or 'N/A'}",
        f"stars: {repo.get('stars_total', '?')}",
    ]
    if repo.get("stars_gained"):
        lines.append(f"stars_this_week: {repo['stars_gained']}")
    if repo.get("updated"):
        lines.append(f"last_push: {repo['updated']}")
    content = "\n".join(lines)
    return f"[{idx}] " + wrap(repo["source"], content, uid=str(idx))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=None, help="GitHub Personal Access Token (read:public_repo)")
    parser.add_argument("--since", default="weekly", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--filter-seen", action="store_true",
                        help="Exclut les repos déjà présentés dans un digest précédent")
    args = parser.parse_args()

    results = {}

    # 1. Trending
    print(f"[*] GitHub Trending ({args.since})…", file=sys.stderr)
    try:
        trending = fetch_trending(since=args.since, token=args.token)
        print(f"[OK] Trending : {len(trending)} repos", file=sys.stderr)
    except Exception as e:
        print(f"[ERR] Trending : {e}", file=sys.stderr)
        trending = []
    results["trending"] = trending

    time.sleep(1)

    # 2. topic:sysops
    print("[*] GitHub topic:sysops…", file=sys.stderr)
    try:
        sysops = fetch_topic_repos("sysops", per_page=25, token=args.token)
        print(f"[OK] sysops : {len(sysops)} repos", file=sys.stderr)
    except Exception as e:
        print(f"[ERR] sysops : {e}", file=sys.stderr)
        sysops = []
    results["sysops"] = sysops

    time.sleep(1)

    # 3. topic:devops
    print("[*] GitHub topic:devops…", file=sys.stderr)
    try:
        devops = fetch_topic_repos("devops", per_page=25, token=args.token)
        print(f"[OK] devops : {len(devops)} repos", file=sys.stderr)
    except Exception as e:
        print(f"[ERR] devops : {e}", file=sys.stderr)
        devops = []
    results["devops"] = devops

    # Filtre seen si demandé
    all_repos = trending + sysops + devops
    skipped = 0
    if args.filter_seen:
        from seen_store import github_store
        all_repos, skipped = github_store.filter_unseen(all_repos, key_fn=lambda r: r["name"])
        print(f"[seen] {skipped} repos filtrés (déjà vus), {len(all_repos)} restants", file=sys.stderr)
        # Recalcule les listes filtrées pour cohérence dans results
        seen_names = {r["name"] for r in all_repos}
        results["trending"] = [r for r in trending if r["name"] in seen_names]
        results["sysops"]   = [r for r in sysops   if r["name"] in seen_names]
        results["devops"]   = [r for r in devops    if r["name"] in seen_names]

    # Build wrapped listing
    header = build_prompt_header()
    wrapped = "\n\n".join(wrap_repo(r, i) for i, r in enumerate(all_repos))
    results["wrapped_listing"] = f"{header}\n\n{wrapped}"
    results["count"] = len(all_repos)
    results["skipped_seen"] = skipped

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
