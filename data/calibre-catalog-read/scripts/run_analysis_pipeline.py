#!/usr/bin/env -S uv run python
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, subprocess, tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent


def run(cmd: list[str]) -> str:
    cp = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if cp.returncode != 0:
        raise RuntimeError(f"cmd failed ({cp.returncode}): {' '.join(cmd)}\n{cp.stderr}")
    return cp.stdout


def extract_text(epub: Path, out_txt: Path) -> None:
    run(["ebook-convert", str(epub), str(out_txt)])


def simple_analysis(text: str, lang: str) -> dict:
    """Fallback local analysis.

    Keep this language-neutral and lightweight.
    Preferred path is subagent-generated analysis passed via --analysis-json,
    where language is controlled by user-selected subagent prompt/settings.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    body = "\n".join(lines)
    head = body[:12000]

    summary = "Auto analysis from opening sections with reread anchors."
    highlights = [
        "Extract key points from opening content.",
        "Preserve reread guidance for quick return to source.",
        "Persist structure suitable for metadata HTML embedding.",
    ]
    reread = [{"section": "opening", "page": "EPUB-loc", "chunk_id": "auto-intro", "reason": "context refresh"}]

    kws = []
    for kw in ["chapter", "contents", "summary", "introduction", "data", "design", "history", "pirate", "AI", "Python"]:
        if kw.lower() in head.lower():
            kws.append(kw)
    if kws:
        highlights.append("Detected keywords: " + ", ".join(kws[:6]))
    return {"summary": summary, "highlights": highlights[:5], "reread": reread}


OC_START = "<!-- OC_ANALYSIS_START -->"
OC_END = "<!-- OC_ANALYSIS_END -->"

I18N = {
    "ja": {
        "title": "OpenClaw解析",
        "summary": "要約",
        "key_points": "重要ポイント",
        "reread": "再読ガイド",
        "generated_at": "生成日時",
        "file_hash": "ファイルハッシュ",
        "analysis_tags": "解析タグ",
        "section": "章/節",
        "page": "ページ",
        "chunk": "チャンク",
    },
    "en": {
        "title": "OpenClaw Analysis",
        "summary": "Summary",
        "key_points": "Key points",
        "reread": "Reread guide",
        "generated_at": "generated_at",
        "file_hash": "file_hash",
        "analysis_tags": "analysis_tags",
        "section": "section",
        "page": "page",
        "chunk": "chunk",
    },
}


def split_multi(v):
    if v is None:
        return []
    if isinstance(v, list):
        raw = [str(x) for x in v]
    else:
        raw = re.split(r"[,;\n]", str(v))
    out, seen = [], set()
    for x in raw:
        t = x.strip()
        if not t:
            continue
        k = t.casefold()
        if k in seen:
            continue
        seen.add(k)
        out.append(t)
    return out


def render_analysis_html(analysis: dict, default_lang: str = "ja") -> str:
    summary = str(analysis.get("summary", "")).strip()
    highlights = split_multi(analysis.get("highlights", []))
    tags = split_multi(analysis.get("tags", []))
    reread = analysis.get("reread", [])
    generated_at = str(analysis.get("generated_at", "")).strip() or dt.datetime.now(dt.timezone.utc).isoformat()
    source_hash = str(analysis.get("file_hash", "")).strip()

    lang = str(analysis.get("lang", default_lang)).strip().lower()
    if lang not in I18N:
        lang = default_lang if default_lang in I18N else "en"
    tr = I18N[lang]

    lines = [OC_START, '<div class="openclaw-analysis">', f"<h3>{tr['title']}</h3>"]
    if summary:
        lines.append(f"<p><strong>{tr['summary']}:</strong> {summary}</p>")
    if highlights:
        lines.append(f"<h4>{tr['key_points']}</h4><ul>")
        for h in highlights:
            lines.append(f"<li>{h}</li>")
        lines.append("</ul>")
    if reread and isinstance(reread, list):
        lines.append(f"<h4>{tr['reread']}</h4><ul>")
        for item in reread:
            if not isinstance(item, dict):
                continue
            section = str(item.get("section", "")).strip()
            page = str(item.get("page", "")).strip()
            chunk = str(item.get("chunk_id", "")).strip()
            reason = str(item.get("reason", "")).strip()
            parts = [
                p for p in [
                    f"{tr['section']}: {section}" if section else "",
                    f"{tr['page']}: {page}" if page else "",
                    f"{tr['chunk']}: {chunk}" if chunk else "",
                    reason,
                ] if p
            ]
            if parts:
                lines.append(f"<li>{' | '.join(parts)}</li>")
        lines.append("</ul>")

    meta_bits = [f"{tr['generated_at']}: {generated_at}"]
    if source_hash:
        meta_bits.append(f"{tr['file_hash']}: {source_hash}")
    if tags:
        meta_bits.append(f"{tr['analysis_tags']}: {', '.join(tags)}")
    lines.append(f"<p><em>{' / '.join(meta_bits)}</em></p>")
    lines.append("</div>")
    lines.append(OC_END)
    return "\n".join(lines)


def upsert_oc_block(existing_html: str, oc_block_html: str) -> str:
    existing = existing_html or ""
    pattern = re.compile(re.escape(OC_START) + r".*?" + re.escape(OC_END), re.DOTALL)
    if pattern.search(existing):
        return pattern.sub(oc_block_html, existing)
    if existing.strip():
        return existing.rstrip() + "\n\n" + oc_block_html
    return oc_block_html


def is_excluded_content(meta: dict) -> tuple[bool, str]:
    title = str(meta.get("title") or "").lower()
    tags = [str(t).lower() for t in (meta.get("tags") or [])]
    manga_keys = ["漫画", "コミック", "マンガ", "comic", "manga", "graphic novel"]
    for k in manga_keys:
        if k in title:
            return True, f"title matched excluded keyword: {k}"
        if any(k in t for t in tags):
            return True, f"tag matched excluded keyword: {k}"
    return False, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-library", required=True)
    ap.add_argument("--book-id", required=True, type=int)
    ap.add_argument("--db", default=str(SKILL_ROOT / "state" / "calibre_analysis.sqlite"))
    ap.add_argument("--username", default=os.environ.get("CALIBRE_USERNAME", ""))
    ap.add_argument("--password-env", default="CALIBRE_PASSWORD")
    ap.add_argument("--format", default="EPUB")
    ap.add_argument("--lang", default="ja", choices=["ja", "en"])
    ap.add_argument("--cache-dir", default=str(SKILL_ROOT / "state" / "cache" / "pipeline"))
    ap.add_argument("--analysis-json", help="Optional path to subagent-produced analysis JSON (schema in references/subagent-analysis.schema.json)")
    ap.add_argument("--min-text-chars", type=int, default=1200, help="Minimum extracted text chars before proceeding without confirmation")
    ap.add_argument("--force-low-text", action="store_true", help="Proceed even when extracted text is below threshold")
    ns = ap.parse_args()

    pw = os.environ.get(ns.password_env, "")
    auth = []
    if ns.username:
        auth += ["--username", ns.username]
    if pw:
        auth += ["--password", pw]

    cdir = Path(ns.cache_dir) / str(ns.book_id)
    cdir.mkdir(parents=True, exist_ok=True)

    # metadata
    rows = json.loads(run(["calibredb", "--with-library", ns.with_library, *auth, "list", "--for-machine", "--search", f"id:{ns.book_id}", "--fields", "id,title,tags,formats", "--limit", "2"]))
    if not rows:
        raise SystemExit("book not found")
    title = rows[0].get("title", "")

    excluded, reason = is_excluded_content(rows[0])
    if excluded:
        print(json.dumps({"ok": True, "skipped": True, "reason": "excluded_content", "detail": reason, "book_id": ns.book_id, "title": title}, ensure_ascii=False))
        return

    # export and hash
    run(["calibredb", "--with-library", ns.with_library, *auth, "export", str(ns.book_id), "--to-dir", str(cdir), "--single-dir", "--formats", ns.format, "--dont-write-opf", "--dont-save-cover", "--dont-save-extra-files", "--replace-whitespace"])
    exts = list(cdir.glob(f"*.{ns.format.lower()}"))
    if not exts:
        raise SystemExit(f"no exported {ns.format}")
    src = exts[0]
    fhash = "sha256:" + hashlib.sha256(src.read_bytes()).hexdigest()

    # status check
    st = json.loads(run(["uv", "run", "python", str(SCRIPT_DIR / "analysis_db.py"), "status", "--db", ns.db, "--book-id", str(ns.book_id), "--format", ns.format]))
    if st.get("status") and st["status"].get("file_hash") == fhash:
        print(json.dumps({"ok": True, "skipped": True, "reason": "same_hash", "book_id": ns.book_id, "file_hash": fhash}, ensure_ascii=False))
        return

    txt = cdir / f"book_{ns.book_id}.txt"
    extract_text(src, txt)

    extracted = txt.read_text(errors="ignore")
    text_chars = len("".join(ch for ch in extracted if not ch.isspace()))
    if (not ns.analysis_json) and (not ns.force_low_text) and text_chars < ns.min_text_chars:
        print(json.dumps({
            "ok": True,
            "skipped": True,
            "reason": "low_text_requires_confirmation",
            "book_id": ns.book_id,
            "title": title,
            "text_chars": text_chars,
            "min_text_chars": ns.min_text_chars,
            "prompt_en": "Extracted text is very short, likely image/comic-heavy. Summary quality may be poor. Continue anyway?"
        }, ensure_ascii=False))
        return

    if ns.analysis_json:
        analysis_core = json.loads(Path(ns.analysis_json).read_text())
    else:
        analysis_core = simple_analysis(extracted, ns.lang)

    record = {
        "book_id": ns.book_id,
        "library_id": ns.with_library.split("#", 1)[-1],
        "title": title,
        "format": ns.format,
        "file_hash": fhash,
        "lang": ns.lang,
        "summary": analysis_core["summary"],
        "highlights": analysis_core["highlights"],
        "reread": analysis_core["reread"],
        "tags": ["ai-summary", "cached-analysis"],
    }

    # upsert cache record
    subprocess.run(["uv", "run", "python", str(SCRIPT_DIR / "analysis_db.py"), "upsert", "--db", ns.db],
                   input=json.dumps(record, ensure_ascii=False), text=True, check=True)

    # Apply comments update directly here to keep this skill independent.
    current = json.loads(run([
        "calibredb", "--with-library", ns.with_library, *auth,
        "list", "--for-machine", "--search", f"id:{ns.book_id}",
        "--fields", "id,comments", "--limit", "2",
    ]))
    existing_comments = ""
    if current:
        existing_comments = str(current[0].get("comments") or "")

    analysis_for_html = {
        "lang": ns.lang,
        "summary": record["summary"],
        "highlights": record["highlights"],
        "reread": record["reread"],
        "tags": record["tags"],
        "file_hash": fhash,
    }
    oc_block = render_analysis_html(analysis_for_html, default_lang=ns.lang)
    merged_comments = upsert_oc_block(existing_comments, oc_block)

    run([
        "calibredb", "--with-library", ns.with_library, *auth,
        "set_metadata", str(ns.book_id),
        "--field", f"comments:{merged_comments}",
    ])

    print(json.dumps({"ok": True, "book_id": ns.book_id, "title": title, "file_hash": fhash, "updated": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
