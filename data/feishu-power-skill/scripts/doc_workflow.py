#!/usr/bin/env python3
"""
doc_workflow.py — 飞书文档工作流引擎
模板化文档生成 + Bitable 数据填充 + 文档创建
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import feishu_api as api


# ============================================================
# 模板引擎
# ============================================================

def render_template(template: str, context: Dict[str, Any]) -> str:
    """渲染模板，支持 {{变量}} 和 {{#each 列表}}...{{/each}} 语法
    
    变量: {{name}}, {{date}}, {{summary.total}}
    循环: {{#each items}}  {{name}} | {{value}}  {{/each}}
    条件: {{#if flag}}...{{/if}}
    内置变量: {{TODAY}}, {{YESTERDAY}}, {{WEEK_START}}, {{WEEK_END}}, {{NOW}}
    """
    # 注入内置变量
    today = datetime.now()
    builtins = {
        "TODAY": today.strftime("%Y-%m-%d"),
        "YESTERDAY": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
        "WEEK_START": (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d"),
        "WEEK_END": (today - timedelta(days=today.weekday()) + timedelta(days=6)).strftime("%Y-%m-%d"),
        "NOW": today.strftime("%Y-%m-%d %H:%M"),
    }
    ctx = {**builtins, **context}

    result = template

    # 处理 {{#each list}}...{{/each}}
    each_pattern = re.compile(r'\{\{#each\s+([\w.]+)\}\}(.*?)\{\{/each\}\}', re.DOTALL)
    def replace_each(m):
        key = m.group(1)
        body = m.group(2).strip("\n")  # 去掉循环体首尾换行
        items = _resolve_dotted(ctx, key)
        if not isinstance(items, list):
            return ""
        lines = []
        for idx, item in enumerate(items):
            line = body
            if isinstance(item, dict):
                # 跳过全空记录
                if all(v is None or v == "" or v == [] for v in item.values()):
                    continue
                # 处理循环体内的 {{#if field}}...{{/if}}（访问当前迭代项字段）
                line = _resolve_inner_if(line, item)
                for k, v in item.items():
                    line = line.replace("{{" + k + "}}", _to_str(v))
                line = line.replace("{{@index}}", str(idx))
            else:
                line = line.replace("{{this}}", _to_str(item))
            lines.append(line)
        return "\n".join(lines)

    result = each_pattern.sub(replace_each, result)

    # 处理 {{#if key}}...{{/if}} — 支持点号路径和中文字段名
    if_pattern = re.compile(r'\{\{#if\s+([\w.\u4e00-\u9fff]+)\}\}(.*?)\{\{/if\}\}', re.DOTALL)
    def replace_if(m):
        key = m.group(1)
        body = m.group(2)
        val = _resolve_dotted(ctx, key)
        if val and val != [] and val != 0:
            return body
        return ""
    result = if_pattern.sub(replace_if, result)

    # 处理 {{variable}} — 支持点号访问嵌套字段和中文字段名
    var_pattern = re.compile(r'\{\{([\w.\u4e00-\u9fff]+)\}\}')
    def replace_var(m):
        key = m.group(1)
        val = _resolve_dotted(ctx, key)
        return _to_str(val) if val is not None else m.group(0)
    result = var_pattern.sub(replace_var, result)

    return result


def _resolve_inner_if(text: str, item: Dict[str, Any]) -> str:
    """处理循环体内的 {{#if field}}...{{/if}}，从当前迭代项查找字段值"""
    pattern = re.compile(r'\{\{#if\s+([\w.\u4e00-\u9fff]+)\}\}(.*?)\{\{/if\}\}', re.DOTALL)
    def replace(m):
        key = m.group(1)
        body = m.group(2)
        val = item.get(key)
        if val and val != [] and val != 0:
            return body
        return ""
    return pattern.sub(replace, text)


def _resolve_dotted(ctx: Dict, key: str) -> Any:
    """解析点号路径: summary.total → ctx["summary"]["total"]"""
    parts = key.split(".")
    current = ctx
    for p in parts:
        if isinstance(current, dict):
            current = current.get(p)
        else:
            return None
        if current is None:
            return None
    return current


def _to_str(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return f"{val:.2f}"
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val)


# ============================================================
# Bitable 数据提取 → 模板上下文
# ============================================================

def build_context_from_bitable(
    app_token: str,
    table_id: str,
    group_by: Optional[str] = None,
    filter_str: Optional[str] = None,
    extra: Optional[Dict] = None,
) -> Dict[str, Any]:
    """从 Bitable 表提取数据，构建模板上下文
    
    返回:
    {
        "records": [...],           # 原始记录列表
        "total": 数量,
        "fields": [...],            # 字段名列表
        "groups": {"A": [...], ...} # 按 group_by 分组（可选）
        "summary": {                # 自动统计
            "total": N,
            "by_status": {"完成": 5, "进行中": 3},
            ...
        }
    }
    """
    fields = api.bitable_list_fields(app_token, table_id)
    records = api.bitable_list_all_records(app_token, table_id, filter_str=filter_str)

    field_names = [f.get("field_name", "") for f in fields]
    field_types = {f.get("field_name", ""): f.get("type", 0) for f in fields}

    # 提取纯文本记录
    clean_records = []
    for r in records:
        row = {}
        for fname in field_names:
            raw = r.get("fields", {}).get(fname)
            row[fname] = _extract_display_value(raw, field_types.get(fname, 0))
        clean_records.append(row)

    ctx: Dict[str, Any] = {
        "records": clean_records,
        "total": len(clean_records),
        "fields": field_names,
    }

    # 分组
    if group_by and group_by in field_names:
        groups: Dict[str, List] = {}
        for row in clean_records:
            key = str(row.get(group_by, "未分类"))
            groups.setdefault(key, []).append(row)
        ctx["groups"] = groups

    # 自动统计：单选字段做分布，数值字段做汇总
    summary: Dict[str, Any] = {"total": len(clean_records)}
    for fname, ftype in field_types.items():
        values = [r.get(fname) for r in clean_records if r.get(fname)]
        if ftype == 3:  # SingleSelect
            dist = {}
            for v in values:
                dist[str(v)] = dist.get(str(v), 0) + 1
            summary[f"by_{fname}"] = dist
        elif ftype == 2:  # Number
            nums = []
            for v in values:
                if isinstance(v, (int, float)):
                    nums.append(v)
                elif isinstance(v, str):
                    try:
                        nums.append(float(v))
                    except ValueError:
                        pass
            if nums:
                summary[f"{fname}_sum"] = round(sum(nums), 2)
                summary[f"{fname}_avg"] = round(sum(nums) / len(nums), 2)
                summary[f"{fname}_max"] = max(nums)
                summary[f"{fname}_min"] = min(nums)
    ctx["summary"] = summary

    # 合并额外上下文
    if extra:
        ctx.update(extra)

    return ctx


def _extract_display_value(raw: Any, ftype: int) -> Any:
    """从飞书字段原始值提取可显示的值"""
    if raw is None:
        return None
    if isinstance(raw, (str, int, float, bool)):
        return raw
    if isinstance(raw, list):
        # 富文本 / 多选 / 人员
        if not raw:
            return None
        first = raw[0]
        if isinstance(first, dict):
            if "text" in first:  # 富文本
                return "".join(item.get("text", "") for item in raw)
            if "name" in first:  # 人员
                return ", ".join(item.get("name", "") for item in raw)
            if "id" in first:  # 人员 (open_id)
                return ", ".join(item.get("name", item.get("id", "")) for item in raw)
        # 多选字符串列表
        return [str(v) for v in raw]
    if isinstance(raw, dict):
        if "text" in raw:
            return raw["text"]
        if "link" in raw:
            return raw["link"]
    return str(raw)


# ============================================================
# 文档生成
# ============================================================

def generate_doc(
    template_path: str,
    context: Dict[str, Any],
    title: Optional[str] = None,
    folder_token: Optional[str] = None,
    output_local: Optional[str] = None,
) -> Dict[str, str]:
    """从模板 + 上下文生成飞书文档
    
    Args:
        template_path: 模板文件路径 (.md)
        context: 模板变量上下文
        title: 文档标题（默认从模板第一行提取）
        folder_token: 飞书文件夹 token（可选）
        output_local: 同时保存本地文件路径（可选）
    
    Returns:
        {"doc_token": "xxx", "url": "https://...", "title": "xxx"}
    """
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    rendered = render_template(template, context)

    # 提取标题
    if not title:
        first_line = rendered.split("\n")[0].strip()
        if first_line.startswith("#"):
            title = first_line.lstrip("#").strip()
        else:
            title = f"报告_{datetime.now().strftime('%Y%m%d_%H%M')}"

    # 保存本地副本
    if output_local:
        os.makedirs(os.path.dirname(output_local) or ".", exist_ok=True)
        with open(output_local, "w", encoding="utf-8") as f:
            f.write(rendered)

    # 创建飞书文档
    doc_data = api.docx_create_document(title, folder_token)
    doc_token = doc_data.get("document", {}).get("document_id", "")

    if not doc_token:
        raise Exception(f"创建文档失败: {doc_data}")

    # 写入内容：将 markdown 转为飞书 blocks，分批写入（每批最多 50 个）
    blocks = _markdown_to_blocks(rendered)
    BATCH_SIZE = 50
    for i in range(0, len(blocks), BATCH_SIZE):
        chunk = blocks[i : i + BATCH_SIZE]
        api.docx_create_block(doc_token, doc_token, chunk)
        if i + BATCH_SIZE < len(blocks):
            import time
            time.sleep(0.3)  # 避免限流

    url = f"https://my.feishu.cn/docx/{doc_token}"
    return {"doc_token": doc_token, "url": url, "title": title}


def _markdown_to_blocks(md: str) -> List[Dict]:
    """将 Markdown 转为飞书 Block 结构
    
    支持: 标题(h1-h6), 段落, 无序列表, 有序列表, 分割线, 表格
    """
    blocks = []
    lines = md.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 空行跳过
        if not stripped:
            i += 1
            continue

        # 分割线
        if stripped in ("---", "***", "___"):
            blocks.append({"block_type": 22, "divider": {}})
            i += 1
            continue

        # 标题
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            # 飞书 heading block_type: 3=h1, 4=h2, ..., 11=h9
            block_type = 2 + level
            blocks.append({
                "block_type": block_type,
                f"heading{level}": {
                    "elements": [{"text_run": {"content": text}}]
                }
            })
            i += 1
            continue

        # 无序列表
        if re.match(r'^[-*+]\s+', stripped):
            text = re.sub(r'^[-*+]\s+', '', stripped)
            blocks.append({
                "block_type": 2,
                "text": {
                    "elements": [{"text_run": {"content": text}}],
                    "style": {"list": "bullet"}
                }
            })
            i += 1
            continue

        # 有序列表
        ol_match = re.match(r'^(\d+)\.\s+(.+)$', stripped)
        if ol_match:
            text = ol_match.group(2)
            blocks.append({
                "block_type": 2,
                "text": {
                    "elements": [{"text_run": {"content": text}}],
                    "style": {"list": "number"}
                }
            })
            i += 1
            continue

        # 表格：检测 | 开头的连续行
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            table_block = _parse_table(table_lines)
            if table_block:
                blocks.append(table_block)
            continue

        # 普通段落
        blocks.append({
            "block_type": 2,  # text
            "text": {
                "elements": [{"text_run": {"content": stripped}}]
            }
        })
        i += 1

    return blocks


def _parse_table(lines: List[str]) -> Optional[Dict]:
    """解析 Markdown 表格为飞书 table block
    
    飞书 table block 结构比较特殊，需要先创建 table 再填充 cells。
    这里简化处理：将表格转为文本段落（飞书 API 创建表格较复杂）。
    """
    if len(lines) < 2:
        return None

    # 解析表头和数据行
    rows = []
    for line in lines:
        # 跳过分隔行 |---|---|
        if re.match(r'^\|[\s\-:|]+\|$', line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)

    if not rows:
        return None

    # 转为格式化文本（飞书 API 直接创建表格需要多步操作，MVP 先用文本）
    text_lines = []
    header = rows[0]
    text_lines.append(" | ".join(header))
    text_lines.append("-" * (len(" | ".join(header))))
    for row in rows[1:]:
        # 补齐列数
        while len(row) < len(header):
            row.append("")
        text_lines.append(" | ".join(row[:len(header)]))

    return {
        "block_type": 2,
        "text": {
            "elements": [{"text_run": {"content": "\n".join(text_lines)}}]
        }
    }


# ============================================================
# 快捷工作流：Bitable → 文档（一步到位）
# ============================================================

def bitable_to_doc(
    app_token: str,
    table_id: str,
    template_path: str,
    title: Optional[str] = None,
    group_by: Optional[str] = None,
    filter_str: Optional[str] = None,
    folder_token: Optional[str] = None,
    output_local: Optional[str] = None,
    extra_context: Optional[Dict] = None,
) -> Dict[str, str]:
    """一步完成：Bitable 数据 → 模板渲染 → 飞书文档
    
    这是最常用的入口函数。
    """
    ctx = build_context_from_bitable(
        app_token, table_id,
        group_by=group_by,
        filter_str=filter_str,
        extra=extra_context,
    )
    return generate_doc(
        template_path, ctx,
        title=title,
        folder_token=folder_token,
        output_local=output_local,
    )


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="飞书文档工作流引擎")
    sub = parser.add_subparsers(dest="command", required=True)

    # render — 纯模板渲染（不创建飞书文档）
    p_render = sub.add_parser("render", help="渲染模板到本地文件")
    p_render.add_argument("--template", required=True, help="模板文件路径")
    p_render.add_argument("--context", help="上下文 JSON 文件")
    p_render.add_argument("--output", default="-", help="输出文件（- 为 stdout）")

    # generate — Bitable 数据 → 飞书文档
    p_gen = sub.add_parser("generate", help="从 Bitable 数据生成飞书文档")
    p_gen.add_argument("--app", required=True, help="Bitable app token")
    p_gen.add_argument("--table", required=True, help="Table ID")
    p_gen.add_argument("--template", required=True, help="模板文件路径")
    p_gen.add_argument("--title", help="文档标题")
    p_gen.add_argument("--group-by", help="分组字段")
    p_gen.add_argument("--filter", help="过滤条件")
    p_gen.add_argument("--folder", help="飞书文件夹 token")
    p_gen.add_argument("--local", help="同时保存本地副本路径")
    p_gen.add_argument("--extra", help="额外上下文 JSON 字符串")

    # context — 仅提取 Bitable 上下文（调试用）
    p_ctx = sub.add_parser("context", help="提取 Bitable 数据上下文")
    p_ctx.add_argument("--app", required=True, help="Bitable app token")
    p_ctx.add_argument("--table", required=True, help="Table ID")
    p_ctx.add_argument("--group-by", help="分组字段")
    p_ctx.add_argument("--filter", help="过滤条件")

    args = parser.parse_args()

    if args.command == "render":
        with open(args.template, "r", encoding="utf-8") as f:
            template = f.read()
        ctx = {}
        if args.context:
            with open(args.context, "r", encoding="utf-8") as f:
                ctx = json.load(f)
        rendered = render_template(template, ctx)
        if args.output == "-":
            print(rendered)
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(rendered)
            print(f"已保存: {args.output}")

    elif args.command == "generate":
        extra = json.loads(args.extra) if args.extra else None
        result = bitable_to_doc(
            args.app, args.table, args.template,
            title=args.title,
            group_by=args.group_by,
            filter_str=args.filter,
            folder_token=args.folder,
            output_local=args.local,
            extra_context=extra,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "context":
        ctx = build_context_from_bitable(
            args.app, args.table,
            group_by=args.group_by,
            filter_str=args.filter,
        )
        print(json.dumps(ctx, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
