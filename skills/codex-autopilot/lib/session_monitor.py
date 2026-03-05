#!/usr/bin/env python3
"""
Layer 1: Session Monitor
- 扫描 Codex Desktop session JSONL 文件
- 基于 mtime 判定会话状态 (ACTIVE/IDLE/DONE)
- 读取最后 assistant 消息
"""

import json
import os
import time
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from glob import glob
from pathlib import Path
from typing import Dict, List, Optional

# 状态判定阈值 (秒)
ACTIVE_THRESHOLD = 120   # < 120s = Codex 正在工作
IDLE_THRESHOLD = 360     # 120s ~ 360s = 刚停下来，等待输入
                         # > 360s = 已完成/长时间无活动


class SessionState(Enum):
    ACTIVE = "active"    # Codex 正在工作
    IDLE = "idle"        # Codex 停下来了，等待输入
    DONE = "done"        # 长时间无活动


def _extract_session_id(jsonl_path: str) -> Optional[str]:
    """从 JSONL 文件名提取 session UUID"""
    # 格式: rollout-2026-02-06T21-49-15-019c36a5-b6ef-75f0-b9f6-0bcee9c3e085.jsonl
    import re
    basename = os.path.basename(jsonl_path)
    # UUID 格式: 8-4-4-4-12 hex
    match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', basename)
    return match.group(1) if match else None


@dataclass
class SessionInfo:
    path: str
    cwd: str
    mtime: float
    file_size: int = 0  # 文件大小（字节），用于选择最长的 session
    session_id: Optional[str] = None  # Codex session UUID（用于 codex resume）
    
    @property
    def age_seconds(self) -> float:
        return time.time() - self.mtime


# 缓存: {jsonl_path → cwd}
# session_meta 是第一行，不会变，只需读一次
_session_meta_cache: Dict[str, str] = {}


def _read_session_meta(jsonl_path: str) -> Optional[str]:
    """读取 session JSONL 第一行的 cwd"""
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            line = f.readline()
            if not line:
                return None
            data = json.loads(line)
            if data.get('type') == 'session_meta':
                return data.get('payload', {}).get('cwd')
    except (json.JSONDecodeError, IOError, OSError):
        pass
    return None


def discover_sessions(project_dirs: List[str]) -> Dict[str, SessionInfo]:
    """
    扫描所有 session，按 cwd 分配给各项目
    
    Args:
        project_dirs: 项目目录列表
        
    Returns:
        {project_dir → SessionInfo} 映射，每个项目取最新 mtime 的 session
    """
    global _session_meta_cache
    sessions: Dict[str, SessionInfo] = {}
    
    today = date.today()
    
    codex_sessions_base = os.path.expanduser("~/.codex/sessions")
    
    # 策略: 先扫最近 7 天的目录，再用 find 补漏最近修改的文件
    # Codex 会持续写入旧日期目录下的 session 文件
    scan_dates = [today - timedelta(days=i) for i in range(7)]
    
    seen_paths = set()
    all_jsonl_paths = []
    
    # 1. 按日期目录扫描
    for d in scan_dates:
        pattern = os.path.join(codex_sessions_base, f"{d:%Y/%m/%d}", "*.jsonl")
        for p in glob(pattern):
            if p not in seen_paths:
                seen_paths.add(p)
                all_jsonl_paths.append(p)
    
    # 2. 补漏: 扫描所有最近 60 分钟内修改过的 JSONL（捕获跨日期的活跃 session）
    try:
        import subprocess
        result = subprocess.run(
            ['find', codex_sessions_base, '-name', '*.jsonl', '-mmin', '-60'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for p in result.stdout.strip().split('\n'):
                if p and p not in seen_paths:
                    seen_paths.add(p)
                    all_jsonl_paths.append(p)
    except Exception:
        pass  # find 失败不影响主流程
    
    for jsonl_path in all_jsonl_paths:
            try:
                mtime = os.path.getmtime(jsonl_path)
            except OSError:
                continue
            
            # 缓存 session_meta
            if jsonl_path not in _session_meta_cache:
                cwd = _read_session_meta(jsonl_path)
                if cwd:
                    _session_meta_cache[jsonl_path] = cwd
                else:
                    continue
            
            cwd = _session_meta_cache.get(jsonl_path)
            if not cwd:
                continue
            
            # 匹配项目目录
            for project_dir in project_dirs:
                # 标准化路径用于比较
                norm_cwd = os.path.normpath(cwd)
                norm_project = os.path.normpath(project_dir)
                
                if norm_cwd.startswith(norm_project) or norm_cwd == norm_project:
                    try:
                        file_size = os.path.getsize(jsonl_path)
                    except OSError:
                        file_size = 0
                    
                    session_id = _extract_session_id(jsonl_path)
                    existing = sessions.get(project_dir)
                    if not existing:
                        sessions[project_dir] = SessionInfo(
                            path=jsonl_path,
                            cwd=cwd,
                            mtime=mtime,
                            file_size=file_size,
                            session_id=session_id
                        )
                    else:
                        # 优先选最大的 session（最长对话历史）
                        # 同样大则选最新修改的
                        if file_size > existing.file_size or (
                            file_size == existing.file_size and mtime > existing.mtime
                        ):
                            sessions[project_dir] = SessionInfo(
                                path=jsonl_path,
                                cwd=cwd,
                                mtime=mtime,
                                file_size=file_size,
                                session_id=session_id
                            )
                    break  # 一个 session 只匹配一个项目
    
    return sessions


def get_session_state(session: SessionInfo) -> SessionState:
    """基于 mtime 判定会话状态"""
    age = session.age_seconds
    
    if age < ACTIVE_THRESHOLD:
        return SessionState.ACTIVE
    elif age < IDLE_THRESHOLD:
        return SessionState.IDLE
    else:
        return SessionState.DONE


def is_last_message_from_user(session_path: str) -> bool:
    """
    检查 session 最后一条消息是否是 user message
    
    如果是，说明我们刚发了回复、Codex 还没输出——这轮应该跳过。
    
    Returns:
        True = 最后是 user message，False = 最后是 assistant 或其他
    """
    try:
        file_size = os.path.getsize(session_path)
        read_size = min(file_size, 50 * 1024)  # 读 50KB 足够
        
        with open(session_path, 'rb') as f:
            if read_size < file_size:
                f.seek(-read_size, 2)
            content = f.read().decode('utf-8', errors='replace')
        
        lines = content.strip().split('\n')
        
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            msg_type = data.get('type', '')
            
            # user_message 类型
            if msg_type == 'user_message':
                return True
            
            # response_item 中的 user message（codex exec resume 写入的格式）
            if msg_type == 'response_item':
                payload = data.get('payload', {})
                if payload.get('role') == 'user' and payload.get('type') == 'message':
                    return True
                if payload.get('role') == 'assistant':
                    return False
            
            # event_msg 跳过继续找
            if msg_type == 'event_msg':
                continue
            
            # turn_context 跳过
            if msg_type == 'turn_context':
                continue
                
            # 其他类型，不确定
            break
        
        return False
    except (IOError, OSError):
        return False


def read_last_assistant_message(session_path: str, max_chars: int = 4000) -> Optional[str]:
    """
    从 JSONL 尾部逆向读取最后一条 assistant 消息
    
    查找条件:
    - type = response_item
    - payload.type = message
    - payload.role = assistant
    - payload.content[].type = output_text
    
    Returns:
        最后 assistant 消息的文本，截断到 max_chars
    """
    try:
        # 从文件尾部读取
        # 大 session 可能 100+MB，读 200KB 确保覆盖最后的 assistant 消息
        file_size = os.path.getsize(session_path)
        read_size = min(file_size, 200 * 1024)
        
        with open(session_path, 'rb') as f:
            if read_size < file_size:
                f.seek(-read_size, 2)  # 从尾部往前 seek
            content = f.read().decode('utf-8', errors='replace')
        
        # 按行分割，逆序查找
        lines = content.strip().split('\n')
        
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            if data.get('type') != 'response_item':
                continue
            
            payload = data.get('payload', {})
            if payload.get('type') != 'message':
                continue
            if payload.get('role') != 'assistant':
                continue
            
            # 提取 output_text
            contents = payload.get('content', [])
            texts = []
            for c in contents:
                if c.get('type') == 'output_text':
                    texts.append(c.get('text', ''))
            
            if texts:
                full_text = '\n'.join(texts)
                return full_text[:max_chars] if len(full_text) > max_chars else full_text
        
        return None
        
    except (IOError, OSError) as e:
        return None


def clear_cache():
    """清除 session meta 缓存（用于测试）"""
    global _session_meta_cache
    _session_meta_cache = {}
