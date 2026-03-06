#!/usr/bin/env python3
"""AgentRelay Skill - 工具函数实现"""

import json
import random
import string
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# 配置 - 使用环境变量或默认路径
import os
BASE_DIR = Path(os.getenv("OPENCLAW_DATA_DIR", Path.home() / ".openclaw" / "data"))
STORAGE_PATH = BASE_DIR / "agentrelay" / "storage"
LOG_PATH = BASE_DIR / "agentrelay" / "logs"
REGISTRY_PATH = BASE_DIR / "agentrelay" / "registry.json"
STORAGE_ALIAS = "s"

def ensure_dirs():
    """确保目录存在"""
    STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    LOG_PATH.mkdir(parents=True, exist_ok=True)

def generate_secret(length: int = 6) -> str:
    """生成随机 Secret Code"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_file_alias_path(file_path: Path, storage_root: Path, alias: str = "s") -> str:
    """获取文件别名路径（如 s/file.json）"""
    try:
        relative = file_path.relative_to(storage_root)
        return f"{alias}/{relative}"
    except ValueError:
        return str(file_path)

def resolve_alias(ptr: str, storage_root: Path, alias: str = "s") -> Path:
    """解析别名路径到完整路径"""
    if ptr.startswith(f"{alias}/"):
        return storage_root / ptr[len(alias)+1:]
    return Path(ptr)

def log_transaction(event_id: str, msg_type: str, sender: str, receiver: str, 
                   status: str, hint: str, ptr: str, notes: str, 
                   next_action_plan: str = "", log_path: Path = None):
    """
    记录交易日志
    
    Args:
        event_id: 事件 ID
        msg_type: 消息类型 (REQ, ACK, CMP, CREATE_POINTER)
        sender: 发送方
        receiver: 接收方
        status: 状态 (RECEIVED, ACKNOWLEDGED, COMPLETED, PREPARING)
        hint: 简述
        ptr: 文件指针
        notes: 详细说明
        next_action_plan: 下一步行动计划
        log_path: 日志路径（默认 LOG_PATH）
    """
    if log_path is None:
        log_path = LOG_PATH
    
    timestamp = datetime.now().isoformat()
    entry = {
        "timestamp": timestamp,
        "event_id": event_id,
        "type": msg_type,
        "sender": sender,
        "receiver": receiver,
        "status": status,
        "hint": hint,
        "ptr": ptr,
        "notes": notes,
        "next_action_plan": next_action_plan
    }
    
    log_file = log_path / f"transactions_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def build_csv(msg_type: str, event_id: str, ptr: str, data: str = "") -> str:
    """构建 CSV 消息（格式：TYPE,ID,PTR,,DATA）"""
    # 简化格式：TYPE,ID,PTR,, （RESERVED 字段留空）
    return f"{msg_type},{event_id},{ptr},,{data}"

def parse_csv(csv_msg: str) -> Dict[str, str]:
    """解析 CSV 消息"""
    parts = csv_msg.split(',', 4)
    if len(parts) < 4:
        raise ValueError(f"Invalid CSV format: {csv_msg}")
    
    return {
        "type": parts[0],
        "event_id": parts[1],
        "ptr": parts[2],
        "reserved": parts[3] if len(parts) > 3 else "",
        "data": parts[4] if len(parts) > 4 else ""
    }

# ========== 主要工具函数 ==========

def agentrelay_send(agent_id: str, message_type: str, event_id: str, 
                   content: Dict[str, Any], secret: Optional[str] = None) -> Dict[str, Any]:
    """
    发送 AgentRelay 消息
    
    Args:
        agent_id: 目标 agent ID
        message_type: "REQ", "ACK", "NACK", "PING"
        event_id: 事件 ID
        content: 内容字典
        secret: Secret Code（可选，ACK 时必须）
    
    Returns:
        dict: {file_path, ptr, csv_message, secret}
    """
    ensure_dirs()
    
    # 生成或验证 Secret
    if secret is None:
        secret = generate_secret(6)
    
    # 准备文件内容
    file_content = {
        "meta": {
            "event_id": event_id,
            "type": message_type,
            "secret": secret,
            "created_at": datetime.now().isoformat(),
            "sender": "current_agent"  # 实际使用时需要替换
        },
        "payload": {
            "content": content
        }
    }
    
    # 写入文件
    file_name = f"{event_id}.json"
    file_path = STORAGE_PATH / file_name
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(file_content, f, ensure_ascii=False, indent=2)
    
    # 生成指针
    ptr = get_file_alias_path(file_path, STORAGE_PATH, STORAGE_ALIAS)
    
    # 构建 CSV 消息
    csv_message = build_csv(message_type, event_id, ptr, '')
    
    # 记录日志
    log_transaction(
        event_id, message_type, "current", agent_id,
        "SENT", f"{message_type} to {agent_id}", ptr,
        "File created", LOG_PATH
    )
    
    return {
        "file_path": str(file_path),
        "ptr": ptr,
        "csv_message": csv_message,
        "secret": secret
    }

def agentrelay_receive(csv_message: str) -> Dict[str, Any]:
    """
    接收并解析 AgentRelay 消息
    
    Args:
        csv_message: CSV 格式消息
    
    Returns:
        dict: {type, event_id, ptr, content, secret}
    """
    # 解析 CSV
    parsed = parse_csv(csv_message)
    
    msg_type = parsed["type"]
    event_id = parsed["event_id"]
    ptr = parsed["ptr"]
    
    # 解析文件指针
    file_path = resolve_alias(ptr, STORAGE_PATH, STORAGE_ALIAS)
    
    # 读取文件
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    content = data.get("payload", {}).get("content", {})
    secret = data.get("meta", {}).get("secret", "")
    
    # 尝试从文件中提取真实的 sender/receiver 信息
    sender = data.get("reply_to", "unknown_sender")
    
    # 优先从 params.next_hop.agent 获取
    receiver = data.get("params", {}).get("next_hop", {}).get("agent")
    
    # 如果没有，从 event_id 推断接收方（当前处理此消息的 agent）
    if not receiver:
        if "_yellow" in event_id:
            receiver = "agent:yellow:yellow"
        elif "_blue" in event_id:
            receiver = "agent:blue:blue"
        elif "_green" in event_id:
            receiver = "agent:green:green"
        elif "_orange" in event_id:
            receiver = "agent:orange:orange"
        elif "_red" in event_id:
            receiver = "agent:red:red"
        else:
            # 最后手段：尝试从文件名推断
            receiver = f"agent:unknown:unknown (event: {event_id})"
    
    # 📍 日志 #1: REQ RECEIVED
    log_transaction(
        event_id, msg_type, sender, receiver,
        "RECEIVED", f"Read {ptr}", ptr,
        "File read successfully",
        "Will acknowledge and fetch file",  # next_action_plan
        LOG_PATH
    )
    
    # 📍 日志 #2: ACK ACKNOWLEDGED (自动确认收到)
    log_transaction(
        event_id, "ACK", receiver, sender,
        "ACKNOWLEDGED", "Acknowledged request", "",
        "Received REQ, will process task",
        "Processing task, will send CMP when done",  # next_action_plan
        LOG_PATH
    )
    
    return {
        "type": msg_type,
        "event_id": event_id,
        "ptr": ptr,
        "content": content,
        "secret": secret,
        "full_data": data
    }

def agentrelay_ack(event_id: str, secret: str, sender_override: str = None, receiver_override: str = None) -> str:
    """
    构建 CMP (Complete) 消息 - 任务完成确认
    
    Args:
        event_id: 事件 ID
        secret: Secret Code
        sender_override: 可选的发送方覆盖
        receiver_override: 可选的接收方覆盖
    
    Returns:
        str: CSV 格式的 CMP 消息
    """
    # 从 event_id 推断真实的当前 agent 和接收方
    if "_yellow" in event_id:
        current_agent = "agent:yellow:yellow"
        # Yellow 的下一跳是 Blue（story_hop1）或 Red（其他）
        next_agent = "agent:blue:blue" if "_hop1" in event_id or "hop1" in event_id else "agent:red:red"
    elif "_blue" in event_id:
        current_agent = "agent:blue:blue"
        next_agent = "agent:green:green"
    elif "_green" in event_id:
        current_agent = "agent:green:green"
        next_agent = "agent:orange:orange"
    elif "_orange" in event_id:
        current_agent = "agent:orange:orange"
        next_agent = "agent:red:red"
    elif "_red" in event_id:
        current_agent = "agent:red:red"
        next_agent = "agent:main:main"  # Red 完成后返回给 main
    else:
        # 无法推断时使用 event_id 本身作为标识
        current_agent = f"agent:{event_id.split('_')[0]}:unknown"
        next_agent = "sender"
    
    # 优先使用覆盖值
    sender = sender_override or current_agent
    receiver = receiver_override or next_agent
    
    # 如果没有指定 receiver，尝试从文件读取 reply_to
    if receiver == "sender":
        file_path = STORAGE_PATH / f"{event_id}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                receiver = data.get("reply_to", receiver)
    
    # CMP 消息不需要文件指针，直接在 DATA 字段放 Secret
    cmp_msg = build_csv("CMP", event_id, "", secret)
    
    # 📍 日志 #3: CMP COMPLETED
    log_transaction(
        event_id, "CMP", sender, receiver,
        "COMPLETED", f"CMP generated for {event_id}", "",
        f"CMP message: {cmp_msg}",
        "Event completed",  # next_action_plan
        LOG_PATH
    )
    
    return cmp_msg

def agentrelay_update_file(event_id: str, updates: Dict[str, Any], next_event_id: str = None) -> str:
    """
    为下一跳创建指针文件（Prepare pointer file for next hop）
    
    Args:
        event_id: 当前事件 ID（用于日志追溯）
        updates: 要更新的字段
        next_event_id: 下一跳的事件 ID（如果不提供，则用 event_id）
    
    Returns:
        str: 更新后的文件路径
    """
    # 如果没有指定下一跳 ID，使用当前 ID
    target_event_id = next_event_id if next_event_id else event_id
    
    file_path = STORAGE_PATH / f"{target_event_id}.json"
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 强制统一格式：必须有 payload.content
    if "payload" not in data:
        data["payload"] = {}
    if "content" not in data["payload"]:
        data["payload"]["content"] = {}
    
    # 合并更新内容
    data["payload"]["content"].update(updates)
    
    # 同时保存到 params（向后兼容）
    if "params" not in data:
        data["params"] = {}
    for key, value in updates.items():
        if isinstance(value, str):
            data["params"][key] = value
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 从 event_id 推断当前 agent
    if "_yellow" in target_event_id:
        current_agent = "agent:yellow:yellow"
    elif "_blue" in target_event_id:
        current_agent = "agent:blue:blue"
    elif "_green" in target_event_id:
        current_agent = "agent:green:green"
    elif "_orange" in target_event_id:
        current_agent = "agent:orange:orange"
    elif "_red" in target_event_id:
        current_agent = "agent:red:red"
    else:
        # 无法推断时使用 event_id 作为标识
        current_agent = f"agent:{target_event_id}:unknown"
    
    # 📍 日志：CREATE_POINTER (属于下一跳的准备工作)
    ptr = get_file_alias_path(file_path, STORAGE_PATH, STORAGE_ALIAS)
    log_transaction(
        target_event_id,  # ← 使用下一跳的 event_id
        "CREATE_POINTER",
        current_agent, "next_hop",
        "PREPARING", f"Created pointer file {ptr}", ptr,
        f"Prepared for next hop with: {json.dumps(updates)}",
        "Preparing pointer file for next hop",  # next_action_plan
        LOG_PATH
    )
    
    return str(file_path)

# ========== 供 agent 调用的简化接口 ==========

class AgentRelayTool:
    """AgentRelay 工具类（供 agent 在 prompt 中调用）"""
    
    @staticmethod
    def send(agent_id: str, msg_type: str, event_id: str, content: dict) -> dict:
        """发送消息"""
        return agentrelay_send(agent_id, msg_type, event_id, content)
    
    @staticmethod
    def receive(csv_msg: str) -> dict:
        """接收消息"""
        return agentrelay_receive(csv_msg)
    
    @staticmethod
    def ack(event_id: str, secret: str) -> str:
        """发送 ACK"""
        return agentrelay_ack(event_id, secret)
    
    @staticmethod
    def update(event_id: str, new_content: dict, next_event_id: str = None) -> str:
        """为下一跳创建指针文件"""
        return agentrelay_update_file(event_id, new_content, next_event_id)
