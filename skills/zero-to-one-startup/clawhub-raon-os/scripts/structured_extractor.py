#!/usr/bin/env python3
"""
Raon OS — Structured Extractor
정부공고 텍스트에서 구조화된 JSON 스키마 추출 및 필터링.

Python 3.9+ compatible
"""

from __future__ import annotations  # Python 3.9 compatibility

import json
import re
import sys
from pathlib import Path
from typing import Optional, Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from raon_llm import chat, prompt_to_messages


# ─── Schema 정의 ─────────────────────────────────────────────────────────────

GOV_PROGRAM_SCHEMA: dict = {
    "program_name": str,
    "operator": str,           # 운영기관
    "eligibility": list,       # 자격조건 리스트
    "excluded": list,          # 제외 대상
    "budget_won": int,         # 예산 (원)
    "deadline": str,           # 마감일 ISO 형식 (YYYY-MM-DD)
    "application_url": str,
    "industry_focus": list,    # 우대 분야
    "keywords": list,          # 검색 키워드
}


def _default_schema() -> dict:
    """빈 스키마 인스턴스 반환."""
    return {
        "program_name": "",
        "operator": "",
        "eligibility": [],
        "excluded": [],
        "budget_won": 0,
        "deadline": "",
        "application_url": "",
        "industry_focus": [],
        "keywords": [],
    }


# ─── 추출기 ──────────────────────────────────────────────────────────────────

def extract_program_schema(text: str) -> dict:
    """
    LLM으로 공고문 텍스트 → GOV_PROGRAM_SCHEMA JSON 추출.
    LLM 실패 시 규칙 기반 추출로 폴백.
    """
    extract_prompt = (
        f"다음 정부 지원사업 공고문에서 구조화된 정보를 추출해. JSON 형식으로만 답해.\n\n"
        f"공고문:\n{text[:3000]}\n\n"
        f"추출할 정보:\n"
        f"- program_name: 사업명\n"
        f"- operator: 운영기관 (주관기관)\n"
        f"- eligibility: 자격조건 리스트 (배열)\n"
        f"- excluded: 지원 제외 대상 리스트 (배열)\n"
        f"- budget_won: 총 예산 (원 단위 숫자, 없으면 0)\n"
        f"- deadline: 마감일 (YYYY-MM-DD 형식, 없으면 \"\")\n"
        f"- application_url: 신청 URL (없으면 \"\")\n"
        f"- industry_focus: 우대 분야/업종 리스트 (배열)\n"
        f"- keywords: 검색 키워드 리스트 (배열)\n\n"
        f"JSON만 출력 (설명 없이):"
    )

    default = _default_schema()

    try:
        result = chat(prompt_to_messages(extract_prompt))
        if result:
            # JSON 파싱
            json_match = re.search(r"\{.*\}", result, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                schema = dict(default)

                # 타입 검증 및 병합
                _merge_str_field(schema, parsed, "program_name")
                _merge_str_field(schema, parsed, "operator")
                _merge_str_field(schema, parsed, "deadline")
                _merge_str_field(schema, parsed, "application_url")

                _merge_list_field(schema, parsed, "eligibility")
                _merge_list_field(schema, parsed, "excluded")
                _merge_list_field(schema, parsed, "industry_focus")
                _merge_list_field(schema, parsed, "keywords")

                if "budget_won" in parsed:
                    try:
                        raw = parsed["budget_won"]
                        # 문자열일 경우 숫자만 추출
                        if isinstance(raw, str):
                            nums = re.findall(r"\d+", raw.replace(",", ""))
                            schema["budget_won"] = int(nums[0]) if nums else 0
                        else:
                            schema["budget_won"] = int(raw)
                    except (ValueError, TypeError):
                        schema["budget_won"] = 0

                return schema
    except Exception as e:
        print(f"[StructuredExtractor] LLM 추출 실패: {e}", file=sys.stderr)

    # Fallback: 규칙 기반 추출
    return _rule_based_extract(text, default)


def _merge_str_field(schema: dict, parsed: dict, key: str) -> None:
    """문자열 필드 병합 (타입 안전)."""
    if key in parsed and isinstance(parsed[key], str):
        schema[key] = parsed[key]


def _merge_list_field(schema: dict, parsed: dict, key: str) -> None:
    """리스트 필드 병합 (타입 안전)."""
    if key in parsed:
        items = parsed[key]
        if isinstance(items, list):
            schema[key] = [str(i) for i in items]
        elif items:
            schema[key] = [str(items)]


def _rule_based_extract(text: str, default: dict) -> dict:
    """LLM 실패 시 정규표현식 기반 추출."""
    schema = dict(default)

    # 사업명
    name_match = re.search(r"사업명[:\s]+([^\n]+)", text)
    if name_match:
        schema["program_name"] = name_match.group(1).strip()

    # 운영기관
    op_match = re.search(r"(?:주관기관|운영기관|담당기관)[:\s]+([^\n]+)", text)
    if op_match:
        schema["operator"] = op_match.group(1).strip()

    # 마감일
    deadline_patterns = [
        r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})",
        r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일",
    ]
    for pattern in deadline_patterns:
        m = re.search(pattern, text)
        if m:
            g = m.groups()
            if len(g) >= 3:
                schema["deadline"] = f"{int(g[0]):04d}-{int(g[1]):02d}-{int(g[2]):02d}"
                break

    # URL
    url_match = re.search(r"https?://[^\s<>\"]+", text)
    if url_match:
        schema["application_url"] = url_match.group()

    # 예산 (억원 → 원 변환)
    budget_match = re.search(r"예산[:\s]*([0-9,]+)\s*억\s*원", text)
    if budget_match:
        try:
            won = int(budget_match.group(1).replace(",", ""))
            schema["budget_won"] = won * 100_000_000
        except ValueError:
            pass

    # 키워드 추출
    known_keywords = [
        "TIPS", "R&D", "스타트업", "창업", "AI", "바이오", "ICT",
        "제조", "딥테크", "SaaS", "핀테크", "헬스케어",
    ]
    schema["keywords"] = [kw for kw in known_keywords if kw in text]

    # 자격조건 (간단 추출)
    eligibility = []
    for m in re.finditer(r"(?:자격|조건|요건)[:\s]+([^\n.。]+)", text):
        eligibility.append(m.group(1).strip())
    if eligibility:
        schema["eligibility"] = eligibility[:5]

    return schema


# ─── 필터 ────────────────────────────────────────────────────────────────────

def filter_programs(programs: list, criteria: dict) -> list:
    """
    하드 필터 + 소프트 랭킹으로 프로그램 목록 필터링.

    criteria 예시:
    {
        "eligibility": ["창업 5년 이내"],   # eligibility 텍스트 포함 조건
        "excluded_check": ["폐업"],         # excluded에 이 항목이 없어야 함
        "deadline_after": "2026-03-01",     # 마감일 이후
        "industry": "AI",                  # industry_focus 매칭
        "keywords": ["딥테크"],             # keywords 매칭
    }

    반환: 소프트 랭킹 순으로 정렬된 프로그램 리스트
    """
    if not programs:
        return []

    # ── 하드 필터 ──
    passed = []
    for p in programs:
        # deadline_after 필터
        if "deadline_after" in criteria:
            deadline = p.get("deadline", "")
            if deadline and deadline < criteria["deadline_after"]:
                continue

        # excluded_check: 제외 대상에 해당하면 스킵
        if "excluded_check" in criteria:
            excluded = p.get("excluded", [])
            excluded_text = " ".join(str(e) for e in excluded).lower()
            skip = any(
                ec.lower() in excluded_text for ec in criteria["excluded_check"]
            )
            if skip:
                continue

        passed.append(p)

    # ── 소프트 랭킹 ──
    def soft_score(p: dict) -> float:
        score = 0.0

        # industry_focus 매칭
        if "industry" in criteria:
            for focus in p.get("industry_focus", []):
                if criteria["industry"].lower() in str(focus).lower():
                    score += 2.0

        # keywords 매칭
        if "keywords" in criteria:
            p_keywords = p.get("keywords", [])
            for kw in criteria["keywords"]:
                for pk in p_keywords:
                    if kw.lower() in str(pk).lower():
                        score += 1.0

        # eligibility 텍스트 매칭
        if "eligibility" in criteria:
            eligibility_text = " ".join(
                str(e) for e in p.get("eligibility", [])
            ).lower()
            for ec in criteria["eligibility"]:
                if ec.lower() in eligibility_text:
                    score += 1.5

        # budget 보너스
        if p.get("budget_won", 0) > 0:
            score += 0.5

        return score

    ranked = sorted(passed, key=soft_score, reverse=True)
    return ranked


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Raon OS Structured Extractor")
    parser.add_argument("--text", "-t", help="공고문 텍스트 (직접 입력)")
    parser.add_argument("--file", "-f", help="공고문 텍스트 파일 경로")
    args = parser.parse_args()

    input_text = ""
    if args.file:
        input_text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        input_text = args.text
    else:
        parser.print_help()
        sys.exit(1)

    schema = extract_program_schema(input_text)
    print(json.dumps(schema, ensure_ascii=False, indent=2))
