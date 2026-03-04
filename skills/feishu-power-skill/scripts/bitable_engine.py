#!/usr/bin/env python3
"""
bitable_engine.py — 多维表格自动化引擎
批量操作、跨表关联、数据快照、统计摘要
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

import feishu_api as api


# ============================================================
# 批量创建
# ============================================================

def batch_create(app_token: str, table_id: str, records: List[Dict], dry_run: bool = False) -> Dict:
    """批量创建记录，自动分片（每片 500 条）"""
    total = len(records)
    if total == 0:
        return {"created": 0, "message": "没有记录需要创建"}

    if dry_run:
        return {"would_create": total, "sample": records[:3]}

    created = 0
    errors = []
    for i in range(0, total, 500):
        chunk = records[i : i + 500]
        try:
            result = api.bitable_batch_create_records(app_token, table_id, chunk)
            created += len(chunk)
            if i + 500 < total:
                time.sleep(0.5)  # 避免限流
        except Exception as e:
            errors.append({"offset": i, "count": len(chunk), "error": str(e)})

    return {"created": created, "total": total, "errors": errors}


# ============================================================
# 批量更新
# ============================================================

def batch_update(app_token: str, table_id: str, updates: List[Dict], dry_run: bool = False) -> Dict:
    """批量更新记录
    updates: [{"record_id": "xxx", "fields": {...}}, ...]
    """
    total = len(updates)
    if total == 0:
        return {"updated": 0, "message": "没有记录需要更新"}

    if dry_run:
        return {"would_update": total, "sample": updates[:3]}

    updated = 0
    errors = []
    for i in range(0, total, 500):
        chunk = updates[i : i + 500]
        try:
            api.bitable_batch_update_records(app_token, table_id, chunk)
            updated += len(chunk)
            if i + 500 < total:
                time.sleep(0.5)
        except Exception as e:
            errors.append({"offset": i, "count": len(chunk), "error": str(e)})

    return {"updated": updated, "total": total, "errors": errors}


# ============================================================
# 跨表关联查询
# ============================================================

def cross_table_join(
    app_token: str,
    left_table: str,
    right_table: str,
    join_field: str,
    select_fields: Optional[List[str]] = None,
) -> List[Dict]:
    """跨表 JOIN 查询
    在 left_table 和 right_table 之间按 join_field 做内连接
    """
    left_records = api.bitable_list_all_records(app_token, left_table)
    right_records = api.bitable_list_all_records(app_token, right_table)

    # 构建右表索引
    right_index: Dict[str, List[Dict]] = {}
    for r in right_records:
        fields = r.get("fields", {})
        key = _extract_text_value(fields.get(join_field))
        if key:
            right_index.setdefault(key, []).append(fields)

    # JOIN
    results = []
    for lr in left_records:
        left_fields = lr.get("fields", {})
        key = _extract_text_value(left_fields.get(join_field))
        if key and key in right_index:
            for right_fields in right_index[key]:
                merged = {**left_fields, **right_fields}
                if select_fields:
                    merged = {k: v for k, v in merged.items() if k in select_fields}
                results.append(merged)

    return results


# ============================================================
# 数据快照
# ============================================================

def snapshot(
    app_token: str,
    table_id: str,
    output_dir: str = "snapshots",
) -> str:
    """导出当前表数据为 JSON 快照"""
    os.makedirs(output_dir, exist_ok=True)

    fields = api.bitable_list_fields(app_token, table_id)
    records = api.bitable_list_all_records(app_token, table_id)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{table_id}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    snapshot_data = {
        "app_token": app_token,
        "table_id": table_id,
        "snapshot_time": datetime.now().isoformat(),
        "field_count": len(fields),
        "record_count": len(records),
        "fields": [{"name": f.get("field_name"), "type": f.get("type")} for f in fields],
        "records": [{"record_id": r.get("record_id"), "fields": r.get("fields", {})} for r in records],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, ensure_ascii=False, indent=2)

    return filepath


# ============================================================
# 统计摘要
# ============================================================

def stats(app_token: str, table_id: str) -> Dict:
    """生成数据表统计摘要"""
    fields = api.bitable_list_fields(app_token, table_id)
    records = api.bitable_list_all_records(app_token, table_id)

    summary = {
        "table_id": table_id,
        "total_records": len(records),
        "total_fields": len(fields),
        "fields": [],
    }

    for field in fields:
        fname = field.get("field_name", "")
        ftype = field.get("type", 0)
        field_stat = {"name": fname, "type": ftype, "type_name": _field_type_name(ftype)}

        values = [r.get("fields", {}).get(fname) for r in records]
        non_null = [v for v in values if v is not None and v != "" and v != []]
        field_stat["fill_rate"] = f"{len(non_null)}/{len(records)}" if records else "0/0"

        # 数值字段统计
        if ftype == 2:  # Number
            nums = [v for v in non_null if isinstance(v, (int, float))]
            if nums:
                field_stat["min"] = min(nums)
                field_stat["max"] = max(nums)
                field_stat["avg"] = round(sum(nums) / len(nums), 2)
                field_stat["sum"] = round(sum(nums), 2)

        # 单选/多选统计
        elif ftype in (3, 4):  # SingleSelect / MultiSelect
            counter: Dict[str, int] = {}
            for v in non_null:
                if isinstance(v, str):
                    counter[v] = counter.get(v, 0) + 1
                elif isinstance(v, list):
                    for item in v:
                        val = item if isinstance(item, str) else str(item)
                        counter[val] = counter.get(val, 0) + 1
            field_stat["distribution"] = dict(sorted(counter.items(), key=lambda x: -x[1])[:10])

        summary["fields"].append(field_stat)

    return summary


# ============================================================
# 数据导入（CSV / JSON）
# ============================================================

def load_records_from_file(filepath: str) -> List[Dict]:
    """从 CSV 或 JSON 文件加载记录"""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".json":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "records" in data:
            return data["records"]
        else:
            raise ValueError("JSON 格式不对：需要是数组或包含 records 字段的对象")

    elif ext == ".csv":
        records = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 尝试自动转换数值
                record = {}
                for k, v in row.items():
                    try:
                        record[k] = float(v) if "." in v else int(v)
                    except (ValueError, TypeError):
                        record[k] = v
                records.append(record)
        return records

    else:
        raise ValueError(f"不支持的文件格式: {ext}，支持 .json 和 .csv")


# ============================================================
# 辅助函数
# ============================================================

def _extract_text_value(value: Any) -> Optional[str]:
    """从飞书字段值中提取纯文本"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        # 富文本字段: [{"text": "xxx", ...}]
        texts = []
        for item in value:
            if isinstance(item, dict):
                texts.append(item.get("text", ""))
            elif isinstance(item, str):
                texts.append(item)
        return "".join(texts) if texts else None
    if isinstance(value, dict):
        return value.get("text") or value.get("value") or str(value)
    return str(value)


def _field_type_name(ftype: int) -> str:
    """字段类型编号 → 名称"""
    type_map = {
        1: "Text",
        2: "Number",
        3: "SingleSelect",
        4: "MultiSelect",
        5: "DateTime",
        7: "Checkbox",
        11: "Person",
        13: "Phone",
        15: "URL",
        17: "Attachment",
        18: "Link",
        19: "Lookup",
        20: "Formula",
        21: "DuplexLink",
        22: "Location",
        23: "GroupChat",
        1001: "CreatedTime",
        1002: "ModifiedTime",
        1003: "CreatedBy",
        1004: "ModifiedBy",
        1005: "AutoNumber",
    }
    return type_map.get(ftype, f"Unknown({ftype})")


# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Bitable 自动化引擎")
    sub = parser.add_subparsers(dest="command", required=True)

    # batch-create
    p_create = sub.add_parser("batch-create", help="批量创建记录")
    p_create.add_argument("--app", required=True, help="App token")
    p_create.add_argument("--table", required=True, help="Table ID")
    p_create.add_argument("--data", required=True, help="数据文件路径 (JSON/CSV)")
    p_create.add_argument("--dry-run", action="store_true", help="仅预览，不执行")

    # batch-update
    p_update = sub.add_parser("batch-update", help="批量更新记录")
    p_update.add_argument("--app", required=True, help="App token")
    p_update.add_argument("--table", required=True, help="Table ID")
    p_update.add_argument("--data", required=True, help="更新数据文件 (JSON)")
    p_update.add_argument("--dry-run", action="store_true", help="仅预览，不执行")

    # join
    p_join = sub.add_parser("join", help="跨表关联查询")
    p_join.add_argument("--app", required=True, help="App token")
    p_join.add_argument("--left", required=True, help="左表 Table ID")
    p_join.add_argument("--right", required=True, help="右表 Table ID")
    p_join.add_argument("--on", required=True, help="关联字段名")
    p_join.add_argument("--select", help="输出字段（逗号分隔）")

    # snapshot
    p_snap = sub.add_parser("snapshot", help="数据快照")
    p_snap.add_argument("--app", required=True, help="App token")
    p_snap.add_argument("--table", required=True, help="Table ID")
    p_snap.add_argument("--output", default="snapshots", help="输出目录")

    # stats
    p_stats = sub.add_parser("stats", help="统计摘要")
    p_stats.add_argument("--app", required=True, help="App token")
    p_stats.add_argument("--table", required=True, help="Table ID")

    args = parser.parse_args()

    if args.command == "batch-create":
        records = load_records_from_file(args.data)
        result = batch_create(args.app, args.table, records, args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "batch-update":
        updates = load_records_from_file(args.data)
        result = batch_update(args.app, args.table, updates, args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "join":
        select = args.select.split(",") if args.select else None
        results = cross_table_join(args.app, args.left, args.right, args.on, select)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.command == "snapshot":
        filepath = snapshot(args.app, args.table, args.output)
        print(f"快照已保存: {filepath}")

    elif args.command == "stats":
        result = stats(args.app, args.table)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
