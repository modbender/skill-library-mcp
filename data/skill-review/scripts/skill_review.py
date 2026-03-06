#!/usr/bin/env python3
"""ClawHub skill security scan scraper.

Generates a markdown report for the skills found under --skills-dir.

Strategy:
- Determine slug from SKILL.md frontmatter name:
- Visit https://clawhub.ai/<owner>/<slug>
- Expand any collapsed "Details" controls
- Extract Security Scan + Runtime requirements + Comments

Note: ClawHub renders this section client-side; we use Playwright.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LocalSkill:
    path: Path
    slug: str
    local_version: str | None
    homepage: str | None = None


def _read_frontmatter(path: Path) -> dict[str, Any]:
    """Very small YAML frontmatter reader (only key: value lines)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    block = text[4:end]
    out: dict[str, Any] = {}
    for line in block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", line)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        # Strip simple quotes
        v = v.strip('"').strip("'")
        out[k] = v
    return out


def _find_local_skills(skills_dir: Path) -> list[LocalSkill]:
    skills: list[LocalSkill] = []
    for child in sorted(skills_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("_") or child.name.startswith("."):
            continue
        skill_md = child / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = _read_frontmatter(skill_md)
        slug = (fm.get("name") or "").strip()
        if not slug:
            continue
        local_version = (fm.get("version") or "").strip() or None
        homepage = (fm.get("homepage") or "").strip() or None
        skills.append(LocalSkill(path=child, slug=slug, local_version=local_version, homepage=homepage))
    return skills


def _load_suppressions(path: str | None) -> dict[str, list[dict[str, str]]]:
    """Load suppressions file — known-acceptable findings to ignore.

    Format: { "slug": [{"scanner": "VirusTotal|OpenClaw", "reason": "..."}] }
    A slug with any suppression entry will have its corresponding scanner
    status changed to "Acknowledged" in output (instead of Suspicious/Malicious).
    """
    if not path:
        # Auto-detect: look next to this script, then /tmp
        for candidate in [
            Path(__file__).resolve().parent.parent / "suppressions.json",
            Path(__file__).resolve().parent / "suppressions.json",
        ]:
            if candidate.exists():
                path = str(candidate)
                break
    if not path:
        return {}
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}


def _apply_suppressions(
    slug: str,
    vt_status: str | None,
    oc_status: str | None,
    suppressions: dict[str, list[dict[str, str]]],
    vt_analysis: str | None = None,
    oc_summary: str | None = None,
    oc_guidance: str | None = None,
) -> tuple[str | None, str | None, list[dict[str, str]]]:
    """Apply suppressions for a skill.

    Returns (adjusted_vt_status, adjusted_oc_status, applied_suppressions).
    Only Suspicious/Malicious statuses are suppressed; Benign/Pending are left alone.

    Each rule can have:
      - "scanner": "VirusTotal" or "OpenClaw" (required)
      - "pattern": substring to match in the analysis text (optional but recommended)
      - "reason": human-readable justification

    If "pattern" is set, the rule only applies when the pattern appears in the
    relevant analysis text (case-insensitive). This ensures suppressions
    automatically expire when the finding changes (e.g. new version, different issue).
    If "pattern" is omitted, the rule applies unconditionally (legacy behavior).
    """
    rules = suppressions.get(slug, [])
    if not rules:
        return vt_status, oc_status, []

    applied = []
    suppressible = {"Suspicious", "Malicious"}

    for rule in rules:
        scanner = rule.get("scanner", "").strip()
        pattern = rule.get("pattern", "").strip()

        if scanner == "VirusTotal" and vt_status in suppressible:
            if pattern:
                haystack = (vt_analysis or "").lower()
                if pattern.lower() not in haystack:
                    continue  # Pattern doesn't match — don't suppress
            vt_status = "Acknowledged"
            applied.append(rule)
        elif scanner == "OpenClaw" and oc_status in suppressible:
            if pattern:
                haystack = ((oc_summary or "") + " " + (oc_guidance or "")).lower()
                if pattern.lower() not in haystack:
                    continue
            oc_status = "Acknowledged"
            applied.append(rule)

    return vt_status, oc_status, applied


def _load_slug_map(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise SystemExit(f"slug-map not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _md_escape(s: str) -> str:
    return (s or "").replace("|", "\\|").strip()


def _parse_page_text(text: str) -> dict[str, Any]:
    """Parse the main text blob into sections.

    Kept as a fallback because some parts of the page are easier to capture as text,
    but security scan details should prefer DOM scraping.
    """
    t = (text or "").replace("\r", "")
    lines = [ln.strip() for ln in t.split("\n") if ln.strip()]

    # Current version
    version = None
    for i, ln in enumerate(lines):
        if ln.lower() == "current version" and i + 1 < len(lines):
            version = lines[i + 1]
            break

    # Security scan raw block
    sec_raw = None
    if "SECURITY SCAN" in t:
        sec_raw = t.split("SECURITY SCAN", 1)[1]
        # page footer marker seen on ClawHub
        if "Like a lobster shell" in sec_raw:
            sec_raw = sec_raw.split("Like a lobster shell", 1)[0]
        sec_raw = sec_raw.strip()

    sec_lines = [ln.strip() for ln in (sec_raw or "").split("\n") if ln.strip()]
    vt_status = None
    oc_status = None
    oc_conf = None
    oc_reason = None

    def _idx(label: str) -> int:
        try:
            return sec_lines.index(label)
        except ValueError:
            return -1

    vt_i = _idx("VirusTotal")
    if vt_i >= 0 and vt_i + 1 < len(sec_lines):
        vt_status = sec_lines[vt_i + 1]

    oc_i = _idx("OpenClaw")
    if oc_i >= 0 and oc_i + 1 < len(sec_lines):
        oc_status = sec_lines[oc_i + 1]
    if oc_i >= 0 and oc_i + 2 < len(sec_lines):
        oc_conf = sec_lines[oc_i + 2]
    if oc_i >= 0:
        # find the long reason sentence
        for ln in sec_lines[oc_i : oc_i + 100]:
            if ln.startswith("The skill") or ln.startswith("The tool"):
                oc_reason = ln
                break

    # Runtime requirements section
    runtime = None
    rr_idx = next((i for i, ln in enumerate(lines) if ln == "Runtime requirements"), -1)
    if rr_idx >= 0:
        runtime = []
        for j in range(rr_idx, len(lines)):
            if j > rr_idx and lines[j] == "Files":
                break
            runtime.append(lines[j])

    # Comments section
    comments = None
    c_idx = next((i for i, ln in enumerate(lines) if ln == "Comments"), -1)
    if c_idx >= 0:
        comments = lines[c_idx : min(len(lines), c_idx + 200)]

    return {
        "version": version,
        "security": {
            "vtStatus": vt_status,
            "vtLink": None,
            "ocStatus": oc_status,
            "ocConf": oc_conf,
            "ocReason": oc_reason,
            "summary": None,
            "dimensions": None,
            "guidance": None,
            "raw": sec_raw,
        },
        "runtime": runtime,
        "comments": comments,
    }


def _load_vt_api_key() -> str | None:
    """Load VirusTotal API key from env or ~/.openclaw/.env."""
    key = os.environ.get("VIRUSTOTAL_API_KEY")
    if key:
        return key.strip()
    env_path = Path.home() / ".openclaw" / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == "VIRUSTOTAL_API_KEY":
                return v.strip().strip("\"'")
    return None


def _hash_from_vt_url(vt_url: str) -> str | None:
    """Extract the file hash from a VirusTotal GUI URL."""
    # https://www.virustotal.com/gui/file/<hash>
    m = re.search(r"/gui/file/([0-9a-fA-F]{64})", vt_url or "")
    return m.group(1) if m else None


class _VTQuotaExhausted(Exception):
    """Raised when VT API quota is exhausted (daily/monthly limit)."""


# Track request timestamps for client-side rate limiting (4 req/min free tier).
_vt_request_times: list[float] = []
_VT_REQUESTS_PER_MINUTE = 4


def _vt_rate_limit_wait() -> None:
    """Sleep if needed to stay within VT free-tier rate limit (4 req/min)."""
    now = time.time()
    # Purge timestamps older than 60s
    while _vt_request_times and _vt_request_times[0] < now - 60:
        _vt_request_times.pop(0)
    if len(_vt_request_times) >= _VT_REQUESTS_PER_MINUTE:
        wait = 60 - (now - _vt_request_times[0]) + 0.5
        if wait > 0:
            sys.stderr.write(f"    VT rate limit: waiting {wait:.0f}s…\n")
            sys.stderr.flush()
            time.sleep(wait)
    _vt_request_times.append(time.time())


def _query_virustotal_api(file_hash: str, api_key: str) -> dict[str, Any] | None:
    """Query VT v3 API for file info. Returns the attributes dict or None.

    Raises _VTQuotaExhausted on 429 with daily/monthly quota errors so the
    caller can disable further API attempts and fall back to scraping.
    """
    import urllib.request
    import urllib.error

    _vt_rate_limit_wait()

    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    req = urllib.request.Request(url, headers={"x-apikey": api_key})
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            return data.get("data", {}).get("attributes")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # Check if it's a transient per-minute limit or a hard quota
                body = ""
                try:
                    body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    pass
                is_quota = "QuotaExceededError" in body
                if is_quota and ("daily" in body.lower() or "monthly" in body.lower()):
                    sys.stderr.write(f"    VT API quota exhausted — switching to scraping fallback\n")
                    sys.stderr.flush()
                    raise _VTQuotaExhausted(body)
                # Transient rate limit — wait and retry
                if attempt < max_retries:
                    wait = 60 * (attempt + 1)
                    sys.stderr.write(f"    VT API 429 (rate limit) — retrying in {wait}s (attempt {attempt + 1}/{max_retries})…\n")
                    sys.stderr.flush()
                    time.sleep(wait)
                    continue
                sys.stderr.write(f"    VT API 429 — retries exhausted, switching to scraping\n")
                sys.stderr.flush()
                raise _VTQuotaExhausted("rate limit retries exhausted")
            sys.stderr.write(f"    VT API {e.code} for {file_hash}\n")
            return None
        except Exception as e:
            sys.stderr.write(f"    VT API error: {e}\n")
            return None
    return None


def _format_vt_api_result(attrs: dict[str, Any]) -> dict[str, Any]:
    """Extract structured VT data from API attributes into a clean dict."""
    result: dict[str, Any] = {}

    # Detection stats
    stats = attrs.get("last_analysis_stats") or {}
    mal = stats.get("malicious", 0)
    total_scanners = sum(stats.get(k, 0) for k in ("malicious", "suspicious", "undetected", "harmless"))
    if mal > 0:
        result["detection"] = f"{mal} security vendor(s) flagged this file as malicious"
    else:
        result["detection"] = "No security vendors flagged this file as malicious"
    result["detectionStats"] = stats

    # File info
    name = attrs.get("meaningful_name") or ""
    size = attrs.get("size") or 0
    if size >= 1024 * 1024:
        size_str = f"{size / (1024 * 1024):.2f} MB"
    elif size >= 1024:
        size_str = f"{size / 1024:.2f} KB"
    else:
        size_str = f"{size} B"
    if name:
        result["fileInfo"] = f"{name}  Size  {size_str}"

    # Last analysis date
    ts = attrs.get("last_analysis_date")
    if ts:
        import datetime as _dt
        try:
            result["lastAnalysis"] = _dt.datetime.fromtimestamp(ts, tz=_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            pass

    # Code Insights (crowdsourced AI results)
    ai_results = attrs.get("crowdsourced_ai_results") or []
    code_insights = [r for r in ai_results if r.get("category") == "code_insight"]
    if code_insights:
        ci = code_insights[0]
        result["codeInsights"] = {
            "verdict": ci.get("verdict"),
            "source": ci.get("source"),
            "analysis": ci.get("analysis"),
        }

    return result


# ── VT Cache ──────────────────────────────────────────────────────────

_SKILL_DIR = Path(__file__).resolve().parent.parent
_VT_CACHE_DIR = _SKILL_DIR / "vt-cache"


def _vt_cache_path(file_hash: str) -> Path:
    """Return the cache file path for a given file hash."""
    return _VT_CACHE_DIR / f"{file_hash}.json"


def _vt_cache_load(file_hash: str) -> dict[str, Any] | None:
    """Load cached VT result for a file hash. Returns None on miss."""
    p = _vt_cache_path(file_hash)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        sys.stderr.write(f"    VT cache hit: {file_hash[:12]}…\n")
        sys.stderr.flush()
        return data
    except Exception:
        return None


def _vt_cache_store(file_hash: str, result: dict[str, Any] | str | None) -> None:
    """Store a VT result in the cache."""
    _VT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "hash": file_hash,
        "cached_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(timespec="seconds"),
    }
    if isinstance(result, dict):
        entry.update(result)
    elif isinstance(result, str):
        entry["text"] = result
    _vt_cache_path(file_hash).write_text(
        json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _scrape_virustotal(page: Any, vt_url: str, *, api_key: str | None = None) -> str | None:
    """Get VirusTotal analysis for a file.

    Prefers the VT v3 API (clean, structured) when api_key is available.
    Falls back to Playwright scraping of the VT GUI page otherwise.
    Results are cached by file hash — repeated queries for the same
    version return instantly without API calls.
    """
    if not vt_url or "virustotal.com" not in vt_url:
        return None

    file_hash = _hash_from_vt_url(vt_url)
    if not file_hash:
        return None

    # ── Cache check ───────────────────────────────────────────────────
    cached = _vt_cache_load(file_hash)
    if cached is not None:
        # Reconstruct the return value the caller expects
        text = cached.get("text")
        ci_verdict = cached.get("codeInsightsVerdict")
        if ci_verdict is not None:
            return {"text": text, "codeInsightsVerdict": ci_verdict}
        return text

    # ── API path (preferred) ──────────────────────────────────────────
    # _VTQuotaExhausted is intentionally NOT caught here — it propagates
    # to the caller so it can disable API for remaining skills.
    if api_key:
        attrs = _query_virustotal_api(file_hash, api_key)
        if attrs:
            vt = _format_vt_api_result(attrs)
            sections: list[str] = []
            if vt.get("detection"):
                sections.append(f"Detection: {vt['detection']}")
            if vt.get("fileInfo"):
                sections.append(f"File: {vt['fileInfo']}")
            if vt.get("lastAnalysis"):
                sections.append(f"Last analysis: {vt['lastAnalysis']}")
            ci = vt.get("codeInsights")
            if ci and ci.get("analysis"):
                sections.append(f"Code insights: {ci['analysis']}")
            text = "\n".join(sections) if sections else None
            # Return a dict when we have structured data (Code Insights verdict)
            ci_verdict = ci.get("verdict") if ci else None
            result = {"text": text, "codeInsightsVerdict": ci_verdict}
            _vt_cache_store(file_hash, result)
            return result
        # API failed — fall through to scraping

    # ── Scraping fallback (no API key or API error) ───────────────────
    try:
        page.goto(vt_url, wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_selector("vt-ui-file-card, file-view, .file-analysis", timeout=15000)
        except Exception:
            pass
        time.sleep(2)

        structured = page.evaluate(r"""
() => {
    function shadowText(root) {
        let t = '';
        if (!root) return t;
        if (root.shadowRoot) t += shadowText(root.shadowRoot);
        for (const c of (root.childNodes || [])) {
            if (c.nodeType === 3) t += c.textContent;
            else if (c.nodeType === 1) t += shadowText(c);
        }
        return t;
    }
    const body = shadowText(document.body);
    const result = {};
    const det = body.match(/(\d+\s*\/?\s*\d*\s*security vendors?.*?malicious|No security vendors flagged this file as malicious)/i);
    if (det) result.detection = det[0].trim();
    const fname = body.match(/([\w.-]+\.zip|[\w.-]+\.tar\.gz)\s+Size\s+([\d.]+\s*[KMG]B)/i);
    if (fname) result.fileInfo = fname[0].trim();
    const ciIdx = body.indexOf('Code insights');
    if (ciIdx >= 0) {
        let ciText = body.substring(ciIdx + 'Code insights'.length);
        ciText = ciText.replace(/^\s*Show (?:more|less)\s*/i, '');
        const svIdx = ciText.indexOf('Security vendors');
        if (svIdx > 0) ciText = ciText.substring(0, svIdx);
        ciText = ciText.trim();
        if (ciText.length > 20) result.codeInsights = ciText;
    }
    return result;
}
""")
        sections_fb: list[str] = []
        if structured:
            if structured.get("detection"):
                sections_fb.append(f"Detection: {structured['detection']}")
            if structured.get("fileInfo"):
                sections_fb.append(f"File: {structured['fileInfo']}")
            if structured.get("codeInsights"):
                sections_fb.append(f"Code insights: {structured['codeInsights']}")
        result_text = "\n".join(sections_fb) if sections_fb else None
        if result_text:
            _vt_cache_store(file_hash, result_text)
        return result_text

    except Exception as e:
        return f"(VT scrape error: {e})"


def _extract_security_dom(page: Any) -> dict[str, Any] | None:
    """Extract security scan data from the rendered DOM.

    Returns None if the scan panel isn't present (e.g. page layout changed or gated).
    """

    js = r"""
() => {
  const panel = document.querySelector('.scan-results-panel');
  if (!panel) return null;

  const rows = Array.from(panel.querySelectorAll('.scan-result-row'));

  function pickRow(name) {
    for (const r of rows) {
      const n = r.querySelector('.scan-result-scanner-name')?.innerText?.trim();
      if (n === name) return r;
    }
    return null;
  }

  const vtRow = pickRow('VirusTotal');
  const ocRow = pickRow('OpenClaw');

  const vtStatus = vtRow?.querySelector('.scan-result-status')?.innerText?.trim() || null;
  const vtLink = vtRow?.querySelector('a.scan-result-link')?.href || null;

  const ocStatus = ocRow?.querySelector('.scan-result-status')?.innerText?.trim() || null;
  const ocConf = ocRow?.querySelector('.scan-result-confidence')?.innerText?.trim() || null;

  const detail = panel.querySelector('.analysis-detail');
  const summary = detail?.querySelector('.analysis-summary-text')?.innerText?.trim() || null;

  // Expand details if collapsed
  const header = detail?.querySelector('.analysis-detail-header');
  if (header) {
    try { header.click(); } catch (e) {}
  }

  const dims = [];
  const dimRows = Array.from(detail?.querySelectorAll('.dimension-row') || []);
  for (const r of dimRows) {
    const label = r.querySelector('.dimension-label')?.innerText?.trim() || null;
    const body = r.querySelector('.dimension-detail')?.innerText?.trim() || null;
    if (label || body) dims.push({ label, detail: body });
  }

  const guidance = detail?.querySelector('.analysis-guidance')?.innerText?.trim() || null;

  return { vtStatus, vtLink, ocStatus, ocConf, summary, dimensions: dims, guidance };
}
"""

    try:
        return page.evaluate(js)
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Scrape ClawHub Security Scan for local skills")
    ap.add_argument("--owner", default="odrobnik", help="ClawHub owner/handle")
    ap.add_argument("--skills-dir", default=str(Path.home() / "Developer" / "Skills"), help="Folder containing local skills")
    ap.add_argument("--out", default=None, help="Output markdown path (default: /tmp/clawhub-skill-review-YYYY-MM-DD.md)")
    ap.add_argument("--slug-map", default=None, help="Optional JSON mapping of local slug->ClawHub slug")
    ap.add_argument("--only", default=None, help="Only scrape a single slug (after slug-map), e.g. tesla-fleet-api")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of skills (0=all)")
    ap.add_argument("--headful", action="store_true", help="Run browser non-headless")
    ap.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    ap.add_argument("--suppressions", default=None, help="Path to suppressions.json (auto-detected if not set)")

    args = ap.parse_args()

    skills_dir = Path(args.skills_dir).expanduser().resolve()
    if not skills_dir.exists():
        raise SystemExit(f"skills-dir not found: {skills_dir}")

    out_path = Path(args.out) if args.out else Path(f"/tmp/clawhub-skill-review-{dt.date.today().isoformat()}.md")

    slug_map = _load_slug_map(args.slug_map)
    suppressions = _load_suppressions(args.suppressions)
    if suppressions:
        sys.stderr.write(f"Loaded suppressions for {len(suppressions)} skill(s)\n")


    local_skills = _find_local_skills(skills_dir)

    # Apply slug map early so --only matches what we'll scrape.
    mapped_skills: list[LocalSkill] = []
    for s in local_skills:
        mapped_skills.append(LocalSkill(path=s.path, slug=slug_map.get(s.slug, s.slug), local_version=s.local_version, homepage=s.homepage))
    local_skills = mapped_skills

    if args.only:
        local_skills = [s for s in local_skills if s.slug == args.only]

    if args.limit and args.limit > 0:
        local_skills = local_skills[: args.limit]

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        raise SystemExit(
            "Playwright not installed. Run:\n"
            "  python3 -m pip install playwright\n"
            "  python3 -m playwright install chromium\n"
        )

    vt_api_key = _load_vt_api_key()
    if vt_api_key:
        sys.stderr.write("Using VirusTotal API (key loaded)\n")
    else:
        sys.stderr.write("No VIRUSTOTAL_API_KEY — falling back to Playwright scraping for VT\n")

    rows: list[dict[str, Any]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headful)
        page = browser.new_page()

        for s in local_skills:
            slug = s.slug
            url = f"https://clawhub.ai/{args.owner}/{slug}"
            sys.stderr.write(f"Scraping {slug}…\n")
            sys.stderr.flush()

            try:
                # ClawHub renders the scan panel client-side; wait for JS to finish.
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_selector("main", timeout=20000)
                # Prefer to wait for the scan panel; if it's missing, we'll fall back to text parsing.
                try:
                    page.wait_for_selector(".scan-results-panel", timeout=20000)
                except Exception:
                    pass

                # Expand any Details dropdowns.
                try:
                    page.evaluate(
                        """() => {
                            const btns = Array.from(document.querySelectorAll('button'));
                            for (const b of btns) {
                              const t = (b.innerText || '').trim();
                              if (t.includes('Details') && t.includes('▾')) {
                                try { b.click(); } catch (e) {}
                              }
                            }
                        }"""
                    )
                except Exception:
                    pass

                time.sleep(0.15)

                main_el = page.query_selector("main")
                text = main_el.inner_text() if main_el else page.content()

                parsed = _parse_page_text(text)
                sec = parsed.get("security") or {}

                # Prefer DOM extraction (more reliable than parsing text blobs)
                dom_sec = _extract_security_dom(page)
                if dom_sec:
                    sec["domOk"] = True
                    sec.update(
                        {
                            "vtStatus": dom_sec.get("vtStatus") or sec.get("vtStatus"),
                            "vtLink": dom_sec.get("vtLink") or sec.get("vtLink"),
                            "ocStatus": dom_sec.get("ocStatus") or sec.get("ocStatus"),
                            "ocConf": dom_sec.get("ocConf") or sec.get("ocConf"),
                            "summary": dom_sec.get("summary"),
                            "dimensions": dom_sec.get("dimensions"),
                            "guidance": dom_sec.get("guidance"),
                        }
                    )
                else:
                    sec["domOk"] = False
                    # Fallback: try to locate VT report link
                    try:
                        a = page.query_selector("a[href*='virustotal.com/gui/file/']")
                        if a:
                            sec["vtLink"] = a.get_attribute("href")
                    except Exception:
                        pass

                # Scrape VirusTotal analysis if we have a link
                vt_analysis = None
                vt_link = sec.get("vtLink")
                if vt_link:
                    sys.stderr.write(f"  ↳ Fetching VirusTotal for {slug}…\n")
                    sys.stderr.flush()
                    try:
                        vt_analysis = _scrape_virustotal(page, vt_link, api_key=vt_api_key)
                    except _VTQuotaExhausted:
                        # Disable API for remaining skills, fall back to scraping
                        vt_api_key = None
                        vt_analysis = _scrape_virustotal(page, vt_link, api_key=None)
                # Handle structured return from API (dict) vs plain text from scraping
                ci_verdict = None
                if isinstance(vt_analysis, dict):
                    ci_verdict = vt_analysis.get("codeInsightsVerdict")
                    vt_analysis = vt_analysis.get("text")
                sec["vtAnalysis"] = vt_analysis
                sec["codeInsightsVerdict"] = ci_verdict

                rows.append(
                    {
                        "slug": slug,
                        "url": url,
                        "localVersion": s.local_version,
                        "pageVersion": parsed.get("version"),
                        "homepage": s.homepage,
                        "security": sec,
                        "runtime": parsed.get("runtime"),
                        "comments": parsed.get("comments"),
                    }
                )
            except Exception as e:
                rows.append({"slug": slug, "url": url, "homepage": s.homepage, "error": str(e)})

        browser.close()

    # JSON mode — output structured data and exit
    if args.json:
        out_obj = {
            "owner": args.owner,
            "generated": dt.datetime.now().isoformat(timespec="seconds"),
            "skills": [],
        }
        for r in rows:
            skill_obj: dict[str, Any] = {
                "slug": r.get("slug"),
                "url": r.get("url"),
                "homepage": r.get("homepage"),
                "localVersion": r.get("localVersion"),
                "clawHubVersion": r.get("pageVersion"),
            }
            if r.get("error"):
                skill_obj["error"] = r["error"]
            else:
                sec = r.get("security") or {}
                vt_st = sec.get("vtStatus")
                oc_st = sec.get("ocStatus")

                # Upgrade VT status based on Code Insights verdict
                # If CI says "suspicious" but VT engines show Pending/Benign,
                # elevate to "Suspicious" so it's visible on the dashboard
                ci_verdict = sec.get("codeInsightsVerdict")
                if ci_verdict and ci_verdict.lower() == "suspicious":
                    if vt_st in (None, "Pending", "Benign"):
                        vt_st = "Suspicious"

                vt_st, oc_st, applied = _apply_suppressions(
                    r.get("slug", ""), vt_st, oc_st, suppressions,
                    vt_analysis=sec.get("vtAnalysis"),
                    oc_summary=sec.get("summary"),
                    oc_guidance=sec.get("guidance"),
                )
                skill_obj["virustotal"] = {
                    "status": vt_st,
                    "link": sec.get("vtLink"),
                    "analysis": sec.get("vtAnalysis"),
                    "codeInsightsVerdict": ci_verdict,
                }
                skill_obj["openclaw"] = {
                    "status": oc_st,
                    "confidence": sec.get("ocConf"),
                    "summary": sec.get("summary"),
                    "dimensions": sec.get("dimensions"),
                    "guidance": sec.get("guidance"),
                }
                if applied:
                    skill_obj["suppressions"] = applied
                skill_obj["runtime"] = r.get("runtime")
                skill_obj["comments"] = r.get("comments")
            out_obj["skills"].append(skill_obj)

        json_str = json.dumps(out_obj, ensure_ascii=False, indent=2)
        if args.out:
            out_path.write_text(json_str + "\n", encoding="utf-8")
            print(str(out_path))
        else:
            print(json_str)
        return

    # Write markdown
    lines: list[str] = []
    lines.append(f"# ClawHub Skill Review — {args.owner}")
    lines.append("")
    lines.append(f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    lines.append("## Index")
    lines.append("")
    lines.append("| Slug | Local | ClawHub | VirusTotal | OpenClaw | Confidence | VT link |")
    lines.append("|---|---:|---:|---|---|---|---|")

    for r in rows:
        if r.get("error"):
            lines.append(f"| {_md_escape(r['slug'])} |  |  | ERROR |  |  |  |");
            continue
        sec = r.get("security") or {}
        vt_st = sec.get("vtStatus") or ""
        oc_st = sec.get("ocStatus") or ""
        vt_st, oc_st, _ = _apply_suppressions(
            r.get("slug", ""), vt_st, oc_st, suppressions,
            vt_analysis=sec.get("vtAnalysis"),
            oc_summary=sec.get("summary"),
            oc_guidance=sec.get("guidance"),
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_escape(r.get("slug", "")),
                    _md_escape(r.get("localVersion") or ""),
                    _md_escape(r.get("pageVersion") or ""),
                    _md_escape(vt_st or ""),
                    _md_escape(oc_st or ""),
                    _md_escape(sec.get("ocConf") or ""),
                    sec.get("vtLink") or "",
                ]
            )
            + " |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Details")
    lines.append("")

    for r in rows:
        lines.append(f"### {r.get('slug')}")
        lines.append(f"URL: {r.get('url')}")
        if r.get("homepage"):
            lines.append(f"Homepage: {r['homepage']}")
        if r.get("error"):
            lines.append("")
            lines.append(f"**Error:** `{r['error']}`")
            lines.append("")
            lines.append("---")
            lines.append("")
            continue

        lines.append("")
        lines.append(f"Local version: `{r.get('localVersion')}`")
        lines.append(f"ClawHub version: `{r.get('pageVersion')}`")
        lines.append("")

        sec = r.get("security") or {}
        lines.append("**Security Scan:**")
        lines.append("")
        lines.append(f"- VirusTotal: {sec.get('vtStatus') or '—'}")
        if sec.get("vtLink"):
            lines.append(f"  - {sec.get('vtLink')}")
        if sec.get("vtAnalysis"):
            lines.append("")
            lines.append("**VirusTotal analysis:**")
            lines.append("```text")
            lines.append(str(sec["vtAnalysis"]).strip())
            lines.append("```")
            lines.append("")
        lines.append(f"- OpenClaw: {sec.get('ocStatus') or '—'} ({sec.get('ocConf') or '—'})")
        if sec.get("summary"):
            lines.append(f"- Summary: {sec.get('summary')}")

        if sec.get("dimensions"):
            lines.append("")
            lines.append("**OpenClaw analysis dimensions:**")
            for d in sec.get("dimensions") or []:
                label = d.get("label") or "(unknown)"
                detail = d.get("detail") or ""
                lines.append(f"- {label}: {detail}")

        if sec.get("guidance"):
            lines.append("")
            lines.append("**OpenClaw guidance:**")
            lines.append("```text")
            lines.append(str(sec.get("guidance")).strip())
            lines.append("```")

        # Only include raw text fallback when DOM extraction failed (avoids duplicate content).
        if not sec.get("domOk"):
            lines.append("")
            lines.append("**Security Scan (raw text fallback):**")
            lines.append("```text")
            lines.append((sec.get("raw") or "(missing)").strip())
            lines.append("```")

        lines.append("")
        lines.append("**Runtime requirements (as shown):**")
        lines.append("```text")
        rt = r.get("runtime")
        lines.append("\n".join(rt) if rt else "(none shown)")
        lines.append("```")

        lines.append("")
        lines.append("**Comments (as shown):**")
        lines.append("```text")
        c = r.get("comments")
        lines.append("\n".join(c) if c else "(none shown)")
        lines.append("```")

        lines.append("")
        lines.append("---")
        lines.append("")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
