#!/usr/bin/env python3
# ⚠️ DEPRECATED: 此文件已被 scripts/watchdog.sh 替代。
# 仅 cleanup-state.py 仍在使用。请勿添加新功能。
"""
Codex Autopilot v3 — tmux + CLI 模式

架构:
  tmux session "autopilot" 中每个项目一个 window，运行 codex resume (TUI)
  launchd 每 60s 触发本脚本:
    1. 扫描 session JSONL → 找到 idle 的项目
    2. 分析意图 → 生成回复
    3. tmux send-keys 发送到对应 pane
    4. Telegram 通知

主要变更 (v2 → v3):
  - 去掉所有 GUI 发送 (ax_helper / AppleScript / CGEvent)
  - 去掉 window_router
  - 发送统一走 tmux send-keys + codex exec resume fallback
  - 预检去掉 GUI / CGEvent 权限检查
  - 启动时自动创建/维护 tmux session
"""

import hashlib
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict, Optional, Tuple

# 添加 lib 到 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.session_monitor import (
    SessionState,
    discover_sessions,
    get_session_state,
    is_last_message_from_user,
    read_last_assistant_message,
)
from lib.input_sender import (
    check_codex_cli,
    check_tmux_session,
    send_reply,
    setup_tmux_session,
    verify_send,
)
from lib.intent_analyzer import Intent, analyze_intent, get_intent_description
from lib.reply_generator import (
    generate_reply,
    generate_done_failed_reply,
    generate_next_task_reply,
    generate_all_tasks_complete_reply,
    generate_human_review_notice,
)
from lib.project_scanner import format_progress, scan_project_progress
from lib.telegram_notifier import (
    TelegramNotifier,
    create_notifier_from_config,
    format_error_notification,
    format_send_notification,
)
from lib.state_manager import (
    GlobalState,
    TaskStateInfo,
    check_cooldown,
    check_daily_limit,
    get_project_state,
    get_total_daily_sends,
    increment_send_count,
    load_config,
    load_state,
    record_history,
    save_state,
)

# Phase 2: 任务编排
from lib.task_orchestrator import (
    Task,
    TaskState,
    TasksConfig,
    CyclicDependencyError,
    load_tasks,
    get_ready_tasks,
    dispatch_next_task,
    build_prompt,
    mark_task_complete,
    mark_task_running,
    get_task_by_id,
    get_all_completed,
    format_task_progress,
)
from lib.done_checker import (
    check_done_conditions,
    format_done_result,
)

# Phase 3: 多项目调度
from lib.scheduler import (
    ProjectInfo,
    ProjectLifecycle,
    load_all_projects,
    schedule_projects,
    update_project_lifecycle,
    update_project_send_order,
)
from lib.telegram_bot import (
    TelegramCommandHandler,
    create_command_handler_from_config,
)

# 日志配置
LOG_DIR = "/tmp/autopilot"
LOG_FILE = os.path.join(LOG_DIR, "autopilot.log")
LOG_MAX_SIZE = 1024 * 1024  # 1MB
LOG_BACKUP_COUNT = 2


def setup_logging():
    """配置日志"""
    os.makedirs(LOG_DIR, exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []
    
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    ))
    root_logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s'
    ))
    root_logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)


logger = setup_logging()


def preflight_checks(config: dict) -> bool:
    """
    启动预检
    
    v3: 只检查 codex CLI 可用性（不再需要 GUI/AX 权限）
    """
    if not check_codex_cli(config):
        logger.error("预检失败: codex CLI 不可用")
        return False
    logger.info("预检通过: codex CLI")
    return True


def compute_output_hash(text: Optional[str]) -> Optional[str]:
    """计算输出文本的哈希（循环检测）"""
    if not text:
        return None
    return hashlib.md5(text[:500].encode()).hexdigest()


def find_tasks_yaml(project_dir: str) -> Optional[str]:
    """查找项目的 tasks.yaml"""
    project_name = os.path.basename(project_dir)
    
    path1 = os.path.join(os.path.expanduser("~/.autopilot"), "projects",
                         project_name, "tasks.yaml")
    if os.path.exists(path1):
        return path1
    
    path2 = os.path.join(project_dir, ".autopilot", "tasks.yaml")
    if os.path.exists(path2):
        return path2
    
    return None


def extract_codex_summary(last_message: str, max_length: int = 200) -> str:
    """从 Codex 输出中提取摘要"""
    if not last_message:
        return ""
    
    paragraphs = [p.strip() for p in last_message.split('\n\n') if p.strip()]
    if not paragraphs:
        return last_message[:max_length]
    
    for para in reversed(paragraphs):
        if not para.startswith('```') and not para.startswith('    '):
            return para[:max_length] + ("..." if len(para) > max_length else "")
    
    return paragraphs[-1][:max_length]


def process_project_with_tasks(
    project_dir: str,
    tasks_config: TasksConfig,
    config: dict,
    state: GlobalState,
    session,
    last_message: str,
    intent: Intent,
    notifier: Optional[TelegramNotifier]
) -> Tuple[bool, Optional[str]]:
    """带任务编排的项目处理 (Phase 2)"""
    project_name = tasks_config.project_name or os.path.basename(project_dir)
    proj_state = get_project_state(state, project_dir)
    
    if not proj_state.task_states:
        for task in tasks_config.tasks:
            proj_state.task_states[task.id] = TaskStateInfo()
    
    current_task_id = proj_state.current_task
    current_task = None
    if current_task_id:
        current_task = get_task_by_id(tasks_config.tasks, current_task_id)
    
    if not current_task:
        try:
            next_task, prompt = dispatch_next_task(
                tasks_config.tasks, proj_state.task_states
            )
        except CyclicDependencyError as e:
            logger.error(f"循环依赖: {e}")
            if notifier:
                notifier.send_simple(f"❌ 项目 {project_name} 检测到循环依赖: {e}")
            return False, None
        
        if next_task is None:
            if get_all_completed(tasks_config.tasks, proj_state.task_states):
                if notifier:
                    notifier.send_simple(f"🎉 项目 {project_name} 所有任务完成！")
                return False, None
            return False, None
        
        if prompt is None:
            notice = generate_human_review_notice(next_task.name, next_task.prompt)
            if notifier:
                notifier.send_simple(f"⏸ 项目 {project_name}: {notice}")
            return False, None
        
        proj_state.current_task = next_task.id
        return True, prompt
    
    if intent == Intent.TASK_COMPLETE:
        logger.info(f"检测到任务完成意图，验证完成条件...")
        default_min_size = tasks_config.get_default("min_file_size", 100)
        done_result = check_done_conditions(
            current_task.done_when, project_dir, default_min_size
        )
        
        logger.info(f"完成条件检测: {done_result.summary}")
        
        if done_result.passed:
            codex_summary = extract_codex_summary(last_message)
            mark_task_complete(current_task_id, proj_state.task_states, codex_summary)
            
            try:
                next_task, prompt = dispatch_next_task(
                    tasks_config.tasks, proj_state.task_states
                )
            except CyclicDependencyError as e:
                logger.error(f"循环依赖: {e}")
                return False, None
            
            if next_task is None:
                if get_all_completed(tasks_config.tasks, proj_state.task_states):
                    if notifier:
                        notifier.send_simple(
                            f"🎉 项目 {project_name} 所有 {len(tasks_config.tasks)} 个任务完成！"
                        )
                    proj_state.current_task = None
                    return False, None
                return False, None
            
            if prompt is None:
                notice = generate_human_review_notice(next_task.name, next_task.prompt)
                if notifier:
                    notifier.send_simple(f"⏸ 项目 {project_name}: {notice}")
                proj_state.current_task = next_task.id
                return False, None
            
            reply = generate_next_task_reply(
                prompt, current_task.name, current_task.on_complete
            )
            proj_state.current_task = next_task.id
            
            if notifier:
                notifier.send_simple(
                    f"✅ 项目 {project_name}: 任务 [{current_task.name}] 完成，开始 [{next_task.name}]"
                )
            return True, reply
        else:
            reply = generate_done_failed_reply(done_result, current_task.name)
            task_state = proj_state.task_states.get(current_task_id)
            if task_state:
                task_state.last_codex_output = last_message[:500]
            return True, reply
    
    return True, None


def process_project(
    project: ProjectInfo,
    config: dict,
    state: GlobalState,
    sessions: Dict[str, object],
    notifier: Optional[TelegramNotifier],
) -> bool:
    """
    处理单个项目
    
    v3: 使用 tmux send-keys 发送，不再需要 window_router
    """
    project_name = project.name
    project_dir = project.dir
    
    logger.info(f"处理项目: {project_name} (priority={project.priority})")
    
    proj_state = get_project_state(state, project_dir)
    
    if project.lifecycle == ProjectLifecycle.ENABLED:
        update_project_lifecycle(project, ProjectLifecycle.RUNNING, state)
    
    # 冷却期
    cooldown = project.get_override('cooldown', config.get('cooldown', 120))
    if check_cooldown(proj_state, cooldown):
        logger.info(f"项目 {project_name} 在冷却期，跳过")
        return False
    
    # 每日限制
    max_daily = project.get_override('max_daily_sends', config.get('max_daily_sends', 50))
    if check_daily_limit(proj_state, max_daily):
        logger.warning(f"项目 {project_name} 达到每日发送限制 ({max_daily})")
        return False
    
    # 全局限制
    max_total = config.get('max_daily_sends_total', 200)
    if get_total_daily_sends(state) >= max_total:
        logger.warning(f"全局每日发送限制已达到 ({max_total})")
        return False
    
    # 获取 session
    if project_dir not in sessions:
        logger.info(f"项目 {project_name} 没有活跃的 Codex session")
        return False
    
    session = sessions[project_dir]
    session_state = get_session_state(session)
    
    logger.info(f"Session 状态: {session_state.value} (age: {session.age_seconds:.0f}s)")
    
    if session_state == SessionState.ACTIVE:
        logger.info(f"Codex 正在工作，跳过")
        return False
    
    max_done_age = config.get('max_done_age', 7200)
    if session_state == SessionState.DONE and session.age_seconds > max_done_age:
        logger.info(f"Session 停止超过 {max_done_age}s，跳过")
        return False
    
    # 检查是否刚发过回复
    if is_last_message_from_user(session.path):
        user_wait_timeout = config.get('user_wait_timeout', 600)
        if session.age_seconds < user_wait_timeout:
            logger.info(f"等待 Codex 响应 ({session.age_seconds:.0f}s/{user_wait_timeout}s)")
            return False
        else:
            logger.warning(f"等待超时 ({session.age_seconds:.0f}s > {user_wait_timeout}s)，重发")
            proj_state.last_output_hash = None
            proj_state.loop_count = 0
    
    # 读取最后 assistant 消息
    last_message = read_last_assistant_message(session.path)
    if not last_message:
        logger.warning(f"无法读取 Codex 最后输出")
        return False
    
    logger.info(f"最后输出 ({len(last_message)} 字符): {last_message[:100]}...")
    
    # 循环检测
    output_hash = compute_output_hash(last_message)
    loop_threshold = config.get('loop_detection_threshold', 3)
    
    if proj_state.last_output_hash == output_hash and proj_state.loop_count > 0:
        if proj_state.loop_count >= loop_threshold:
            error_msg = f"检测到循环：连续 {loop_threshold} 次相似输出"
            logger.warning(error_msg)
            record_history(state, "loop_detected", project_name, error=error_msg)
            if notifier:
                notifier.send_simple(format_error_notification(project_name, error_msg))
            update_project_lifecycle(project, ProjectLifecycle.ERROR, state)
            return False
        else:
            logger.info(f"输出未变化 (loop_count={proj_state.loop_count}/{loop_threshold})")
            return False
    
    # 分析意图
    intent = analyze_intent(last_message)
    intent_desc = get_intent_description(intent)
    logger.info(f"识别意图: {intent.value} ({intent_desc})")
    
    # 任务编排
    tasks_config = project.tasks_config
    if not tasks_config:
        tasks_yaml_path = find_tasks_yaml(project_dir)
        if tasks_yaml_path:
            tasks_config = load_tasks(tasks_yaml_path)
    
    reply = None
    
    if tasks_config and tasks_config.tasks:
        logger.info(f"任务编排模式，{len(tasks_config.tasks)} 个任务")
        should_send, task_reply = process_project_with_tasks(
            project_dir, tasks_config, config, state,
            session, last_message, intent, notifier
        )
        if not should_send:
            return False
        if task_reply:
            reply = task_reply
    
    if reply is None:
        progress = scan_project_progress(project_dir)
        progress_str = format_progress(progress)
        reply = generate_reply(intent, context=progress_str, last_output=last_message)
    
    logger.info(f"生成回复: {reply[:100]}...")
    
    # 发送回复（tmux → CLI fallback）
    session_id = getattr(session, 'session_id', None)
    
    if not send_reply(reply, project_name, session_id, project_dir, config):
        error_msg = "发送回复失败"
        logger.error(error_msg)
        proj_state.consecutive_failures += 1
        record_history(state, "send_failed", project_name, intent.value, reply,
                       success=False, error=error_msg)
        
        max_failures = config.get('max_consecutive_failures', 5)
        if proj_state.consecutive_failures >= max_failures:
            error_msg = f"连续失败 {max_failures} 次"
            if notifier:
                notifier.send_simple(format_error_notification(project_name, error_msg))
            update_project_lifecycle(project, ProjectLifecycle.ERROR, state)
        return False
    
    # 发送成功
    proj_state.consecutive_failures = 0
    increment_send_count(proj_state)
    record_history(state, "send", project_name, intent.value, reply)
    
    # 循环检测更新
    if proj_state.last_output_hash == output_hash:
        proj_state.loop_count += 1
    else:
        proj_state.last_output_hash = output_hash
        proj_state.loop_count = 1
    
    update_project_send_order(project_name, state)
    
    # 任务状态更新
    if tasks_config and proj_state.current_task:
        task_state = proj_state.task_states.get(proj_state.current_task)
        if task_state:
            task_state.sends += 1
            task_state.last_send_at = datetime.now().isoformat()
    
    # Telegram 通知
    if notifier:
        notifier.send_simple(format_send_notification(project_name, reply[:200], intent_desc))
    
    # 验证发送
    verify_poll = config.get('verify_poll_interval', 5)
    verify_max = config.get('verify_max_wait', 30)
    if verify_send(session.path, verify_poll, verify_max):
        logger.info("发送验证成功")
    else:
        logger.info("发送验证超时")
    
    return True


def ensure_tmux_sessions(projects, sessions, config):
    """确保所有有活跃 session 的项目都在 tmux 中运行"""
    tmux_projects = []
    for project in projects:
        session = sessions.get(project.dir)
        if session and session.session_id:
            tmux_projects.append((project.name, project.dir, session.session_id))
    
    if tmux_projects:
        setup_tmux_session(tmux_projects, config)


def run_startup_state_cleanup() -> None:
    """启动时调用 cleanup-state.py，清理 state.json 中的僵尸项目数据。"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cleanup_script = os.path.join(base_dir, "scripts", "cleanup-state.py")
    config_path = os.path.join(base_dir, "config.yaml")
    state_path = os.path.join(base_dir, "state.json")

    if not os.path.exists(cleanup_script):
        logger.warning(f"状态清理脚本不存在，跳过: {cleanup_script}")
        return

    try:
        result = subprocess.run(
            [sys.executable, cleanup_script, "--config", config_path, "--state", state_path],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:
        logger.warning(f"启动状态清理执行失败: {exc}")
        return

    if result.stdout and result.stdout.strip():
        logger.info(result.stdout.strip())
    if result.returncode != 0:
        error_detail = result.stderr.strip() if result.stderr else f"exit={result.returncode}"
        logger.warning(f"启动状态清理失败: {error_detail}")


def main():
    """
    主入口 (v3)
    
    流程:
    1. 预检（codex CLI）
    2. 加载项目 + 发现 sessions
    3. 确保 tmux session 存在
    4. 轮询 Telegram 命令
    5. 调度 + 处理项目
    6. 保存状态
    """
    logger.info("=" * 50)
    logger.info("Autopilot v3 启动 (tmux + CLI)")
    
    config = load_config()
    if not config:
        logger.error("无法加载配置")
        return

    run_startup_state_cleanup()
    state = load_state()
    state.last_tick_at = datetime.now().isoformat()
    if not state.started_at:
        state.started_at = datetime.now().isoformat()
    
    notifier = create_notifier_from_config(config)
    command_handler = create_command_handler_from_config(config)
    
    # 预检
    if not preflight_checks(config):
        logger.error("预检失败，退出")
        if notifier:
            notifier.send_simple("❌ Autopilot 预检失败: codex CLI 不可用")
        return
    
    # 加载项目
    projects = load_all_projects(config)
    if not projects:
        logger.warning("没有找到任何项目")
        save_state(state)
        return
    
    logger.info(f"加载了 {len(projects)} 个项目")
    
    # 发现 sessions
    project_dirs = [p.dir for p in projects]
    sessions = discover_sessions(project_dirs)
    logger.info(f"发现 {len(sessions)} 个活跃 session")
    
    # 确保 tmux session 存在（自动创建/维护）
    ensure_tmux_sessions(projects, sessions, config)
    
    # Telegram 命令
    if command_handler:
        commands = command_handler.poll_commands(timeout=0)
        for cmd in commands:
            logger.info(f"处理命令: /{cmd.command} {cmd.project_name or ''}")
            result = command_handler.handle_command(cmd, projects, state, sessions)
            if cmd.chat_id:
                command_handler.send_reply(cmd.chat_id, result.message, cmd.message_id)
    
    # 调度
    scheduled_projects = schedule_projects(projects, sessions, config, state)
    
    if not scheduled_projects:
        logger.info("没有可调度的项目")
        save_state(state)
        return
    
    # 处理项目
    sends_this_tick = 0
    max_sends_per_tick = config.get('scheduler', {}).get('max_sends_per_tick', 1)
    inter_project_delay = config.get('scheduler', {}).get('inter_project_delay', 5)
    
    for project in scheduled_projects:
        if sends_this_tick >= max_sends_per_tick:
            logger.info(f"达到单次 tick 发送限制 ({max_sends_per_tick})")
            break
        
        max_total = config.get('max_daily_sends_total', 200)
        if get_total_daily_sends(state) >= max_total:
            logger.warning(f"全局每日发送限制已达到 ({max_total})")
            if notifier:
                notifier.send_simple("⚠️ 全局每日发送上限已达到")
            break
        
        try:
            if process_project(project, config, state, sessions, notifier):
                sends_this_tick += 1
                if sends_this_tick < max_sends_per_tick and inter_project_delay > 0:
                    time.sleep(inter_project_delay)
        except Exception as e:
            logger.exception(f"处理项目 {project.name} 异常: {e}")
            record_history(state, "error", project.name,
                           error=str(e), success=False)
    
    save_state(state)
    
    logger.info(f"Autopilot 完成，本次发送 {sends_this_tick} 条")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
