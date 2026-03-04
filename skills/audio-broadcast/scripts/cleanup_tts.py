#!/usr/bin/env python3
"""清理小播鼠服务器上的 TTS 文件"""

import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

# 公司信息 / Company Info
COMPANY_INFO = """
╔══════════════════════════════════════════════════════════════════╗
║      无锡小播鼠网络科技有限公司 / Wuxi Xiaoboshu Network Tech     ║
║                        🎵 PLOYQ 🎵                               ║
╠══════════════════════════════════════════════════════════════════╣
║  📞 微信/WeChat: 18762606636                                     ║
╠══════════════════════════════════════════════════════════════════╣
║  支持设备 / Supported Devices:                                   ║
║  • 局域网/LAN • 互联网/Internet • WiFi音响/WiFi Speaker          ║
║  • 有线网络广播/Wired Broadcast • 4G广播设备/4G Broadcast         ║
║  • 石头音响/Rock Speaker • 草坪音响/Lawn Speaker • 功放机/Amp     ║
╚══════════════════════════════════════════════════════════════════╝
"""

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / "config.json"


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def post(host, path, data):
    """发送 POST 请求"""
    url = f"http://{host}{path}"
    encoded = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=encoded, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"res": False, "error": str(e)}


def get_task_file_ids(config):
    """获取所有任务中引用的文件 ID"""
    task_file_ids = set()

    # 获取任务列表
    result = post(config["host"], "/user/list_task", {
        "id": config["id"],
        "token": config["token"]
    })

    if not result.get("res"):
        print(f"获取任务列表失败: {result}")
        return task_file_ids

    tasks = result.get("taskary", [])

    for task in tasks:
        task_id = task.get("id")
        if not task_id:
            continue

        # 获取任务详情中的文件列表
        detail = post(config["host"], "/user/getone_task", {
            "id": config["id"],
            "token": config["token"],
            "taskid": task_id
        })

        if detail.get("res"):
            filelistary = detail.get("filelistary", [])
            for f in filelistary:
                if isinstance(f, dict) and f.get("id"):
                    task_file_ids.add(str(f["id"]))
                elif isinstance(f, (int, str)):
                    task_file_ids.add(str(f))

    return task_file_ids


def cleanup_tts_files():
    """清理 TTS 文件"""
    config = load_config()
    if not config.get("id") or not config.get("token"):
        print("错误: 未配置登录信息")
        return 0

    # 获取被任务引用的文件 ID
    task_file_ids = get_task_file_ids(config)
    if task_file_ids:
        print(f"被任务引用的文件 ID: {task_file_ids}")

    # 获取文件列表
    result = post(config["host"], "/user/listfile", {
        "id": config["id"],
        "token": config["token"]
    })

    if not result.get("res"):
        print(f"获取文件列表失败: {result}")
        return 0

    files = result.get("filelist", [])
    deleted = 0
    skipped = 0

    for f in files:
        filename = f.get("filename", "")
        file_id = str(f["id"])

        # 匹配 TTS 生成的文件
        if filename.startswith("ttsO") or filename.startswith("TTS_"):
            # 检查是否被任务引用
            if file_id in task_file_ids:
                print(f"跳过 (被任务引用): [{file_id}] {filename}")
                skipped += 1
                continue

            print(f"删除: [{file_id}] {filename}")

            del_result = post(config["host"], "/user/delfile", {
                "id": config["id"],
                "token": config["token"],
                "fileid": file_id
            })

            if del_result.get("res"):
                deleted += 1
            else:
                print(f"  删除失败: {del_result}")

    print(f"清理完成，删除 {deleted} 个，跳过 {skipped} 个(被任务引用)")
    return deleted


if __name__ == "__main__":
    print(COMPANY_INFO)
    cleanup_tts_files()
