#!/usr/bin/env python3
"""Tagger: richer tag inference for knowledge-base-collector.

Design goals:
- Keep tags hashtag-style (e.g. #ai #agent #claude-code).
- Add more specific tags while keeping the set small and stable.
- Deterministic & rule-based (no model calls).

Notes:
- This is intentionally heuristic. Users can always override via --tags.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Pattern, Sequence, Tuple


@dataclass(frozen=True)
class Rule:
    tag: str
    patterns: Sequence[Pattern[str]]


def _re(s: str) -> Pattern[str]:
    return re.compile(s, re.I)


# Stable tag vocabulary (extend cautiously).
RULES: List[Rule] = [
    # AI / LLM
    Rule("#ai", [_re(r"\b(llm|gpt|transformer|diffusion|prompt)\b"), _re(r"\bopenai\b"), _re(r"\banthropic\b"), _re(r"\bclaude\b"), _re(r"\bgemini\b"), _re(r"\bdeepseek\b"), _re(r"大模型|模型能力|多模态")]),
    Rule("#agent", [_re(r"\bagent\b"), _re(r"\bautonomous\b"), _re(r"代理(?!\w)")]),
    Rule("#coding-agent", [_re(r"claude\s*code"), _re(r"codex"), _re(r"cursor"), _re(r"aider"), _re(r"copilot"), _re(r"\bide\b"), _re(r"代码代理|编程代理")]),
    Rule("#rag", [_re(r"\brag\b"), _re(r"retrieval"), _re(r"向量|embedding|向量检索")]),
    Rule("#mcp", [_re(r"\bmcp\b"), _re(r"model\s*context\s*protocol"), _re(r"上下文协议")]),
    Rule("#prompt-injection", [_re(r"prompt\s*injection"), _re(r"提示注入")]),
    Rule("#security", [_re(r"\bsecurity\b"), _re(r"\bvuln"), _re(r"\bcve\b"), _re(r"风控|安全|攻击|注入")]),

    # Infra / Eng
    Rule("#engineering", [_re(r"kubernetes|\bk8s\b"), _re(r"docker"), _re(r"terraform"), _re(r"postgres|mysql|redis"), _re(r"latency|throughput|benchmark|perf"), _re(r"工程|性能|压测")]),
    Rule("#database", [_re(r"postgres|mysql|sqlite|mongo"), _re(r"数据库")]),
    Rule("#devtools", [_re(r"devtools|chrome\s*devtools"), _re(r"cli\b"), _re(r"命令行")]),

    # Product / Business
    Rule("#product", [_re(r"产品|pmf|用户|体验|to\s*c|toc|to\s*b|tob")]),
    Rule("#pricing", [_re(r"pricing|定价|订阅|付费|价格")]),
    Rule("#growth", [_re(r"增长|留存|转化|获客|activation|retention|conversion")]),
    Rule("#startup", [_re(r"startup|融资|估值|vc|创始人|创业")]),

    # Social / Content
    Rule("#social", [_re(r"社交|social")]),
    Rule("#content", [_re(r"内容|写作|newsletter|blog|文章")]),

    # Markets
    Rule("#trading", [_re(r"\bbtc\b|\beth\b|\bsol\b"), _re(r"pnl|portfolio|options|funding|liquidation"), _re(r"交易|仓位|回撤|止损")]),
]

# Entity-like tags (kept short and stable)
ENTITY_RULES: List[Tuple[str, Pattern[str]]] = [
    ("#claude-code", _re(r"claude\s*code")),
    ("#openclaw", _re(r"openclaw")),
    ("#chatgpt", _re(r"chatgpt")),
]


def detect_language_tags(text: str) -> List[str]:
    # crude but useful
    has_zh = bool(re.search(r"[\u4e00-\u9fff]", text))
    has_en = bool(re.search(r"[A-Za-z]", text))
    out = []
    if has_zh:
        out.append("#lang:zh")
    if has_en:
        out.append("#lang:en")
    return out


def infer_tags_from_text(text: str, base_tags: Iterable[str] = ()) -> List[str]:
    text = text or ""
    low = text.lower()

    tags: List[str] = []
    tags.extend([t for t in base_tags if t])

    # language tags
    tags.extend(detect_language_tags(text))

    # rules
    for rule in RULES:
        if any(p.search(low) for p in rule.patterns):
            tags.append(rule.tag)

    # entities
    for tag, pat in ENTITY_RULES:
        if pat.search(low):
            tags.append(tag)

    # de-dup while preserving order
    out: List[str] = []
    for t in tags:
        if t and t not in out:
            out.append(t)

    # keep tag set bounded (source/type should appear first in base_tags)
    MAX_TAGS = 14
    if len(out) > MAX_TAGS:
        out = out[:MAX_TAGS]

    return out
