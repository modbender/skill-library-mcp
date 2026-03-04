#!/usr/bin/env python3
"""
parse_web3_scope.py
Parse Web3 bug bounty scope/rules files into structured JSON.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PLATFORM_KEYWORDS = {
    "immunefi": "immunefi",
    "hackenproof": "hackenproof",
    "hackerone": "hackerone-web3",
    "bugcrowd": "bugcrowd-web3",
    "yeswehack": "yeswehack",
}

CHAIN_KEYWORDS = {
    "ethereum": "ethereum",
    "mainnet": "ethereum",
    "arbitrum": "arbitrum",
    "base": "base",
    "optimism": "optimism",
    "polygon": "polygon",
    "bsc": "bsc",
    "avalanche": "avalanche",
    "sonic": "sonic",
    "sui": "sui",
}

ASSET_KEYWORDS = {
    "smart contract": "smart-contract",
    "contract": "smart-contract",
    "wallet": "wallet",
    "sdk": "sdk",
    "bridge": "bridge",
    "frontend": "frontend",
    "dapp": "frontend",
    "api": "api",
    "off-chain": "offchain",
    "offchain": "offchain",
}


def parse_scope(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    lower = text.lower()

    data: dict[str, Any] = {
        "program_name": extract_program_name(lines, path.stem),
        "platform": detect_platform(lower),
        "in_scope": [],
        "out_of_scope": [],
        "excluded_vulnerability_classes": [],
        "chains": sorted(set(extract_chains(lower))),
        "asset_types": sorted(set(extract_asset_types(lower))),
        "special_rules": extract_special_rules(lines),
    }

    data["in_scope"] = extract_section_items(lines, ("in scope", "scope included"), negate=False)
    data["out_of_scope"] = extract_section_items(lines, ("out of scope", "excluded"), negate=True)
    data["excluded_vulnerability_classes"] = extract_excluded_classes(text)
    return data


def extract_program_name(lines: list[str], fallback: str) -> str:
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return fallback


def detect_platform(lower_text: str) -> str:
    for needle, name in PLATFORM_KEYWORDS.items():
        if needle in lower_text:
            return name
    return "unknown"


def extract_chains(lower_text: str) -> list[str]:
    found: list[str] = []
    for needle, chain in CHAIN_KEYWORDS.items():
        if re.search(rf"\b{re.escape(needle)}\b", lower_text):
            found.append(chain)
    return found


def extract_asset_types(lower_text: str) -> list[str]:
    found: list[str] = []
    for needle, asset in ASSET_KEYWORDS.items():
        if needle in lower_text:
            found.append(asset)
    return found


def extract_section_items(lines: list[str], section_names: tuple[str, ...], negate: bool) -> list[str]:
    found: list[str] = []
    in_section = False
    section_pattern = re.compile("|".join(re.escape(s) for s in section_names), re.IGNORECASE)
    bullet_pattern = re.compile(r"^\s*[-*+]\s+(.+)$")
    numbered_pattern = re.compile(r"^\s*\d+\.\s+(.+)$")

    for raw in lines:
        line = raw.strip()
        if line.startswith("#"):
            in_section = bool(section_pattern.search(line))
            continue
        if not in_section:
            continue
        if line.startswith("#"):
            in_section = False
            continue
        m = bullet_pattern.match(raw) or numbered_pattern.match(raw)
        if m:
            value = m.group(1).strip()
            if value and value not in found:
                found.append(value)

    if not found:
        fallback_pattern = re.compile(r"^\s*[-*+]\s+(.+)$", re.MULTILINE)
        for item in fallback_pattern.findall("\n".join(lines)):
            lower = item.lower()
            if negate and ("out" in lower or "exclude" in lower):
                found.append(item.strip())
            elif not negate and ("http" in lower or "contract" in lower or "address" in lower):
                found.append(item.strip())
    return found


def extract_excluded_classes(text: str) -> list[str]:
    lower = text.lower()
    classes = [
        "gas optimization",
        "centralization risk",
        "phishing/social engineering",
        "best practices only",
        "informational",
        "dos with no impact",
    ]
    found: list[str] = []
    for item in classes:
        if item in lower:
            found.append(item)
    pattern = re.compile(r"(?:not eligible|excluded|out of scope)[:\s]+([^\n]+)", re.IGNORECASE)
    for match in pattern.findall(text):
        val = match.strip()
        if val and val not in found:
            found.append(val)
    return found


def extract_special_rules(lines: list[str]) -> list[str]:
    rules: list[str] = []
    markers = (
        "no automated scanning",
        "testnet only",
        "kyc required",
        "forbidden",
        "no dos",
        "responsible disclosure",
    )
    for line in lines:
        low = line.lower()
        if any(m in low for m in markers):
            rules.append(line.strip())
    return rules


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse a Web3 scope/rules file into structured JSON.")
    parser.add_argument("scope_file", help="Path to the scope file (md/txt).")
    parser.add_argument("--output", "-o", help="Output JSON file path.")
    parser.add_argument("--json-only", action="store_true", help="Print JSON only.")
    args = parser.parse_args()

    path = Path(args.scope_file)
    if not path.exists():
        raise SystemExit(f"Scope file not found: {path}")

    data = parse_scope(path)
    output = json.dumps(data, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        if not args.json_only:
            print(f"Structured scope saved to: {args.output}")

    if args.json_only:
        print(output)
        return

    print(f"Program: {data['program_name']}")
    print(f"Platform: {data['platform']}")
    print(f"Chains: {', '.join(data['chains']) if data['chains'] else 'unknown'}")
    print(f"In scope items: {len(data['in_scope'])}")
    print(f"Out-of-scope items: {len(data['out_of_scope'])}")
    if not args.output:
        print(output)


if __name__ == "__main__":
    main()
