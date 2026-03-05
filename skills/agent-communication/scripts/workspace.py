#!/usr/bin/env python3
"""
共享工作空间工具
用法: 
  python3 workspace.py --write --key <key> --value <value>
  python3 workspace.py --read --key <key>
  python3 workspace.py --list
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
WORKSPACE_DIR = DATA_DIR / "workspace"

def write_data(key: str, value: str, agent: str = "main") -> dict:
    """
    写入共享数据
    
    Args:
        key: 数据键
        value: 数据值
        agent: 写入的Agent
    
    Returns:
        写入结果
    """
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 解析value (支持JSON)
    try:
        parsed_value = json.loads(value)
    except:
        parsed_value = value
    
    data = {
        "key": key,
        "value": parsed_value,
        "updated_by": agent,
        "updated_at": datetime.now().isoformat()
    }
    
    data_file = WORKSPACE_DIR / f"{key}.json"
    with open(data_file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return {
        "success": True,
        "key": key,
        "updated_at": data["updated_at"]
    }

def read_data(key: str) -> dict:
    """
    读取共享数据
    
    Args:
        key: 数据键
    
    Returns:
        数据内容
    """
    data_file = WORKSPACE_DIR / f"{key}.json"
    
    if data_file.exists():
        with open(data_file) as f:
            return json.load(f)
    
    return {
        "success": False,
        "key": key,
        "error": "数据不存在"
    }

def list_data() -> dict:
    """列出所有共享数据"""
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    
    items = []
    for data_file in WORKSPACE_DIR.glob("*.json"):
        with open(data_file) as f:
            items.append(json.load(f))
    
    return {
        "count": len(items),
        "items": items
    }

def delete_data(key: str) -> dict:
    """删除共享数据"""
    data_file = WORKSPACE_DIR / f"{key}.json"
    
    if data_file.exists():
        data_file.unlink()
        return {"success": True, "key": key, "deleted": True}
    
    return {"success": False, "key": key, "error": "数据不存在"}

def main():
    parser = argparse.ArgumentParser(description="共享工作空间工具")
    parser.add_argument("--write", action="store_true", help="写入数据")
    parser.add_argument("--read", action="store_true", help="读取数据")
    parser.add_argument("--list", action="store_true", help="列出所有数据")
    parser.add_argument("--delete", action="store_true", help="删除数据")
    parser.add_argument("--key", help="数据键")
    parser.add_argument("--value", help="数据值")
    parser.add_argument("--agent", default="main", help="写入Agent")
    
    args = parser.parse_args()
    
    if args.write and args.key and args.value:
        result = write_data(args.key, args.value, args.agent)
    elif args.read and args.key:
        result = read_data(args.key)
    elif args.delete and args.key:
        result = delete_data(args.key)
    elif args.list:
        result = list_data()
    else:
        result = list_data()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()