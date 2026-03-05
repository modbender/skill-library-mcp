#!/usr/bin/env python3
"""
Crypto Learning Script
加密货币学习脚本
"""

import json
import os
import sys
from datetime import datetime, timedelta

# 路径配置
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_FILE = os.path.join(SKILL_DIR, "content.json")
PROGRESS_FILE = os.path.join(SKILL_DIR, "progress.json")


def load_json(filepath):
    """加载 JSON 文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 文件不存在: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        return None


def save_json(filepath, data):
    """保存 JSON 文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return False


def get_current_learning_content():
    """获取当前学习内容"""
    content = load_json(CONTENT_FILE)
    progress = load_json(PROGRESS_FILE)

    if not content or not progress:
        return None

    stage = content['stages'][progress['current_stage']]
    topic = stage['topics'][progress['current_topic_index']]
    subtopic = topic['subtopics'][progress['current_subtopic_index']]

    return {
        'stage_name': stage['name'],
        'topic_name': topic['name'],
        'subtopic_title': subtopic['title'],
        'subtopic_content': subtopic['content'],
        'subtopic_id': subtopic['id']
    }


def update_progress():
    """更新学习进度"""
    progress = load_json(PROGRESS_FILE)
    content = load_json(CONTENT_FILE)

    if not progress or not content:
        return False

    # 记录当前完成的子主题
    stage = content['stages'][progress['current_stage']]
    topic = stage['topics'][progress['current_topic_index']]
    subtopic = topic['subtopics'][progress['current_subtopic_index']]

    if subtopic['id'] not in progress['completed_subtopics']:
        progress['completed_subtopics'].append(subtopic['id'])

    # 移动到下一个子主题
    progress['current_subtopic_index'] += 1

    # 如果当前主题的子主题都学完了，移动到下一个主题
    if progress['current_subtopic_index'] >= len(topic['subtopics']):
        progress['current_subtopic_index'] = 0
        progress['current_topic_index'] += 1

        # 如果当前阶段的主题都学完了，移动到下一个阶段
        if progress['current_topic_index'] >= len(stage['topics']):
            progress['current_topic_index'] = 0
            stages = list(content['stages'].keys())
            current_index = stages.index(progress['current_stage'])

            if current_index < len(stages) - 1:
                progress['current_stage'] = stages[current_index + 1]
            else:
                # 所有阶段都学完了
                progress['enabled'] = False
                print("🎉 恭喜！你已经完成了所有学习内容！")
                return True

    # 更新其他信息
    progress['last_push_date'] = datetime.now().strftime('%Y-%m-%d')
    progress['total_days_completed'] += 1

    return save_json(PROGRESS_FILE, progress)


def get_next_topic_preview():
    """获取下一个学习主题预览"""
    progress = load_json(PROGRESS_FILE)
    content = load_json(CONTENT_FILE)

    if not progress or not content:
        return None

    stage = content['stages'][progress['current_stage']]
    topic = stage['topics'][progress['current_topic_index']]
    next_subtopic_idx = progress['current_subtopic_index']

    # 如果当前主题的子主题都学完了，预览下一个主题
    if next_subtopic_idx >= len(topic['subtopics']):
        next_subtopictopic_idx = 0
        next_topic_idx = progress['current_topic_index'] + 1

        if next_topic_idx >= len(stage['topics']):
            next_topic_idx = 0
            stages = list(content['stages'].keys())
            current_index = stages.index(progress['current_stage'])

            if current_index < len(stages) - 1:
                next_stage = content['stages'][stages[current_index + 1]]
                next_topic = next_stage['topics'][0]
                next_subtopic = next_topic['subtopics'][0]
                return f"{next_stage['name']} - {next_topic['name']} - {next_subtopic['title']}"
            else:
                return "学习计划已完成！"
        else:
            next_topic = stage['topics'][next_topic_idx]
            next_subtopic = next_topic['subtopics'][0]
            return f"{stage['name']} - {next_topic['name']} - {next_subtopic['title']}"
    else:
        next_subtopic = topic['subtopics'][next_subtopic_idx]
        return f"{stage['name']} - {topic['name']} - {next_subtopic['title']}"


def show_progress():
    """显示学习进度"""
    progress = load_json(PROGRESS_FILE)
    content = load_json(CONTENT_FILE)

    if not progress or not content:
        return

    print("\n📊 学习进度")
    print("=" * 50)
    print(f"用户: {progress['user_id']}")
    print(f"开始时间: {progress['started_at'][:10]}")
    print(f"已完成天数: {progress['total_days_completed']}")
    print(f"最后学习: {progress['last_push_date']}")
    print(f"状态: {'✅ 进行中' if progress['enabled'] else '⏸️ 已暂停'}")

    stage = content['stages'][progress['current_stage']]
    topic = stage['topics'][progress['current_topic_index']]
    subtopic = topic['subtopics'][progress['current_subtopic_index']]

    print(f"\n当前位置:")
    print(f"  阶段: {stage['name']}")
    print(f"  主题: {topic['name']}")
    print(f"  今日: {subtopic['title']}")

    print(f"\n已完成知识点: {len(progress['completed_subtopics'])} 个")
    print("=" * 50)


def skip_today():
    """跳过今天的学习"""
    progress = load_json(PROGRESS_FILE)
    if not progress:
        return False

    today = datetime.now().strftime('%Y-%m-%d')
    if today not in progress['skipped_dates']:
        progress['skipped_dates'].append(today)

    return save_json(PROGRESS_FILE, progress)


def reset_progress():
    """重置学习进度"""
    content = load_json(CONTENT_FILE)
    if not content:
        return False

    progress = {
        "user_id": "hmzo",
        "started_at": datetime.now().isoformat(),
        "current_stage": "beginner",
        "current_topic_index": 0,
        "current_subtopic_index": 0,
        "completed_subtopics": [],
        "skipped_dates": [],
        "last_push_date": None,
        "total_days_completed": 0,
        "enabled": True
    }

    return save_json(PROGRESS_FILE, progress)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 learn.py today      - 获取今日学习内容")
        print("  python3 learn.py progress   - 查看学习进度")
        print("  python3 learn.py skip       - 跳过今天")
        print("  python3 learn.py reset      - 重置计划")
        print("  python3 learn.py next       - 预览下一个主题")
        return

    command = sys.argv[1]

    if command == "today":
        learning_content = get_current_learning_content()
        if learning_content:
            print(json.dumps(learning_content, ensure_ascii=False, indent=2))
        else:
            print("❌ 无法获取学习内容")

    elif command == "progress":
        show_progress()

    elif command == "skip":
        if skip_today():
            print("✅ 已跳过今天的学习")
        else:
            print("❌ 跳过失败")

    elif command == "reset":
        if reset_progress():
            print("✅ 学习计划已重置")
        else:
            print("❌ 重置失败")

    elif command == "next":
        next_topic = get_next_topic_preview()
        print(f"下一个主题: {next_topic}")

    elif command == "update":
        if update_progress():
            print("✅ 进度已更新")
        else:
            print("❌ 更新失败")

    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()
