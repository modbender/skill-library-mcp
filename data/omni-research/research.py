#!/usr/bin/env python3
"""omni-research: Multi-source deep research using the user's own browser sessions.

Connects to the user's running browser via CDP. No API keys needed —
uses whatever services the user is already logged into.

Usage:
    python3 research.py "your research query"
    python3 research.py --sources perplexity,gemini "query"
    python3 research.py --sources gemini-api "quick query"
"""

import asyncio
import json
import sys
import time
from pathlib import Path

import httpx

from browser import BrowserBridge, ensure_browser_bridge

CONFIG_PATH = Path.home() / ".config" / "omni-research" / "config.json"

DEFAULT_CONFIG = {
    "cdp_port": None,
    "cliproxy_url": "http://127.0.0.1:8317/v1",
    "cliproxy_key": "magi-proxy-key-2026",
    "synthesis_model": "glm-4.7",
    "gemini_api_model": "gemini-2.5-flash",
    "timeout_browser": 180,
    "timeout_api": 30,
}


def load_config() -> dict:
    config = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            config.update(json.load(f))
    return config


# ── Browser sources (CDP) ────────────────────────────────────────────────


async def query_perplexity_browser(browser: BrowserBridge, query: str) -> str:
    """Query Perplexity via user's logged-in browser."""
    try:
        return await browser.query_in_tab(
            url="https://www.perplexity.ai/",
            focus_js='document.querySelector("div[contenteditable=true]").focus()',
            query=query,
            extract_js="""(() => {
                const bodyText = document.body.innerText;
                // Check if still loading
                if (bodyText.includes('思考中') || bodyText.includes('搜尋中') || bodyText.includes('Searching')) return '';
                // Strategy 1: find .prose or markdown containers
                const prose = document.querySelectorAll('.prose, [class*="prose"], [class*="markdown"]');
                if (prose.length > 0) {
                    const last = prose[prose.length-1].innerText;
                    if (last.length > 100) return last;
                }
                // Strategy 2: find answer text from body content
                const lines = bodyText.split('\\n').filter(l => l.trim().length > 40);
                if (lines.length > 3) return lines.join('\\n');
                return '';
            })()""",
            wait_before=8.0,
            wait_after=15.0,
            poll_interval=3.0,
            poll_max=35,
            min_length=300,
        )
    except Exception as e:
        return f"[Perplexity] Error: {e}"


async def query_grok_browser(browser: BrowserBridge, query: str) -> str:
    """Query Grok via user's logged-in session on grok.com."""
    try:
        return await browser.query_in_tab(
            url="https://grok.com/",
            focus_js="""(() => {
                const pm = document.querySelector('.ProseMirror');
                if (pm) { pm.focus(); return 'prosemirror'; }
                const ta = document.querySelector('textarea');
                if (ta) { ta.focus(); return 'textarea'; }
                const ce = document.querySelector('[contenteditable="true"]');
                if (ce) { ce.focus(); return 'ce'; }
                return 'none';
            })()""",
            query=query,
            extract_js="""(() => {
                // Strategy 1: response-content-markdown (exact Grok selector)
                const md = document.querySelectorAll('.response-content-markdown, [class*="response-content-markdown"]');
                if (md.length > 0) {
                    const last = md[md.length-1].innerText;
                    if (last.length > 30) return last;
                }
                // Strategy 2: message-bubble (Grok chat bubble)
                const bubbles = document.querySelectorAll('[class*="message-bubble"]');
                if (bubbles.length > 0) {
                    const last = bubbles[bubbles.length-1].innerText;
                    if (last.length > 30) return last;
                }
                // Strategy 3: chat scroll area (contains all messages minus sidebar)
                const scroll = document.querySelector('[class*="overflow-y-auto"][class*="scrollbar-gutter"]');
                if (scroll && scroll.innerText.length > 50) {
                    // Strip the user query (first line) to get just the response
                    const lines = scroll.innerText.split('\\n').filter(l => l.trim());
                    const responseStart = lines.findIndex((l, i) => i > 0 && l.length > 20);
                    if (responseStart > 0) return lines.slice(responseStart).join('\\n');
                }
                return '';
            })()""",
            wait_before=8.0,
            wait_after=12.0,
            poll_interval=3.0,
            poll_max=30,
            min_length=50,
        )
    except Exception as e:
        return f"[Grok] Error: {e}"


async def query_gemini_browser(browser: BrowserBridge, query: str) -> str:
    """Query Gemini via user's logged-in Google session."""
    try:
        return await browser.query_in_tab(
            url="https://gemini.google.com/app",
            focus_js="""(() => {
                const tb = document.querySelector('[role="textbox"]');
                if (tb) { tb.focus(); return 'textbox'; }
                const ce = document.querySelector('[contenteditable="true"]');
                if (ce) { ce.focus(); return 'ce'; }
                return 'none';
            })()""",
            query=query,
            extract_js="""(() => {
                // Gemini response containers
                const sels = ['.model-response-text', '.response-content', '[class*="markdown"]', '.message-content'];
                for (const s of sels) {
                    const els = document.querySelectorAll(s);
                    if (els.length > 0 && els[els.length-1].innerText.length > 50) return els[els.length-1].innerText;
                }
                // Fallback: largest content div
                const allDivs = document.querySelectorAll('div');
                let best = null, bestLen = 0;
                for (const d of allDivs) {
                    const t = d.innerText;
                    if (t.length > 200 && t.length < 15000 && !d.querySelector('nav, header, aside')) {
                        if (t.length > bestLen) { bestLen = t.length; best = d; }
                    }
                }
                if (best) return best.innerText;
                return '';
            })()""",
            wait_before=5.0,
            wait_after=15.0,
            poll_interval=3.0,
            poll_max=30,
            min_length=200,
        )
    except Exception as e:
        return f"[Gemini] Error: {e}"


# ── API sources ──────────────────────────────────────────────────────────


async def _cliproxy_chat(config: dict, model: str, messages: list[dict]) -> str:
    url = config["cliproxy_url"]
    key = config["cliproxy_key"]
    async with httpx.AsyncClient(timeout=config["timeout_api"]) as client:
        for attempt in range(3):
            resp = await client.post(
                f"{url}/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={"model": model, "messages": messages, "max_tokens": 4096},
            )
            if resp.status_code == 429:
                wait = 3 * (attempt + 1)
                print(f"  {model}: 429, retry in {wait}s...", file=sys.stderr)
                await asyncio.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        return f"[{model}] Rate limited after 3 retries"


async def query_gemini_api(config: dict, query: str) -> str:
    try:
        return await _cliproxy_chat(
            config, config["gemini_api_model"],
            [
                {"role": "system", "content": "You are a research assistant. Provide detailed, sourced answers."},
                {"role": "user", "content": query},
            ],
        )
    except Exception as e:
        return f"[Gemini API] Error: {e}"


# ── Synthesis ────────────────────────────────────────────────────────────


async def synthesize(config: dict, query: str, results: dict[str, str]) -> str:
    sources_text = ""
    for name, text in results.items():
        truncated = text[:3000] if len(text) > 3000 else text
        sources_text += f"\n\n### {name}\n{truncated}"
    # Try synthesis model, fall back to gemini if rate limited
    for model in [config["synthesis_model"], config["gemini_api_model"]]:
        try:
            return await _cliproxy_chat(
                config, model,
                [
                    {"role": "system", "content": "Synthesize these research results into 3-5 bullet points. Note agreements, disagreements, unique insights. Write in the query's language."},
                    {"role": "user", "content": f"Query: {query}\n\nSources:{sources_text}"},
                ],
            )
        except Exception:
            continue
    return "[Synthesis] All models rate limited"


# ── Source registry ──────────────────────────────────────────────────────

BROWSER_SOURCES = {
    "perplexity": query_perplexity_browser,
    "grok": query_grok_browser,
    "gemini": query_gemini_browser,
}
API_SOURCES = {"gemini-api": query_gemini_api}
ALL_SOURCE_NAMES = list(BROWSER_SOURCES.keys()) + list(API_SOURCES.keys())


# ── Main ─────────────────────────────────────────────────────────────────


async def research(query: str, sources: list[str] | None = None) -> str:
    config = load_config()
    if sources is None:
        sources = list(BROWSER_SOURCES.keys())

    print(f"Researching: {query}", file=sys.stderr)
    print(f"Sources: {', '.join(sources)}", file=sys.stderr)

    need_browser = any(s in BROWSER_SOURCES for s in sources)
    browser = None

    if need_browser:
        try:
            browser = ensure_browser_bridge(config)
            info = browser.get_browser_info()
            print(f"  Browser: {info.get('Browser', '?')} on port {browser.cdp_port}", file=sys.stderr)
        except RuntimeError as e:
            print(f"  {e}", file=sys.stderr)
            sources = [s for s in sources if s in API_SOURCES] or ["gemini-api"]
            print(f"  Falling back to: {', '.join(sources)}", file=sys.stderr)

    start = time.time()
    results = {}

    # Browser sources — run in parallel (each opens its own tab)
    browser_tasks = {}
    for name in sources:
        if name in BROWSER_SOURCES and browser:
            browser_tasks[name] = asyncio.create_task(BROWSER_SOURCES[name](browser, query))

    # API sources — also parallel
    api_tasks = {}
    for name in sources:
        if name in API_SOURCES:
            api_tasks[name] = asyncio.create_task(API_SOURCES[name](config, query))

    # Gather all
    for name, task in {**browser_tasks, **api_tasks}.items():
        try:
            results[name] = await asyncio.wait_for(task, timeout=config["timeout_browser"])
            print(f"  {name}: done ({time.time() - start:.1f}s)", file=sys.stderr)
        except asyncio.TimeoutError:
            results[name] = f"[{name}] Timed out"
            print(f"  {name}: timeout", file=sys.stderr)

    # Synthesize
    if len(results) > 1:
        print("  Synthesizing...", file=sys.stderr)
        summary = await synthesize(config, query, results)
    else:
        summary = None

    elapsed = time.time() - start
    print(f"  Total: {elapsed:.1f}s", file=sys.stderr)

    output = f"## Research: {query}\n"
    for name, text in results.items():
        output += f"\n### {name.title()}\n{text}\n"
    if summary:
        output += f"\n---\n### Summary\n{summary}\n"
    return output


def main():
    import argparse
    parser = argparse.ArgumentParser(description="omni-research")
    parser.add_argument("query", help="Research query")
    parser.add_argument("--sources", "-s", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    sources = args.sources.split(",") if args.sources else None
    result = asyncio.run(research(args.query, sources))
    if args.json:
        print(json.dumps({"query": args.query, "result": result}))
    else:
        print(result)


if __name__ == "__main__":
    main()
