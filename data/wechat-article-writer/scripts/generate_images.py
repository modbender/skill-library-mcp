#!/usr/bin/env python3
"""
公众号图片生成脚本
使用智谱AI API批量生成配图
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

try:
    from zhipuai import ZhipuAI
except ImportError:
    print("请先安装 zhipuai 库: pip install zhipuai", file=sys.stderr)
    sys.exit(1)


_CONFIG_LINE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*(.*)$")


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_config(path: Path) -> dict[str, str]:
    """加载配置文件"""
    config: dict[str, str] = {}
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = _CONFIG_LINE_RE.match(line)
        if not match:
            continue
        key = match.group(1).upper()
        value = _strip_quotes(match.group(2))
        config[key] = value
    return config


def load_requests(input_path: Path) -> list[dict[str, Any]]:
    """加载请求列表"""
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    if input_path.suffix.lower() == ".jsonl":
        requests_list: list[dict[str, Any]] = []
        for line_no, raw_line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_no}: {exc}") from exc
            if not isinstance(obj, dict):
                raise ValueError(f"Invalid JSONL at line {line_no}: expected object")
            requests_list.append(obj)
        return requests_list

    obj = json.loads(input_path.read_text(encoding="utf-8"))
    if isinstance(obj, list) and all(isinstance(item, dict) for item in obj):
        return list(obj)
    raise ValueError("Unsupported input format: use .jsonl or a JSON array")


def _safe_filename_part(value: str) -> str:
    """生成安全的文件名"""
    value = value.strip()
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    return value[:80] if value else "item"


def download_image(url: str, output_path: Path) -> bool:
    """下载图片并保存"""
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        output_path.write_bytes(data)
        return True
    except Exception as e:
        print(f"  下载失败: {e}", file=sys.stderr)
        return False


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="公众号图片批量生成（智谱AI）")
    parser.add_argument("--config", type=Path, default=Path("scripts/image.env"))
    parser.add_argument("--input", type=Path, required=True, help="输入文件（JSON或JSONL格式）")
    parser.add_argument("--out", type=Path, default=None, help="输出目录")
    parser.add_argument("--model", type=str, default=None, help="模型名称（覆盖配置文件）")
    args = parser.parse_args(argv)

    # 加载配置
    config = load_config(args.config)
    api_key = config.get("API_KEY", "").strip()
    model = args.model or config.get("MODEL", "cogview-4").strip()

    if not api_key:
        raise ValueError("Missing API_KEY in config. 请在 image.env 中设置 API_KEY=你的密钥")

    # 初始化客户端
    client = ZhipuAI(api_key=api_key)

    # 加载请求
    raw_requests = load_requests(args.input)
    if not raw_requests:
        print("No valid requests found.", file=sys.stderr)
        return 2

    # 确定输出目录
    if args.out is None:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_dir = Path("outputs") / f"images-{stamp}"
    else:
        out_dir = args.out

    out_dir.mkdir(parents=True, exist_ok=True)

    # 处理每个请求
    success_count = 0
    for idx, raw in enumerate(raw_requests, start=1):
        prompt = str(raw.get("prompt", "")).strip()
        if not prompt:
            continue

        request_id = str(raw.get("id", f"{idx:02d}")).strip()
        request_model = str(raw.get("model", model)).strip()
        request_size = str(raw.get("size", "900x383")).strip()

        print(f"[{request_id}] 生成中... (model: {request_model}, size: {request_size})")

        try:
            # GLM-Image 模型不支持 size 参数
            if request_model.lower() == "glm-image":
                response = client.images.generations(
                    model=request_model,
                    prompt=prompt,
                )
            else:
                # 解析尺寸
                width, height = request_size.lower().split("x")
                size_param = f"{width}*{height}"
                response = client.images.generations(
                    model=request_model,
                    prompt=prompt,
                    size=size_param,
                )

            # 提取图片URL
            if hasattr(response, 'data') and response.data and len(response.data) > 0:
                image_url = response.data[0].url
                print(f"  URL: {image_url}")

                # 下载图片
                filename = f"{request_id}.png"
                output_path = out_dir / filename

                if download_image(image_url, output_path):
                    print(f"  [{request_id}] Saved: {filename}")
                    success_count += 1
                else:
                    print(f"  [{request_id}] 下载失败")
            else:
                print(f"  [{request_id}] 响应中没有图片数据")
                print(f"  响应内容: {response}")

        except Exception as exc:
            print(f"  [{request_id}] Error: {exc}", file=sys.stderr)
            import traceback
            traceback.print_exc()

    print(f"\n完成！成功: {success_count}/{len(raw_requests)}")
    print(f"输出目录: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
