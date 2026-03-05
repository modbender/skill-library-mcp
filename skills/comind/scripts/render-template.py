#!/usr/bin/env python3
"""
CoMind 模板渲染脚本

用法:
  python render-template.py <template_name> [--base-url URL] [--token TOKEN] [--extra KEY=VALUE ...]

示例:
  python render-template.py system-info --base-url http://localhost:3000 --token xxx
  python render-template.py task-push --extra task_id=abc --extra task_title="写报告"
  python render-template.py task-board --extra project_id=abc --extra project_name="项目A"

模板列表:
  system-info   — 系统信息（团队成员、项目概览）
  task-push     — 任务推送上下文
  task-board    — 任务看板 MD 同步格式
  schedules     — 定时任务 MD 同步格式
  deliveries    — 文档交付 MD 同步格式
  chat-project  — 项目聊天上下文
  chat-task     — 任务聊天上下文
  chat-schedule — 定时任务聊天上下文

当提供 --base-url 和 --token 时，脚本会从 CoMind API 获取实时数据填充模板。
否则输出模板原文供参考。
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime


def get_script_dir() -> Path:
    return Path(__file__).resolve().parent


def get_references_dir() -> Path:
    return get_script_dir().parent / "references"


def read_template(name: str) -> str:
    """读取 references/ 目录下的模板文件"""
    path = get_references_dir() / f"{name}.md"
    if not path.exists():
        print(f"错误: 模板 '{name}' 不存在 ({path})", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def strip_frontmatter(content: str) -> str:
    """移除 YAML frontmatter"""
    return re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)


def fetch_system_context(base_url: str, token: str) -> dict:
    """从 CoMind API 获取系统上下文（成员、项目等）"""
    # 通过 MCP external API 批量获取数据
    url = f"{base_url.rstrip('/')}/api/mcp/external"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    # 获取项目列表（通过 search_documents 或直接查询）
    # 由于 V2 的 external API 沿用 V1 的工具体系，我们可以调用多个工具
    results = {}

    # 尝试通过 get_template 获取（如果 V2 仍有此工具）
    try:
        payload = json.dumps({"tool": "get_template", "parameters": {"template_name": "system-info"}}).encode()
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("result"):
                results["system_info"] = data["result"]
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        pass

    return results


def render_mustache(template: str, context: dict) -> str:
    """简易 Mustache 模板渲染"""
    result = strip_frontmatter(template)

    # 处理循环块 {{#array}}...{{/array}}
    def replace_section(match):
        key = match.group(1)
        block = match.group(2)
        value = context.get(key)
        if isinstance(value, list):
            parts = []
            for i, item in enumerate(value):
                rendered = block
                if isinstance(item, dict):
                    for k, v in item.items():
                        rendered = rendered.replace(f"{{{{.{k}}}}}", format_val(v))
                    rendered = rendered.replace("{{.}}", str(item))
                else:
                    rendered = rendered.replace("{{.}}", str(item))
                rendered = rendered.replace("{{@index}}", str(i))
                rendered = rendered.replace("{{@number}}", str(i + 1))
                parts.append(rendered)
            return "".join(parts)
        if value:
            return block
        return ""

    result = re.sub(r"\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}", replace_section, result, flags=re.DOTALL)

    # 处理反向条件块 {{^section}}...{{/section}}
    def replace_inverse(match):
        key = match.group(1)
        block = match.group(2)
        value = context.get(key)
        if not value or (isinstance(value, list) and len(value) == 0):
            return block
        return ""

    result = re.sub(r"\{\{\^(\w+)\}\}(.*?)\{\{/\1\}\}", replace_inverse, result, flags=re.DOTALL)

    # 处理嵌套属性 {{a.b.c}}
    def replace_var(match):
        path = match.group(1)
        parts = path.split(".")
        value = context
        for part in parts:
            if not isinstance(value, dict):
                return match.group(0)
            value = value.get(part)
            if value is None:
                return ""
        return format_val(value)

    result = re.sub(r"\{\{([\w.]+)\}\}", replace_var, result)

    return result


def format_val(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def main():
    parser = argparse.ArgumentParser(description="CoMind 模板渲染")
    parser.add_argument("template", nargs="?", default=None, help="模板名称")
    parser.add_argument("--base-url", default=os.environ.get("COMIND_BASE_URL", ""), help="CoMind 实例地址")
    parser.add_argument("--token", default=os.environ.get("COMIND_API_TOKEN", ""), help="API Token")
    parser.add_argument("--extra", action="append", default=[], help="额外变量 KEY=VALUE")
    parser.add_argument("--list", action="store_true", help="列出所有可用模板")
    parser.add_argument("--raw", action="store_true", help="输出原始模板（不渲染）")
    args = parser.parse_args()

    if args.list:
        refs_dir = get_references_dir()
        if refs_dir.exists():
            for f in sorted(refs_dir.glob("*.md")):
                print(f"  {f.stem}")
        return

    if not args.template:
        parser.error("请指定模板名称，或使用 --list 查看所有模板")

    template = read_template(args.template)

    if args.raw:
        print(template)
        return

    # 构建上下文
    context = {
        "current_date": datetime.now().strftime("%Y/%m/%d"),
        "current_time": datetime.now().strftime("%H:%M"),
    }

    # 从 API 获取实时数据
    if args.base_url and args.token:
        api_data = fetch_system_context(args.base_url, args.token)
        if "system_info" in api_data:
            # 如果拿到了渲染后的 system-info，直接输出
            if args.template == "system-info":
                print(api_data["system_info"])
                return
            context["system_info_available"] = True

    # 解析额外变量
    for extra in args.extra:
        if "=" in extra:
            k, v = extra.split("=", 1)
            context[k.strip()] = v.strip()

    # 渲染
    rendered = render_mustache(template, context)
    print(rendered)


if __name__ == "__main__":
    main()
