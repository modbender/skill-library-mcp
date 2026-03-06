#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw API 使用量监控与手动切换技能
监控当前模型API使用量，需要用户确认后再切换模型

⚠️ 使用前请根据实际环境配置以下路径：
  - OPENCLAW_DIR: OpenClaw配置目录（默认 ~/.openclaw）
  - LOG_DIR: 日志目录（默认 /tmp）
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional

# 配置（可通过环境变量覆盖）
CONFIG_FILE = os.path.expanduser(os.environ.get("OPENCLAW_DIR", "~/.openclaw") + "/openclaw.json")
LOG_FILE = os.path.expanduser(os.environ.get("LOG_DIR", "/tmp") + "/api_monitor.log")
SESSIONS_FILE = os.path.expanduser(os.environ.get("OPENCLAW_DIR", "~/.openclaw") + "/agents/main/sessions/sessions.json")
OPENCLAW_LOG = os.path.expanduser(os.environ.get("LOG_DIR", "/tmp") + "/openclaw.log")

# 可用模型列表（按优先级排序）
MODEL_PRIORITY = [
    "mydamoxing/MiniMax-M2.5-highspeed",
    "mydamoxing/MiniMax-M2.5",
    "volcengine/ark-code-latest",
    "hajimi/claude-sonnet-4-20250511"
]


def log(msg: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(log_msg + "\n")
    except Exception:
        pass  # 日志写入失败不影响主流程


def get_current_model() -> str:
    """获取当前使用的模型"""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        model = config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "")
        return model
    except Exception as e:
        log(f"读取当前模型失败: {e}")
        return ""


def set_model(model: str) -> bool:
    """设置模型并重启Gateway"""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        
        if "agents" not in config:
            config["agents"] = {}
        if "defaults" not in config["agents"]:
            config["agents"]["defaults"] = {}
        if "model" not in config["agents"]["defaults"]:
            config["agents"]["defaults"]["model"] = {}
        
        config["agents"]["defaults"]["model"]["primary"] = model
        
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        log(f"已切换模型到: {model}")
        
        # 重启Gateway（需要相应权限）
        subprocess.run(["pkill", "-f", "openclaw-gateway"], capture_output=True)
        time.sleep(2)
        subprocess.Popen(
            ["nohup", "openclaw", "gateway", "start"],
            stdout=open(OPENCLAW_LOG, "a"),
            stderr=subprocess.STDOUT
        )
        
        return True
    except Exception as e:
        log(f"设置模型失败: {e}")
        return False


def check_api_status() -> Dict:
    """检查API状态，返回需要询问用户的信息"""
    current_model = get_current_model()
    
    # 分析最近的会话日志判断API状态
    result = {
        "ok": True,
        "current_model": current_model,
        "quota_warning": False,
        "error_count": 0,
        "error_types": [],
        "suggestion": ""
    }
    
    # 检查最近的错误
    try:
        if os.path.exists(SESSIONS_FILE):
            with open(SESSIONS_FILE, "r") as f:
                data = json.load(f)
                sessions = data.get("sessions", [])
                
                # 检查最近5个会话
                for session in sessions[-5:]:
                    if session.get("status") == "error":
                        result["error_count"] += 1
                        error_msg = session.get("error", "")
                        if "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
                            result["quota_warning"] = True
                            result["error_types"].append("quota")
                        elif "rate" in error_msg.lower():
                            result["error_types"].append("rate_limit")
    except Exception as e:
        log(f"检查状态失败: {e}")
    
    # 生成建议
    if result["quota_warning"]:
        result["suggestion"] = "API配额可能不足，建议切换模型"
    elif result["error_count"] > 2:
        result["suggestion"] = f"最近有{result['error_count']}次错误，建议检查"
    else:
        result["suggestion"] = "API状态正常"
    
    return result


def get_next_model(current_model: str) -> Optional[str]:
    """获取下一个可用的模型"""
    try:
        current_index = MODEL_PRIORITY.index(current_model) if current_model in MODEL_PRIORITY else -1
        
        for i in range(current_index + 1, len(MODEL_PRIORITY)):
            return MODEL_PRIORITY[i]
        
        return MODEL_PRIORITY[0]
    except Exception as e:
        log(f"获取下一个模型失败: {e}")
        return None


def ask_user_switch() -> bool:
    """生成需要询问用户的消息"""
    current_model = get_current_model()
    status = check_api_status()
    next_model = get_next_model(current_model)
    
    message = f"""
⚠️ API监控报告

当前模型: {current_model}
状态: {status['suggestion']}
错误次数: {status['error_count']}

建议切换到: {next_model}

请确认是否切换？回复"确认"或"取消"
"""
    print(message)
    return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw API 监控（询问确认模式）")
    parser.add_argument("--check", action="store_true", help="检查状态")
    parser.add_argument("--status", action="store_true", help="查看详细状态")
    parser.add_argument("--ask", action="store_true", help="询问用户是否切换")
    parser.add_argument("--confirm", action="store_true", help="确认切换")
    parser.add_argument("--model", type=str, help="指定切换到某个模型")
    parser.add_argument("--list-models", action="store_true", help="列出可用模型")
    parser.add_argument("--config", type=str, help="指定OpenClaw配置目录")
    parser.add_argument("--log-dir", type=str, help="指定日志目录")
    
    args = parser.parse_args()
    
    # 应用自定义路径
    global CONFIG_FILE, LOG_FILE, SESSIONS_FILE, OPENCLAW_LOG
    if args.config:
        CONFIG_FILE = os.path.expanduser(args.config) + "/openclaw.json"
        SESSIONS_FILE = os.path.expanduser(args.config) + "/agents/main/sessions/sessions.json"
    if args.log_dir:
        LOG_FILE = os.path.expanduser(args.log_dir) + "/api_monitor.log"
        OPENCLAW_LOG = os.path.expanduser(args.log_dir) + "/openclaw.log"
    
    if args.list_models:
        print("可用模型列表：")
        for i, model in enumerate(MODEL_PRIORITY, 1):
            current = "← 当前" if model == get_current_model() else ""
            print(f"  {i}. {model} {current}")
    
    elif args.check or args.status:
        status = check_api_status()
        print(f"\n当前模型: {status['current_model']}")
        print(f"状态: {status['suggestion']}")
        print(f"错误次数: {status['error_count']}")
        if status['error_types']:
            print(f"错误类型: {', '.join(set(status['error_types']))}")
    
    elif args.ask:
        ask_user_switch()
    
    elif args.confirm:
        current = get_current_model()
        next_m = get_next_model(current)
        if next_m:
            print(f"确认切换: {current} → {next_m}")
            if set_model(next_m):
                print("切换成功!")
            else:
                print("切换失败!")
        else:
            print("无法获取下一个模型")
    
    elif args.model:
        if set_model(args.model):
            print(f"切换到 {args.model} 成功!")
        else:
            print(f"切换到 {args.model} 失败!")
    
    else:
        # 默认显示状态
        status = check_api_status()
        print(f"当前模型: {status['current_model']}")
        print(f"状态: {status['suggestion']}")


if __name__ == "__main__":
    main()
