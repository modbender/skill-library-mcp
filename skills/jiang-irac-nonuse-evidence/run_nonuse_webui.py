#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import uuid
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from utils.compliance import build_reason_chain, load_rules_and_write_profile
from utils.logger import audit, set_run_context, setup_logger


def resolve_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", "")
        if meipass:
            return Path(meipass).resolve()
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


BASE_DIR = resolve_base_dir()
DEFAULT_PORT = 18765
UI_CONFIRM_RETURN_CODE = 5
DEFAULT_OUTPUT_FORMATS = "docx"
WEBUI_AUTH_TOKEN = ""
WEBUI_REQUIRE_AUTH = False
WEBUI_RUN_ID = f"webui_{uuid.uuid4().hex[:8]}"
WEBUI_LOGGER = setup_logger(__name__, log_dir=(BASE_DIR / "logs"))


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalize_path(p: str) -> str:
    s = (p or "").strip()
    if not s:
        return ""
    return str(Path(s).expanduser().resolve())


def _is_write_auth_ok(header_val: str) -> bool:
    if not WEBUI_REQUIRE_AUTH:
        return True
    if not WEBUI_AUTH_TOKEN:
        return False
    auth = str(header_val or "").strip()
    if not auth.startswith("Bearer "):
        return False
    provided = auth.split(" ", 1)[1].strip()
    return provided == WEBUI_AUTH_TOKEN


def _audit_request(path: str, method: str, remote_addr: str, auth_ok: bool) -> None:
    audit({
        "type": "http_request",
        "step": "webui_request",
        "path": path,
        "method": method,
        "remote_addr": remote_addr,
        "auth_ok": bool(auth_ok),
        "ok": True,
    })


def parse_direct_bind_lines(lines: str) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for ln in (lines or "").splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        parts = [x.strip() for x in s.split("|")]
        if len(parts) < 2:
            continue
        label = parts[0]
        path = parts[1]
        custom_name = parts[2] if len(parts) >= 3 else ""
        if not label or not path:
            continue
        out.append({"label": label, "path": path, "name": custom_name})
    return out


def parse_scan_other_lines(lines: str) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for ln in (lines or "").splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if "|" in s:
            parts = [x.strip() for x in s.split("|")]
            if len(parts) >= 2:
                label = parts[0] or "其他"
                path = parts[1]
                custom_name = parts[2] if len(parts) >= 3 else ""
            else:
                continue
        else:
            # 兼容仅填写路径的一行
            label = "其他"
            path = s
            custom_name = ""
        if not path:
            continue
        out.append({"label": label, "path": path, "name": custom_name})
    return out


def build_scan_group_lines(payload: Dict[str, object], scope: str) -> str:
    if scope == "fast":
        group_defs = [
            ("fast_f1", "商标档案路径"),
            ("fast_f2", "产品包装"),
            ("fast_f3", "使用环境"),
            ("fast_f4", "门头照片"),
            ("fast_f5", "产品实物"),
        ]
    else:
        group_defs = [
            ("full_l1", "合同文件"),
            ("full_l2", "发票凭证"),
            ("full_l3", "订单记录"),
            ("full_l4", "物流信息"),
            ("full_l5", "评价页面"),
        ]
    lines: List[str] = []
    for prefix, label in group_defs:
        p = normalize_path(str(payload.get(f"{prefix}_path", "") or ""))
        if not p:
            continue
        name = str(payload.get(f"{prefix}_name", "") or "").strip()
        if name:
            lines.append(f"{label}|{p}|{name}")
        else:
            lines.append(f"{label}|{p}|")
    return "\n".join(lines)


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


def _safe_name_token(text: str, fallback: str = "其他") -> str:
    s = re.sub(r'[\\/:*?"<>|]+', "_", str(text or "").strip())
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s).strip("._ ")
    return (s[:40] if s else fallback) or fallback


def _link_or_copy_path(src: Path, dst: Path) -> None:
    if dst.exists() or dst.is_symlink():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst, ignore_errors=True)
        else:
            dst.unlink(missing_ok=True)
    if src.is_dir():
        # 目录使用复制而非软链接，确保扫描器可稳定递归进入子文件。
        shutil.copytree(src, dst)
    else:
        try:
            os.symlink(src, dst, target_is_directory=False)
            return
        except OSError as exc:
            audit({
                "type": "filesystem_fallback",
                "step": "link_or_copy_path",
                "file": str(src),
                "ok": True,
                "reason_code": "symlink_failed_fallback_copy",
                "error": str(exc),
            })
        shutil.copy2(src, dst)


def build_scan_mix_dir(
    out_dir: str,
    slot: str,
    base_dir: str,
    other_lines: str,
) -> str:
    base_p = Path(base_dir).resolve() if (base_dir or "").strip() else None
    other_items = parse_scan_other_lines(other_lines)
    if not base_p and not other_items:
        return ""

    mix_root = Path(out_dir).resolve() / "_scan_mix_inputs" / slot
    if mix_root.exists():
        shutil.rmtree(mix_root, ignore_errors=True)
    mix_root.mkdir(parents=True, exist_ok=True)

    seq = 1
    if base_p:
        if not base_p.exists():
            raise RuntimeError(f"{slot}主目录不存在：{base_p}")
        base_name = _safe_name_token(base_p.name, fallback=f"{slot}主目录")
        dst = mix_root / f"{seq:03d}_主目录_{base_name}"
        _link_or_copy_path(base_p, dst)
        seq += 1

    for item in other_items:
        p = normalize_path(str(item.get("path", "") or ""))
        if not p:
            continue
        src = Path(p)
        if not src.exists():
            raise RuntimeError(f"{slot}“其他”路径不存在：{src}")
        name_hint = (
            str(item.get("name", "") or "").strip()
            or str(item.get("label", "") or "").strip()
            or src.stem
            or "其他"
        )
        token = _safe_name_token(name_hint, fallback="其他")
        suffix = src.suffix.lower() if src.is_file() else ""
        dst = mix_root / f"{seq:03d}_{token}{suffix}"
        while dst.exists() or dst.is_symlink():
            seq += 1
            dst = mix_root / f"{seq:03d}_{token}{suffix}"
        _link_or_copy_path(src, dst)
        seq += 1

    return str(mix_root.resolve())


def load_review_data(out_dir: str) -> Dict[str, object]:
    out_path = Path(out_dir).expanduser().resolve()
    summary_path = out_path / "扫描识别摘要.json"
    precheck_path = out_path / "pre_output_checklist.docx"
    xlsx_path = out_path / "nonuse_casebook_自动识别.xlsx"
    summary: Dict[str, object] = {}
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception as exc:
            WEBUI_LOGGER.exception("读取扫描识别摘要失败")
            audit({
                "type": "exception",
                "step": "load_review_data",
                "file": str(summary_path),
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "ok": False,
                "reason_code": "summary_json_parse_failed",
            })
            summary = {}
    case_info_keys = [
        ("case_no", "案件编号"),
        ("reg_no", "商标号"),
        ("mark_name", "商标名称"),
        ("class", "类别"),
        ("respondent", "答辩人"),
        ("applicant", "申请人"),
        ("period_start", "指定期间起"),
        ("period_end", "指定期间止"),
        ("revoked_goods_services", "被撤商品/服务"),
        ("defense_goods_services", "答辩商品/服务"),
        ("agent_company", "代理公司"),
        ("contact_phone", "联系电话"),
    ]
    case_info = []
    for key, label in case_info_keys:
        val = str(summary.get(key, "") or "").strip()
        if val:
            case_info.append({"key": key, "label": label, "value": val})
    stats = [
        {"label": "证据数量", "value": int(summary.get("evidence_count", 0) or 0)},
        {"label": "FAST分项数量", "value": int(summary.get("input_fast_profile_count", 0) or 0)},
        {"label": "FULL分项数量", "value": int(summary.get("input_full_profile_count", 0) or 0)},
        {"label": "直装材料项", "value": int(summary.get("direct_bind_item_count", 0) or 0)},
    ]
    return {
        "out_dir": str(out_path),
        "summary_path": str(summary_path),
        "precheck_docx_path": str(precheck_path),
        "casebook_xlsx_path": str(xlsx_path),
        "precheck_exists": precheck_path.exists(),
        "summary_exists": summary_path.exists(),
        "casebook_exists": xlsx_path.exists(),
        "case_info": case_info,
        "stats": stats,
        "summary": summary,
    }


class RunJob:
    def __init__(self, run_id: str, cmd: List[str], out_dir: str, payload: Optional[Dict[str, object]] = None):
        self.run_id = run_id
        self.cmd = cmd
        self.out_dir = out_dir
        self.payload = payload or {}
        self.status = "running"  # running/success/failed/await_confirm
        self.started_at = now_iso()
        self.finished_at = ""
        self.return_code: Optional[int] = None
        self.logs: List[str] = []
        self.lock = threading.Lock()

    def append_log(self, line: str) -> None:
        with self.lock:
            self.logs.append(line)
            if len(self.logs) > 3000:
                self.logs = self.logs[-3000:]

    def snapshot(self) -> Dict[str, object]:
        with self.lock:
            joined = "".join(self.logs)
        if len(joined) > 120000:
            joined = joined[-120000:]
        return {
            "run_id": self.run_id,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "return_code": self.return_code,
            "out_dir": self.out_dir,
            "logs": joined,
            "running": self.status == "running",
            "await_confirm": self.status == "await_confirm",
        }


class JobWriter:
    def __init__(self, job: RunJob):
        self.job = job

    def write(self, s: str) -> None:
        if not s:
            return
        # Drop noisy parser warnings that do not affect output correctness.
        if "Multiple definitions in dictionary" in s and "key /Info" in s:
            return
        self.job.append_log(s)

    def flush(self) -> None:
        return


class RuntimeState:
    def __init__(self):
        self.lock = threading.Lock()
        self.current: Optional[RunJob] = None

    def get_current(self) -> Optional[RunJob]:
        with self.lock:
            return self.current

    def set_current(self, job: Optional[RunJob]) -> None:
        with self.lock:
            self.current = job


STATE = RuntimeState()


def osascript_choose_folder(prompt: str) -> str:
    safe_prompt = (prompt or "请选择文件夹").replace('"', '\\"')
    script = f'POSIX path of (choose folder with prompt "{safe_prompt}")'
    out = subprocess.check_output(["osascript", "-e", script], text=True).strip()
    return out


def osascript_choose_file(prompt: str) -> str:
    safe_prompt = (prompt or "请选择文件").replace('"', '\\"')
    script = f'POSIX path of (choose file with prompt "{safe_prompt}")'
    out = subprocess.check_output(["osascript", "-e", script], text=True).strip()
    return out


def open_folder(path: str) -> None:
    subprocess.run(["open", path], check=False)


def build_run_command(payload: Dict[str, object]) -> List[str]:
    py = sys.executable
    run_mode = str(payload.get("run_mode", "scan_generate") or "scan_generate")
    out_dir = normalize_path(str(payload.get("out_dir", "")))
    cmd = [
        py,
        str(BASE_DIR / "run_nonuse_case.py"),
        "--out-dir", out_dir,
        "--defense-out", str(payload.get("defense_out", "答辩理由_自动识别.docx") or "答辩理由_自动识别.docx"),
        "--cross-out", str(payload.get("cross_out", "证据目录_自动识别.docx") or "证据目录_自动识别.docx"),
        "--risk-out", str(payload.get("risk_out", "风险报告_自动识别.docx") or "风险报告_自动识别.docx"),
    ]
    precheck_required = "on"
    output_formats = DEFAULT_OUTPUT_FORMATS
    if run_mode == "generate_only":
        xlsx_in = normalize_path(str(payload.get("xlsx_in", "")))
        if xlsx_in:
            cmd.extend(["--only-generate-xlsx", xlsx_in])
        cmd.extend(["--regen-doc-only"])
        cmd.extend(["--precheck-required", precheck_required])
        cmd.extend(["--output-formats", output_formats])
        return cmd

    cmd.extend(["--scan-mode", str(payload.get("scan_mode", "fast") or "fast")])
    evidence_dir = normalize_path(str(payload.get("evidence_dir", "")))
    evidence_dir_fast = normalize_path(str(payload.get("evidence_dir_fast", "")))
    evidence_dir_full = normalize_path(str(payload.get("evidence_dir_full", "")))
    if evidence_dir:
        cmd.extend(["--evidence-dir", evidence_dir])
    if evidence_dir_fast:
        cmd.extend(["--evidence-dir-fast", evidence_dir_fast])
    if evidence_dir_full:
        cmd.extend(["--evidence-dir-full", evidence_dir_full])
    direct_bind_root = normalize_path(str(payload.get("direct_bind_root", "")))
    if direct_bind_root:
        cmd.extend(["--direct-bind-root", direct_bind_root])
    direct_bind_misc_lines = str(payload.get("direct_bind_misc_lines", "") or "")
    if direct_bind_misc_lines.strip():
        cmd.extend(["--direct-bind-misc-lines", direct_bind_misc_lines])
    field_to_flag = {
        "case_reg_no": "--case-reg-no",
        "case_mark_name": "--case-mark-name",
        "case_class": "--case-class",
        "case_respondent": "--case-respondent",
        "case_applicant": "--case-applicant",
        "case_goods_services": "--case-goods-services",
        "case_revoked_goods_services": "--case-revoked-goods-services",
        "case_defense_goods_services": "--case-defense-goods-services",
        "case_period_start": "--case-period-start",
        "case_period_end": "--case-period-end",
        "case_mark_image": "--case-mark-image",
        "case_respondent_address": "--case-respondent-address",
        "case_agent_company": "--case-agent-company",
        "case_agent_address": "--case-agent-address",
        "case_contact_phone": "--case-contact-phone",
        "direct_bind_config": "--direct-bind-config",
        "override_case_meta": "--override-case-meta",
    }
    for key, flag in field_to_flag.items():
        v = str(payload.get(key, "") or "").strip()
        if v:
            cmd.extend([flag, v])
    cmd.extend(["--precheck-required", precheck_required])
    cmd.extend(["--output-formats", output_formats])
    return cmd


def _to_int(v: object, default: int) -> int:
    try:
        s = str(v or "").strip()
        return int(s) if s else default
    except Exception as exc:
        WEBUI_LOGGER.exception("整数解析失败")
        audit({
            "type": "exception",
            "step": "to_int",
            "file": "_to_int",
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ok": False,
            "reason_code": "int_parse_failed",
        })
        return default


def run_pipeline_inprocess(payload: Dict[str, object], job: RunJob) -> int:
    writer = JobWriter(job)
    try:
        import argparse as _argparse
        import auto_recognize_and_generate as auto_mod
        import generate_suite_v2 as gen_mod
    except Exception as exc:
        job.append_log(f"[{now_iso()}] 依赖加载失败: {exc}\n")
        job.append_log(traceback.format_exc() + "\n")
        return 1

    run_mode = str(payload.get("run_mode", "scan_generate") or "scan_generate")
    out_dir = Path(normalize_path(str(payload.get("out_dir", ""))))
    out_dir.mkdir(parents=True, exist_ok=True)
    set_run_context(out_dir / "logs", job.run_id)
    logger = setup_logger(__name__, log_dir=(out_dir / "logs"))
    audit({
        "type": "run_start",
        "step": "run_pipeline_inprocess",
        "ok": True,
        "run_id": job.run_id,
        "out_dir": str(out_dir),
        "run_mode": run_mode,
    })
    try:
        rule_profile = load_rules_and_write_profile(
            base_dir=BASE_DIR,
            out_dir=out_dir,
            run_id=job.run_id,
            logger=logger,
            audit=audit,
        )
    except Exception as exc:
        logger.exception("规则加载失败")
        audit({
            "type": "exception",
            "step": "load_rules",
            "file": str(BASE_DIR / "rules"),
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ok": False,
            "reason_code": "rule_load_failed",
        })
        audit({"type": "run_end", "step": "run_pipeline_inprocess", "ok": False, "exit_code": 1})
        return 1
    defense_out = str(payload.get("defense_out", "答辩理由_自动识别.docx") or "答辩理由_自动识别.docx")
    cross_out = str(payload.get("cross_out", "证据目录_自动识别.docx") or "证据目录_自动识别.docx")
    risk_out = str(payload.get("risk_out", "风险报告_自动识别.docx") or "风险报告_自动识别.docx")
    precheck_required = "on"
    output_formats = DEFAULT_OUTPUT_FORMATS
    ui_confirm_before_generate = str(payload.get("ui_confirm_before_generate", "on") or "on")

    with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
        try:
            if run_mode == "generate_only":
                xlsx_in = normalize_path(str(payload.get("xlsx_in", "")))
                if not xlsx_in or not Path(xlsx_in).exists():
                    raise RuntimeError(f"仅重新生成模式下，台账文件不存在：{xlsx_in}")
                xlsx_in_norm = _normalize_casebook_input_for_generate(Path(xlsx_in), out_dir)
                gen_args = _argparse.Namespace(
                    xlsx=str(xlsx_in_norm),
                    defense_template=str(BASE_DIR / "defense_template_v2_REPLACEMENT.docx"),
                    cross_template=str(BASE_DIR / "cross_exam_template_v2_REPLACEMENT.docx"),
                    out_dir=str(out_dir),
                    defense_out=defense_out,
                    cross_out=cross_out,
                    risk_out=risk_out,
                    only_cross="off",
                )
                gen_mod.main(gen_args)
                auto_mod.export_documents_in_formats(
                    out_dir=out_dir,
                    docx_paths=[out_dir / defense_out, out_dir / cross_out, out_dir / risk_out],
                    formats_spec=output_formats,
                )
                build_reason_chain(
                    casebook_path=Path(xlsx_in_norm),
                    out_dir=out_dir,
                    run_id=job.run_id,
                    rule_profile=rule_profile,
                    logger=logger,
                    audit=audit,
                )
                print(f"Generated:\n - {out_dir / defense_out}\n - {out_dir / cross_out}\n - {out_dir / risk_out}")
                audit({"type": "run_end", "step": "run_pipeline_inprocess", "ok": True, "exit_code": 0})
                return 0

            evidence_dir = normalize_path(str(payload.get("evidence_dir", "")))
            evidence_dir_fast = normalize_path(str(payload.get("evidence_dir_fast", "")))
            evidence_dir_full = normalize_path(str(payload.get("evidence_dir_full", "")))
            direct_bind_config = normalize_path(str(payload.get("direct_bind_config", "")))
            if not (evidence_dir or evidence_dir_fast or evidence_dir_full or direct_bind_config):
                raise RuntimeError("识别模式至少需要扫描证据目录（fast/full/不分类文件包）或直装材料")

            xlsx_template = BASE_DIR / "nonuse_casebook_v4_增强识别.xlsx"
            if not xlsx_template.exists():
                raise RuntimeError(f"未找到模板：{xlsx_template}")

            auto_args = _argparse.Namespace(
                evidence_dir=evidence_dir,
                evidence_dir_fast=evidence_dir_fast,
                evidence_dir_full=evidence_dir_full,
                xlsx_template=str(xlsx_template),
                xlsx_out=str(out_dir / "nonuse_casebook_自动识别.xlsx"),
                ocr_cache=str(out_dir / "ocr_cache"),
                generator=str(BASE_DIR / "generate_suite_v2.py"),
                notice_text_hint="",
                out_dir=str(out_dir),
                defense_out=defense_out,
                cross_out=cross_out,
                risk_out=risk_out,
                scan_mode=str(payload.get("scan_mode", "fast") or "fast"),
                max_pages=_to_int(payload.get("max_pages", 2), 2),
                dpi=_to_int(payload.get("dpi", 320), 320),
                notice_max_pages=_to_int(payload.get("notice_max_pages", 6), 6),
                notice_dpi=_to_int(payload.get("notice_dpi", 340), 340),
                organize_dir="",
                scan_report="扫描识别报告.md",
                override_rules="",
                direct_bind_config=direct_bind_config,
                override_case_meta=normalize_path(str(payload.get("override_case_meta", ""))),
                case_reg_no=str(payload.get("case_reg_no", "") or "").strip(),
                case_applicant=str(payload.get("case_applicant", "") or "").strip(),
                case_respondent=str(payload.get("case_respondent", "") or "").strip(),
                case_class=str(payload.get("case_class", "") or "").strip(),
                case_mark_name=str(payload.get("case_mark_name", "") or "").strip(),
                case_mark_image=str(payload.get("case_mark_image", "") or "").strip(),
                case_goods_services=str(payload.get("case_goods_services", "") or "").strip(),
                case_revoked_goods_services=str(payload.get("case_revoked_goods_services", "") or "").strip(),
                case_defense_goods_services=str(payload.get("case_defense_goods_services", "") or "").strip(),
                case_period_start=str(payload.get("case_period_start", "") or "").strip(),
                case_period_end=str(payload.get("case_period_end", "") or "").strip(),
                case_respondent_address=str(payload.get("case_respondent_address", "") or "").strip(),
                case_agent_company=str(payload.get("case_agent_company", "") or "").strip(),
                case_agent_address=str(payload.get("case_agent_address", "") or "").strip(),
                case_contact_phone=str(payload.get("case_contact_phone", "") or "").strip(),
                allow_noisy_mark_name="on" if str(payload.get("case_mark_name", "") or "").strip() else "off",
                caseinfo_fail_fast="off",
                strict_evidence_name="off",
                min_in_period_highmed=8,
                max_low_ratio=0.35,
                max_unknown_ratio=0.30,
                precise_highlight="off",
                precise_highlight_skip_ids="证据24",
                precise_highlight_max_pages=6,
                precise_highlight_max_hits=24,
                precheck_required=precheck_required,
                output_formats=output_formats,
            )

            info = auto_mod.build_casebook(auto_args)
            summary_path = out_dir / "扫描识别摘要.json"
            summary_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
            build_reason_chain(
                casebook_path=Path(auto_args.xlsx_out),
                out_dir=out_dir,
                run_id=job.run_id,
                rule_profile=rule_profile,
                logger=logger,
                audit=audit,
            )
            # 两阶段输出：先生成证据目录，供人工核验后再生成其他文书。
            pre_cross_args = _argparse.Namespace(
                xlsx=auto_args.xlsx_out,
                defense_template=str(BASE_DIR / "defense_template_v2_REPLACEMENT.docx"),
                cross_template=str(BASE_DIR / "cross_exam_template_v2_REPLACEMENT.docx"),
                out_dir=str(out_dir),
                defense_out=defense_out,
                cross_out=cross_out,
                risk_out=risk_out,
                only_cross="on",
            )
            gen_mod.main(pre_cross_args)
            if ui_confirm_before_generate == "on":
                precheck_doc = Path(str(info.get("precheck_docx_path", "") or ""))
                print("扫描与识别已完成，已先生成《证据目录》与输出前核对单。")
                print(f"请进入核对页面确认后再输出正式文书：{precheck_doc}")
                audit({"type": "run_end", "step": "run_pipeline_inprocess", "ok": True, "exit_code": UI_CONFIRM_RETURN_CODE})
                return UI_CONFIRM_RETURN_CODE

            gen_args = _argparse.Namespace(
                xlsx=auto_args.xlsx_out,
                defense_template=str(BASE_DIR / "defense_template_v2_REPLACEMENT.docx"),
                cross_template=str(BASE_DIR / "cross_exam_template_v2_REPLACEMENT.docx"),
                out_dir=str(out_dir),
                defense_out=defense_out,
                cross_out=cross_out,
                risk_out=risk_out,
                only_cross="off",
            )
            gen_mod.main(gen_args)
            auto_mod.export_documents_in_formats(
                out_dir=out_dir,
                docx_paths=[out_dir / defense_out, out_dir / cross_out, out_dir / risk_out],
                formats_spec=output_formats,
            )
            print(f"Generated:\n - {out_dir / defense_out}\n - {out_dir / cross_out}\n - {out_dir / risk_out}")
            audit({"type": "run_end", "step": "run_pipeline_inprocess", "ok": True, "exit_code": 0})
            return 0
        except Exception as exc:
            logger.exception("运行流水线失败")
            audit({
                "type": "exception",
                "step": "run_pipeline_inprocess",
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "ok": False,
                "reason_code": "pipeline_failed",
            })
            print(traceback.format_exc())
            audit({"type": "run_end", "step": "run_pipeline_inprocess", "ok": False, "exit_code": 1})
            return 1


def run_job_worker(job: RunJob) -> None:
    job.append_log(f"[{now_iso()}] RUN: {' '.join(job.cmd)}\n")
    try:
        rc = run_pipeline_inprocess(job.payload, job)
        job.return_code = rc
        if rc == UI_CONFIRM_RETURN_CODE:
            job.status = "await_confirm"
        else:
            job.status = "success" if rc == 0 else "failed"
    except Exception as exc:
        job.return_code = -1
        job.status = "failed"
        job.append_log(f"[{now_iso()}] 运行异常: {exc}\n")
        WEBUI_LOGGER.exception("run_job_worker 异常")
        audit({
            "type": "exception",
            "step": "run_job_worker",
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ok": False,
            "reason_code": "job_worker_failed",
        })
    finally:
        job.finished_at = now_iso()


HTML_PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>撤三证据智审系统</title>
  <style>
    :root{
      --bg1:#eef6ff;
      --bg2:#dcecff;
      --card:#ffffff;
      --line:#d3e4ff;
      --primary:#1976d2;
      --primary2:#1e88e5;
      --text:#13314f;
      --muted:#5f7891;
      --ok:#1b8f5a;
      --err:#c62828;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Helvetica Neue",Arial,sans-serif;
      color:var(--text);
      background:linear-gradient(145deg,var(--bg1),var(--bg2));
      min-height:100vh;
    }
    .wrap{max-width:1080px;margin:28px auto;padding:0 16px}
    .head{
      background:var(--card);
      border:1px solid var(--line);
      border-radius:16px;
      padding:18px 20px;
      box-shadow:0 8px 22px rgba(25,118,210,.08);
      margin-bottom:14px;
    }
    .title{font-size:24px;font-weight:800;color:#0f4a87}
    .sub{font-size:13px;color:var(--muted);margin-top:6px}
    .card{
      background:var(--card);
      border:1px solid var(--line);
      border-radius:16px;
      box-shadow:0 8px 20px rgba(25,118,210,.06);
      padding:18px;
      margin-bottom:14px;
    }
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
    .field label{display:block;font-size:13px;color:#2a5580;margin-bottom:6px}
    .input-row{display:flex;gap:8px}
    input,select,textarea{
      width:100%;
      padding:10px 12px;
      border:1px solid #c6dcff;
      border-radius:10px;
      background:#f7fbff;
      color:#17324d;
      outline:none;
    }
    input:focus,select:focus,textarea:focus{
      border-color:var(--primary2);
      box-shadow:0 0 0 3px rgba(30,136,229,.16);
      background:#fff;
    }
    .btn{
      border:none;
      border-radius:10px;
      padding:10px 14px;
      cursor:pointer;
      font-weight:700;
    }
    .btn-primary{
      background:linear-gradient(180deg,#2f95f6,#1a74d9);
      color:#fff;
    }
    .btn-light{
      background:#edf5ff;
      color:#14599e;
      border:1px solid #c6dcff;
    }
    .actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px}
    .status{
      display:inline-block;
      padding:4px 10px;
      border-radius:999px;
      font-size:12px;
      font-weight:700;
      background:#edf5ff;
      color:#1a5da5;
      border:1px solid #c6dcff;
    }
    .status.ok{background:#ecfff5;color:var(--ok);border-color:#b9e9cf}
    .status.err{background:#fff1f1;color:var(--err);border-color:#f2c1c1}
    .status.await{background:#fff8e9;color:#9a6a00;border-color:#f1d7a4}
    .log{
      width:100%;
      min-height:250px;
      resize:vertical;
      font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;
      font-size:12px;
      background:#f9fcff;
      color:#14324f;
    }
    details summary{
      cursor:pointer;
      color:#1c5f9f;
      font-weight:700;
      margin-bottom:10px;
    }
    .muted{color:var(--muted);font-size:12px}
    .hint-box{
      margin-top:8px;
      padding:8px 10px;
      border-radius:10px;
      border:1px solid #d9e9ff;
      background:#f7fbff;
      font-size:12px;
      color:#1b4a73;
      line-height:1.5;
    }
    .other-list{
      margin-top:6px;
      border:1px dashed #d8e6fb;
      border-radius:10px;
      padding:8px;
      background:#fbfdff;
    }
    .other-row{
      border:1px solid #e6eefb;
      border-radius:8px;
      padding:8px;
      margin-bottom:8px;
      background:#fff;
    }
    .other-row:last-child{
      margin-bottom:0;
    }
    .low-priority details summary,
    details.low-priority summary{
      color:#6f8297;
      font-weight:600;
    }
    .low-priority .muted{
      color:#7f8ea0;
    }
    @media (max-width:900px){.grid{grid-template-columns:1fr}}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="head">
      <div class="title">撤三证据智审系统</div>
      <div class="sub">面向商标撤三案件的本地化证据识别、组证编排、文书生成与风险检查工具</div>
      <div class="sub">作者：@jiangzhongling</div>
    </div>

    <div class="card">
      <div class="grid">
        <div class="field">
          <label>输出目录</label>
          <div class="input-row">
            <input id="out_dir" placeholder="/Users/.../输出目录"/>
            <button class="btn btn-light" onclick="pickFolder('out_dir','请选择输出目录')">选择</button>
          </div>
        </div>
        <div class="field">
          <label>运行状态</label>
          <div id="status_badge" class="status">空闲</div>
        </div>
      </div>

      <div class="grid" style="margin-top:10px;">
        <div class="field">
          <label>fast目录（轻量扫描）</label>
          <div class="input-row">
            <input id="evidence_dir_fast" placeholder="/Users/.../fast目录（现场图/包装/环境等）"/>
            <button class="btn btn-light" onclick="pickFolder('evidence_dir_fast','请选择fast目录')">选择</button>
          </div>
          <div class="muted" style="margin-top:6px;">举例：现场拍摄图、产品包装图、环境图、门头图、无时间锚点图片。</div>
          <div class="muted" style="margin-top:8px;">FAST分项（5项，均可自定义证据名称）：</div>
          <div class="input-row" style="margin-top:6px;">
            <input id="fast_f1_path" placeholder="F1 商标档案路径（文件或目录）"/>
            <button class="btn btn-light" onclick="pickFile('fast_f1_path','请选择F1-商标档案文件')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('fast_f1_path','请选择F1-商标档案目录')">选目录</button>
          </div>
          <input id="fast_f1_name" style="margin-top:6px;" placeholder="F1 自定义证据名称（可空）"/>
          <div class="input-row" style="margin-top:6px;">
            <input id="fast_f2_path" placeholder="F2 产品包装 路径（文件或目录）"/>
            <button class="btn btn-light" onclick="pickFile('fast_f2_path','请选择F2-产品包装文件')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('fast_f2_path','请选择F2-产品包装目录')">选目录</button>
          </div>
          <input id="fast_f2_name" style="margin-top:6px;" placeholder="F2 自定义证据名称（可空）"/>
          <div class="input-row" style="margin-top:6px;">
            <input id="fast_f3_path" placeholder="F3 使用环境 路径（文件或目录）"/>
            <button class="btn btn-light" onclick="pickFile('fast_f3_path','请选择F3-使用环境文件')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('fast_f3_path','请选择F3-使用环境目录')">选目录</button>
          </div>
          <input id="fast_f3_name" style="margin-top:6px;" placeholder="F3 自定义证据名称（可空）"/>
          <div class="input-row" style="margin-top:6px;">
            <input id="fast_f4_path" placeholder="F4 门头照片 路径（文件或目录）"/>
            <button class="btn btn-light" onclick="pickFile('fast_f4_path','请选择F4-门头照片文件')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('fast_f4_path','请选择F4-门头照片目录')">选目录</button>
          </div>
          <input id="fast_f4_name" style="margin-top:6px;" placeholder="F4 自定义证据名称（可空）"/>
          <div class="input-row" style="margin-top:6px;">
            <input id="fast_f5_path" placeholder="F5 产品实物 路径（文件或目录）"/>
            <button class="btn btn-light" onclick="pickFile('fast_f5_path','请选择F5-产品实物文件')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('fast_f5_path','请选择F5-产品实物目录')">选目录</button>
          </div>
          <input id="fast_f5_name" style="margin-top:6px;" placeholder="F5 自定义证据名称（可空）"/>
          <label style="margin-top:8px;">fast-其他分项（与上方一致，可手动增项）</label>
          <div id="fast_other_list" class="other-list"></div>
          <div class="input-row" style="margin-top:6px;">
            <button class="btn btn-light" onclick="addOtherRow('fast_other_list','其他-fast')">+ 添加</button>
          </div>
        </div>
        <div class="field">
          <label>full目录（深度扫描）</label>
          <div class="input-row">
            <input id="evidence_dir_full" placeholder="/Users/.../full目录（合同发票/评价/网店页面等）"/>
            <button class="btn btn-light" onclick="pickFolder('evidence_dir_full','请选择full目录')">选择</button>
          </div>
          <div class="muted" style="margin-top:6px;">举例：合同、发票、订单、物流、网店评价、交易履约页面、平台后台截图。</div>
          <div class="muted" style="margin-top:8px;">FULL分项（5项，均可自定义证据名称）：</div>
          <div class="input-row" style="margin-top:6px;">
            <input id="full_l1_path" placeholder="L1 合同文件 路径（文件或目录）"/>
            <button class="btn btn-light" onclick="pickFile('full_l1_path','请选择L1-合同文件')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('full_l1_path','请选择L1-合同文件目录')">选目录</button>
          </div>
          <input id="full_l1_name" style="margin-top:6px;" placeholder="L1 自定义证据名称（可空）"/>
          <div class="input-row" style="margin-top:6px;">
            <input id="full_l2_path" placeholder="L2 发票凭证 路径（文件或目录）"/>
            <button class="btn btn-light" onclick="pickFile('full_l2_path','请选择L2-发票凭证')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('full_l2_path','请选择L2-发票凭证目录')">选目录</button>
          </div>
          <input id="full_l2_name" style="margin-top:6px;" placeholder="L2 自定义证据名称（可空）"/>
          <div class="input-row" style="margin-top:6px;">
            <input id="full_l3_path" placeholder="L3 订单记录 路径（文件或目录）"/>
            <button class="btn btn-light" onclick="pickFile('full_l3_path','请选择L3-订单记录')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('full_l3_path','请选择L3-订单记录目录')">选目录</button>
          </div>
          <input id="full_l3_name" style="margin-top:6px;" placeholder="L3 自定义证据名称（可空）"/>
          <div class="input-row" style="margin-top:6px;">
            <input id="full_l4_path" placeholder="L4 物流信息 路径（文件或目录）"/>
            <button class="btn btn-light" onclick="pickFile('full_l4_path','请选择L4-物流信息')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('full_l4_path','请选择L4-物流信息目录')">选目录</button>
          </div>
          <input id="full_l4_name" style="margin-top:6px;" placeholder="L4 自定义证据名称（可空）"/>
          <div class="input-row" style="margin-top:6px;">
            <input id="full_l5_path" placeholder="L5 评价页面 路径（文件或目录）"/>
            <button class="btn btn-light" onclick="pickFile('full_l5_path','请选择L5-评价页面')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('full_l5_path','请选择L5-评价页面目录')">选目录</button>
          </div>
          <input id="full_l5_name" style="margin-top:6px;" placeholder="L5 自定义证据名称（可空）"/>
          <label style="margin-top:8px;">full-其他分项（与上方一致，可手动增项）</label>
          <div id="full_other_list" class="other-list"></div>
          <div class="input-row" style="margin-top:6px;">
            <button class="btn btn-light" onclick="addOtherRow('full_other_list','其他-full')">+ 添加</button>
          </div>
        </div>
      </div>

      <div class="grid" style="margin-top:10px;">
        <div class="field">
          <label>扫描模式（默认；作用于“不分类文件包”）</label>
          <select id="scan_mode">
            <option value="mix">mix（推荐，自动分流）</option>
            <option value="fast">fast（快速）</option>
            <option value="full">full（全量）</option>
          </select>
        </div>
        <div class="field">
          <label>输出前核对</label>
          <div class="muted" style="margin-top:12px;">已改为页面核对流程：先识别并生成核对信息，再跳转核对页“同意输出”。</div>
        </div>
      </div>

      <div class="grid" style="margin-top:10px;">
        <div class="field">
          <label>案件信息覆盖文件（可选，支持 JSON/TXT/MD/CSV/XLS/XLSX/DOCX）</label>
          <div class="input-row">
            <input id="override_case_meta" placeholder="/Users/.../case_meta_override.(json/txt/md/csv/xlsx/docx)"/>
            <button class="btn btn-light" onclick="pickFile('override_case_meta','请选择案件信息覆盖文件（JSON/TXT/MD/CSV/XLS/XLSX/DOCX）')">选择</button>
          </div>
        </div>
      </div>
      <div class="hint-box">
        证据自动排序：程序类 → 权属类 → 主体资质类 → 实体实物类 → 网络展示类 → 交易履约类 → 合同票据类 → 其他补强类，同类内按证据时间升序。<br/>
        说明：不扫描直接装订证据不参与OCR；fast/full目录证据按同一排序规则进入《证据目录》和《证据内容_重排合并》。
      </div>

      <details class="low-priority" style="margin-top:10px;">
        <summary>可选：不分类文件包（不建议）</summary>
        <div class="field">
          <label>不分类文件包目录（可能影响扫描结果准确性）</label>
          <div class="input-row">
            <input id="evidence_dir" placeholder="/Users/.../不分类文件包目录"/>
            <button class="btn btn-light" onclick="pickFolder('evidence_dir','请选择不分类文件包目录')">选择</button>
          </div>
          <div class="muted" style="margin-top:6px;">仅在无法按 fast/full 分流时使用，建议优先按双目录分流。</div>
        </div>
      </details>

      <details style="margin-top:10px;">
        <summary>可选：案件信息（不填则自动识别）</summary>
        <div class="muted" style="margin-bottom:8px;">扫描过程中将实时自动生成案件信息（case_meta）；你可手填覆盖并在生成前核验单中最终确认。</div>
        <div class="grid">
          <div class="field"><label>商标号（注册号）</label><input id="case_reg_no"/></div>
          <div class="field"><label>商标名称</label><input id="case_mark_name"/></div>
          <div class="field"><label>商标图样（描述/路径）</label><input id="case_mark_image"/></div>
          <div class="field"><label>类别</label><input id="case_class"/></div>
          <div class="field"><label>答辩人名称</label><input id="case_respondent"/></div>
          <div class="field"><label>答辩人地址</label><input id="case_respondent_address"/></div>
          <div class="field"><label>申请人</label><input id="case_applicant"/></div>
          <div class="field"><label>代理公司名称</label><input id="case_agent_company"/></div>
          <div class="field"><label>代理公司地址</label><input id="case_agent_address"/></div>
          <div class="field"><label>联系电话</label><input id="case_contact_phone"/></div>
          <div class="field"><label>商标答辩期间起</label><input id="case_period_start" placeholder="YYYY-MM-DD"/></div>
          <div class="field"><label>商标答辩期间止</label><input id="case_period_end" placeholder="YYYY-MM-DD"/></div>
          <div class="field"><label>被撤商品/服务（优先）</label><input id="case_revoked_goods_services"/></div>
          <div class="field"><label>答辩商标或服务（可填商标名/服务范围）</label><input id="case_defense_goods_services"/></div>
          <div class="field"><label>被撤商品/服务（兼容字段）</label><input id="case_goods_services"/></div>
        </div>
      </details>

      <details style="margin-top:10px;">
        <summary>可选：不扫描直接装订（固定1~5分组）</summary>
        <div class="muted" style="margin-bottom:8px;">建议：如仅使用直装材料，请同步填写“案件信息”，可显著减少人工核验工作量。</div>
        <div class="field">
          <label>直装根目录（D1~D5，优先推荐）</label>
          <div class="input-row">
            <input id="direct_bind_root" placeholder="/Users/.../direct_bind（含 D1_通知书~D5_其他）"/>
            <button class="btn btn-light" onclick="pickFolder('direct_bind_root','请选择直装根目录（D1~D5）')">选择</button>
          </div>
          <div class="muted" style="margin-top:6px;">目录规范：D1_通知书、D2_主体资质、D3_委托书、D4_照片、D5_其他。</div>
        </div>
        <div class="field" style="margin-top:8px;">
          <label>直装D5-其他扩展（每行：证据命名|路径|自定义显示名可空）</label>
          <textarea id="direct_bind_misc_lines" rows="4" placeholder="公证材料|/path/notary|公证书&#10;获奖证明|/path/award|"></textarea>
          <div class="input-row" style="margin-top:6px;">
            <button class="btn btn-light" onclick="appendDirectOtherLine('direct_bind_misc_lines','file')">其他-选文件</button>
            <button class="btn btn-light" onclick="appendDirectOtherLine('direct_bind_misc_lines','folder')">其他-选目录</button>
          </div>
        </div>
        <div class="field">
          <label>1. 答辩通知书（文件或目录）</label>
          <div class="input-row">
            <input id="direct_notice_path" placeholder="/Users/.../答辩通知书.pdf 或目录"/>
            <button class="btn btn-light" onclick="pickFile('direct_notice_path','请选择答辩通知书文件')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('direct_notice_path','请选择答辩通知书目录')">选目录</button>
          </div>
          <input id="direct_notice_name" style="margin-top:6px;" placeholder="自定义证据名称（可空）"/>
          <div class="muted" style="margin-top:6px;">举例：撤三答辩通知书、补正通知书、送达回执。</div>
        </div>
        <div class="field" style="margin-top:8px;">
          <label>2. 主体资格证明（文件或目录）</label>
          <div class="input-row">
            <input id="direct_subject_path" placeholder="/Users/.../主体资格证明目录"/>
            <button class="btn btn-light" onclick="pickFile('direct_subject_path','请选择主体资格证明文件')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('direct_subject_path','请选择主体资格证明目录')">选目录</button>
          </div>
          <input id="direct_subject_name" style="margin-top:6px;" placeholder="自定义证据名称（可空）"/>
          <div class="muted" style="margin-top:6px;">举例：营业执照、统一社会信用代码信息、资质许可文件。</div>
        </div>
        <div class="field" style="margin-top:8px;">
          <label>3. 委托书（文件或目录）</label>
          <div class="input-row">
            <input id="direct_power_path" placeholder="/Users/.../委托书.pdf 或目录"/>
            <button class="btn btn-light" onclick="pickFile('direct_power_path','请选择委托书文件')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('direct_power_path','请选择委托书目录')">选目录</button>
          </div>
          <input id="direct_power_name" style="margin-top:6px;" placeholder="自定义证据名称（可空）"/>
          <div class="muted" style="margin-top:6px;">举例：商标代理委托书、授权委托证明。</div>
        </div>
        <div class="field" style="margin-top:8px;">
          <label>4. 照片（文件或目录，现场图/包装图等）</label>
          <div class="input-row">
            <input id="direct_photo_path" placeholder="/Users/.../照片目录"/>
            <button class="btn btn-light" onclick="pickFile('direct_photo_path','请选择照片文件')">选文件</button>
            <button class="btn btn-light" onclick="pickFolder('direct_photo_path','请选择照片目录')">选目录</button>
          </div>
          <input id="direct_photo_name" style="margin-top:6px;" placeholder="自定义证据名称（可空）"/>
          <div class="muted" style="margin-top:6px;">举例：厂房、仓储、门头、包装、样品实拍。</div>
        </div>
        <div class="field" style="margin-top:8px;">
          <label>5. 其他（可增加；与上方一致，可手动增项）</label>
          <div id="direct_other_list" class="other-list"></div>
          <div class="input-row" style="margin-top:6px;">
            <button class="btn btn-light" onclick="addOtherRow('direct_other_list','其他')">+ 添加</button>
          </div>
          <div class="muted" style="margin-top:6px;">举例：检测报告、媒体报道、奖项材料、补充说明等。</div>
        </div>
        <div class="field" style="margin-top:8px;">
          <label>高级：直装配置文件（JSON，可选，和以上分组可并用）</label>
          <div class="input-row">
            <input id="direct_bind_config" placeholder="/Users/.../direct_bind_manifest.json"/>
            <button class="btn btn-light" onclick="pickFile('direct_bind_config','请选择直装配置JSON')">选择</button>
          </div>
        </div>
      </details>

      <details style="margin-top:10px;">
        <summary>可选：仅重新生成文书（扫描后人工核验修改再输出）</summary>
        <div class="field">
          <label>已有台账文件路径（支持 xlsx/xls/csv/json）</label>
          <div class="input-row">
            <input id="xlsx_in" placeholder="/Users/.../nonuse_casebook_自动识别.(xlsx/xls/csv/json)"/>
            <button class="btn btn-light" onclick="pickFile('xlsx_in','请选择台账文件（xlsx/xls/csv/json）')">选择</button>
          </div>
        </div>
      </details>

      <div class="actions">
        <button id="run_btn" class="btn btn-primary" onclick="startRun('scan_generate')">开始识别并生成</button>
        <button id="regen_btn" class="btn btn-light" onclick="startRun('generate_only')">仅重新生成文书</button>
        <button id="review_btn" class="btn btn-light" onclick="openReviewPage()">打开核对页面</button>
        <button class="btn btn-light" onclick="openOutDir()">打开输出目录</button>
        <button class="btn btn-light" onclick="clearLog()">清空日志</button>
      </div>
      <div class="muted" style="margin-top:8px;">提示：识别模式可使用“fast/full 双目录分流扫描”或“仅直装不扫描”；仅生成模式只需“输出目录 + 已有台账XLSX”；当前输出格式固定为 DOCX。</div>
      <div class="muted" style="margin-top:6px;">扫描完成后会生成 <code>pre_output_checklist.docx</code> 与核对页；核对通过后点击“同意输出”再生成正式文书。</div>
    </div>

    <div class="card">
      <label style="display:block;font-size:13px;margin-bottom:8px;">实时日志</label>
      <textarea id="logs" class="log" readonly></textarea>
    </div>
  </div>

  <script>
    let pollingTimer = null;
    let latestStatus = "idle";
    let otherRowSeq = 0;

    async function api(path, opts = {}) {
      const resp = await fetch(path, opts);
      const data = await resp.json();
      if (!resp.ok || data.ok === false) {
        throw new Error(data.error || ("HTTP " + resp.status));
      }
      return data;
    }

    function setStatus(s) {
      const el = document.getElementById("status_badge");
      latestStatus = s;
      el.className = "status";
      if (s === "running") {
        el.textContent = "运行中";
      } else if (s === "await_confirm") {
        el.textContent = "待核对确认";
        el.classList.add("await");
      } else if (s === "success") {
        el.textContent = "已完成";
        el.classList.add("ok");
      } else if (s === "failed") {
        el.textContent = "失败";
        el.classList.add("err");
      } else {
        el.textContent = "空闲";
      }
      document.getElementById("run_btn").disabled = (s === "running");
      document.getElementById("regen_btn").disabled = (s === "running");
      document.getElementById("review_btn").disabled = (s === "running");
    }

    function clearLog() {
      document.getElementById("logs").value = "";
    }

    async function pickFolder(targetId, prompt) {
      try {
        const data = await api("/api/pick-folder", {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify({prompt})
        });
        document.getElementById(targetId).value = data.path || "";
      } catch (e) {
        alert("选择目录失败：" + e.message);
      }
    }

    async function pickFile(targetId, prompt) {
      try {
        const data = await api("/api/pick-file", {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify({prompt})
        });
        document.getElementById(targetId).value = data.path || "";
      } catch (e) {
        alert("选择文件失败：" + e.message);
      }
    }

    async function pickToInput(inputId, kind, prompt) {
      try {
        const endpoint = kind === "folder" ? "/api/pick-folder" : "/api/pick-file";
        const data = await api(endpoint, {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify({prompt: prompt || "请选择路径"})
        });
        const el = document.getElementById(inputId);
        if (el) el.value = data.path || "";
      } catch (e) {
        alert("选择失败：" + e.message);
      }
    }

    function removeOtherRow(rowId) {
      const row = document.getElementById(rowId);
      if (row && row.parentNode) row.parentNode.removeChild(row);
    }

    function addOtherRow(containerId, defaultLabel) {
      const box = document.getElementById(containerId);
      if (!box) return;
      otherRowSeq += 1;
      const rowId = `${containerId}_row_${otherRowSeq}`;
      const pathId = `${containerId}_path_${otherRowSeq}`;
      const row = document.createElement("div");
      row.className = "other-row";
      row.id = rowId;
      row.innerHTML = `
        <div class="input-row">
          <input class="other-label" placeholder="证据命名" value="${(defaultLabel || "其他").replace(/"/g, "&quot;")}"/>
          <input id="${pathId}" class="other-path" placeholder="路径（文件或目录）"/>
          <input class="other-name" placeholder="自定义显示名（可空）"/>
        </div>
        <div class="input-row" style="margin-top:6px;">
          <button class="btn btn-light" onclick="pickToInput('${pathId}','file','请选择文件')">选文件</button>
          <button class="btn btn-light" onclick="pickToInput('${pathId}','folder','请选择目录')">选目录</button>
          <button class="btn btn-light" onclick="removeOtherRow('${rowId}')">删除</button>
        </div>
      `;
      box.appendChild(row);
    }

    function collectOtherLines(containerId) {
      const box = document.getElementById(containerId);
      if (!box) return "";
      const rows = box.querySelectorAll(".other-row");
      const lines = [];
      rows.forEach((row) => {
        const labelEl = row.querySelector(".other-label");
        const pathEl = row.querySelector(".other-path");
        const nameEl = row.querySelector(".other-name");
        const label = (labelEl && labelEl.value || "").trim() || "其他";
        const path = (pathEl && pathEl.value || "").trim();
        const name = (nameEl && nameEl.value || "").trim();
        if (!path) return;
        lines.push(`${label}|${path}|${name}`);
      });
      return lines.join("\\n");
    }

    async function appendCustomPathLine(targetId, kind, defaultLabel, namePrompt) {
      try {
        const endpoint = kind === "folder" ? "/api/pick-folder" : "/api/pick-file";
        const pickPrompt = kind === "folder" ? "请选择目录" : "请选择文件";
        const data = await api(endpoint, {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify({prompt: pickPrompt})
        });
        const pickedPath = (data.path || "").trim();
        if (!pickedPath) return;
        const customName = (prompt(namePrompt || "请输入自定义证据命名（可空）", "") || "").trim();
        const line = `${defaultLabel || "其他"}|${pickedPath}|${customName}`;
        const el = document.getElementById(targetId);
        const cur = (el.value || "").trim();
        el.value = cur ? (cur + "\\n" + line) : line;
      } catch (e) {
        alert("添加失败：" + e.message);
      }
    }

    async function appendScanOtherLine(targetId, mode, kind) {
      const modeText = mode === "full" ? "full" : "fast";
      await appendCustomPathLine(
        targetId,
        kind,
        `其他-${modeText}`,
        `请输入${modeText}目录“其他”证据命名（可空）`
      );
    }

    async function appendDirectOtherLine(targetId, kind) {
      await appendCustomPathLine(targetId, kind, "其他", "请输入直装“其他”证据命名（可空）");
    }

    async function openOutDir() {
      const outDir = document.getElementById("out_dir").value.trim();
      if (!outDir) { alert("请先填写输出目录。"); return; }
      try {
        await api("/api/open-out", {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify({path: outDir})
        });
      } catch (e) {
        alert("打开目录失败：" + e.message);
      }
    }

    function openReviewPage() {
      const outDir = document.getElementById("out_dir").value.trim();
      if (!outDir) { alert("请先填写输出目录。"); return; }
      window.location.href = "/review?out_dir=" + encodeURIComponent(outDir);
    }

    async function startRun(runMode) {
      const payload = {
        run_mode: runMode || "scan_generate",
        evidence_dir: document.getElementById("evidence_dir").value.trim(),
        evidence_dir_fast: document.getElementById("evidence_dir_fast").value.trim(),
        evidence_dir_full: document.getElementById("evidence_dir_full").value.trim(),
        fast_f1_path: document.getElementById("fast_f1_path").value.trim(),
        fast_f1_name: document.getElementById("fast_f1_name").value.trim(),
        fast_f2_path: document.getElementById("fast_f2_path").value.trim(),
        fast_f2_name: document.getElementById("fast_f2_name").value.trim(),
        fast_f3_path: document.getElementById("fast_f3_path").value.trim(),
        fast_f3_name: document.getElementById("fast_f3_name").value.trim(),
        fast_f4_path: document.getElementById("fast_f4_path").value.trim(),
        fast_f4_name: document.getElementById("fast_f4_name").value.trim(),
        fast_f5_path: document.getElementById("fast_f5_path").value.trim(),
        fast_f5_name: document.getElementById("fast_f5_name").value.trim(),
        full_l1_path: document.getElementById("full_l1_path").value.trim(),
        full_l1_name: document.getElementById("full_l1_name").value.trim(),
        full_l2_path: document.getElementById("full_l2_path").value.trim(),
        full_l2_name: document.getElementById("full_l2_name").value.trim(),
        full_l3_path: document.getElementById("full_l3_path").value.trim(),
        full_l3_name: document.getElementById("full_l3_name").value.trim(),
        full_l4_path: document.getElementById("full_l4_path").value.trim(),
        full_l4_name: document.getElementById("full_l4_name").value.trim(),
        full_l5_path: document.getElementById("full_l5_path").value.trim(),
        full_l5_name: document.getElementById("full_l5_name").value.trim(),
        evidence_fast_other_lines: collectOtherLines("fast_other_list"),
        evidence_full_other_lines: collectOtherLines("full_other_list"),
        out_dir: document.getElementById("out_dir").value.trim(),
        scan_mode: document.getElementById("scan_mode").value,
        case_reg_no: document.getElementById("case_reg_no").value.trim(),
        case_mark_name: document.getElementById("case_mark_name").value.trim(),
        case_mark_image: document.getElementById("case_mark_image").value.trim(),
        case_class: document.getElementById("case_class").value.trim(),
        case_respondent: document.getElementById("case_respondent").value.trim(),
        case_respondent_address: document.getElementById("case_respondent_address").value.trim(),
        case_applicant: document.getElementById("case_applicant").value.trim(),
        case_agent_company: document.getElementById("case_agent_company").value.trim(),
        case_agent_address: document.getElementById("case_agent_address").value.trim(),
        case_contact_phone: document.getElementById("case_contact_phone").value.trim(),
        case_goods_services: document.getElementById("case_goods_services").value.trim(),
        case_revoked_goods_services: document.getElementById("case_revoked_goods_services").value.trim(),
        case_defense_goods_services: document.getElementById("case_defense_goods_services").value.trim(),
        case_period_start: document.getElementById("case_period_start").value.trim(),
        case_period_end: document.getElementById("case_period_end").value.trim(),
        precheck_required: "off",
        ui_confirm_before_generate: "on",
        output_formats: "docx",
        override_case_meta: document.getElementById("override_case_meta").value.trim(),
        direct_bind_config: document.getElementById("direct_bind_config").value.trim(),
        direct_bind_root: document.getElementById("direct_bind_root").value.trim(),
        direct_bind_misc_lines: document.getElementById("direct_bind_misc_lines").value,
        direct_notice_path: document.getElementById("direct_notice_path").value.trim(),
        direct_notice_name: document.getElementById("direct_notice_name").value.trim(),
        direct_subject_path: document.getElementById("direct_subject_path").value.trim(),
        direct_subject_name: document.getElementById("direct_subject_name").value.trim(),
        direct_power_path: document.getElementById("direct_power_path").value.trim(),
        direct_power_name: document.getElementById("direct_power_name").value.trim(),
        direct_photo_path: document.getElementById("direct_photo_path").value.trim(),
        direct_photo_name: document.getElementById("direct_photo_name").value.trim(),
        direct_other_lines: collectOtherLines("direct_other_list"),
        xlsx_in: document.getElementById("xlsx_in").value.trim(),
      };
      if (!payload.out_dir) {
        alert("请先填写输出目录。");
        return;
      }
      if (payload.run_mode === "generate_only") {
        if (!payload.xlsx_in) {
          alert("仅重新生成文书模式下，请提供已有台账文件路径。");
          return;
        }
      } else {
        const hasFastOther = !!(payload.evidence_fast_other_lines || "").trim();
        const hasFullOther = !!(payload.evidence_full_other_lines || "").trim();
        const hasFastGroups = !!(
          payload.fast_f1_path || payload.fast_f2_path || payload.fast_f3_path || payload.fast_f4_path || payload.fast_f5_path
        );
        const hasFullGroups = !!(
          payload.full_l1_path || payload.full_l2_path || payload.full_l3_path || payload.full_l4_path || payload.full_l5_path
        );
        const hasAnyEvidenceDir = !!(
          payload.evidence_dir || payload.evidence_dir_fast || payload.evidence_dir_full || hasFastOther || hasFullOther || hasFastGroups || hasFullGroups
        );
        const hasDirectBind = !!(
          payload.direct_bind_config ||
          payload.direct_bind_root ||
          ((payload.direct_bind_misc_lines || "").trim()) ||
          payload.direct_notice_path ||
          payload.direct_subject_path ||
          payload.direct_power_path ||
          payload.direct_photo_path ||
          ((payload.direct_other_lines || "").trim())
        );
        if (!hasAnyEvidenceDir && !hasDirectBind) {
          alert("请提供扫描证据目录（fast/full/不分类文件包）或不扫描直装材料。");
          return;
        }
        if (!hasAnyEvidenceDir && hasDirectBind) {
          const hasCaseCore = !!(
            payload.case_reg_no &&
            payload.case_mark_name &&
            payload.case_period_start &&
            payload.case_period_end
          );
          if (!hasCaseCore) {
            alert("提示：当前为“仅直装不扫描”模式，建议补充案件信息（商标号、商标名称、指定期间）以提高生成准确性。");
          }
        }
      }
      try {
        const data = await api("/api/run", {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify(payload)
        });
        setStatus("running");
        if (pollingTimer) clearInterval(pollingTimer);
        pollingTimer = setInterval(refreshStatus, 1200);
        await refreshStatus();
        alert("已开始运行，run_id：" + data.run_id);
      } catch (e) {
        alert("启动失败：" + e.message);
      }
    }

    async function refreshStatus() {
      try {
        const data = await api("/api/status");
        setStatus(data.status || "idle");
        const logsEl = document.getElementById("logs");
        logsEl.value = data.logs || "";
        logsEl.scrollTop = logsEl.scrollHeight;
        if (data.status === "success" || data.status === "failed") {
          if (pollingTimer) {
            clearInterval(pollingTimer);
            pollingTimer = null;
          }
        }
        if (data.status === "await_confirm") {
          if (pollingTimer) {
            clearInterval(pollingTimer);
            pollingTimer = null;
          }
          alert("扫描识别完成，请进入“核对页面”确认后再输出正式文书。");
          openReviewPage();
        }
      } catch (e) {
        setStatus("failed");
      }
    }

    (async function init(){
      addOtherRow("fast_other_list", "其他-fast");
      addOtherRow("full_other_list", "其他-full");
      addOtherRow("direct_other_list", "其他");
      await refreshStatus();
      pollingTimer = setInterval(refreshStatus, 1600);
    })();
  </script>
</body>
</html>
"""


REVIEW_PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>输出前核对</title>
  <style>
    :root{
      --bg1:#eef6ff;
      --bg2:#dcecff;
      --card:#ffffff;
      --line:#d3e4ff;
      --primary:#1976d2;
      --text:#13314f;
      --muted:#5f7891;
      --ok:#1b8f5a;
      --err:#c62828;
    }
    *{box-sizing:border-box}
    body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",Arial,sans-serif;color:var(--text);background:linear-gradient(145deg,var(--bg1),var(--bg2));min-height:100vh}
    .wrap{max-width:980px;margin:22px auto;padding:0 14px}
    .card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;box-shadow:0 6px 16px rgba(25,118,210,.08);margin-bottom:12px}
    .title{font-size:22px;font-weight:800;color:#0f4a87}
    .muted{color:var(--muted);font-size:12px}
    .actions{display:flex;gap:8px;flex-wrap:wrap}
    .btn{border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:700}
    .btn-primary{background:linear-gradient(180deg,#2f95f6,#1a74d9);color:#fff}
    .btn-light{background:#edf5ff;color:#14599e;border:1px solid #c6dcff}
    .kv{display:grid;grid-template-columns:180px 1fr;gap:8px 12px;font-size:13px}
    .kv .k{color:#29567f}
    .kv .v{word-break:break-all}
    .stats{display:flex;gap:10px;flex-wrap:wrap}
    .stat{padding:8px 10px;border:1px solid #c6dcff;border-radius:10px;background:#f6fbff;font-size:12px}
    .warn{color:var(--err);font-size:13px;font-weight:700}
    .ok{color:var(--ok);font-size:13px;font-weight:700}
    textarea{width:100%;min-height:180px;border:1px solid #c6dcff;border-radius:10px;background:#f9fcff;padding:10px;font-size:12px}
    code{background:#edf5ff;padding:2px 5px;border-radius:6px}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="title">输出前核对页面</div>
      <div class="muted" style="margin-top:6px;">请核对案件信息与证据目录摘要。确认无误后，点击“同意输出并生成文书”。</div>
    </div>

    <div class="card">
      <div class="kv">
        <div class="k">输出目录</div><div class="v"><code id="out_dir_text"></code></div>
        <div class="k">核对单</div><div class="v"><code id="precheck_path_text"></code></div>
        <div class="k">台账</div><div class="v"><code id="casebook_path_text"></code></div>
      </div>
      <div class="actions" style="margin-top:10px;">
        <button class="btn btn-light" onclick="openPath('precheck')">打开核对单</button>
        <button class="btn btn-light" onclick="openPath('out')">打开输出目录</button>
        <button class="btn btn-light" onclick="goBack()">返回主页面</button>
      </div>
      <div id="review_notice" style="margin-top:8px;" class="muted"></div>
    </div>

    <div class="card">
      <div style="font-weight:700;margin-bottom:8px;">案件信息摘要</div>
      <div id="case_info_box" class="kv"></div>
    </div>

    <div class="card">
      <div style="font-weight:700;margin-bottom:8px;">识别统计</div>
      <div id="stats_box" class="stats"></div>
    </div>

    <div class="card">
      <div style="font-weight:700;margin-bottom:8px;">识别摘要（JSON）</div>
      <textarea id="summary_text" readonly></textarea>
    </div>

    <div class="card">
      <label><input type="checkbox" id="agree_ok"/> 我已核对信息无误</label>
      <label style="margin-left:14px;"><input type="checkbox" id="agree_output"/> 我同意输出正式文书</label>
      <div class="actions" style="margin-top:12px;">
        <button class="btn btn-primary" onclick="confirmGenerate()">同意输出并生成文书</button>
      </div>
    </div>
  </div>

  <script>
    let reviewData = null;
    const qs = new URLSearchParams(window.location.search || "");
    const outDir = (qs.get("out_dir") || "").trim();

    async function api(path, opts = {}) {
      const resp = await fetch(path, opts);
      const data = await resp.json();
      if (!resp.ok || data.ok === false) {
        throw new Error(data.error || ("HTTP " + resp.status));
      }
      return data;
    }

    function esc(s) {
      return String(s || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    }

    function goBack() {
      window.location.href = "/";
    }

    async function openPath(kind) {
      if (!reviewData) return;
      const path = kind === "precheck" ? reviewData.precheck_docx_path : reviewData.out_dir;
      if (!path) return;
      await api("/api/open-out", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({path})
      });
    }

    function renderCaseInfo(items) {
      const box = document.getElementById("case_info_box");
      if (!items || !items.length) {
        box.innerHTML = "<div class='muted'>未提取到稳定案件信息，请在核对单中手工补充。</div>";
        return;
      }
      box.innerHTML = items.map(it => `<div class='k'>${esc(it.label)}</div><div class='v'>${esc(it.value)}</div>`).join("");
    }

    function renderStats(items) {
      const box = document.getElementById("stats_box");
      if (!items || !items.length) {
        box.innerHTML = "<div class='muted'>无统计数据</div>";
        return;
      }
      box.innerHTML = items.map(it => `<div class='stat'>${esc(it.label)}：<b>${esc(it.value)}</b></div>`).join("");
    }

    async function loadReviewData() {
      if (!outDir) {
        alert("缺少 out_dir 参数，无法加载核对信息。");
        goBack();
        return;
      }
      const data = await api("/api/review-data?out_dir=" + encodeURIComponent(outDir));
      reviewData = data;
      document.getElementById("out_dir_text").textContent = data.out_dir || "";
      document.getElementById("precheck_path_text").textContent = data.precheck_docx_path || "";
      document.getElementById("casebook_path_text").textContent = data.casebook_xlsx_path || "";
      renderCaseInfo(data.case_info || []);
      renderStats(data.stats || []);
      document.getElementById("summary_text").value = JSON.stringify(data.summary || {}, null, 2);
      const noticeEl = document.getElementById("review_notice");
      if (!data.summary_exists || !data.casebook_exists || !data.precheck_exists) {
        noticeEl.className = "warn";
        noticeEl.textContent = "警告：核对所需文件不完整，请先返回主页面重新执行扫描。";
      } else {
        noticeEl.className = "ok";
        noticeEl.textContent = "核对文件已就绪。确认后将仅输出 DOCX 正式文书。";
      }
    }

    async function confirmGenerate() {
      if (!reviewData) return;
      if (!document.getElementById("agree_ok").checked || !document.getElementById("agree_output").checked) {
        alert("请先勾选“信息无误”和“同意输出”。");
        return;
      }
      try {
        const data = await api("/api/confirm-generate", {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify({
            out_dir: reviewData.out_dir,
            agree: true
          })
        });
        alert("已启动正式输出任务，run_id：" + data.run_id);
        goBack();
      } catch (e) {
        alert("启动输出失败：" + e.message);
      }
    }

    loadReviewData().catch((e) => {
      alert("加载核对信息失败：" + e.message);
    });
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "NonUseWebUI/1.0"

    def log_message(self, format: str, *args) -> None:
        return

    def _send_json(self, obj: Dict[str, object], status: int = 200) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_html(self, html: str) -> None:
        raw = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> Dict[str, object]:
        size = int(self.headers.get("Content-Length", "0") or "0")
        data = self.rfile.read(size) if size > 0 else b"{}"
        return json.loads(data.decode("utf-8") or "{}")

    def _auth_ok(self) -> bool:
        return _is_write_auth_ok(self.headers.get("Authorization", ""))

    def _require_write_auth(self) -> bool:
        ok = self._auth_ok()
        if not ok:
            self._send_json({"ok": False, "error": "Forbidden"}, 403)
            return False
        return True

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        _audit_request(parsed.path, "GET", str(self.client_address[0]), self._auth_ok())
        if parsed.path == "/":
            self._send_html(HTML_PAGE)
            return
        if parsed.path == "/review":
            self._send_html(REVIEW_PAGE)
            return
        if parsed.path == "/api/ping":
            self._send_json({"ok": True, "message": "pong", "time": now_iso()})
            return
        if parsed.path == "/api/review-data":
            q = parse_qs(parsed.query or "")
            out_dir = normalize_path((q.get("out_dir", [""])[0] or ""))
            if not out_dir:
                self._send_json({"ok": False, "error": "缺少 out_dir 参数"}, 400)
                return
            data = load_review_data(out_dir)
            data["ok"] = True
            self._send_json(data)
            return
        if parsed.path == "/api/status":
            cur = STATE.get_current()
            if cur is None:
                self._send_json({"ok": True, "status": "idle", "running": False, "await_confirm": False, "logs": ""})
            else:
                snap = cur.snapshot()
                snap["ok"] = True
                self._send_json(snap)
            return
        self._send_json({"ok": False, "error": "Not Found"}, 404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        auth_ok = self._auth_ok()
        _audit_request(parsed.path, "POST", str(self.client_address[0]), auth_ok)
        if not self._require_write_auth():
            return
        if parsed.path == "/api/pick-folder":
            try:
                payload = self._read_json()
                prompt = str(payload.get("prompt", "") or "请选择目录")
                path = osascript_choose_folder(prompt)
                self._send_json({"ok": True, "path": path})
            except subprocess.CalledProcessError:
                self._send_json({"ok": False, "error": "用户取消选择"}, 400)
            except Exception as exc:
                WEBUI_LOGGER.exception("选择目录失败")
                audit({
                    "type": "exception",
                    "step": "api_pick_folder",
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "ok": False,
                    "reason_code": "pick_folder_failed",
                })
                self._send_json({"ok": False, "error": f"选择目录失败：{exc}"}, 500)
            return

        if parsed.path == "/api/pick-file":
            try:
                payload = self._read_json()
                prompt = str(payload.get("prompt", "") or "请选择文件")
                path = osascript_choose_file(prompt)
                self._send_json({"ok": True, "path": path})
            except subprocess.CalledProcessError:
                self._send_json({"ok": False, "error": "用户取消选择"}, 400)
            except Exception as exc:
                WEBUI_LOGGER.exception("选择文件失败")
                audit({
                    "type": "exception",
                    "step": "api_pick_file",
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "ok": False,
                    "reason_code": "pick_file_failed",
                })
                self._send_json({"ok": False, "error": f"选择文件失败：{exc}"}, 500)
            return

        if parsed.path == "/api/open-out":
            try:
                payload = self._read_json()
                path = normalize_path(str(payload.get("path", "")))
                if not path:
                    self._send_json({"ok": False, "error": "路径不能为空"}, 400)
                    return
                open_folder(path)
                self._send_json({"ok": True})
            except Exception as exc:
                WEBUI_LOGGER.exception("打开目录失败")
                audit({
                    "type": "exception",
                    "step": "api_open_out",
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "ok": False,
                    "reason_code": "open_out_failed",
                })
                self._send_json({"ok": False, "error": f"打开失败：{exc}"}, 500)
            return

        if parsed.path == "/api/confirm-generate":
            try:
                payload = self._read_json()
                out_dir = normalize_path(str(payload.get("out_dir", "")))
                agree = bool(payload.get("agree", False))
                if not out_dir:
                    self._send_json({"ok": False, "error": "输出目录不能为空"}, 400)
                    return
                if not agree:
                    self._send_json({"ok": False, "error": "请先确认同意输出"}, 400)
                    return
                review = load_review_data(out_dir)
                xlsx_in = str(review.get("casebook_xlsx_path", "") or "")
                if not xlsx_in or (not Path(xlsx_in).exists()):
                    self._send_json({"ok": False, "error": f"未找到台账文件，无法生成：{xlsx_in}"}, 400)
                    return
                cur = STATE.get_current()
                if cur is not None and cur.status == "running":
                    self._send_json({"ok": False, "error": "已有任务在运行，请稍后"}, 409)
                    return

                gen_payload: Dict[str, object] = {
                    "run_mode": "generate_only",
                    "out_dir": out_dir,
                    "xlsx_in": xlsx_in,
                    "precheck_required": "off",
                    "output_formats": DEFAULT_OUTPUT_FORMATS,
                    "ui_confirm_before_generate": "off",
                    "defense_out": "答辩理由_自动识别.docx",
                    "cross_out": "证据目录_自动识别.docx",
                    "risk_out": "风险报告_自动识别.docx",
                }
                if cur is not None and normalize_path(cur.out_dir) == out_dir:
                    for k in ["defense_out", "cross_out", "risk_out"]:
                        v = str(cur.payload.get(k, "") or "").strip()
                        if v:
                            gen_payload[k] = v

                run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
                cmd = build_run_command(gen_payload)
                job = RunJob(run_id=run_id, cmd=cmd, out_dir=out_dir, payload=gen_payload)
                STATE.set_current(job)
                t = threading.Thread(target=run_job_worker, args=(job,), daemon=True)
                t.start()
                self._send_json({"ok": True, "run_id": run_id})
            except RuntimeError as exc:
                self._send_json({"ok": False, "error": str(exc)}, 400)
            except Exception as exc:
                WEBUI_LOGGER.exception("确认输出失败")
                audit({
                    "type": "exception",
                    "step": "api_confirm_generate",
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "ok": False,
                    "reason_code": "confirm_generate_failed",
                })
                self._send_json({"ok": False, "error": f"启动失败：{exc}"}, 500)
            return

        if parsed.path == "/api/run":
            try:
                payload = self._read_json()
                run_mode = str(payload.get("run_mode", "scan_generate") or "scan_generate")
                evidence_dir = normalize_path(str(payload.get("evidence_dir", "")))
                evidence_dir_fast = normalize_path(str(payload.get("evidence_dir_fast", "")))
                evidence_dir_full = normalize_path(str(payload.get("evidence_dir_full", "")))
                direct_bind_root = normalize_path(str(payload.get("direct_bind_root", "")))
                out_dir = normalize_path(str(payload.get("out_dir", "")))
                payload["evidence_dir"] = evidence_dir
                payload["evidence_dir_fast"] = evidence_dir_fast
                payload["evidence_dir_full"] = evidence_dir_full
                payload["direct_bind_root"] = direct_bind_root
                payload["precheck_required"] = "off"
                payload["output_formats"] = DEFAULT_OUTPUT_FORMATS
                payload["ui_confirm_before_generate"] = "on" if run_mode == "scan_generate" else "off"
                if not out_dir:
                    self._send_json({"ok": False, "error": "输出目录不能为空"}, 400)
                    return
                Path(out_dir).mkdir(parents=True, exist_ok=True)

                if run_mode == "generate_only":
                    xlsx_in = normalize_path(str(payload.get("xlsx_in", "")))
                    if not xlsx_in:
                        self._send_json({"ok": False, "error": "仅重新生成模式需要提供台账文件路径（支持 xlsx/xls/csv/json）"}, 400)
                        return
                    xlsx_p = Path(xlsx_in)
                    if not xlsx_p.exists() or not xlsx_p.is_file():
                        self._send_json({"ok": False, "error": f"台账文件不存在：{xlsx_p}"}, 400)
                        return
                    payload["xlsx_in"] = str(xlsx_p.resolve())
                else:
                    fast_group_lines = build_scan_group_lines(payload, "fast")
                    full_group_lines = build_scan_group_lines(payload, "full")
                    fast_other_lines = str(payload.get("evidence_fast_other_lines", "") or "")
                    full_other_lines = str(payload.get("evidence_full_other_lines", "") or "")
                    fast_all_lines = "\n".join([x for x in [fast_group_lines, fast_other_lines] if x.strip()])
                    full_all_lines = "\n".join([x for x in [full_group_lines, full_other_lines] if x.strip()])

                    if fast_all_lines.strip():
                        evidence_dir_fast = build_scan_mix_dir(
                            out_dir=out_dir,
                            slot="fast",
                            base_dir=evidence_dir_fast,
                            other_lines=fast_all_lines,
                        )
                        payload["evidence_dir_fast"] = evidence_dir_fast
                    if full_all_lines.strip():
                        evidence_dir_full = build_scan_mix_dir(
                            out_dir=out_dir,
                            slot="full",
                            base_dir=evidence_dir_full,
                            other_lines=full_all_lines,
                        )
                        payload["evidence_dir_full"] = evidence_dir_full

                    evidence_inputs: List[Path] = []
                    for d in [evidence_dir, evidence_dir_fast, evidence_dir_full]:
                        if d:
                            evidence_inputs.append(Path(d))
                    for d in evidence_inputs:
                        if not d.is_dir():
                            self._send_json({"ok": False, "error": f"证据目录不存在或不是目录：{d}"}, 400)
                            return
                    for d in evidence_inputs:
                        if Path(out_dir).resolve().is_relative_to(d.resolve()):
                            self._send_json({"ok": False, "error": f"输出目录不能位于证据目录内部：{d}"}, 400)
                            return

                    manual_direct_items: List[Dict[str, str]] = []
                    direct_bind_misc_lines = str(payload.get("direct_bind_misc_lines", "") or "")

                    if direct_bind_root:
                        root_p = Path(direct_bind_root)
                        if not root_p.exists() or not root_p.is_dir():
                            self._send_json({"ok": False, "error": f"直装根目录不存在或不是目录：{root_p}"}, 400)
                            return
                        root_pairs = [
                            ("答辩通知书", "D1_通知书"),
                            ("主体资格证明", "D2_主体资质"),
                            ("委托书", "D3_委托书"),
                            ("照片", "D4_照片"),
                            ("其他", "D5_其他"),
                        ]
                        for label, dirname in root_pairs:
                            rp = root_p / dirname
                            if rp.exists():
                                manual_direct_items.append({
                                    "label": label,
                                    "path": str(rp.resolve()),
                                    "name": "",
                                })
                        if direct_bind_misc_lines.strip():
                            root_misc_items = parse_direct_bind_lines(direct_bind_misc_lines)
                            for it in root_misc_items:
                                p = normalize_path(it.get("path", ""))
                                if not p:
                                    continue
                                pp = Path(p)
                                if not pp.exists():
                                    self._send_json({"ok": False, "error": f"直装根目录“其他扩展”路径不存在：{pp}"}, 400)
                                    return
                                lb = str(it.get("label", "") or "").strip() or "其他"
                                if not lb.startswith("其他"):
                                    lb = f"其他-{lb}"
                                manual_direct_items.append({
                                    "label": lb,
                                    "path": str(pp.resolve()),
                                    "name": str(it.get("name", "") or "").strip(),
                                })

                    fixed_direct_pairs = [
                        ("答辩通知书", normalize_path(str(payload.get("direct_notice_path", ""))), str(payload.get("direct_notice_name", "") or "").strip()),
                        ("主体资格证明", normalize_path(str(payload.get("direct_subject_path", ""))), str(payload.get("direct_subject_name", "") or "").strip()),
                        ("委托书", normalize_path(str(payload.get("direct_power_path", ""))), str(payload.get("direct_power_name", "") or "").strip()),
                        ("照片", normalize_path(str(payload.get("direct_photo_path", ""))), str(payload.get("direct_photo_name", "") or "").strip()),
                    ]
                    for label, p, custom_name in fixed_direct_pairs:
                        if not p:
                            continue
                        pp = Path(p)
                        if not pp.exists():
                            self._send_json({"ok": False, "error": f"直装材料路径不存在：{label} -> {pp}"}, 400)
                            return
                        manual_direct_items.append({
                            "label": label,
                            "path": str(pp.resolve()),
                            "name": custom_name,
                        })

                    direct_other_lines = str(payload.get("direct_other_lines", "") or "")
                    if not direct_other_lines.strip():
                        direct_other_lines = str(payload.get("direct_bind_lines", "") or "")
                    if direct_other_lines.strip():
                        other_items = parse_direct_bind_lines(direct_other_lines)
                        for it in other_items:
                            p = normalize_path(it.get("path", ""))
                            if not p:
                                continue
                            pp = Path(p)
                            if not pp.exists():
                                self._send_json({"ok": False, "error": f"直装“其他”路径不存在：{p}"}, 400)
                                return
                            lb = str(it.get("label", "") or "").strip() or "其他"
                            if not lb.startswith("其他"):
                                lb = f"其他-{lb}"
                            manual_direct_items.append({
                                "label": lb,
                                "path": str(pp.resolve()),
                                "name": str(it.get("name", "") or "").strip(),
                            })
                    if (not direct_bind_root) and direct_bind_misc_lines.strip():
                        misc_items = parse_direct_bind_lines(direct_bind_misc_lines)
                        for it in misc_items:
                            p = normalize_path(it.get("path", ""))
                            if not p:
                                continue
                            pp = Path(p)
                            if not pp.exists():
                                self._send_json({"ok": False, "error": f"直装“其他扩展”路径不存在：{p}"}, 400)
                                return
                            lb = str(it.get("label", "") or "").strip() or "其他"
                            if not lb.startswith("其他"):
                                lb = f"其他-{lb}"
                            manual_direct_items.append({
                                "label": lb,
                                "path": str(pp.resolve()),
                                "name": str(it.get("name", "") or "").strip(),
                            })

                    direct_bind_config = normalize_path(str(payload.get("direct_bind_config", "")))
                    config_items: List[Dict[str, str]] = []
                    if direct_bind_config:
                        dcfg = Path(direct_bind_config)
                        if not dcfg.exists() or not dcfg.is_file():
                            self._send_json({"ok": False, "error": f"直装配置文件不存在：{dcfg}"}, 400)
                            return
                        try:
                            raw = json.loads(dcfg.read_text(encoding="utf-8"))
                            config_items = raw.get("items", []) if isinstance(raw, dict) else (raw if isinstance(raw, list) else [])
                        except Exception as exc:
                            self._send_json({"ok": False, "error": f"直装配置文件解析失败：{exc}"}, 400)
                            return
                        fixed_cfg_items: List[Dict[str, str]] = []
                        for it in config_items:
                            if not isinstance(it, dict):
                                continue
                            p = normalize_path(str(it.get("path", "") or ""))
                            if not p:
                                continue
                            pp = Path(p)
                            if not pp.exists():
                                self._send_json({"ok": False, "error": f"直装配置路径不存在：{pp}"}, 400)
                                return
                            fixed_cfg_items.append({
                                "label": str(it.get("label", "") or "其他").strip() or "其他",
                                "path": str(pp.resolve()),
                                "name": str(it.get("name", "") or it.get("custom_name", "") or "").strip(),
                            })
                        config_items = fixed_cfg_items

                    merged_items = manual_direct_items + config_items
                    if merged_items:
                        manifest_path = Path(out_dir) / "direct_bind_manifest_manual.json"
                        manifest_path.write_text(
                            json.dumps({"items": merged_items}, ensure_ascii=False, indent=2),
                            encoding="utf-8",
                        )
                        payload["direct_bind_config"] = str(manifest_path.resolve())
                    elif direct_bind_config:
                        payload["direct_bind_config"] = str(Path(direct_bind_config).resolve())

                    has_scan_inputs = len(evidence_inputs) > 0
                    has_direct_inputs = bool(str(payload.get("direct_bind_config", "") or "").strip())
                    if not has_scan_inputs and not has_direct_inputs:
                        self._send_json(
                            {"ok": False, "error": "请至少提供扫描证据目录（fast/full/不分类文件包）或直装材料"},
                            400,
                        )
                        return

                cur = STATE.get_current()
                if cur is not None and cur.status == "running":
                    self._send_json({"ok": False, "error": "已有任务在运行，请稍后"}, 409)
                    return

                run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
                cmd = build_run_command(payload)
                job = RunJob(run_id=run_id, cmd=cmd, out_dir=out_dir, payload=payload)
                STATE.set_current(job)

                t = threading.Thread(target=run_job_worker, args=(job,), daemon=True)
                t.start()
                self._send_json({"ok": True, "run_id": run_id})
            except RuntimeError as exc:
                self._send_json({"ok": False, "error": str(exc)}, 400)
            except Exception as exc:
                WEBUI_LOGGER.exception("启动任务失败")
                audit({
                    "type": "exception",
                    "step": "api_run",
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "ok": False,
                    "reason_code": "api_run_failed",
                })
                self._send_json({"ok": False, "error": f"启动失败：{exc}"}, 500)
            return

        self._send_json({"ok": False, "error": "Not Found"}, 404)


def main() -> None:
    global WEBUI_AUTH_TOKEN, WEBUI_REQUIRE_AUTH, WEBUI_LOGGER
    ap = argparse.ArgumentParser(description="撤三证据智审系统本地Web界面")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--token", default="", help="非本机监听时必须提供，写接口使用 Bearer Token 鉴权")
    ap.add_argument("--no-browser", action="store_true", help="启动后不自动打开浏览器")
    args = ap.parse_args()

    token = str(args.token or os.environ.get("NONUSE_WEBUI_TOKEN", "")).strip()
    WEBUI_AUTH_TOKEN = token
    WEBUI_REQUIRE_AUTH = (args.host != "127.0.0.1") or bool(token)
    set_run_context(BASE_DIR / "logs", WEBUI_RUN_ID)
    WEBUI_LOGGER = setup_logger(__name__, log_dir=(BASE_DIR / "logs"))
    if args.host != "127.0.0.1" and not token:
        WEBUI_LOGGER.error("非本机绑定必须显式提供 --token 或 NONUSE_WEBUI_TOKEN")
        audit({
            "type": "run_end",
            "step": "webui_main",
            "ok": False,
            "reason_code": "missing_token_for_non_localhost",
            "exit_code": 2,
        })
        raise SystemExit(2)

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    audit({
        "type": "run_start",
        "step": "webui_main",
        "ok": True,
        "host": args.host,
        "port": args.port,
        "auth_required": WEBUI_REQUIRE_AUTH,
    })
    print(f"[{now_iso()}] WebUI running at http://{args.host}:{args.port}/")
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(f"http://{args.host}:{args.port}/")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        WEBUI_LOGGER.info("收到中断信号，准备关闭 WebUI")
        audit({
            "type": "signal",
            "step": "webui_main",
            "file": __file__,
            "ok": True,
            "reason_code": "keyboard_interrupt",
        })
    finally:
        server.server_close()
        audit({
            "type": "run_end",
            "step": "webui_main",
            "ok": True,
            "exit_code": 0,
        })


if __name__ == "__main__":
    main()
