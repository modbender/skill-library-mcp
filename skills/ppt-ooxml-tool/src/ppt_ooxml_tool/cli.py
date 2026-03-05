#!/usr/bin/env python3
"""Reusable OOXML text workflow tool for unpacked PPTX directories.

Subcommands:
- help: print bilingual usage guide with input/output path expectations
- unpack: extract .pptx to unpacked OOXML directory
- collect: export all <a:t> text runs to TSV with stable IDs
- apply: apply translated TSV back into XML text runs by ID
- normalize: enforce glossary replacements in <a:t> and set typeface (auto by language)
- validate: XML parse check and optional font consistency check
- repack: create .pptx from unpacked OOXML folder
- workflow: one-shot pipeline for agent/tool integrations
- runfile: execute JSON job spec (tool-agnostic entrypoint)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from zipfile import ZIP_DEFLATED, ZipFile

A_TEXT_RE = re.compile(r"<a:t>(.*?)</a:t>", re.DOTALL)
TYPEFACE_RE = re.compile(r'typeface="[^"]*"')

LANG_FONT_PRESETS: Dict[str, str] = {
    # Mainstream language defaults for Office/PPT compatibility.
    "en": "Calibri",
    "ja": "Yu Gothic",
    "zh-cn": "Microsoft YaHei",
    "zh-tw": "Microsoft JhengHei",
    "ko": "Malgun Gothic",
    "ar": "Tahoma",
}

HELP_TEXT_EN = """[PPT OOXML Translator] Usage Guide

1) Input paths
- Packed mode (.pptx): provide an absolute or relative path, e.g. /data/in.pptx or ./in.pptx
- Unpacked mode: provide OOXML root directory containing [Content_Types].xml and ppt/

2) Typical workflow
- unpack:  .pptx -> unpacked folder
- collect: unpacked folder -> translation TSV
- apply:   translation TSV -> updated XML text
- normalize: glossary + font by language preset
- validate: XML parse + font consistency
- repack: updated unpacked folder -> output .pptx

3) Output locations (defaults)
- translation TSV: <unpacked_root>/translation.<lang>.tsv
- repacked PPTX:   <unpacked_root>.out.pptx (or user --output path)

4) Language font presets
- en: Calibri
- ja: Yu Gothic
- zh-cn: Microsoft YaHei
- zh-tw: Microsoft JhengHei
- ko: Malgun Gothic
- ar: Tahoma

5) Example commands
- unpack:
  python3 ppt_ooxml_tool.py unpack --input ./input.pptx --output ./unpacked
- collect:
  python3 ppt_ooxml_tool.py collect --root ./unpacked --include slides,notes --output ./translation.ja.tsv
- apply:
  python3 ppt_ooxml_tool.py apply --root ./unpacked --tsv ./translation.ja.tsv
- normalize:
  python3 ppt_ooxml_tool.py normalize --root ./unpacked --include slides,notes,masters --lang ja --glossary ./glossary.json
- validate:
  python3 ppt_ooxml_tool.py validate --root ./unpacked --include slides,notes,masters --lang ja
- repack:
  python3 ppt_ooxml_tool.py repack --root ./unpacked --output ./output.ja.pptx

6) Interop-friendly modes
- Add --json to any command for machine-readable output
- Use workflow for single-command automation
- Use runfile with a JSON job spec for generic tool adapters
"""

HELP_TEXT_ZH = """【PPT OOXML 翻译工具】使用说明

1）输入路径
- 压缩包模式（.pptx）：传入绝对路径或相对路径，例如 /data/in.pptx 或 ./in.pptx
- 已解压模式：传入包含 [Content_Types].xml 和 ppt/ 的 OOXML 根目录

2）标准流程
- unpack：  .pptx -> 解压目录
- collect： 解压目录 -> 翻译 TSV
- apply：   翻译 TSV -> 写回 XML 文本
- normalize：按术语表+语言预设统一字体
- validate：校验 XML 可解析 + 字体一致性
- repack：  解压目录 -> 输出 .pptx

3）输出位置（默认）
- 翻译 TSV：<unpacked_root>/translation.<lang>.tsv
- 回包 PPTX：<unpacked_root>.out.pptx（或你传入的 --output）

4）语言字体预设
- en: Calibri
- ja: Yu Gothic
- zh-cn: Microsoft YaHei
- zh-tw: Microsoft JhengHei
- ko: Malgun Gothic
- ar: Tahoma

5）命令示例
- 解压：
  python3 ppt_ooxml_tool.py unpack --input ./input.pptx --output ./unpacked
- 抽取：
  python3 ppt_ooxml_tool.py collect --root ./unpacked --include slides,notes --output ./translation.ja.tsv
- 写回：
  python3 ppt_ooxml_tool.py apply --root ./unpacked --tsv ./translation.ja.tsv
- 规范化：
  python3 ppt_ooxml_tool.py normalize --root ./unpacked --include slides,notes,masters --lang ja --glossary ./glossary.json
- 校验：
  python3 ppt_ooxml_tool.py validate --root ./unpacked --include slides,notes,masters --lang ja
- 回包：
  python3 ppt_ooxml_tool.py repack --root ./unpacked --output ./output.ja.pptx

6）跨工具兼容模式
- 所有命令可加 --json，输出机器可读结果
- workflow 支持单命令流水线
- runfile 支持 JSON 任务清单，便于外部代理接入
"""


def xml_escape_text(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def iter_target_files(root: Path, include: str) -> Iterable[Path]:
    include_set = {x.strip() for x in include.split(",") if x.strip()}
    if "slides" in include_set:
        for p in sorted((root / "ppt" / "slides").glob("slide*.xml")):
            if p.is_file():
                yield p
    if "notes" in include_set:
        notes_dir = root / "ppt" / "notesSlides"
        if notes_dir.exists():
            for p in sorted(notes_dir.glob("notesSlide*.xml")):
                if p.is_file():
                    yield p
    if "masters" in include_set:
        for base, pattern in [
            (root / "ppt" / "slideMasters", "slideMaster*.xml"),
            (root / "ppt" / "slideLayouts", "slideLayout*.xml"),
        ]:
            if base.exists():
                for p in sorted(base.glob(pattern)):
                    if p.is_file():
                        yield p


def normalize_lang_code(lang: str) -> str:
    return lang.strip().lower().replace("_", "-")


def resolve_font(font: str | None, lang: str | None) -> str:
    if font:
        return font
    if lang:
        key = normalize_lang_code(lang)
        if key in LANG_FONT_PRESETS:
            return LANG_FONT_PRESETS[key]
    return "Calibri"


def unpack(input_pptx: Path, output_root: Path) -> int:
    if not input_pptx.exists():
        raise FileNotFoundError(f"Input .pptx not found: {input_pptx}")
    output_root.mkdir(parents=True, exist_ok=True)
    with ZipFile(input_pptx, "r") as zf:
        zf.extractall(output_root)
        return len(zf.infolist())


@dataclass
class TextRow:
    row_id: str
    file: str
    seq: int
    source: str
    target: str
    notes: str


def collect_rows(root: Path, include: str) -> List[TextRow]:
    rows: List[TextRow] = []
    for f in iter_target_files(root, include):
        rel = f.relative_to(root).as_posix()
        content = f.read_text(encoding="utf-8")
        seq = 0
        for m in A_TEXT_RE.finditer(content):
            seq += 1
            src = m.group(1)
            row_id = f"{rel}#{seq}"
            rows.append(TextRow(row_id=row_id, file=rel, seq=seq, source=src, target="", notes=""))
    return rows


def write_tsv(rows: List[TextRow], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fp:
        w = csv.writer(fp, dialect="excel-tab", quoting=csv.QUOTE_MINIMAL)
        w.writerow(["id", "file", "seq", "source", "target", "notes"])
        for r in rows:
            w.writerow([r.row_id, r.file, r.seq, r.source, r.target, r.notes])


def read_tsv(tsv_path: Path) -> List[Dict[str, str]]:
    with tsv_path.open("r", encoding="utf-8", newline="") as fp:
        r = csv.DictReader(fp, dialect="excel-tab")
        required = {"id", "file", "seq", "source", "target"}
        missing = required - set(r.fieldnames or [])
        if missing:
            raise ValueError(f"TSV missing required headers: {sorted(missing)}")
        return list(r)


def apply_translations(root: Path, tsv_path: Path) -> Tuple[int, int]:
    rows = read_tsv(tsv_path)
    by_file_seq: Dict[Tuple[str, int], str] = {}
    for row in rows:
        file_rel = row["file"].strip()
        seq = int(row["seq"])
        target = row.get("target", "")
        if target is None or target == "":
            continue
        by_file_seq[(file_rel, seq)] = target

    file_to_rows: Dict[str, List[int]] = {}
    for file_rel, seq in by_file_seq:
        file_to_rows.setdefault(file_rel, []).append(seq)

    files_changed = 0
    texts_changed = 0

    for file_rel, seqs in file_to_rows.items():
        path = root / file_rel
        if not path.exists():
            raise FileNotFoundError(f"Missing XML file from TSV: {file_rel}")

        content = path.read_text(encoding="utf-8")
        matches = list(A_TEXT_RE.finditer(content))
        max_seq = len(matches)

        for seq in seqs:
            if seq < 1 or seq > max_seq:
                raise IndexError(f"Sequence out of range for {file_rel}: {seq} > {max_seq}")

        out: List[str] = []
        last = 0
        changed_this_file = 0

        for i, m in enumerate(matches, start=1):
            out.append(content[last : m.start(1)])
            key = (file_rel, i)
            if key in by_file_seq:
                original = m.group(1)
                translated = by_file_seq[key]
                escaped = xml_escape_text(translated)
                out.append(escaped)
                if escaped != original:
                    changed_this_file += 1
            else:
                out.append(m.group(1))
            last = m.end(1)

        out.append(content[last:])

        if changed_this_file > 0:
            path.write_text("".join(out), encoding="utf-8")
            files_changed += 1
            texts_changed += changed_this_file

    return files_changed, texts_changed


def normalize(
    root: Path,
    include: str,
    font: str | None,
    lang: str | None,
    glossary_json: Path | None,
) -> Tuple[int, int, int, str]:
    glossary: Dict[str, str] = {}
    if glossary_json:
        glossary = json.loads(glossary_json.read_text(encoding="utf-8"))
        if not isinstance(glossary, dict):
            raise ValueError("Glossary JSON must be an object: {\"from\": \"to\"}")

    files_changed = 0
    text_replacements = 0
    font_replacements = 0
    resolved_font = resolve_font(font, lang)

    for f in iter_target_files(root, include):
        content = f.read_text(encoding="utf-8")

        def repl_text(m: re.Match[str]) -> str:
            nonlocal text_replacements
            text = m.group(1)
            new_text = text
            for src, dst in glossary.items():
                new_text = new_text.replace(src, dst)
            if new_text != text:
                text_replacements += 1
            return f"<a:t>{xml_escape_text(new_text)}</a:t>"

        new_content = A_TEXT_RE.sub(repl_text, content)

        before_fonts = len(TYPEFACE_RE.findall(new_content))
        new_content2 = TYPEFACE_RE.sub(f'typeface="{resolved_font}"', new_content)
        if before_fonts:
            font_replacements += before_fonts

        if new_content2 != content:
            f.write_text(new_content2, encoding="utf-8")
            files_changed += 1

    return files_changed, text_replacements, font_replacements, resolved_font


def validate(
    root: Path,
    include: str,
    expected_font: str | None,
    lang: str | None,
) -> Tuple[int, int, str | None]:
    xml_count = 0
    font_issues = 0
    resolved_expected = resolve_font(expected_font, lang) if (expected_font or lang) else None

    for f in iter_target_files(root, include):
        xml_count += 1
        ET.parse(f)
        if resolved_expected:
            content = f.read_text(encoding="utf-8")
            bad = re.search(rf'typeface="(?!{re.escape(resolved_expected)}\b)[^"]+"', content)
            if bad:
                font_issues += 1

    return xml_count, font_issues, resolved_expected


def repack(unpacked_root: Path, output_pptx: Path) -> int:
    files = [p for p in unpacked_root.rglob("*") if p.is_file()]
    with ZipFile(output_pptx, "w", compression=ZIP_DEFLATED) as zf:
        for p in files:
            rel = p.relative_to(unpacked_root)
            if any(part == "__MACOSX" for part in rel.parts):
                continue
            if rel.name == ".DS_Store":
                continue
            zf.write(p, arcname=rel.as_posix())
    return len(files)


def run_workflow(
    *,
    input_pptx: Path | None,
    root: Path,
    include: str,
    tsv: Path,
    lang: str | None,
    font: str | None,
    glossary: Path | None,
    output_pptx: Path,
) -> Dict[str, object]:
    result: Dict[str, object] = {
        "input_pptx": str(input_pptx) if input_pptx else None,
        "root": str(root),
        "include": include,
        "tsv": str(tsv),
        "output_pptx": str(output_pptx),
    }

    if input_pptx is not None:
        unpacked = unpack(input_pptx, root)
        result["unpacked_entries"] = unpacked

    rows = collect_rows(root, include)
    write_tsv(rows, tsv)
    result["collected_rows"] = len(rows)

    files_changed, texts_changed = apply_translations(root, tsv)
    result["applied"] = {"files_changed": files_changed, "texts_changed": texts_changed}

    n_files, n_text, n_font, resolved_font = normalize(root, include, font, lang, glossary)
    result["normalized"] = {
        "files_changed": n_files,
        "text_replacements": n_text,
        "font_assignments": n_font,
        "font": resolved_font,
    }

    xml_count, font_issues, expected = validate(root, include, resolved_font, None)
    result["validated"] = {
        "xml_files": xml_count,
        "expected_font": expected,
        "font_issues": font_issues,
    }

    packed = repack(root, output_pptx)
    result["repacked_entries"] = packed
    result["ok"] = font_issues == 0
    return result


def run_job_file(job_file: Path) -> Dict[str, object]:
    job = json.loads(job_file.read_text(encoding="utf-8"))
    if not isinstance(job, dict):
        raise ValueError("Job file must be a JSON object")

    mode = job.get("mode", "workflow")
    if mode != "workflow":
        raise ValueError("Only mode='workflow' is supported in runfile")

    input_pptx = Path(job["input_pptx"]) if job.get("input_pptx") else None
    root = Path(job["root"])
    include = str(job.get("include", "slides"))
    tsv = Path(job.get("tsv", root / f"translation.{job.get('lang', 'target')}.tsv"))
    lang = job.get("lang")
    font = job.get("font")
    glossary = Path(job["glossary"]) if job.get("glossary") else None
    output_pptx = Path(job.get("output_pptx", f"{root}.out.pptx"))

    return run_workflow(
        input_pptx=input_pptx,
        root=root,
        include=include,
        tsv=tsv,
        lang=lang,
        font=font,
        glossary=glossary,
        output_pptx=output_pptx,
    )


def emit(payload: Dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    message = payload.get("message")
    if isinstance(message, str):
        print(message)
    else:
        print(payload)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="PPT OOXML translation workflow tool")
    p.add_argument("--json", action="store_true", help="machine-readable JSON output")
    sub = p.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("help", help="print usage guide")
    h.add_argument("--lang", default="both", choices=["zh", "en", "both"], help="guide language")

    u = sub.add_parser("unpack", help="unpack .pptx into OOXML folder")
    u.add_argument("--input", required=True, type=Path, help="input .pptx path")
    u.add_argument("--output", required=True, type=Path, help="unpacked root output dir")

    c = sub.add_parser("collect", help="collect text runs into TSV")
    c.add_argument("--root", required=True, type=Path, help="unpacked PPTX root")
    c.add_argument("--include", default="slides", help="slides,notes,masters")
    c.add_argument("--output", required=True, type=Path, help="output TSV path")

    a = sub.add_parser("apply", help="apply translated TSV into XML")
    a.add_argument("--root", required=True, type=Path, help="unpacked PPTX root")
    a.add_argument("--tsv", required=True, type=Path, help="translated TSV path")

    n = sub.add_parser("normalize", help="normalize terms and font")
    n.add_argument("--root", required=True, type=Path, help="unpacked PPTX root")
    n.add_argument("--include", default="slides", help="slides,notes,masters")
    n.add_argument("--font", default=None, help="target font name (optional)")
    n.add_argument("--lang", default=None, help="language code for font preset (e.g. ja, en, zh-cn)")
    n.add_argument("--glossary", type=Path, default=None, help="JSON glossary file")

    v = sub.add_parser("validate", help="validate XML and optional font consistency")
    v.add_argument("--root", required=True, type=Path, help="unpacked PPTX root")
    v.add_argument("--include", default="slides", help="slides,notes,masters")
    v.add_argument("--expected-font", default=None, help="expected typeface name")
    v.add_argument("--lang", default=None, help="language code for font preset (e.g. ja, en, zh-cn)")

    r = sub.add_parser("repack", help="repack unpacked OOXML to .pptx")
    r.add_argument("--root", required=True, type=Path, help="unpacked PPTX root")
    r.add_argument("--output", required=True, type=Path, help="output .pptx path")

    w = sub.add_parser("workflow", help="one-shot pipeline")
    w.add_argument("--input", type=Path, default=None, help="optional input .pptx (skip if already unpacked)")
    w.add_argument("--root", required=True, type=Path, help="unpacked PPTX root")
    w.add_argument("--include", default="slides,notes,masters", help="slides,notes,masters")
    w.add_argument("--tsv", type=Path, default=None, help="translation TSV path")
    w.add_argument("--lang", default=None, help="language code for font preset")
    w.add_argument("--font", default=None, help="override target font")
    w.add_argument("--glossary", type=Path, default=None, help="glossary JSON path")
    w.add_argument("--output", required=True, type=Path, help="output .pptx path")

    j = sub.add_parser("runfile", help="run JSON job spec")
    j.add_argument("--job", required=True, type=Path, help="path to JSON job file")

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "help":
        payload = {"ok": True, "lang": args.lang}
        zh = HELP_TEXT_ZH if args.lang in ("zh", "both") else None
        en = HELP_TEXT_EN if args.lang in ("en", "both") else None
        if args.json:
            payload["zh"] = zh
            payload["en"] = en
            payload["message"] = "help returned"
            emit(payload, True)
        else:
            if zh:
                print(zh)
            if en:
                print(en)
        return 0

    if args.cmd == "unpack":
        count = unpack(args.input, args.output)
        emit(
            {"ok": True, "command": "unpack", "entries": count, "output": str(args.output), "message": f"Unpacked {count} entries -> {args.output}"},
            args.json,
        )
        return 0

    if args.cmd == "collect":
        rows = collect_rows(args.root, args.include)
        write_tsv(rows, args.output)
        emit(
            {
                "ok": True,
                "command": "collect",
                "rows": len(rows),
                "include": args.include,
                "output": str(args.output),
                "message": f"Collected {len(rows)} text runs -> {args.output}",
            },
            args.json,
        )
        return 0

    if args.cmd == "apply":
        files_changed, texts_changed = apply_translations(args.root, args.tsv)
        emit(
            {
                "ok": True,
                "command": "apply",
                "files_changed": files_changed,
                "texts_changed": texts_changed,
                "message": f"Applied translations: files_changed={files_changed}, texts_changed={texts_changed}",
            },
            args.json,
        )
        return 0

    if args.cmd == "normalize":
        files_changed, text_repl, font_repl, resolved_font = normalize(
            args.root, args.include, args.font, args.lang, args.glossary
        )
        emit(
            {
                "ok": True,
                "command": "normalize",
                "files_changed": files_changed,
                "text_replacements": text_repl,
                "font_assignments": font_repl,
                "font": resolved_font,
                "message": "Normalized: "
                f"files_changed={files_changed}, text_replacements={text_repl}, "
                f"font_assignments={font_repl}, font={resolved_font}",
            },
            args.json,
        )
        return 0

    if args.cmd == "validate":
        xml_count, font_issues, resolved_expected = validate(
            args.root, args.include, args.expected_font, args.lang
        )
        emit(
            {
                "ok": font_issues == 0 if resolved_expected else True,
                "command": "validate",
                "xml_files": xml_count,
                "expected_font": resolved_expected,
                "font_issues": font_issues,
                "message": f"Validated XML files: {xml_count}",
            },
            args.json,
        )
        if resolved_expected:
            return 1 if font_issues else 0
        return 0

    if args.cmd == "repack":
        added = repack(args.root, args.output)
        emit(
            {
                "ok": True,
                "command": "repack",
                "entries": added,
                "output": str(args.output),
                "message": f"Packed {added} filesystem entries into {args.output}",
            },
            args.json,
        )
        return 0

    if args.cmd == "workflow":
        tsv = args.tsv or Path(args.root) / f"translation.{(args.lang or 'target')}.tsv"
        result = run_workflow(
            input_pptx=args.input,
            root=args.root,
            include=args.include,
            tsv=tsv,
            lang=args.lang,
            font=args.font,
            glossary=args.glossary,
            output_pptx=args.output,
        )
        result["command"] = "workflow"
        result["message"] = f"Workflow done -> {args.output}"
        emit(result, args.json)
        return 0 if result.get("ok", False) else 1

    if args.cmd == "runfile":
        result = run_job_file(args.job)
        result["command"] = "runfile"
        result["message"] = f"Runfile done -> {result.get('output_pptx')}"
        emit(result, args.json)
        return 0 if result.get("ok", False) else 1

    parser.print_help()
    return 2


def _main_guard() -> int:
    try:
        return main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(_main_guard())
