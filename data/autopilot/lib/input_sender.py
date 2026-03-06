#!/usr/bin/env python3
"""
Layer 1: Input Sender — tmux + CLI 模式

发送方式：
  1. tmux send-keys: 向对应项目的 tmux pane 发送文本（TUI 可见）
  2. codex exec resume: 后台非交互发送（fallback）

验证方式：
  - 检查 session JSONL 文件大小变化
"""

import logging
import os
import subprocess
import time
from typing import Optional

logger = logging.getLogger(__name__)

# tmux session 名称
TMUX_SESSION = "autopilot"

# codex CLI 路径（launchd 环境 PATH 可能不含 /opt/homebrew/bin）
CODEX_PATH = "/opt/homebrew/bin/codex"
TMUX_PATH = "/opt/homebrew/bin/tmux"


def _get_codex_path(config: Optional[dict] = None) -> str:
    """获取 codex CLI 路径"""
    if config and config.get("codex_path"):
        return config["codex_path"]
    return CODEX_PATH


def _get_tmux_path(config: Optional[dict] = None) -> str:
    """获取 tmux 路径"""
    if config and config.get("tmux_path"):
        return config["tmux_path"]
    return TMUX_PATH


def check_codex_cli(config: Optional[dict] = None) -> bool:
    """检查 codex CLI 是否可用"""
    codex = _get_codex_path(config)
    return os.path.isfile(codex) and os.access(codex, os.X_OK)


def check_tmux_session(config: Optional[dict] = None) -> bool:
    """检查 autopilot tmux session 是否存在"""
    tmux = _get_tmux_path(config)
    try:
        result = subprocess.run(
            [tmux, 'has-session', '-t', TMUX_SESSION],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def list_tmux_windows(config: Optional[dict] = None) -> list:
    """列出 autopilot tmux session 的所有 window 名称"""
    tmux = _get_tmux_path(config)
    try:
        result = subprocess.run(
            [tmux, 'list-windows', '-t', TMUX_SESSION, '-F', '#{window_name}'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return [w.strip() for w in result.stdout.strip().split('\n') if w.strip()]
    except Exception:
        pass
    return []


def get_tmux_pane_pid(window_name: str, config: Optional[dict] = None) -> Optional[int]:
    """获取 tmux pane 中运行的进程 PID"""
    tmux = _get_tmux_path(config)
    try:
        result = subprocess.run(
            [tmux, 'list-panes', '-t', f'{TMUX_SESSION}:{window_name}',
             '-F', '#{pane_pid}'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip().split('\n')[0])
    except Exception:
        pass
    return None


def _get_pane_command(window_name: str, config: Optional[dict] = None) -> Optional[str]:
    """获取 tmux pane 当前运行的命令名"""
    tmux = _get_tmux_path(config)
    try:
        result = subprocess.run(
            [tmux, 'list-panes', '-t', f'{TMUX_SESSION}:{window_name}',
             '-F', '#{pane_current_command}'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except Exception:
        pass
    return None


def is_pane_running_codex(window_name: str, config: Optional[dict] = None) -> bool:
    """检查 tmux pane 是否有 codex 进程在运行"""
    cmd = _get_pane_command(window_name, config)
    return cmd is not None and cmd not in ('bash', 'zsh', 'sh', 'fish')


def capture_pane_output(window_name: str, lines: int = 50,
                        config: Optional[dict] = None) -> Optional[str]:
    """捕获 tmux pane 的最近输出"""
    tmux = _get_tmux_path(config)
    try:
        result = subprocess.run(
            [tmux, 'capture-pane', '-t', f'{TMUX_SESSION}:{window_name}',
             '-p', '-S', f'-{lines}'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass
    return None


def send_reply_via_tmux(reply: str, window_name: str,
                        config: Optional[dict] = None) -> bool:
    """
    通过 tmux send-keys 发送回复到对应项目 pane
    
    Codex TUI 在该 pane 中运行，消息会出现在 TUI 中。
    
    Args:
        reply: 要发送的回复文本
        window_name: tmux window 名称（项目名）
        config: 配置
    
    Returns:
        是否成功
    """
    tmux = _get_tmux_path(config)
    
    # 检查 window 存在
    windows = list_tmux_windows(config)
    if window_name not in windows:
        logger.error(f"tmux window '{window_name}' 不存在 (有: {windows})")
        return False
    
    # 检查 codex 是否在运行（防止在 shell prompt 里执行回复文本）
    if not is_pane_running_codex(window_name, config):
        logger.error(f"tmux window '{window_name}' 中 codex 未运行，跳过发送（防误执行）")
        return False
    
    try:
        # 将多行文本合并为单行（Codex TUI 不支持多行输入）
        # 换行符替换为空格，避免 tmux send-keys 把 \n 当回车
        single_line = reply.replace('\n', ' ').replace('\r', ' ').strip()
        
        # 使用 -l (literal) 避免特殊字符被解释
        result = subprocess.run(
            [tmux, 'send-keys', '-t', f'{TMUX_SESSION}:{window_name}',
             '-l', single_line],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            logger.error(f"tmux send-keys 文本失败: {result.stderr}")
            return False
        
        # 短暂等待确保文本输入完成
        time.sleep(0.1)
        
        # 发送 Enter
        result = subprocess.run(
            [tmux, 'send-keys', '-t', f'{TMUX_SESSION}:{window_name}',
             'Enter'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            logger.error(f"tmux send-keys Enter 失败: {result.stderr}")
            return False
        
        logger.info(f"通过 tmux 发送回复 ({len(reply)}字符) 到 window={window_name}")
        return True
    except subprocess.TimeoutExpired:
        logger.error("tmux send-keys 超时")
        return False
    except Exception as e:
        logger.exception(f"tmux send-keys 异常: {e}")
        return False


def send_reply_via_cli(reply: str, session_id: str,
                       project_dir: Optional[str] = None,
                       config: Optional[dict] = None) -> bool:
    """
    通过 codex exec resume 后台发送（fallback）
    
    非交互模式，不显示 TUI。
    
    Args:
        reply: 要发送的回复文本
        session_id: Codex session UUID
        project_dir: 项目目录
        config: 配置
    
    Returns:
        是否成功启动
    """
    codex = _get_codex_path(config)
    
    try:
        cmd = [codex, 'exec', 'resume', session_id, reply, '--full-auto']
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_dir or os.path.expanduser('~'),
        )
        
        # 等几秒看有没有立即报错
        try:
            _, stderr = process.communicate(timeout=5)
            if process.returncode is not None and process.returncode != 0:
                logger.error(f"codex exec resume 失败: {stderr[:200]}")
                return False
        except subprocess.TimeoutExpired:
            pass  # 正常，codex 在后台运行
        
        logger.info(f"CLI 发送成功 ({len(reply)}字符) session={session_id[:8]}")
        return True
    except FileNotFoundError:
        logger.error(f"codex 命令未找到: {codex}")
        return False
    except Exception as e:
        logger.exception(f"CLI 发送异常: {e}")
        return False


def send_reply(reply: str, project_name: str,
               session_id: Optional[str] = None,
               project_dir: Optional[str] = None,
               config: Optional[dict] = None) -> bool:
    """
    统一发送入口
    
    优先 tmux send-keys（TUI 可见），失败后 fallback 到 codex exec resume
    
    Args:
        reply: 回复文本
        project_name: 项目名称（也是 tmux window 名称）
        session_id: Codex session UUID（CLI fallback 用）
        project_dir: 项目目录（CLI fallback 用）
        config: 配置
    """
    # Tier 1: tmux send-keys
    if check_tmux_session(config):
        if send_reply_via_tmux(reply, project_name, config):
            return True
        logger.warning(f"tmux 发送失败，尝试 CLI fallback")
    else:
        logger.warning("autopilot tmux session 不存在")
    
    # Tier 2: codex exec resume (fallback)
    if session_id:
        return send_reply_via_cli(reply, session_id, project_dir, config)
    
    logger.error("发送失败：无 tmux session 且无 session_id 用于 CLI fallback")
    return False


def verify_send(session_path: str, poll_interval: int = 5,
                max_wait: int = 30) -> bool:
    """
    验证发送：检查 session JSONL 文件大小变化
    """
    try:
        original_size = os.path.getsize(session_path)
    except OSError:
        return False
    
    for _ in range(max_wait // poll_interval):
        time.sleep(poll_interval)
        try:
            if os.path.getsize(session_path) > original_size:
                logger.info("验证成功：Codex 已响应")
                return True
        except OSError:
            continue
    
    logger.warning(f"验证超时：{max_wait}s 内未检测到响应")
    return False


def setup_tmux_session(projects: list, config: Optional[dict] = None) -> bool:
    """
    创建 autopilot tmux session，每个项目一个 window
    
    如果 session 已存在，只补充缺失的 window。
    
    Args:
        projects: [(project_name, project_dir, session_id), ...]
        config: 配置
    
    Returns:
        是否成功
    """
    tmux = _get_tmux_path(config)
    codex = _get_codex_path(config)
    
    if not projects:
        return False
    
    session_exists = check_tmux_session(config)
    existing_windows = list_tmux_windows(config) if session_exists else []
    
    for i, (name, project_dir, session_id) in enumerate(projects):
        if name in existing_windows:
            # 检查 pane 是否有活跃进程（codex 或 node）
            pane_cmd = _get_pane_command(name, config)
            if pane_cmd and pane_cmd not in ('bash', 'zsh', 'sh', 'fish'):
                logger.info(f"Window '{name}' 已存在且有进程 ({pane_cmd})，跳过")
                continue
            else:
                # shell prompt = codex 已退出，不自动重启
                # 让 autopilot 的调度逻辑在需要时通过 send_reply 发送
                logger.info(f"Window '{name}' 中 codex 已退出，等待调度")
                continue
        
        # 创建 window
        codex_cmd = f"cd {project_dir} && {codex} resume {session_id} --full-auto"
        
        if not session_exists and i == 0:
            # 创建 session + 第一个 window
            subprocess.run(
                [tmux, 'new-session', '-d', '-s', TMUX_SESSION,
                 '-n', name, '-c', project_dir],
                capture_output=True, timeout=5
            )
            subprocess.run(
                [tmux, 'send-keys', '-t', f'{TMUX_SESSION}:{name}',
                 codex_cmd, 'Enter'],
                capture_output=True, timeout=5
            )
            session_exists = True
        else:
            # 添加 window
            subprocess.run(
                [tmux, 'new-window', '-t', TMUX_SESSION,
                 '-n', name, '-c', project_dir],
                capture_output=True, timeout=5
            )
            subprocess.run(
                [tmux, 'send-keys', '-t', f'{TMUX_SESSION}:{name}',
                 codex_cmd, 'Enter'],
                capture_output=True, timeout=5
            )
        
        logger.info(f"创建 tmux window '{name}' → codex resume {session_id[:8]}...")
        time.sleep(1)  # 给 codex 启动时间
    
    return True
