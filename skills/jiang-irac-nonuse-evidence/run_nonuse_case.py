#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from datetime import datetime, timezone
import os
import subprocess
import sys
from pathlib import Path
import json
import shutil
import re
import tempfile
import traceback
import uuid
import zipfile
from typing import Any
import yaml

from utils.compliance import build_reason_chain, load_rules_and_write_profile
from utils.logger import audit, set_run_context, setup_logger

SUPPORTED_EVIDENCE_EXTS = {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
OFFICE_HINT_EXTS = {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}
SOFFICE_BIN = shutil.which("soffice") or "/Applications/LibreOffice.app/Contents/MacOS/soffice"
DEFAULT_DOCX2PDF_TIMEOUT = 180
LOGGER = setup_logger(__name__, log_dir=(Path(__file__).resolve().parent / "logs"))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_docx2pdf_fail_log(logs_dir: Path, payload: dict[str, Any]) -> None:
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        fail_log = logs_dir / "docx2pdf_fail.log"
        with fail_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as exc:
        LOGGER.exception("写入 docx2pdf_fail.log 失败")
        audit({
            "type": "exception",
            "step": "write_docx2pdf_fail_log",
            "file": str(logs_dir / "docx2pdf_fail.log"),
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ok": False,
            "reason_code": "docx2pdf_fail_log_write_failed",
        })


def _resolve_docx2pdf_timeout(cli_timeout: int = 0) -> int:
    if int(cli_timeout or 0) > 0:
        return int(cli_timeout)
    env_val = os.environ.get("NONUSE_DOCX2PDF_TIMEOUT", "").strip()
    if env_val:
        try:
            parsed = int(env_val)
            if parsed > 0:
                return parsed
        except ValueError:
            LOGGER.exception("环境变量 NONUSE_DOCX2PDF_TIMEOUT 非法")
            audit({
                "type": "exception",
                "step": "resolve_docx2pdf_timeout",
                "file": "NONUSE_DOCX2PDF_TIMEOUT",
                "error": f"invalid_integer:{env_val}",
                "traceback": "",
                "ok": False,
                "reason_code": "invalid_docx2pdf_timeout_env",
            })
    rule_path = Path(__file__).resolve().parent / "rules" / "time_rules.yaml"
    if rule_path.exists():
        try:
            raw = yaml.safe_load(rule_path.read_text(encoding="utf-8")) or {}
            val = int(raw.get("docx2pdf_timeout_sec", DEFAULT_DOCX2PDF_TIMEOUT))
            if val > 0:
                return val
        except Exception as exc:
            LOGGER.exception("读取 time_rules.yaml 失败")
            audit({
                "type": "exception",
                "step": "resolve_docx2pdf_timeout",
                "file": str(rule_path),
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "ok": False,
                "reason_code": "time_rules_read_failed",
            })
    return DEFAULT_DOCX2PDF_TIMEOUT


def _is_subpath(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except Exception as exc:
        LOGGER.exception("路径子目录关系判断失败")
        audit({
            "type": "exception",
            "step": "is_subpath",
            "file": f"{child} -> {parent}",
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ok": False,
            "reason_code": "is_subpath_failed",
        })
        return False


def _collect_files_by_ext(root: Path, exts: set[str]) -> list[Path]:
    return [
        p for p in root.rglob("*")
        if p.is_file() and not p.name.startswith("._") and p.suffix.lower() in exts
    ]


def _set_cli_arg(cmd: list[str], flag: str, value: str) -> list[str]:
    out = list(cmd)
    for i in range(len(out) - 1):
        if out[i] == flag:
            out[i + 1] = str(value)
            return out
    out.extend([flag, str(value)])
    return out


def _office_converter_available() -> bool:
    return Path(SOFFICE_BIN).exists()


def _parse_caseinfo_missing(ci_path: Path) -> set[str]:
    missing: set[str] = set()
    if not ci_path.exists():
        return missing
    try:
        ci = json.loads(ci_path.read_text(encoding="utf-8"))
        errs = "；".join(ci.get("errors", []))
    except Exception as exc:
        LOGGER.exception("解析 caseinfo_validation.json 失败")
        audit({
            "type": "exception",
            "step": "parse_caseinfo_missing",
            "file": str(ci_path),
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ok": False,
            "reason_code": "caseinfo_validation_parse_failed",
        })
        return missing
    if "reg_no 缺失或无效" in errs or "reg_no 格式不合法" in errs:
        missing.add("reg_no")
    if "applicant 缺失或无效" in errs:
        missing.add("applicant")
    if "respondent 缺失或无效" in errs:
        missing.add("respondent")
    if "class 缺失或无效" in errs:
        missing.add("class")
    if "mark_name 缺失或无效" in errs or "mark_name 疑似噪音词" in errs:
        missing.add("mark_name")
    return missing


def _prompt_caseinfo_overrides(missing: set[str]) -> dict[str, str]:
    if not missing or not sys.stdin.isatty():
        return {}
    print("\n检测到案情关键信息缺失，可选手工补录（直接回车可跳过）：")
    mapping = [
        ("reg_no", "请输入商标注册号"),
        ("applicant", "请输入申请人"),
        ("respondent", "请输入被申请人/注册人"),
        ("class", "请输入类别（数字）"),
        ("mark_name", "请输入商标名称"),
    ]
    out: dict[str, str] = {}
    for key, prompt in mapping:
        if key not in missing:
            continue
        val = input(f"{prompt}: ").strip()
        if val:
            out[key] = val
    return out


def _apply_caseinfo_overrides(cmd: list[str], overrides: dict[str, str]) -> list[str]:
    out = list(cmd)
    key_to_flag = {
        "reg_no": "--case-reg-no",
        "applicant": "--case-applicant",
        "respondent": "--case-respondent",
        "class": "--case-class",
        "mark_name": "--case-mark-name",
        "goods_services": "--case-goods-services",
    }
    for k, v in overrides.items():
        flag = key_to_flag.get(k)
        if not flag or not v:
            continue
        out = _set_cli_arg(out, flag, v)
        if k == "mark_name":
            out = _set_cli_arg(out, "--allow-noisy-mark-name", "on")
    return out


def _parse_output_formats(spec: str) -> list[str]:
    txt = str(spec or "").strip().lower()
    if not txt:
        return ["docx"]
    out: list[str] = []
    for token in re.split(r"[,;\s]+", txt):
        t = token.strip().lower()
        if not t:
            continue
        if t.startswith("."):
            t = t[1:]
        if t in {"docx", "pdf", "md", "txt", "html"} and t not in out:
            out.append(t)
    return out or ["docx"]


def _docx_to_pdf(src_docx: Path, dst_pdf: Path, logs_dir: Path, timeout_sec: int) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": False,
        "out_pdf_path": str(dst_pdf),
        "reason_code": "unknown",
    }
    if not Path(SOFFICE_BIN).exists():
        result["reason_code"] = "soffice_missing"
        return result
    dst_pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="docx2pdf_") as td:
        td_path = Path(td)
        cmd = [
            SOFFICE_BIN,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(td_path),
            str(src_docx),
        ]
        try:
            p = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_sec,
            )
        except subprocess.TimeoutExpired as exc:
            result["reason_code"] = "TIMEOUT"
            _write_docx2pdf_fail_log(logs_dir, {
                "cmd": cmd,
                "reason_code": "TIMEOUT",
                "timeout_sec": timeout_sec,
                "stdout": str(exc.stdout or ""),
                "stderr": str(exc.stderr or ""),
                "source": str(src_docx),
            })
            audit({
                "type": "docx2pdf_fail",
                "step": "docx2pdf",
                "file": str(src_docx),
                "ok": False,
                "reason_code": "TIMEOUT",
                "stderr_summary": str(exc.stderr or "")[:400],
            })
            return result
        if p.returncode != 0:
            result["reason_code"] = "RETURNCODE"
            _write_docx2pdf_fail_log(logs_dir, {
                "cmd": cmd,
                "reason_code": "RETURNCODE",
                "return_code": p.returncode,
                "stdout": p.stdout,
                "stderr": p.stderr,
                "source": str(src_docx),
            })
            audit({
                "type": "docx2pdf_fail",
                "step": "docx2pdf",
                "file": str(src_docx),
                "ok": False,
                "reason_code": "RETURNCODE",
                "stderr_summary": str(p.stderr or "")[:400],
            })
            return result
        produced = td_path / f"{src_docx.stem}.pdf"
        if not produced.exists():
            cands = sorted(td_path.glob("*.pdf"))
            if not cands:
                result["reason_code"] = "PDF_NOT_FOUND"
                _write_docx2pdf_fail_log(logs_dir, {
                    "cmd": cmd,
                    "reason_code": "PDF_NOT_FOUND",
                    "return_code": p.returncode,
                    "stdout": p.stdout,
                    "stderr": p.stderr,
                    "source": str(src_docx),
                })
                audit({
                    "type": "docx2pdf_fail",
                    "step": "docx2pdf",
                    "file": str(src_docx),
                    "ok": False,
                    "reason_code": "PDF_NOT_FOUND",
                    "stderr_summary": str(p.stderr or "")[:400],
                })
                return result
            produced = cands[0]
        shutil.move(str(produced), str(dst_pdf))
    result["ok"] = dst_pdf.exists()
    result["reason_code"] = "ok" if result["ok"] else "move_failed"
    return result


def _docx_text_via_xml(docx_path: Path) -> str:
    if not docx_path.exists():
        return ""
    try:
        with zipfile.ZipFile(docx_path, "r") as zf:
            xml = zf.read("word/document.xml").decode("utf-8", errors="ignore")
    except Exception as exc:
        LOGGER.exception("DOCX 文本抽取失败")
        audit({
            "type": "exception",
            "step": "docx_text_via_xml",
            "file": str(docx_path),
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ok": False,
            "reason_code": "docx_text_extract_failed",
        })
        return ""
    text = re.sub(r"</w:p>", "\n", xml)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _export_additional_formats(
    out_dir: Path,
    docx_files: list[Path],
    formats_spec: str,
    docx2pdf_timeout: int = 0,
) -> dict[str, Any]:
    formats = _parse_output_formats(formats_spec)
    result: dict[str, Any] = {"formats": formats, "generated": [], "warnings": []}
    logs_dir = out_dir / "logs"
    timeout_sec = _resolve_docx2pdf_timeout(docx2pdf_timeout)
    for src in docx_files:
        if not src.exists():
            result["warnings"].append(f"文书不存在：{src}")
            continue
        base = src.with_suffix("")
        text = ""
        if any(f in formats for f in ["txt", "md", "html"]):
            text = _docx_text_via_xml(src)
        if "pdf" in formats:
            dst_pdf = base.with_suffix(".pdf")
            conv = _docx_to_pdf(src, dst_pdf, logs_dir=logs_dir, timeout_sec=timeout_sec)
            if conv.get("ok"):
                result["generated"].append(str(dst_pdf))
            else:
                result["warnings"].append(
                    f"PDF导出失败：{src.name}（reason_code={conv.get('reason_code','unknown')}）"
                )
        if "txt" in formats:
            dst = base.with_suffix(".txt")
            dst.write_text(text, encoding="utf-8")
            result["generated"].append(str(dst))
        if "md" in formats:
            dst = base.with_suffix(".md")
            dst.write_text(f"# {src.stem}\n\n```\n{text}\n```\n", encoding="utf-8")
            result["generated"].append(str(dst))
        if "html" in formats:
            dst = base.with_suffix(".html")
            esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            dst.write_text(
                "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"></head>"
                f"<body><pre>{esc}</pre></body></html>",
                encoding="utf-8",
            )
            result["generated"].append(str(dst))
    return result


def _is_precheck_approved(docx_path: Path) -> bool:
    text = _docx_text_via_xml(docx_path)
    if not text:
        return False
    text = text.replace("[✓]", "☑").replace("[√]", "☑").replace("✅", "☑")
    return ("☑ 信息无误" in text) and ("☑ 同意输出" in text)


def _normalize_casebook_input_for_generate(src_path: Path, out_dir: Path) -> Path:
    suffix = src_path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return src_path
    try:
        import pandas as pd
    except Exception as exc:
        raise RuntimeError(f"台账文件格式需转换为xlsx，但未能加载pandas：{exc}")

    out_xlsx = out_dir / "_regen_casebook_runtime.xlsx"
    ci_default = pd.DataFrame([{
        "案件编号": "",
        "注册号": "",
        "申请人": "",
        "被申请人": "",
        "类别": "",
        "商标名称": "",
        "指定期间起": "",
        "指定期间止": "",
    }])

    if suffix == ".csv":
        try:
            df_def = pd.read_csv(src_path, dtype=str).fillna("")
        except Exception as exc:
            raise RuntimeError(f"CSV台账读取失败：{src_path} ({exc})")
        with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
            ci_default.to_excel(writer, sheet_name="CaseInfo", index=False)
            df_def.to_excel(writer, sheet_name="DefenseEvidence", index=False)
            pd.DataFrame([]).to_excel(writer, sheet_name="OpponentEvidence", index=False)
        return out_xlsx

    if suffix == ".json":
        try:
            raw = json.loads(src_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise RuntimeError(f"JSON台账读取失败：{src_path} ({exc})")
        if isinstance(raw, dict):
            ci_raw = raw.get("CaseInfo") or raw.get("case_info") or raw.get("case_meta") or raw.get("case") or {}
            de_raw = raw.get("DefenseEvidence") or raw.get("defense_evidence") or raw.get("evidence") or []
            op_raw = raw.get("OpponentEvidence") or raw.get("opponent_evidence") or []
        elif isinstance(raw, list):
            ci_raw, de_raw, op_raw = {}, raw, []
        else:
            raise RuntimeError(f"JSON台账格式不支持：{src_path}")
        ci_df = pd.DataFrame(ci_raw if isinstance(ci_raw, list) else [ci_raw]).fillna("")
        if ci_df.empty:
            ci_df = ci_default
        de_df = pd.DataFrame(de_raw if isinstance(de_raw, list) else [de_raw]).fillna("")
        op_df = pd.DataFrame(op_raw if isinstance(op_raw, list) else [op_raw]).fillna("")
        with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
            ci_df.to_excel(writer, sheet_name="CaseInfo", index=False)
            de_df.to_excel(writer, sheet_name="DefenseEvidence", index=False)
            op_df.to_excel(writer, sheet_name="OpponentEvidence", index=False)
        return out_xlsx

    raise RuntimeError(f"仅重新生成模式暂不支持该台账文件格式：{src_path.suffix}（支持 xlsx/xls/csv/json）")


def _parse_named_lines(lines: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for ln in (lines or "").splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        parts = [x.strip() for x in s.split("|")]
        if len(parts) < 2:
            continue
        out.append({
            "label": parts[0] or "其他",
            "path": parts[1],
            "name": parts[2] if len(parts) >= 3 else "",
        })
    return out


def _resolve_direct_bind_root(root: Path, misc_lines: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    pairs = [
        ("答辩通知书", "D1_通知书"),
        ("主体资格证明", "D2_主体资质"),
        ("委托书", "D3_委托书"),
        ("照片", "D4_照片"),
        ("其他", "D5_其他"),
    ]
    for label, dirname in pairs:
        p = root / dirname
        if p.exists():
            items.append({"label": label, "path": str(p.resolve()), "name": ""})
    for it in _parse_named_lines(misc_lines):
        p = Path(it["path"]).expanduser().resolve()
        if not p.exists():
            raise RuntimeError(f"direct_bind_root 的“其他”路径不存在：{p}")
        lb = it["label"] if it["label"].startswith("其他") else f"其他-{it['label']}"
        items.append({"label": lb, "path": str(p), "name": it.get("name", "")})
    return items


def _write_direct_bind_manifest(out_dir: Path, items: list[dict[str, str]]) -> Path:
    manifest = out_dir / "direct_bind_manifest_runtime.json"
    payload = {"items": items}
    manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description="撤三证据智审系统程序入口（通用版）")
    ap.add_argument("--evidence-dir", default="", help="通用证据目录（兼容旧参数）")
    ap.add_argument("--fast-root", default="", help="FAST主入口目录（/fast_root）")
    ap.add_argument("--full-root", default="", help="FULL主入口目录（/full_root）")
    ap.add_argument("--evidence-dir-fast", default="", help="fast目录：现场图/包装/环境等无需深度时间锚点扫描证据")
    ap.add_argument("--evidence-dir-full", default="", help="full目录：合同发票/网店评价等需要深度时间节点分析证据")
    ap.add_argument("--out-dir", required=True, help="输出目录")
    ap.add_argument("--scan-mode", choices=["full", "fast", "mix"], default="mix", help="扫描模式：fast/full/mix")
    ap.add_argument("--precise-highlight", choices=["on", "off"], default="off", help="已停用参数（保留兼容）：证据高亮统一关闭")
    ap.add_argument("--skip-highlight-ids", default="证据24", help="已停用参数（保留兼容）")
    ap.add_argument("--max-pages", type=int, default=2, help="普通证据扫描页数上限（fast推荐2）")
    ap.add_argument("--notice-max-pages", type=int, default=6, help="通知书扫描页数上限（fast推荐6）")
    ap.add_argument("--dpi", type=int, default=320, help="普通证据OCR DPI")
    ap.add_argument("--notice-dpi", type=int, default=340, help="通知书OCR DPI")
    ap.add_argument("--strict-evidence-name", choices=["on", "off"], default="off", help="已停用门禁参数（保留兼容）：证据命名仅评估不拦截")
    ap.add_argument("--direct-bind-config", default="", help="直装证据配置JSON（不参与扫描，直接装订）")
    ap.add_argument("--direct-bind-root", default="", help="直装证据根目录（含D1~D5子目录）")
    ap.add_argument("--direct-bind-misc-lines", default="", help="直装D5扩展：每行 显示名|路径|自定义名可空")
    ap.add_argument("--only-generate-xlsx", default="", help="仅重新生成文书：指定已有台账文件（支持 xlsx/xls/csv/json）")
    ap.add_argument("--regen-doc-only", action="store_true", help="仅重新生成文书（使用输出目录中的台账）")
    ap.add_argument("--precheck-required", choices=["on", "off"], default="on", help="是否强制核验单勾选后才允许输出")
    ap.add_argument("--output-formats", default="docx", help="输出格式：docx,pdf,md,txt,html")
    ap.add_argument("--override-case-meta", default="", help="案件信息覆盖JSON（通知书OCR/自动识别结果之上，手填之下）")
    ap.add_argument("--case-reg-no", default="", help="人工指定：注册号")
    ap.add_argument("--case-applicant", default="", help="人工指定：申请人")
    ap.add_argument("--case-respondent", default="", help="人工指定：被申请人/注册人")
    ap.add_argument("--case-class", default="", help="人工指定：类别")
    ap.add_argument("--case-mark-name", default="", help="人工指定：商标名称")
    ap.add_argument("--case-mark-image", default="", help="人工指定：商标图样（文字描述或路径）")
    ap.add_argument("--case-goods-services", default="", help="人工指定：核定商品/服务")
    ap.add_argument("--case-revoked-goods-services", default="", help="人工指定：被撤商品/服务")
    ap.add_argument("--case-defense-goods-services", default="", help="人工指定：答辩商品/服务")
    ap.add_argument("--case-period-start", default="", help="人工指定：指定期间起")
    ap.add_argument("--case-period-end", default="", help="人工指定：指定期间止")
    ap.add_argument("--case-respondent-address", default="", help="人工指定：答辩人地址")
    ap.add_argument("--case-agent-company", default="", help="人工指定：代理公司名称")
    ap.add_argument("--case-agent-address", default="", help="人工指定：代理公司地址")
    ap.add_argument("--case-contact-phone", default="", help="人工指定：联系电话")
    ap.add_argument("--defense-out", default="答辩理由_自动识别.docx", help="文书输出名：答辩理由")
    ap.add_argument("--cross-out", default="证据目录_自动识别.docx", help="文书输出名：证据目录")
    ap.add_argument("--risk-out", default="风险报告_自动识别.docx", help="文书输出名：风险报告")
    ap.add_argument("--docx2pdf-timeout", type=int, default=0, help="LibreOffice 转 PDF 超时秒数（默认180，可被环境变量 NONUSE_DOCX2PDF_TIMEOUT 覆盖）")
    args = ap.parse_args()

    if (not args.evidence_dir_fast.strip()) and args.fast_root.strip():
        args.evidence_dir_fast = args.fast_root.strip()
    if (not args.evidence_dir_full.strip()) and args.full_root.strip():
        args.evidence_dir_full = args.full_root.strip()
    if args.regen_doc_only and not args.only_generate_xlsx.strip():
        args.only_generate_xlsx = str((Path(args.out_dir) / "nonuse_casebook_自动识别.xlsx").resolve())

    base = Path(__file__).resolve().parent
    py = sys.executable
    auto = base / "auto_recognize_and_generate.py"
    gen = base / "generate_suite_v2.py"
    tpl = base / "nonuse_casebook_v4_增强识别.xlsx"

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"
    logs_dir = out_dir / "logs"
    set_run_context(logs_dir, run_id)
    global LOGGER
    logger = setup_logger(__name__, log_dir=logs_dir)
    LOGGER = logger
    rc = 1
    audit({
        "type": "run_start",
        "step": "main",
        "ok": True,
        "out_dir": str(out_dir),
        "run_mode": "generate_only" if args.only_generate_xlsx.strip() else "scan_generate",
    })
    try:
        rule_profile = load_rules_and_write_profile(
            base_dir=base,
            out_dir=out_dir,
            run_id=run_id,
            logger=logger,
            audit=audit,
        )
    except Exception as exc:
        logger.exception("规则加载失败")
        audit({
            "type": "exception",
            "step": "load_rules",
            "file": str(base / "rules"),
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ok": False,
            "reason_code": "rule_load_failed",
        })
        rc = 1
        audit({"type": "run_end", "step": "main", "ok": False, "exit_code": rc})
        return rc

    # 模式A：仅重新生成文书（跳过扫描识别）
    if args.only_generate_xlsx.strip():
        casebook_in = Path(args.only_generate_xlsx).expanduser().resolve()
        if not casebook_in.exists() or not casebook_in.is_file():
            print(f"错误：仅生成模式下，台账文件不存在：{casebook_in}")
            rc = 2
            audit({"type": "run_end", "step": "generate_only", "ok": False, "exit_code": rc})
            return rc
        try:
            xlsx_in = _normalize_casebook_input_for_generate(casebook_in, out_dir)
        except Exception as exc:
            logger.exception("台账文件格式处理失败")
            audit({
                "type": "exception",
                "step": "normalize_casebook",
                "file": str(casebook_in),
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "ok": False,
                "reason_code": "casebook_normalize_failed",
            })
            print(f"错误：台账文件格式处理失败：{exc}")
            rc = 2
            audit({"type": "run_end", "step": "generate_only", "ok": False, "exit_code": rc})
            return rc
        precheck_doc = out_dir / "pre_output_checklist.docx"
        if args.precheck_required == "on":
            if not precheck_doc.exists() or (not _is_precheck_approved(precheck_doc)):
                print("错误：生成前信息核验单未勾选确认，已禁止输出。")
                print(f"请先勾选“☑ 信息无误”“☑ 同意输出”：{precheck_doc}")
                rc = 4
                audit({"type": "run_end", "step": "generate_only", "ok": False, "exit_code": rc})
                return rc
        cmd_gen = [
            py,
            str(gen),
            "--xlsx", str(xlsx_in),
            "--out-dir", str(out_dir),
            "--defense-out", args.defense_out,
            "--cross-out", args.cross_out,
            "--risk-out", args.risk_out,
        ]
        print("GEN:", " ".join(cmd_gen))
        p = subprocess.run(cmd_gen)
        rc = p.returncode
        if p.returncode == 0:
            _export_additional_formats(
                out_dir=out_dir,
                docx_files=[
                    out_dir / args.defense_out,
                    out_dir / args.cross_out,
                    out_dir / args.risk_out,
                ],
                formats_spec=args.output_formats,
                docx2pdf_timeout=args.docx2pdf_timeout,
            )
            print("\n完成。主要输出：")
            print("-", out_dir / args.defense_out)
            print("-", out_dir / args.cross_out)
            print("-", out_dir / args.risk_out)
            try:
                build_reason_chain(
                    casebook_path=Path(xlsx_in),
                    out_dir=out_dir,
                    run_id=run_id,
                    rule_profile=rule_profile,
                    logger=logger,
                    audit=audit,
                )
            except Exception as exc:
                logger.exception("生成 reason_chain 失败")
                audit({
                    "type": "exception",
                    "step": "build_reason_chain",
                    "file": str(xlsx_in),
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "ok": False,
                    "reason_code": "reason_chain_failed",
                })
                rc = 1
        audit({"type": "run_end", "step": "generate_only", "ok": rc == 0, "exit_code": rc})
        return rc

    evidence_inputs: list[tuple[str, Path]] = []
    if args.evidence_dir.strip():
        evidence_inputs.append(("通用目录", Path(args.evidence_dir).resolve()))
    if args.evidence_dir_fast.strip():
        evidence_inputs.append(("fast目录", Path(args.evidence_dir_fast).resolve()))
    if args.evidence_dir_full.strip():
        evidence_inputs.append(("full目录", Path(args.evidence_dir_full).resolve()))

    direct_bind_config_runtime = args.direct_bind_config.strip()
    merged_direct_items: list[dict[str, str]] = []
    if direct_bind_config_runtime:
        cfg = Path(direct_bind_config_runtime).expanduser().resolve()
        if not cfg.exists() or not cfg.is_file():
            print(f"错误：直装配置不存在：{cfg}")
            rc = 2
            audit({"type": "run_end", "step": "validate_inputs", "ok": False, "exit_code": rc})
            return rc
        try:
            raw = json.loads(cfg.read_text(encoding="utf-8"))
            items = raw.get("items", []) if isinstance(raw, dict) else (raw if isinstance(raw, list) else [])
            for it in items:
                if not isinstance(it, dict):
                    continue
                p = Path(str(it.get("path", "") or "")).expanduser().resolve()
                if not p.exists():
                    continue
                merged_direct_items.append({
                    "label": str(it.get("label", "") or "其他").strip() or "其他",
                    "path": str(p),
                    "name": str(it.get("name", "") or it.get("custom_name", "") or "").strip(),
                })
        except Exception as exc:
            logger.exception("直装配置解析失败")
            audit({
                "type": "exception",
                "step": "parse_direct_bind_config",
                "file": str(cfg),
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "ok": False,
                "reason_code": "direct_bind_parse_failed",
            })
            print(f"错误：直装配置解析失败：{cfg} ({exc})")
            rc = 2
            audit({"type": "run_end", "step": "validate_inputs", "ok": False, "exit_code": rc})
            return rc
    if args.direct_bind_root.strip():
        db_root = Path(args.direct_bind_root).expanduser().resolve()
        if not db_root.exists() or not db_root.is_dir():
            print(f"错误：直装根目录不存在或不是目录：{db_root}")
            rc = 2
            audit({"type": "run_end", "step": "validate_inputs", "ok": False, "exit_code": rc})
            return rc
        try:
            merged_direct_items.extend(_resolve_direct_bind_root(db_root, args.direct_bind_misc_lines))
        except Exception as exc:
            logger.exception("直装根目录解析失败")
            audit({
                "type": "exception",
                "step": "resolve_direct_bind_root",
                "file": str(db_root),
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "ok": False,
                "reason_code": "direct_bind_root_failed",
            })
            print(f"错误：直装根目录解析失败：{exc}")
            rc = 2
            audit({"type": "run_end", "step": "validate_inputs", "ok": False, "exit_code": rc})
            return rc
    elif args.direct_bind_misc_lines.strip():
        for it in _parse_named_lines(args.direct_bind_misc_lines):
            p = Path(it["path"]).expanduser().resolve()
            if not p.exists():
                print(f"错误：直装“其他”路径不存在：{p}")
                rc = 2
                audit({"type": "run_end", "step": "validate_inputs", "ok": False, "exit_code": rc})
                return rc
            lb = it["label"] if it["label"].startswith("其他") else f"其他-{it['label']}"
            merged_direct_items.append({"label": lb, "path": str(p), "name": it.get("name", "")})
    if merged_direct_items:
        manifest = _write_direct_bind_manifest(out_dir, merged_direct_items)
        direct_bind_config_runtime = str(manifest.resolve())

    has_direct_bind = bool(direct_bind_config_runtime)
    if not evidence_inputs and not has_direct_bind:
        print("错误：至少需要提供扫描证据目录（--evidence-dir/--evidence-dir-fast/--evidence-dir-full）或 --direct-bind-config。")
        rc = 2
        audit({"type": "run_end", "step": "validate_inputs", "ok": False, "exit_code": rc})
        return rc

    # 基础输入校验：目录存在且输出目录不在任何证据目录内部
    for label, d in evidence_inputs:
        if not d.exists() or not d.is_dir():
            print(f"错误：{label}不存在或不是目录：{d}")
            rc = 2
            audit({"type": "run_end", "step": "validate_inputs", "ok": False, "exit_code": rc})
            return rc
        if _is_subpath(out_dir, d):
            print("错误：输出目录不能位于证据目录内部，否则会把输出再次当作证据扫描。")
            print(f"冲突目录：{d}")
            print(f"当前输出目录：{out_dir}")
            print("请改为证据目录外的独立路径后重试。")
            rc = 2
            audit({"type": "run_end", "step": "validate_inputs", "ok": False, "exit_code": rc})
            return rc

    supported_files_map: dict[str, Path] = {}
    office_files_map: dict[str, Path] = {}
    if evidence_inputs:
        for _, d in evidence_inputs:
            for p in _collect_files_by_ext(d, SUPPORTED_EVIDENCE_EXTS):
                supported_files_map[str(p.resolve())] = p
            for p in _collect_files_by_ext(d, OFFICE_HINT_EXTS):
                office_files_map[str(p.resolve())] = p
    supported_files = list(supported_files_map.values())
    office_files = list(office_files_map.values())
    supported_count = len(supported_files)
    if evidence_inputs:
        if supported_count == 0:
            if office_files and _office_converter_available():
                print(f"提示：输入目录仅检测到 Office 文件 {len(office_files)} 个，将先直读文本识别，再转PDF用于归档。")
            else:
                print("错误：输入目录未发现可识别文件。")
                for label, d in evidence_inputs:
                    print(f" - {label}：{d}")
                print("支持格式：PDF/JPG/JPEG/PNG/BMP/TIF/TIFF/WEBP")
                if office_files:
                    print(f"检测到 Office 文件 {len(office_files)} 个，但未检测到 LibreOffice/soffice。")
                    print("请安装 LibreOffice 后重试，或先手工导出 PDF。")
                rc = 2
                audit({"type": "run_end", "step": "validate_inputs", "ok": False, "exit_code": rc})
                return rc
        if office_files:
            if _office_converter_available():
                print(f"提示：检测到 Office 文件 {len(office_files)} 个，将先直读文本识别，再自动转PDF用于证据包。")
            else:
                print(f"提示：检测到 Office 文件 {len(office_files)} 个，当前未检测到转换器。")
                print("如需纳入证据识别，请先安装 LibreOffice 或先导出为 PDF。")
    elif has_direct_bind:
        print("提示：当前仅使用“不扫描直接装订”材料（direct-bind），未配置扫描证据目录。")

    xlsx_out = out_dir / "nonuse_casebook_自动识别.xlsx"
    ocr_cache = out_dir / "ocr_cache"

    cmd = [
        py,
        str(auto),
        "--xlsx-template", str(tpl),
        "--xlsx-out", str(xlsx_out),
        "--ocr-cache", str(ocr_cache),
        "--generator", str(gen),
        "--out-dir", str(out_dir),
        "--scan-mode", args.scan_mode,
        "--max-pages", str(args.max_pages),
        "--notice-max-pages", str(args.notice_max_pages),
        "--dpi", str(args.dpi),
        "--notice-dpi", str(args.notice_dpi),
        "--strict-evidence-name", args.strict_evidence_name,
        "--caseinfo-fail-fast", "off",
    ]
    if args.evidence_dir.strip():
        cmd += ["--evidence-dir", str(Path(args.evidence_dir).resolve())]
    if args.evidence_dir_fast.strip():
        cmd += ["--evidence-dir-fast", str(Path(args.evidence_dir_fast).resolve())]
    if args.evidence_dir_full.strip():
        cmd += ["--evidence-dir-full", str(Path(args.evidence_dir_full).resolve())]
    if direct_bind_config_runtime:
        cmd += ["--direct-bind-config", str(Path(direct_bind_config_runtime).expanduser().resolve())]
    if args.override_case_meta.strip():
        cmd += ["--override-case-meta", str(Path(args.override_case_meta).expanduser().resolve())]
    cmd += ["--precheck-required", args.precheck_required]
    cmd += ["--output-formats", args.output_formats]
    if args.case_reg_no:
        cmd += ["--case-reg-no", args.case_reg_no]
    if args.case_applicant:
        cmd += ["--case-applicant", args.case_applicant]
    if args.case_respondent:
        cmd += ["--case-respondent", args.case_respondent]
    if args.case_class:
        cmd += ["--case-class", args.case_class]
    if args.case_mark_name:
        cmd += ["--case-mark-name", args.case_mark_name]
        cmd += ["--allow-noisy-mark-name", "on"]
    if args.case_mark_image:
        cmd += ["--case-mark-image", args.case_mark_image]
    if args.case_goods_services:
        cmd += ["--case-goods-services", args.case_goods_services]
    if args.case_revoked_goods_services:
        cmd += ["--case-revoked-goods-services", args.case_revoked_goods_services]
    if args.case_defense_goods_services:
        cmd += ["--case-defense-goods-services", args.case_defense_goods_services]
    if args.case_period_start:
        cmd += ["--case-period-start", args.case_period_start]
    if args.case_period_end:
        cmd += ["--case-period-end", args.case_period_end]
    if args.case_respondent_address:
        cmd += ["--case-respondent-address", args.case_respondent_address]
    if args.case_agent_company:
        cmd += ["--case-agent-company", args.case_agent_company]
    if args.case_agent_address:
        cmd += ["--case-agent-address", args.case_agent_address]
    if args.case_contact_phone:
        cmd += ["--case-contact-phone", args.case_contact_phone]
    if args.defense_out:
        cmd += ["--defense-out", args.defense_out]
    if args.cross_out:
        cmd += ["--cross-out", args.cross_out]
    if args.risk_out:
        cmd += ["--risk-out", args.risk_out]

    print("RUN:", " ".join(cmd))
    p = subprocess.run(cmd)
    rc = p.returncode
    if p.returncode != 0:
        if p.returncode == 4:
            print("\n已生成核验单，但未勾选确认，正式文书输出被阻止。")
            print("请编辑并勾选：", out_dir / "pre_output_checklist.docx")
            print("然后使用 --regen-doc-only 重新输出。")
            audit({"type": "run_end", "step": "scan_generate", "ok": False, "exit_code": rc})
            return rc
        print("\n执行失败。")
        print("请查看以下诊断文件（如存在）：")
        print("-", out_dir / "caseinfo_validation.json")
        print("-", out_dir / "time_quality_validation.json")
        print("-", out_dir / "name_quality_validation.json")
        print("-", out_dir / "page_map_validation.json")
        audit({"type": "run_end", "step": "scan_generate", "ok": False, "exit_code": rc})
        return rc

    if p.returncode == 0:
        print("\n完成。主要输出：")
        print("-", out_dir / "答辩理由_自动识别.docx")
        print("-", out_dir / "证据目录_自动识别.docx")
        print("-", out_dir / "风险报告_自动识别.docx")
        print("-", out_dir / "证据内容_重排合并.pdf")
        try:
            build_reason_chain(
                casebook_path=xlsx_out,
                out_dir=out_dir,
                run_id=run_id,
                rule_profile=rule_profile,
                logger=logger,
                audit=audit,
            )
        except Exception as exc:
            logger.exception("生成 reason_chain 失败")
            audit({
                "type": "exception",
                "step": "build_reason_chain",
                "file": str(xlsx_out),
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "ok": False,
                "reason_code": "reason_chain_failed",
            })
            rc = 1
    audit({"type": "run_end", "step": "scan_generate", "ok": rc == 0, "exit_code": rc})
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
