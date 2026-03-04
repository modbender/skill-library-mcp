#!/usr/bin/env python3
"""
STP V2 核心编排脚本
负责异步子代理执行的任务编排
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

WORKSPACE_ROOT = Path.home() / ".openclaw" / "workspace"
TASKS_DIR = WORKSPACE_ROOT / "tasks"


def sessions_history_sync(session_key: str, limit: int = 10) -> Dict[str, Any]:
    """
    读取子代理会话状态
    通过 sessions.json 和 jsonl 文件获取活动状态
    """
    import time
    
    sessions_file = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json"
    
    if not sessions_file.exists():
        return {"error": "sessions.json not found"}
    
    try:
        sessions_data = json.loads(sessions_file.read_text(encoding='utf-8'))
        
        # 查找对应的会话
        session_info = sessions_data.get(session_key)
        if not session_info:
            return {"error": f"session {session_key} not found", "available_sessions": list(sessions_data.keys())[:10]}
        
        updated_at = session_info.get("updatedAt", 0)
        current_time = int(time.time() * 1000)  # milliseconds
        elapsed_ms = current_time - updated_at
        elapsed_seconds = elapsed_ms / 1000
        
        # 读取 jsonl 文件获取更多信息
        session_file_path = session_info.get("sessionFile")
        last_message = None
        last_msg_type = None
        tool_count = 0
        tool_call_count = 0
        tool_result_count = 0
        
        if session_file_path and Path(session_file_path).exists():
            try:
                with open(session_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    tool_call_count = len([l for l in lines if '"toolCall"' in l])
                    tool_result_count = len([l for l in lines if '"toolResult"' in l])
                    tool_count = tool_call_count
                    if lines:
                        # 获取最后几行
                        for line in reversed(lines[-10:]):
                            try:
                                last_msg = json.loads(line)
                                msg_type = last_msg.get('type')
                                if msg_type:
                                    last_message = last_msg
                                    last_msg_type = msg_type
                                    break
                            except:
                                pass
            except Exception:
                pass
        
        # 判断是否正在等待工具返回（工作中）
        # 如果最后一条消息是 toolCall 且没有对应的 toolResult，可能是工作中
        is_waiting = last_msg_type == "message" and tool_call_count > tool_result_count
        is_running = is_waiting or (elapsed_seconds < 300 and tool_call_count > tool_result_count)
        
        return {
            "session_key": session_key,
            "updated_at": updated_at,
            "elapsed_seconds": elapsed_seconds,
            "elapsed_minutes": int(elapsed_seconds / 60),
            "tool_count": tool_count,
            "tool_call_count": tool_call_count,
            "tool_result_count": tool_result_count,
            "last_msg_type": last_msg_type,
            "is_waiting": is_waiting,  # 等待工具返回
            "is_running": is_running,    # 正在执行
            "is_recent": elapsed_seconds < 300,  # 5 分钟内有活动
            "last_message": str(last_message)[:200] if last_message else None,
        }
        
    except json.JSONDecodeError:
        return {"error": "json decode error"}
    except Exception as e:
        return {"error": str(e)}


class TaskOrchestrator:
    """任务编排器"""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.task_dir = TASKS_DIR / f"task-{task_id}"
        self.steps_file = self.task_dir / "task_steps.md"
        
    # ========== 文件操作 ==========
    
    def read_steps_md(self) -> Dict[int, Dict[str, Any]]:
        """读取 task_steps.md，返回步骤字典"""
        if not self.steps_file.exists():
            return {}
        
        content = self.steps_file.read_text(encoding='utf-8')
        steps = {}
        
        # 解析步骤信息
        current_step = None
        in_step = False
        
        for line in content.split('\n'):
            stripped = line.strip()
            
            # 检测新步骤
            step_match = re.match(r'^###\s*步骤\s*(\d+)[:：]?(.+)$', stripped)
            if step_match:
                step_num = int(step_match.group(1))
                current_step = step_num
                steps[step_num] = {
                    'num': step_num,
                    'desc': step_match.group(2).strip(),
                    'status': '待执行',
                    'exec_subagent': None,
                    'exec_runid': None,
                    'verify_subagent': None,
                    'verify_runid': None,
                    'timeout_exec': 0,
                    'timeout_verify': 0,
                    'exec_prompt': '',
                    'verify_criteria': '',
                }
                in_step = True
                continue
            
            if in_step and current_step:
                # 解析状态
                if '**状态**' in stripped:
                    status_match = re.search(r':\s*(.+)$', stripped)
                    if status_match:
                        steps[current_step]['status'] = status_match.group(1).strip()
                
                # 解析执行子代理
                if '**执行子代理**' in stripped:
                    subagent_match = re.search(r':\s*(.+)$', stripped)
                    if subagent_match:
                        parts = subagent_match.group(1).split('(runId:')
                        steps[current_step]['exec_subagent'] = parts[0].strip() if parts else ''
                        if len(parts) > 1:
                            steps[current_step]['exec_runid'] = parts[1].replace(')', '').strip()
                
                # 解析检验子代理
                if '**检验子代理**' in stripped:
                    subagent_match = re.search(r':\s*(.+)$', stripped)
                    if subagent_match:
                        parts = subagent_match.group(1).split('(runId:')
                        steps[current_step]['verify_subagent'] = parts[0].strip() if parts else ''
                        if len(parts) > 1:
                            steps[current_step]['verify_runid'] = parts[1].replace(')', '').strip()
                
                # 解析超时计数
                if '**超时计数**' in stripped:
                    timeout_match = re.search(r'执行\((\d+)/2\)\s*\|\s*检验\((\d+)/2\)', stripped)
                    if timeout_match:
                        steps[current_step]['timeout_exec'] = int(timeout_match.group(1))
                        steps[current_step]['timeout_verify'] = int(timeout_match.group(2))
                
                # 解析执行 Prompt
                if '**执行 Prompt**' in stripped:
                    prompt_match = re.search(r':\s*(.+)$', stripped)
                    if prompt_match:
                        steps[current_step]['exec_prompt'] = prompt_match.group(1).strip()
                
                # 解析检验标准
                if '**检验标准**' in stripped:
                    criteria_match = re.search(r':\s*(.+)$', stripped)
                    if criteria_match:
                        steps[current_step]['verify_criteria'] = criteria_match.group(1).strip()
        
        return steps
    
    def write_steps_md(self, steps: Dict[int, Dict[str, Any]], task_info: Dict[str, Any], cleanup_info: Dict[str, Any] = None):
        """写入 task_steps.md"""
        # 构建清理信息
        cleanup_section = ""
        if cleanup_info:
            killed_subagents = cleanup_info.get('killed_subagents', [])
            cron_removed = cleanup_info.get('cron_removed', [])
            killed_pids = cleanup_info.get('killed_pids', [])
            
            if killed_subagents or cron_removed or killed_pids:
                cleanup_section = f"""
## 任务清理信息
- **中断/完成时间**: {cleanup_info.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
- **终止子代理**: {', '.join(killed_subagents) if killed_subagents else '无'}
- **删除 Cron**: {', '.join(cron_removed) if cron_removed else '无'}
- **终止进程**: {', '.join(map(str, killed_pids)) if killed_pids else '无'}
"""
        
        content = f"""## 任务基础信息
- 任务名称：{task_info.get('name', '未知')}
- 任务ID：task-{self.task_id}
- 创建时间：{task_info.get('created', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
- 步骤超时时间：{task_info.get('timeout', '无超时')}{f"\n- **Cron Job**: {task_info.get('cron', '无')}" if task_info.get('cron') else ""}

## 核心执行步骤

"""
        for step_num in sorted(steps.keys()):
            step = steps[step_num]
            status_icon = {
                '待执行': '[ ]',
                '执行中': '[>]',
                '待检验': '[?]',
                '检验中': '[*]',
                '已完成': '[✓]',
                '失败': '[✗]',
                '已中断': '[!]',
            }.get(step['status'], '[ ]')
            
            content += f"""### 步骤 {step_num}：{step['desc']}
- **状态**: {step['status']}
- **执行子代理**: {step['exec_subagent'] or '待创建'} ({f"runId: {step['exec_runid']}" if step['exec_runid'] else ''})
- **检验子代理**: {step['verify_subagent'] or '待创建'} ({f"runId: {step['verify_runid']}" if step['verify_runid'] else ''})
- **超时计数**: 执行({step['timeout_exec']}/2) | 检验({step['timeout_verify']}/2)
- **执行 Prompt**: {step['exec_prompt'] or '无'}
- **检验标准**: {step['verify_criteria'] or '无'}

"""
        
        content += """## 步骤状态说明
- [ ] 待执行
- [>] 执行中
- [?] 待检验
- [*] 检验中
- [✓] 已完成
- [✗] 失败
- [!] 已中断
"""
        
        # 添加清理信息
        if cleanup_section:
            content += cleanup_section
            
        self.steps_file.write_text(content, encoding='utf-8')
    
    # ========== 任务操作 ==========
    
    def start(self, plan_file: str) -> Dict[str, Any]:
        """启动任务"""
        if not self.task_dir.exists():
            self.task_dir.mkdir(parents=True, exist_ok=True)
            (self.task_dir / "temp" / "scripts").mkdir(parents=True, exist_ok=True)
            (self.task_dir / "temp" / "downloads").mkdir(parents=True, exist_ok=True)
        
        # 解析计划书
        plan_path = Path(plan_file)
        if not plan_path.exists():
            return {"status": "error", "error": f"计划书不存在: {plan_file}"}
        
        content = plan_path.read_text(encoding='utf-8')
        
        # 解析任务信息
        task_name = ""
        timeout = "无超时"
        cleanup_dir = "否"
        steps = {}
        
        lines = content.split('\n')
        in_steps = False
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('# ') and not task_name:
                task_name = stripped[2:].strip()
            
            if '步骤超时时间' in stripped:
                timeout_match = re.search(r':\s*(.+)$', stripped)
                if timeout_match:
                    timeout = timeout_match.group(1).strip()
            
            if '任务完成后删除目录' in stripped or '完成后删除' in stripped:
                cleanup_match = re.search(r':\s*(.+)$', stripped)
                if cleanup_match:
                    cleanup_dir = cleanup_match.group(1).strip()
            
            if '## 核心执行步骤' in stripped:
                in_steps = True
                continue
            
            if in_steps:
                # 检测步骤
                step_match = re.match(r'^-\s*\[\s*\]\s*步骤\s*(\d+)[:：]?(.+)$', stripped)
                if step_match:
                    step_num = int(step_match.group(1))
                    desc = step_match.group(2).strip()
                    steps[step_num] = {
                        'num': step_num,
                        'desc': desc,
                        'status': '待执行',
                        'exec_subagent': None,
                        'exec_runid': None,
                        'verify_subagent': None,
                        'verify_runid': None,
                        'timeout_exec': 0,
                        'timeout_verify': 0,
                        'exec_prompt': '',
                        'verify_criteria': '',
                    }
                    continue
                
                # 检测执行 Prompt
                if '**执行 Prompt**' in stripped:
                    prompt_match = re.search(r':\s*(.+)$', stripped)
                    if prompt_match and steps:
                        steps[max(steps.keys())]['exec_prompt'] = prompt_match.group(1).strip()
                    continue
                
                # 检测检验标准
                if '**检验标准**' in stripped:
                    criteria_match = re.search(r':\s*(.+)$', stripped)
                    if criteria_match and steps:
                        steps[max(steps.keys())]['verify_criteria'] = criteria_match.group(1).strip()
                    continue
        
        print(f"任务启动: task-{self.task_id}")
        print(f"任务名称: {task_name}")
        print(f"总步骤数: {len(steps)}")
        
        # 写入步骤文档
        task_info = {
            'name': task_name,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timeout': timeout,
            'cleanup_dir': cleanup_dir if 'cleanup_dir' in dir() and cleanup_dir else '否',
            'cron': f'stp-heartbeat-{self.task_id}',
        }
        self.write_steps_md(steps, task_info)
        
        return {
            "status": "accepted",
            "task_id": self.task_id,
            "task_name": task_name,
            "total_steps": len(steps),
            "next_step": 1,
        }
    
    def get_next_step(self) -> Optional[int]:
        """获取下一个待执行的步骤号"""
        steps = self.read_steps_md()
        for step_num in sorted(steps.keys()):
            if steps[step_num]['status'] == '待执行':
                return step_num
        return None
    
    def get_step_info(self, step_num: int) -> Optional[Dict[str, Any]]:
        """获取步骤信息"""
        steps = self.read_steps_md()
        return steps.get(step_num)
    
    def update_step_status(self, step_num: int, status: str, 
                           exec_subagent: str = None, exec_runid: str = None,
                           verify_subagent: str = None, verify_runid: str = None):
        """更新步骤状态"""
        steps = self.read_steps_md()
        if step_num not in steps:
            return {"status": "error", "error": f"步骤 {step_num} 不存在"}
        
        step = steps[step_num]
        step['status'] = status
        
        if exec_subagent:
            step['exec_subagent'] = exec_subagent
        if exec_runid:
            step['exec_runid'] = exec_runid
        if verify_subagent:
            step['verify_subagent'] = verify_subagent
        if verify_runid:
            step['verify_runid'] = verify_runid
        
        # 读取任务信息
        task_info = {'name': '未知', 'timeout': '无超时'}
        if self.steps_file.exists():
            content = self.steps_file.read_text(encoding='utf-8')
            name_match = re.search(r'- 任务名称：(.+)$', content, re.MULTILINE)
            if name_match:
                task_info['name'] = name_match.group(1).strip()
            timeout_match = re.search(r'- 步骤超时时间：(.+)$', content, re.MULTILINE)
            if timeout_match:
                task_info['timeout'] = timeout_match.group(1).strip()
        
        self.write_steps_md(steps, task_info)
        print(f"步骤 {step_num} 状态更新: {status}")
        
        return {"status": "ok", "step_num": step_num, "new_status": status}
    
    def increment_timeout(self, step_num: int, is_exec: bool = True) -> int:
        """增加超时计数"""
        steps = self.read_steps_md()
        if step_num not in steps:
            return -1
        
        if is_exec:
            steps[step_num]['timeout_exec'] += 1
            count = steps[step_num]['timeout_exec']
        else:
            steps[step_num]['timeout_verify'] += 1
            count = steps[step_num]['timeout_verify']
        
        task_info = {'name': '未知', 'timeout': '无超时'}
        if self.steps_file.exists():
            content = self.steps_file.read_text(encoding='utf-8')
            name_match = re.search(r'- 任务名称：(.+)$', content, re.MULTILINE)
            if name_match:
                task_info['name'] = name_match.group(1).strip()
            timeout_match = re.search(r'- 步骤超时时间：(.+)$', content, re.MULTILINE)
            if timeout_match:
                task_info['timeout'] = timeout_match.group(1).strip()
        
        self.write_steps_md(steps, task_info)
        return count
    
    def get_active_subagents(self) -> List[Dict[str, Any]]:
        """获取所有活跃子代理"""
        steps = self.read_steps_md()
        active = []
        
        for step_num, step in steps.items():
            status = step['status']
            
            if status in ['执行中', '检验中']:
                if step.get('exec_subagent') and step.get('exec_runid'):
                    active.append({
                        'step': step_num,
                        'type': 'exec',
                        'subagent': step['exec_subagent'],
                        'runid': step['exec_runid'],
                        'timeout_count': step['timeout_exec'],
                    })
                if step.get('verify_subagent') and step.get('verify_runid'):
                    active.append({
                        'step': step_num,
                        'type': 'verify',
                        'subagent': step['verify_subagent'],
                        'runid': step['verify_runid'],
                        'timeout_count': step['timeout_verify'],
                    })
        
        return active
    
    def interrupt_all(self) -> Dict[str, Any]:
        """中断所有活跃子代理"""
        steps = self.read_steps_md()
        killed = []
        killed_pids = []
        
        for step_num, step in steps.items():
            status = step['status']
            
            if status in ['执行中', '检验中']:
                # 更新状态为已中断
                step['status'] = '已中断'
                
                if step.get('exec_subagent'):
                    killed.append(step['exec_subagent'])
                if step.get('verify_subagent'):
                    killed.append(step['verify_subagent'])
        
        task_info = {'name': '未知', 'timeout': '无超时', 'cron': f'stp-heartbeat-{self.task_id}'}
        if self.steps_file.exists():
            content = self.steps_file.read_text(encoding='utf-8')
            name_match = re.search(r'- 任务名称：(.+)$', content, re.MULTILINE)
            if name_match:
                task_info['name'] = name_match.group(1).strip()
            timeout_match = re.search(r'- 步骤超时时间：(.+)$', content, re.MULTILINE)
            if timeout_match:
                task_info['timeout'] = timeout_match.group(1).strip()
            cron_match = re.search(r'- \*\*Cron Job\*\*: (.+)$', content, re.MULTILINE)
            if cron_match:
                task_info['cron'] = cron_match.group(1).strip()
        
        # 构建清理信息
        cleanup_info = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'killed_subagents': killed,
            'cron_removed': [f'stp-heartbeat-{self.task_id}'],
            'killed_pids': killed_pids
        }
        
        self.write_steps_md(steps, task_info, cleanup_info)
        
        # 提取 subagent ID 部分用于 kill（去掉前缀）
        subagent_ids = []
        for k in killed:
            # 从 "agent:main:subagent:xxx" 提取 "subagent:xxx"
            if 'subagent:' in k:
                subagent_ids.append(k)
        
        print(f"任务中断，已终止 {len(killed)} 个子代理")
        print(f"清理信息: {cleanup_info}")
        
        return {
            "status": "ok", 
            "killed_subagents": killed,
            "killed_pids": killed_pids,
            "cron_removed": [f'stp-heartbeat-{self.task_id}'],
            "subagent_ids_for_kill": subagent_ids  # 可直接用于 subagents 工具
        }


def get_task_id_from_dir(task_dir: str) -> str:
    """从目录名提取 task ID"""
    if task_dir.startswith('task-'):
        return task_dir.replace('task-', '')
    return task_dir


def cmd_start(args: List[str]):
    """启动任务"""
    if not args:
        print("❌ 错误：缺少计划书路径")
        sys.exit(1)
    
    plan_file = args[0]
    plan_path = Path(plan_file).expanduser()
    
    if not plan_path.exists():
        # 尝试在 task-list 中查找
        plan_path = WORKSPACE_ROOT / "task-list" / plan_file
        if not plan_path.exists():
            print(f"❌ 错误：计划书不存在: {plan_file}")
            sys.exit(1)
    
    # 生成 task ID
    task_counter_file = TASKS_DIR / ".task_counter"
    if task_counter_file.exists():
        task_id = int(task_counter_file.read_text().strip()) + 1
    else:
        task_id = 1
    task_counter_file.write_text(str(task_id))
    
    orchestrator = TaskOrchestrator(str(task_id))
    result = orchestrator.start(str(plan_path))
    
    # 创建 cron job 用于 heartbeat 检查
    cron_name = f"stp-heartbeat-{task_id}"
    cron_message = f"执行 STP 任务 heartbeat 检查：\n\npython3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py heartbeat {task_id}"
    
    try:
        import subprocess
        subprocess.run([
            "openclaw", "cron", "add",
            "--name", cron_name,
            "--every", "10m",
            "--session", "isolated",
            "--announce",
            "--channel", "webchat",
            "--message", cron_message,
            "--description", f"STP task-{task_id} heartbeat"
        ], capture_output=True, timeout=30)
        result["cron_created"] = cron_name
    except Exception as e:
        result["cron_error"] = str(e)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_status(args: List[str]):
    """查看任务状态"""
    if not args:
        print("❌ 错误：缺少任务 ID")
        sys.exit(1)
    
    task_id = get_task_id_from_dir(args[0])
    orchestrator = TaskOrchestrator(task_id)
    
    steps = orchestrator.read_steps_md()
    active = orchestrator.get_active_subagents()
    
    result = {
        "task_id": task_id,
        "task_dir": str(orchestrator.task_dir),
        "total_steps": len(steps),
        "active_subagents": active,
        "steps": steps,
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_heartbeat(args: List[str]):
    """检查 heartbeat - 检测子代理是否卡死"""
    # 优先使用参数传入的 task_id
    task_id = None
    
    if args:
        task_id = get_task_id_from_dir(args[0])
    
    if not task_id:
        print(json.dumps({"status": "ok", "message": "请指定任务 ID"}, ensure_ascii=False))
        return {"status": "ok", "message": "task_id required"}
    
    orchestrator = TaskOrchestrator(task_id)
    
    # 从 task_steps.md 获取已知子代理
    steps = orchestrator.read_steps_md()
    known_subagents = orchestrator.get_active_subagents()
    
    result = {
        "task_id": task_id,
        "known_subagents": len(known_subagents),
        "checks": [],
    }
    
    if not known_subagents:
        # 没有已知子代理，直接清理 cron
        cron_name = f"stp-heartbeat-{task_id}"
        try:
            import subprocess
            proc = subprocess.run(["openclaw", "cron", "rm", cron_name], capture_output=True, timeout=30)
            if proc.returncode == 0:
                result["cron_removed"] = cron_name
            else:
                result["cron_error"] = f"命令返回非零: {proc.returncode}"
                print(f"⚠️ 清理 cron 失败: {result['cron_error']}", file=sys.stderr)
        except Exception as e:
            result["cron_error"] = str(e)
            print(f"❌ 清理 cron 失败: {e}", file=sys.stderr)
        result["message"] = "无活跃子代理，任务已完成"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    
    # 检查每个子代理的实际状态
    stuck_subagents = []
    completed_subagents = []
    error_count = 0
    
    for sub in known_subagents:
        subagent_key = sub['subagent']
        step_num = sub['step']
        sub_type = sub['type']
        
        session_info = sessions_history_sync(subagent_key)
        
        if "error" in session_info:
            error_count += 1
            result["checks"].append({
                "subagent": subagent_key,
                "step": step_num,
                "type": sub_type,
                "status": "error",
                "message": session_info.get("error"),
            })
            continue
        
        elapsed_minutes = session_info.get("elapsed_minutes", 0)
        tool_count = session_info.get("tool_count", 0)
        is_running = session_info.get("is_running", False)
        is_recent = session_info.get("is_recent", False)
        
        # 判断状态
        if tool_count == 0:
            # 从未调用过工具，可能还没开始
            status = "pending"
            message = "等待开始"
        elif is_running and elapsed_minutes > 30:
            # 超过 30 分钟仍在工作中，可能卡住
            status = "stuck"
            message = f"已 {elapsed_minutes} 分钟仍在工作中，可能卡住"
            
            # 增加超时计数
            is_exec = sub_type == 'exec'
            new_count = orchestrator.increment_timeout(step_num, is_exec)
            
            stuck_subagents.append({
                "subagent": subagent_key,
                "step": step_num,
                "type": sub_type,
                "elapsed_minutes": elapsed_minutes,
                "timeout_count": new_count,
            })
        elif not is_running and elapsed_minutes > 5:
            # 超过 5 分钟无活动，已完成
            status = "completed"
            message = f"已完成，最后活动 {elapsed_minutes} 分钟前"
            completed_subagents.append({
                "subagent": subagent_key,
                "step": step_num,
                "type": sub_type,
                "elapsed_minutes": elapsed_minutes,
            })
        elif not is_running:
            # 不在工作中，但时间不长
            status = "idle"
            message = f"空闲中，最后活动 {elapsed_minutes} 分钟前"
        else:
            # 正在工作中
            status = "running"
            message = f"执行中，最后活动 {elapsed_minutes} 分钟前"
        
        result["checks"].append({
            "subagent": subagent_key,
            "step": step_num,
            "type": sub_type,
            "status": status,
            "elapsed_minutes": elapsed_minutes,
            "tool_count": tool_count,
            "message": message,
        })
    
    result["stuck_subagents"] = stuck_subagents
    result["stuck_count"] = len(stuck_subagents)
    result["completed_subagents"] = completed_subagents
    
    # 判断是否需要清理 cron job
    # 1. 没有活跃子代理（任务已完成/中断）
    # 2. 所有子代理都不在工作中（completed/idle）
    # 3. 所有子代理会话都不存在（可能已清理）
    need_cleanup = (
        len(known_subagents) == 0 or 
        len(completed_subagents) == len(known_subagents) or
        error_count == len(known_subagents)
    )
    
    if need_cleanup:
        # 自动删除 cron job
        cron_name = f"stp-heartbeat-{task_id}"
        try:
            import subprocess
            proc = subprocess.run([
                "openclaw", "cron", "rm", cron_name
            ], capture_output=True, timeout=30)
            if proc.returncode == 0:
                result["cron_removed"] = cron_name
                result["cleanup_reason"] = "所有子代理已完成，任务结束"
            else:
                result["cron_error"] = f"命令返回非零: {proc.returncode}, stderr: {proc.stderr.decode() if proc.stderr else ''}"
                print(f"⚠️ 清理 cron 失败: {result['cron_error']}", file=sys.stderr)
        except Exception as e:
            result["cron_error"] = str(e)
            print(f"❌ 清理 cron 失败: {e}", file=sys.stderr)
        
        # 检查是否需要删除任务目录
        try:
            steps_content = orchestrator.steps_file.read_text(encoding='utf-8')
            cleanup_match = re.search(r'- 任务完成后删除目录：(.+)$', steps_content, re.MULTILINE)
            if cleanup_match and '是' in cleanup_match.group(1):
                # 删除任务目录
                import shutil
                shutil.rmtree(orchestrator.task_dir)
                result["task_dir_deleted"] = str(orchestrator.task_dir)
                result["cleanup_reason"] = "任务完成且设置删除目录"
        except Exception as e:
            result["cleanup_error"] = str(e)
        
        # 更新 task_steps.md 添加清理信息
        if result.get("cron_removed"):
            try:
                # 读取任务信息
                task_info = {'name': '未知', 'timeout': '无超时', 'cron': result.get("cron_removed", [])}
                if orchestrator.steps_file.exists():
                    content = orchestrator.steps_file.read_text(encoding='utf-8')
                    name_match = re.search(r'- 任务名称：(.+)$', content, re.MULTILINE)
                    if name_match:
                        task_info['name'] = name_match.group(1).strip()
                    timeout_match = re.search(r'- 步骤超时时间：(.+)$', content, re.MULTILINE)
                    if timeout_match:
                        task_info['timeout'] = timeout_match.group(1).strip()
                
                # 读取当前步骤
                steps = orchestrator.read_steps_md()
                
                # 构建清理信息
                cron_removed = result.get("cron_removed", "")
                # 确保是列表
                if isinstance(cron_removed, str):
                    cron_removed = [cron_removed] if cron_removed else []
                cleanup_info = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'killed_subagents': [],  # 自然完成时没有终止子代理
                    'cron_removed': cron_removed,
                    'killed_pids': []
                }
                
                orchestrator.write_steps_md(steps, task_info, cleanup_info)
                result["steps_file_updated"] = True
            except Exception as e:
                result["steps_update_error"] = str(e)
    
    result["need_cleanup"] = need_cleanup
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_interrupt(args: List[str]):
    """中断任务"""
    if not args:
        print("❌ 错误：缺少任务 ID")
        sys.exit(1)
    
    task_id = get_task_id_from_dir(args[0])
    orchestrator = TaskOrchestrator(task_id)
    
    result = orchestrator.interrupt_all()
    
    # 删除对应的 cron job
    cron_name = f"stp-heartbeat-{task_id}"
    try:
        import subprocess
        proc = subprocess.run([
            "openclaw", "cron", "rm", cron_name
        ], capture_output=True, timeout=30)
        if proc.returncode == 0:
            result["cron_removed"] = cron_name
        else:
            result["cron_error"] = f"命令返回非零: {proc.returncode}"
    except Exception as e:
        result["cron_error"] = str(e)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_update(args: List[str]):
    """更新步骤状态"""
    # 用法: stp_orchestrator.py update <task_id> <step_num> <status> [exec_subagent] [exec_runid]
    if len(args) < 3:
        print("❌ 错误：参数不足")
        print("用法: stp_orchestrator.py update <task_id> <step_num> <status> [exec_subagent] [exec_runid]")
        sys.exit(1)
    
    task_id = get_task_id_from_dir(args[0])
    step_num = int(args[1])
    status = args[2]
    
    exec_subagent = args[3] if len(args) > 3 else None
    exec_runid = args[4] if len(args) > 4 else None
    verify_subagent = args[5] if len(args) > 5 else None
    verify_runid = args[6] if len(args) > 6 else None
    
    orchestrator = TaskOrchestrator(task_id)
    result = orchestrator.update_step_status(
        step_num, status,
        exec_subagent=exec_subagent, exec_runid=exec_runid,
        verify_subagent=verify_subagent, verify_runid=verify_runid
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_timeout(args: List[str]):
    """增加超时计数"""
    # 用法: stp_orchestrator.py timeout <task_id> <step_num> <exec|verify>
    if len(args) < 3:
        print("❌ 错误：参数不足")
        print("用法: stp_orchestrator.py timeout <task_id> <step_num> <exec|verify>")
        sys.exit(1)
    
    task_id = get_task_id_from_dir(args[0])
    step_num = int(args[1])
    is_exec = args[2] == 'exec'
    
    orchestrator = TaskOrchestrator(task_id)
    count = orchestrator.increment_timeout(step_num, is_exec)
    
    result = {
        "task_id": task_id,
        "step_num": step_num,
        "type": args[2],
        "new_count": count,
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result




def main():
    if len(sys.argv) < 2:
        print("""📋 STP V2 任务编排器

用法：
  stp_orchestrator.py start <计划书路径>     # 启动任务
  stp_orchestrator.py status <任务ID>        # 查看任务状态
  stp_orchestrator.py heartbeat <任务ID>     # 检查 heartbeat
  stp_orchestrator.py interrupt <任务ID>    # 中断任务
  stp_orchestrator.py update <任务ID> <步骤> <状态> [exec_subagent] [exec_runid] [verify_subagent] [verify_runid]
  stp_orchestrator.py timeout <任务ID> <步骤> <exec|verify>
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        'start': cmd_start,
        'status': cmd_status,
        'heartbeat': cmd_heartbeat,
        'interrupt': cmd_interrupt,
        'update': cmd_update,
        'timeout': cmd_timeout,
    }
    
    if cmd not in commands:
        print(f"❌ 错误：未知命令: {cmd}")
        sys.exit(1)
    
    commands[cmd](args)


if __name__ == "__main__":
    main()
