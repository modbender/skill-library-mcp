#!/usr/bin/env python3
"""
管理孩子的学习档案。

用法:
  python3 manage_profile.py <data_dir> init --name 小明 --age 9 --grade 3
  python3 manage_profile.py <data_dir> show
  python3 manage_profile.py <data_dir> update --interests "恐龙,太空"
  python3 manage_profile.py <data_dir> log-session --file session.json
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_PROFILE = {
    "name": "小朋友",
    "age": 9,
    "grade": 3,
    "interests": [],
    "preferred_subjects": ["数学"],
    "current_difficulty": 1,  # 1=基础, 2=进阶, 3=挑战
    "weak_topics": [],
    "strong_topics": [],
    "total_sessions": 0,
    "total_questions": 0,
    "lifetime_accuracy": 0,
    "created_at": "",
    "updated_at": "",
}


def init_profile(data_dir, name, age, grade, interests=None):
    """初始化孩子档案"""
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, "sessions"), exist_ok=True)

    profile = DEFAULT_PROFILE.copy()
    profile["name"] = name
    profile["age"] = age
    profile["grade"] = grade
    profile["interests"] = interests or []
    profile["created_at"] = datetime.now().isoformat()
    profile["updated_at"] = datetime.now().isoformat()

    path = os.path.join(data_dir, "profile.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    print(f"✅ 档案已创建: {path}")
    print(json.dumps(profile, ensure_ascii=False, indent=2))
    return profile


def show_profile(data_dir):
    """显示档案"""
    path = os.path.join(data_dir, "profile.json")
    if not os.path.exists(path):
        print("❌ 档案不存在，请先初始化")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    print(json.dumps(profile, ensure_ascii=False, indent=2))
    return profile


def update_profile(data_dir, **kwargs):
    """更新档案字段"""
    path = os.path.join(data_dir, "profile.json")
    if not os.path.exists(path):
        print("❌ 档案不存在，请先初始化")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    for key, value in kwargs.items():
        if value is not None and key in profile:
            profile[key] = value

    profile["updated_at"] = datetime.now().isoformat()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    print(f"✅ 档案已更新")
    print(json.dumps(profile, ensure_ascii=False, indent=2))
    return profile


def log_session(data_dir, session_data=None, file_path=None):
    """记录一次学习会话"""
    sessions_dir = os.path.join(data_dir, "sessions")
    os.makedirs(sessions_dir, exist_ok=True)

    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            session_data = json.load(f)
    elif session_data is None:
        # 从 stdin 读取
        session_data = json.load(sys.stdin)

    # 生成文件名
    now = datetime.now()
    fname = now.strftime("%Y-%m-%d_%H%M") + ".json"
    fpath = os.path.join(sessions_dir, fname)

    # 确保有时间戳
    if "timestamp" not in session_data:
        session_data["timestamp"] = now.isoformat()

    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

    # 更新档案统计
    profile_path = os.path.join(data_dir, "profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)

        questions = session_data.get("questions", [])
        correct = sum(1 for q in questions if q.get("result") == "correct")

        profile["total_sessions"] = profile.get("total_sessions", 0) + 1
        profile["total_questions"] = profile.get("total_questions", 0) + len(questions)

        # 重新计算正确率
        total_q = profile["total_questions"]
        old_correct = profile.get("lifetime_accuracy", 0) / 100 * (total_q - len(questions))
        new_correct = old_correct + correct
        profile["lifetime_accuracy"] = round(new_correct / total_q * 100, 1) if total_q > 0 else 0

        profile["updated_at"] = now.isoformat()

        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

    print(f"✅ 学习记录已保存: {fpath}")
    print(f"   题目数: {len(session_data.get('questions', []))}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="管理学习档案")
    parser.add_argument("data_dir", help="数据目录路径")
    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="初始化档案")
    p_init.add_argument("--name", required=True)
    p_init.add_argument("--age", type=int, required=True)
    p_init.add_argument("--grade", type=int, required=True)
    p_init.add_argument("--interests", help="兴趣列表，逗号分隔")

    # show
    sub.add_parser("show", help="显示档案")

    # update
    p_update = sub.add_parser("update", help="更新档案")
    p_update.add_argument("--name")
    p_update.add_argument("--age", type=int)
    p_update.add_argument("--grade", type=int)
    p_update.add_argument("--interests", help="兴趣列表，逗号分隔")
    p_update.add_argument("--difficulty", type=int, choices=[1, 2, 3])

    # log-session
    p_log = sub.add_parser("log-session", help="记录学习会话")
    p_log.add_argument("--file", help="会话JSON文件路径")

    args = parser.parse_args()

    if args.command == "init":
        interests = args.interests.split(",") if args.interests else []
        init_profile(args.data_dir, args.name, args.age, args.grade, interests)
    elif args.command == "show":
        show_profile(args.data_dir)
    elif args.command == "update":
        updates = {}
        if args.name:
            updates["name"] = args.name
        if args.age:
            updates["age"] = args.age
        if args.grade:
            updates["grade"] = args.grade
        if args.interests:
            updates["interests"] = args.interests.split(",")
        if hasattr(args, "difficulty") and args.difficulty:
            updates["current_difficulty"] = args.difficulty
        update_profile(args.data_dir, **updates)
    elif args.command == "log-session":
        log_session(args.data_dir, file_path=args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
