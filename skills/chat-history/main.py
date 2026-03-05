#!/usr/bin/env python3
"""
Chat History - 主脚本 (v2.0)
支持多种命令和触发关键词
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta

# 配置（自动检测路径）
# 优先使用环境变量，否则使用OpenClaw默认路径
OPENCLAW_DIR = os.path.expanduser(os.environ.get("OPENCLAW_DIR", "~/.openclaw"))
WORKSPACE_DIR = os.path.expanduser(os.environ.get("OPENCLAW_WORKSPACE", os.path.join(OPENCLAW_DIR, "workspace")))

ARCHIVE_DIR = os.path.join(WORKSPACE_DIR, "conversation-archives")
SEARCH_INDEX = os.path.join(ARCHIVE_DIR, "search-index.json")
EVALUATIONS_INDEX = os.path.join(ARCHIVE_DIR, "evaluations-index.json")
STATUS_FILE = os.path.join(ARCHIVE_DIR, "status.json")
LOG_FILE = os.path.join(ARCHIVE_DIR, "chat-archive.log")

def ensure_directories():
    """确保所有目录存在"""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

def load_status():
    """加载状态"""
    if not os.path.exists(STATUS_FILE):
        return {
            "enabled": False,
            "first_run": True,
            "last_archive": None,
            "archive_time": "03:55",
            "total_messages": 0,
            "total_files": 0,
            "channels": []
        }
    with open(STATUS_FILE, "r") as f:
        return json.load(f)

def save_status(status):
    """保存状态"""
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

def log_message(message):
    """写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

def check_cron_setup():
    """检查定时任务是否已设置"""
    try:
        result = os.popen("crontab -l 2>/dev/null | grep chat-history").read()
        return "chat-history" in result
    except:
        return False

def setup_cron():
    """设置定时任务"""
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(skill_dir, "archive-daily.sh")
    main_py_path = os.path.join(skill_dir, "main.py")

    # 创建脚本
    with open(script_path, "w") as f:
        f.write(f"""#!/bin/bash
cd {skill_dir}
python3 {main_py_path} --archive >> {LOG_FILE} 2>&1
""")

    os.chmod(script_path, 0o755)

    # 添加到crontab（3:55 归档，早于4:00清空）
    cron_line = "55 3 * * * {0}".format(script_path)

    # 读取现有crontab
    try:
        existing = os.popen("crontab -l 2>/dev/null").read()
    except:
        existing = ""

    # 移除旧的chat-history任务
    lines = [line for line in existing.split("\n") if "chat-history" not in line and line.strip()]
    base_cron = "\n".join(lines) + "\n"

    # 添加新任务
    new_cron = base_cron + "\n" + cron_line + "\n"

    # 写入临时文件并加载
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(new_cron)
        temp_file = f.name

    os.system(f"crontab {temp_file}")
    os.unlink(temp_file)

    return True, "success"

def remove_cron():
    """移除定时任务"""
    import tempfile

    try:
        existing = os.popen("crontab -l 2>/dev/null").read()
    except:
        existing = ""

    # 移除包含chat-history的行
    lines = existing.split("\n")
    new_lines = [line for line in lines if "chat-history" not in line and line.strip()]

    new_cron = "\n".join(new_lines) + "\n"

    # 写入临时文件并加载
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(new_cron)
        temp_file = f.name

    os.system(f"crontab {temp_file}")
    os.unlink(temp_file)

    return True

def set_archive_time(new_time):
    """设置自动归档时间

    Args:
        new_time: 格式 "HH:MM"，例如 "03:55"

    Returns:
        (success, message)
    """
    # 验证时间格式
    if not re.match(r"^\d{2}:\d{2}$", new_time):
        return False, "时间格式错误，请使用 HH:MM 格式（例如：03:55）"

    hour, minute = map(int, new_time.split(":"))

    # 验证时间范围
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return False, "时间超出范围，小时必须为 0-23，分钟必须为 0-59"

    # 检查是否早于OpenClaw清空时间（4:00）
    if hour == 4 and minute >= 0:
        return False, "⚠️  不建议设置为 04:00 或更晚，因为OpenClaw在 04:00 清空session窗口，可能丢失 00:00-04:00 的聊天记录。建议设置为 03:55 或更早。"

    # 更新状态文件
    status = load_status()
    status["archive_time"] = new_time
    save_status(status)

    # 获取skill目录
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(skill_dir, "archive-daily.sh")
    main_py_path = os.path.join(skill_dir, "main.py")

    # 更新crontab
    try:
        existing = os.popen("crontab -l 2>/dev/null").read()
    except:
        existing = ""

    # 移除所有旧的chat-history任务（archive-daily.sh）
    # 注意：这会移除所有包含archive-daily.sh的任务行
    lines = [line for line in existing.split("\n") if "archive-daily.sh" not in line and line.strip()]
    base_cron = "\n".join(lines) + "\n"

    # 创建新的cron任务
    cron_line = f"{minute} {hour} * * * {script_path}"
    new_cron = base_cron + "\n" + cron_line + "\n"

    # 写入临时文件并加载
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(new_cron)
        temp_file = f.name

    os.system(f"crontab {temp_file}")
    os.unlink(temp_file)

    # 更新archive-daily.sh
    with open(script_path, "w") as f:
        f.write(f"""#!/bin/bash
cd {skill_dir}
python3 {main_py_path} --archive >> {LOG_FILE} 2>&1
""")

    os.chmod(script_path, 0o755)

    return True, f"✅ 自动归档时间已更新为 {new_time}"

def initialize_evaluations_index():
    """初始化评估索引"""
    if not os.path.exists(EVALUATIONS_INDEX):
        with open(EVALUATIONS_INDEX, "w") as f:
            json.dump({"evaluations": []}, f, indent=2, ensure_ascii=False)

def add_evaluation(name, date, risk_level, conclusion, details="", trigger_words=[]):
    """添加评估记录"""
    initialize_evaluations_index()

    with open(EVALUATIONS_INDEX, "r") as f:
        data = json.load(f)

    evaluation = {
        "name": name,
        "date": date,
        "risk_level": risk_level,
        "conclusion": conclusion,
        "details": details,
        "trigger_words": trigger_words
    }

    data["evaluations"].append(evaluation)

    with open(EVALUATIONS_INDEX, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def list_evaluations():
    """列出所有评估"""
    if not os.path.exists(EVALUATIONS_INDEX):
        return "📋 暂无评估记录\n"

    with open(EVALUATIONS_INDEX, "r") as f:
        data = json.load(f)

    evaluations = data.get("evaluations", [])

    if not evaluations:
        return "📋 暂无评估记录\n"

    output = []
    output.append(f"✅ 找到 {len(evaluations)} 个评估过的 skills\n")

    for i, ev in enumerate(evaluations, 1):
        risk_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(ev["risk_level"], "⚪")

        output.append(f"\n[{i}] {ev['name']}")
        output.append(f"   评估日期: {ev['date']}")
        output.append(f"   风险等级: {risk_emoji} {ev['risk_level']}")
        output.append(f"   结论: {ev['conclusion']}")
        if ev['details']:
            output.append(f"   详情: {ev['details']}")
        if ev['trigger_words']:
            output.append(f"   触发词: {', '.join(ev['trigger_words'])}")

    output.append("\n")
    return "\n".join(output)

def search_evaluations(keyword):
    """搜索评估记录"""
    if not os.path.exists(EVALUATIONS_INDEX):
        return "📋 暂无评估记录\n"

    with open(EVALUATIONS_INDEX, "r") as f:
        data = json.load(f)

    evaluations = data.get("evaluations", [])
    results = []

    for ev in evaluations:
        if (keyword.lower() in ev['name'].lower() or
            keyword.lower() in ev['conclusion'].lower() or
            keyword.lower() in ev.get('details', '').lower()):
            results.append(ev)

    if not results:
        return f"❌ 未找到包含\"{keyword}\"的评估记录\n"

    output = []
    output.append(f"✅ 找到 {len(results)} 个评估包含\"{keyword}\"\n")

    for i, ev in enumerate(results, 1):
        risk_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(ev["risk_level"], "⚪")

        output.append(f"\n[{i}] {ev['name']}")
        output.append(f"   评估日期: {ev['date']}")
        output.append(f"   风险等级: {risk_emoji} {ev['risk_level']}")
        output.append(f"   结论: {ev['conclusion']}")

    output.append("\n")
    return "\n".join(output)

def show_help():
    """显示帮助信息"""
    help_text = """
📚 Chat History 指令列表

基础命令：
• /chat_history - 查看本帮助
• /chat_history start - 启动自动归档
• /chat_history stop - 停止自动归档
• /chat_history status - 查看归档状态
• /chat_history timing - 查看或设置归档时间
• /chat_history keyword - 列出所有触发关键词

搜索命令：
• /chat_history search <关键词> - 搜索对话
• /chat_history list - 列出所有归档
• /chat_history list channel - 列出Channel端归档
• /chat_history list webui - 列出WebUI端归档
• /chat_history yyyymmdd - 列出指定日期的归档

评估命令：
• /chat_history list-evaluations - 列出评估过的skills
• /chat_history search-evaluations <关键词> - 搜索评估记录

提示：也可以通过自然语言触发，详见下方触发关键词列表
"""
    return help_text

def show_status():
    """显示状态"""
    status = load_status()

    output = []
    output.append("📊 归档状态\n")
    output.append(f"自动归档: {'✅ 已启用' if status['enabled'] else '❌ 已禁用'}")
    output.append(f"定时任务: 每天 {status['archive_time']}")

    if status.get('last_archive'):
        output.append(f"上次归档: {status['last_archive']}")

    output.append(f"归档总数: {status['total_sessions']} 个会话")
    output.append(f"归档文件夹: {ARCHIVE_DIR}\n")

    # 检查文件数量
    channel_count = len(os.listdir(CHANNEL_DIR)) if os.path.exists(CHANNEL_DIR) else 0
    webui_count = len(os.listdir(WEBUI_DIR)) if os.path.exists(WEBUI_DIR) else 0

    output.append(f"Channel端归档: {channel_count} 个文件")
    output.append(f"WebUI端归档: {webui_count} 个文件")

    index_exists = "✅ 已更新" if os.path.exists(SEARCH_INDEX) else "❌ 未更新"
    output.append(f"搜索索引: {index_exists}\n")

    return "\n".join(output)

def show_keywords():
    """显示触发关键词"""
    keywords_text = """
🔑 触发关键词列表

通用触发：
• 我想不起来了 • 我记不清了 • 找不到之前的对话
• 找聊天 • 查记录 • 搜索聊天记录
• 聊天记录 • 对话记录 • 历史记录
• 以前的聊天 • 之前的对话 • 归档 • 备份

英文触发：
• chat history • conversation history • chat log
• conversation log • search history • find chat
• old chat • previous conversation • archive • backup

命令触发：
• 归档 • 搜索对话 • 列出对话 • 找记录 • 查历史

评估查询：
• 评估过的skills • 评估记录 • skill评估

提示：输入任意关键词即可自动触发搜索或归档功能
"""
    return keywords_text

def list_all_archives():
    """列出所有归档"""
    if not os.path.exists(ARCHIVE_DIR):
        return "📋 暂无归档记录\n"

    files = [f for f in os.listdir(ARCHIVE_DIR) if f.endswith('.txt')]

    if not files:
        return "📋 暂无归档记录\n"

    # 按日期排序
    files.sort(reverse=True)

    output = []
    output.append("📚 所有归档记录\n")
    output.append(f"共 {len(files)} 个文件\n")

    for f in files:
        output.append(f"  • {f}")

    output.append("\n")
    return "\n".join(output)

def list_channel_archives(channel="channel"):
    """
    列出特定channel的归档

    Args:
        channel: channel名称（例如：webui, imessage, telegram）
    """
    if not os.path.exists(ARCHIVE_DIR):
        return f"📋 {channel}端暂无归档记录\n"

    files = [f for f in os.listdir(ARCHIVE_DIR) if f.endswith('.txt') and f.endswith(f"-{channel}.txt")]

    if not files:
        return f"📋 {channel}端暂无归档记录\n"

    # 按日期排序
    files.sort(reverse=True)

    output = []
    output.append(f"📱 {channel}端归档 ({len(files)} 个文件)\n")

    for f in files:
        output.append(f"  • {f}")

    output.append("\n")
    return "\n".join(output)

def list_date_archives(date_str):
    """
    列出指定日期的归档

    Args:
        date_str: 日期字符串（YYYYMMDD 或 YYYY-MM-DD）
    """
    # 验证日期格式：YYYYMMDD
    if not re.match(r"^\d{8}$", date_str):
        try:
            # 尝试解析日期格式
            date_obj = datetime.strptime(date_str, "%Y-%m-%d" if '-' in date_str else "%Y%m%d")
            date_str = date_obj.strftime("%Y%m%d")
        except:
            return "❌ 日期格式错误，请使用 YYYYMMDD 或 YYYY-MM-DD 格式\n"

    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    prefix_date = date_str  # YYYYMMDD格式，用于匹配文件名

    output = []
    output.append(f"📅 {formatted_date} 的归档记录\n")

    found = False

    # 搜索归档文件（匹配 YYYYMMDD-channel.txt）
    files = [f for f in os.listdir(ARCHIVE_DIR) if f.endswith('.txt') and f.startswith(prefix_date)]
    if files:
        found = True
        files.sort()
        output.append(f"找到 {len(files)} 个文件:")
        for f in files:
            output.append(f"  • {f}")
    # 按channel分组
    channels = {}
    for f in files:
        parts = f.replace('.txt', '').split('-')
        if len(parts) >= 2:
            channel = parts[-1]
            if channel not in channels:
                channels[channel] = []
            channels[channel].append(f)
    output.append(f"\n按channel分组:")
    for channel, channel_files in sorted(channels.items()):
        output.append(f"  {channel} ({len(channel_files)} 个):")
        for f in channel_files:
            output.append(f"    • {f}")

    if not found:
        output.append("❌ 未找到该日期的归档记录\n")
    else:
        output.append("\n")

    return "\n".join(output)

def main():
    """主函数"""
    ensure_directories()
    status = load_status()

    # 命令行参数处理
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--help" or command == "-h":
            print(show_help())
            return

        elif command == "--archive":
            # 执行归档（直接从JSONL文件）
            log_message("开始归档...")
            print("📦 开始归档...")

            # 导入新的归档脚本
            import importlib.util
            spec = importlib.util.spec_from_file_location("archive_from_jsonl", os.path.join(os.path.dirname(__file__), "archive_from_jsonl.py"))
            archive_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(archive_module)

            # 执行归档
            count = archive_module.archive_all_sessions()

            status["last_archive"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status["total_sessions"] = status.get("total_sessions", 0) + count
            save_status(status)

            log_message(f"归档完成: {count} 条消息")
            print(f"✅ 归档完成: {count} 条消息\n")
            return

        elif command == "--status":
            print(show_status())
            return

        elif command == "--start":
            # 启动自动归档
            print("🎉 Chat History 启动\n")

            # 检查是否已有定时任务
            if check_cron_setup():
                print("⚠️  检测到已有定时任务（每天 03:55）")
                print("❌ 命令执行失败：已经有相同的定时任务了\n")
                print("💡 提示：使用 /chat_history status 查看状态")
                print("💡 提示：如需重置，请先使用 /chat_history stop，再重新启动\n")
                return

            print("📦 自动归档功能")

            result, message = setup_cron()
            if result:
                status["enabled"] = True

                # 首次运行，询问是否立即归档历史
                if status.get("first_run", True):
                    print("📦 这是首次启动\n")
                    print("🤔 是否立即归档过往所有聊天记录？")
                    print("  [Y] 立即归档   [N] 稍后   [S] 跳过\n")
                    print("💡 提示：自动选择了 [S] 跳过")
                    print("💡 提示：稍后可以使用 /chat_history 手动归档，或等定时任务自动执行\n")

                    status["first_run"] = False
                    save_status(status)
                else:
                    status["first_run"] = False
                    save_status(status)

                print("✅ 已设置定时任务（每天 03:55）")
                print("✅ 自动归档已启动\n")
                log_message("启动自动归档")
            else:
                print(f"❌ 设置定时任务失败: {message}\n")
            return

        elif command == "--stop":
            # 停止自动归档
            print("⏹️  停止自动归档...")

            result = remove_cron()
            if result:
                status["enabled"] = False
                save_status(status)

                print("✅ 已停止自动归档\n")
                print("注意：之前归档的记录仍然保留\n")
                print("提示：使用 /chat_history start 重新启动\n")
                log_message("停止自动归档")
            else:
                print("❌ 停止失败\n")
            return

        elif command == "--timing":
            # 设置自动归档时间
            if len(sys.argv) < 3:
                print("⏰ 归档时间配置\n")

                current_time = status.get("archive_time", "03:55")
                print(f"当前归档时间: {current_time}\n")

                print("使用方法:")
                print("  /chat_history timing <时间>")
                print("  例如: /chat_history timing 03:55\n")

                print("⚠️  注意事项:")
                print("  1. 时间格式: HH:MM (24小时制)")
                print("  2. 小时范围: 00-23, 分钟范围: 00-59")
                print("  3. 建议设置为 03:55 或更早（早于OpenClaw 04:00清空）")
                print("  4. 设置为 04:00 或更晚可能导致丢失 00:00-04:00 的聊天记录\n")

                print("常见时间设置:")
                print("  03:55 - 早于OpenClaw清空（推荐）✅")
                print("  02:00 - 提前归档")
                print("  01:00 - 更早归档")
                print("  23:59 - 前一天晚上归档 ❌（会丢失0:00-4:00的聊天）\n")

                return

            new_time = sys.argv[2]

            result, message = set_archive_time(new_time)
            if result:
                print(message)
                print(f"\n下一次归档将在 {new_time} 执行")
                print("使用 /chat_history status 查看状态\n")
                log_message(f"归档时间更新为 {new_time}")
            else:
                print(message)
                print("\n使用 /chat_history timing 查看帮助\n")
            return

        elif command == "--list-evaluations":
            print(list_evaluations())
            return

        elif command == "--search-evaluations" and len(sys.argv) > 2:
            keyword = sys.argv[2]
            print(search_evaluations(keyword))
            return

        elif command == "--list":
            # 检查是否有子命令参数
            if len(sys.argv) > 2:
                subcommand = sys.argv[2]

                # 检查是否channel名称
                if subcommand in ["webui", "channel", "imessage", "telegram"]:
                    print(list_channel_archives(subcommand))
                    return

                # 检查是否是日期格式（YYYYMMDD或YYYY-MM-DD）
                elif re.match(r"^\d{8}$", subcommand) or re.match(r"^\d{4}-\d{2}-\d{2}$", subcommand):
                    date_str = subcommand.replace("-", "")
                    print(list_date_archives(date_str))
                    return

                # 未知子命令
                else:
                    print(f"❌ 未知子命令: {subcommand}\n")
                    print(show_help())
                    return

            # 没有子命令参数，列出所有
            else:
                print(list_all_archives())
                return

        elif command == "--keyword":
            print(show_keywords())
            return

        elif command == "--search":
            # 搜索对话记录（简化版，后续可扩展）
            if len(sys.argv) < 3:
                print("❌ 搜索需要关键词\n")
                print("用法: /chat_history search <关键词>\n")
                return

            keyword = sys.argv[2]
            print(f"🔍 搜索: {keyword}\n")

            if not os.path.exists(ARCHIVE_DIR):
                print("❌ 归档目录不存在\n")
                return

            files = [f for f in os.listdir(ARCHIVE_DIR) if f.endswith('.txt')]
            if not files:
                print("❌ 暂无归档记录\n")
                return

            results = 0
            output = []

            for f in sorted(files):
                filepath = os.path.join(ARCHIVE_DIR, f)
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if keyword in content:
                        results += 1

                        output.append(f"[{results}] 📱 {f}")
                        output.append(f"路径: {filepath}")

                        # 显示第一个匹配片段
                        first_match_pos = content.find(keyword)
                        context_start = max(0, first_match_pos - 200)
                        context_end = min(len(content), first_match_pos + 200)

                        output.append(f"\n片段:")
                        output.append("..." + content[context_start:context_end] + "...")
                        output.append("\n")

            if results == 0:
                print(f"❌ 未找到包含 '{keyword}' 的对话记录\n")
            else:
                output.insert(0, f"✅ 找到 {results} 个匹配结果\n\n")
                print("\n".join(output))
            return

        # 检查是否直接是日期格式（例如：python3 main.py 20260222）
        elif re.match(r"^\d{8}$", command):
            print(list_date_archives(command))
            return

    # 如果没有参数，显示帮助
    print(show_help())

if __name__ == "__main__":
    main()
