#!/usr/bin/env python3
"""Build sub-agent parsing task prompt from raw input + contract.

This helper prepares a deterministic task payload for sessions_spawn.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build sub-agent parser task prompt")
    parser.add_argument("--input-file", required=True, help="Raw input text/txt/md/json file")
    parser.add_argument("--contract-file", required=True, help="Path to subagent-parser-contract.md")
    parser.add_argument("--output", help="Write prompt to this file")
    parser.add_argument("--project-id", default="", help="Optional project id hint")
    args = parser.parse_args()

    raw_input = load_text(Path(args.input_file).expanduser()).strip()
    contract = load_text(Path(args.contract_file).expanduser()).strip()

    prompt = f"""你是 storyboard 解析子代理。请严格根据以下契约输出 JSON。

[Contract]
{contract}

[Extra Requirements]
1) 仅输出 JSON，不要 markdown，不要解释。
2) 模型默认：video=doubao-seedance-1-5-pro-251215, image=doubao-seedream-5-0-260128。
3) continuity 默认 mode=style-anchor，除非原文明确要求 chain-last-frame。
4) 画内中文文字请强化“清晰可读、无乱码”。
5) 若 project_id 缺失，使用: {args.project_id or 'story-auto'}。

[Raw Input]
<<<RAW_INPUT>>>
{raw_input}
<<<END_RAW_INPUT>>>
"""

    if args.output:
        out_path = Path(args.output).expanduser()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(prompt, encoding="utf-8")
        print(str(out_path))
    else:
        print(prompt)


if __name__ == "__main__":
    main()
