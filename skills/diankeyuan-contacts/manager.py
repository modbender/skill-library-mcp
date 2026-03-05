#!/usr/bin/env python3
"""
电科院联系人管理工具
命令行界面管理电科院人员和科室信息
"""

import json
import sys
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("/Users/aibin/.openclaw/workspace/diankeyuan_contacts.json")

def load_data():
    """加载数据"""
    if not DATA_FILE.exists():
        return {"meta": {"version": "1.0.0", "totalMembers": 0}, "departments": {}, "quickSearch": {}}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """保存数据"""
    data["meta"]["updatedAt"] = datetime.now().strftime("%Y-%m-%d")
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_member(name, department, role="", office="", notes=""):
    """添加人员"""
    data = load_data()
    
    # 解析科室（格式：所 - 室）
    if '-' in department:
        parts = department.split('-', 1)
        institute = parts[0].strip()
        room = parts[1].strip() if len(parts) > 1 else ""
    else:
        institute = department
        room = ""
    
    # 创建科室结构
    if institute not in data["departments"]:
        data["departments"][institute] = {}
    
    if room not in data["departments"][institute]:
        data["departments"][institute][room] = {"office": office, "members": []}
    
    # 检查是否已存在
    for member in data["departments"][institute][room]["members"]:
        if member["name"] == name:
            print(f"⚠️  {name} 已存在于 {institute}-{room}")
            return False
    
    # 添加新成员
    member = {
        "name": name,
        "role": role,
        "office": office,
        "phone": "",
        "email": "",
        "wechat": "",
        "addedAt": datetime.now().strftime("%Y-%m-%d"),
        "updatedAt": datetime.now().strftime("%Y-%m-%d"),
        "notes": notes
    }
    
    data["departments"][institute][room]["members"].append(member)
    data["meta"]["totalMembers"] += 1
    
    # 更新快速搜索
    data["quickSearch"][name] = f"{institute}-{room}-{role}-{office}"
    
    save_data(data)
    print(f"✅ 已添加：{name} ({institute}-{room}, {role}, 办公室 {office})")
    return True

def query_member(name):
    """查询人员"""
    data = load_data()
    
    # 模糊搜索
    results = []
    for institute, rooms in data["departments"].items():
        for room, info in rooms.items():
            for member in info["members"]:
                if name.lower() in member["name"].lower():
                    results.append({
                        "name": member["name"],
                        "institute": institute,
                        "room": room,
                        "role": member["role"],
                        "office": member["office"]
                    })
    
    if not results:
        print(f"❌ 未找到：{name}")
        return None
    
    # 显示结果
    for r in results:
        print(f"👤 {r['name']}")
        print(f"   科室：{r['institute']}-{r['room']}")
        print(f"   职务：{r['role'] or '未填写'}")
        print(f"   办公室：{r['office']}")
        print()
    
    return results

def list_all():
    """列出所有人员"""
    data = load_data()
    
    print(f"📊 电科院联系人列表 (共 {data['meta']['totalMembers']} 人)\n")
    
    for institute, info in data["departments"].items():
        location = info.get("location", "")
        location_text = f" ({location})" if location else ""
        print(f"🏢 {institute}{location_text}")
        
        # 检查是否有 members（扁平结构）或 rooms（嵌套结构）
        if "members" in info:
            # 扁平结构（如计量所）
            for member in info["members"]:
                role = f" - {member['role']}" if member['role'] else ""
                office = f" (办公室 {member['office']})" if member['office'] else ""
                print(f"   • {member['name']}{role}{office}")
        else:
            # 嵌套结构（如系统所）
            for room, room_info in info.items():
                if isinstance(room_info, dict) and "members" in room_info:
                    office = room_info.get("office", "")
                    office_text = f"办公室 {office}" if office else ""
                    print(f"   📍 {room} ({office_text})")
                    for member in room_info["members"]:
                        role = f" - {member['role']}" if member['role'] else ""
                        print(f"      • {member['name']}{role}")
        print()

def list_departments():
    """列出所有科室"""
    data = load_data()
    
    print("🏢 电科院科室列表\n")
    
    for institute, info in data["departments"].items():
        location = info.get("location", "")
        location_text = f" ({location})" if location else ""
        print(f"📁 {institute}{location_text}")
        
        # 检查是否有 members（扁平结构）或 rooms（嵌套结构）
        if "members" in info:
            member_count = len(info["members"])
            print(f"   └─ {institute} ({member_count}人)")
        else:
            for room, room_info in info.items():
                if isinstance(room_info, dict) and "members" in room_info:
                    member_count = len(room_info["members"])
                    office = room_info.get("office", "")
                    office_text = f"办公室 {office}" if office else ""
                    print(f"   └─ {room} ({office_text}, {member_count}人)")
        print()

def update_member(name, field, new_value):
    """更新人员信息"""
    data = load_data()
    
    for institute, rooms in data["departments"].items():
        for room, info in rooms.items():
            for member in info["members"]:
                if member["name"] == name:
                    if field in member:
                        old_value = member[field]
                        member[field] = new_value
                        member["updatedAt"] = datetime.now().strftime("%Y-%m-%d")
                        save_data(data)
                        print(f"✅ 已更新：{name} 的 {field} 从 '{old_value}' → '{new_value}'")
                        return True
                    else:
                        print(f"❌ 未知字段：{field}")
                        return False
    
    print(f"❌ 未找到：{name}")
    return False

def delete_member(name):
    """删除人员"""
    data = load_data()
    
    for institute, rooms in data["departments"].items():
        for room, info in rooms.items():
            for i, member in enumerate(info["members"]):
                if member["name"] == name:
                    info["members"].pop(i)
                    data["meta"]["totalMembers"] -= 1
                    if name in data["quickSearch"]:
                        del data["quickSearch"][name]
                    save_data(data)
                    print(f"✅ 已删除：{name}")
                    return True
    
    print(f"❌ 未找到：{name}")
    return False

def print_help():
    """打印帮助"""
    print("""
🦞 电科院联系人管理工具

用法:
  python diankeyuan_manager.py add [姓名] [科室] [职务] [办公室]
  python diankeyuan_manager.py query [姓名]
  python diankeyuan_manager.py list
  python diankeyuan_manager.py departments
  python diankeyuan_manager.py update [姓名] [字段] [新值]
  python diankeyuan_manager.py delete [姓名]
  python diankeyuan_manager.py help

示例:
  python diankeyuan_manager.py add 叶新 系统所 - 二次评估室 市场 1512
  python diankeyuan_manager.py query 叶新
  python diankeyuan_manager.py update 叶新 role 市场经理
  python diankeyuan_manager.py delete 叶新
""")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "add" and len(sys.argv) >= 5:
        add_member(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "", sys.argv[5] if len(sys.argv) > 5 else "")
    elif command == "query" and len(sys.argv) >= 3:
        query_member(sys.argv[2])
    elif command == "list":
        list_all()
    elif command == "departments":
        list_departments()
    elif command == "update" and len(sys.argv) >= 5:
        update_member(sys.argv[2], sys.argv[3], sys.argv[4])
    elif command == "delete" and len(sys.argv) >= 3:
        delete_member(sys.argv[2])
    else:
        print_help()
