#!/usr/bin/env python3
"""
Layer 2: Reply Generator
- 根据意图生成回复文本
- Phase 2: 支持任务编排和完成条件验证
"""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .intent_analyzer import Intent

if TYPE_CHECKING:
    from .done_checker import DoneResult
    from .task_orchestrator import Task

logger = logging.getLogger(__name__)


# 回复模板
REPLY_TEMPLATES = {
    Intent.ERROR: "分析这个错误的根本原因并修复。修复后继续当前任务。",
    
    Intent.CHOICE: "用你的专业判断选择最合适的方案，直接执行。优先考虑：简洁性、可维护性、性能。",
    
    Intent.CONFIRM: "是的，继续。",
    
    Intent.TASK_COMPLETE: "很好，任务完成。继续下一步工作。",
    
    Intent.REVIEW: "根据 review 结论：1. 修复所有 [BLOCK] 项 2. 处理 [CHANGES] 建议 3. 修复后重新自检",
    
    Intent.DEFAULT: "继续。",
}


def generate_reply(intent: Intent, context: Optional[str] = None,
                   last_output: Optional[str] = None) -> str:
    """
    根据意图和上下文生成回复文本
    
    Args:
        intent: 识别出的意图
        context: 可选的上下文信息（如当前任务名、进度等）
        last_output: Codex 的最后输出（用于更智能的回复）
    
    Returns:
        回复文本
    """
    base_reply = REPLY_TEMPLATES.get(intent, REPLY_TEMPLATES[Intent.DEFAULT])
    
    # 根据意图 + 输出内容生成更精准的回复
    if intent == Intent.ERROR:
        return _generate_error_reply(last_output, context)
    elif intent == Intent.CHOICE:
        return _generate_choice_reply(last_output, context)
    elif intent == Intent.CONFIRM:
        return "是的，继续。"
    elif intent == Intent.TASK_COMPLETE:
        return _generate_complete_reply(last_output, context)
    elif intent == Intent.REVIEW:
        return _generate_review_reply(last_output, context)
    elif intent == Intent.DEFAULT:
        return _generate_default_reply(last_output, context)
    
    return base_reply


def _generate_error_reply(output: Optional[str], context: Optional[str]) -> str:
    """根据错误内容生成修复指令"""
    reply = "分析这个错误的根本原因并修复。"
    
    if output:
        # 检测具体错误类型给出更精准的指令
        if "TypeScript" in output or "TypeError" in output or "type" in output.lower():
            reply = "修复类型错误。检查类型定义和接口是否匹配。"
        elif "import" in output.lower() or "ModuleNotFoundError" in output or "Cannot find module" in output:
            reply = "修复导入错误。检查依赖是否安装、路径是否正确。"
        elif "build" in output.lower() or "compile" in output.lower():
            reply = "修复构建错误。查看完整错误信息，逐个解决。"
        elif "test" in output.lower() and ("fail" in output.lower() or "error" in output.lower()):
            reply = "修复失败的测试。分析测试期望和实际输出的差异。"
    
    if context:
        reply += f" 修复后继续 {context}。"
    else:
        reply += " 修复后继续当前任务。"
    
    return reply


def _generate_choice_reply(output: Optional[str], context: Optional[str]) -> str:
    """根据选择内容生成决策"""
    return "用你的专业判断选择最合适的方案，直接执行。优先考虑：简洁性、可维护性、性能。不需要再问我。"


def _generate_complete_reply(output: Optional[str], context: Optional[str]) -> str:
    """任务完成后的回复"""
    return "好的。检查还有没有待办事项，有的话继续处理，没有就做一个完整的自检和总结。"


def _generate_review_reply(output: Optional[str], context: Optional[str]) -> str:
    """Review 结果的回复"""
    if output:
        block_count = output.count("[BLOCK]") + output.count("[CRITICAL]")
        if block_count > 0:
            return f"有 {block_count} 个阻塞问题。优先修复所有 BLOCK/CRITICAL 项，然后处理其他建议。修复后重新自检。"
    return "根据 review 结论：1. 修复所有阻塞项 2. 处理改进建议 3. 修复后重新自检。"


def _generate_default_reply(output: Optional[str], context: Optional[str]) -> str:
    """默认回复——Codex 停下来了但原因不明"""
    if output:
        output_lower = output.lower()
        
        # 如果输出在问问题或请求反馈
        if any(q in output for q in ["?", "？", "吗", "呢"]):
            return "看起来没问题，按你的判断继续。"
        
        # 如果是状态报告/摘要
        if any(k in output for k in ["总结", "summary", "Summary", "状态", "进度", "progress"]):
            return "收到。继续下一步工作。"
        
        # 如果提到文件创建/修改
        if any(k in output_lower for k in ["created", "updated", "wrote", "已创建", "已更新", "已写入"]):
            return "好的，继续。"
    
    # 最简洁的默认回复
    return "继续。"


def generate_push_reply(task_name: Optional[str] = None, 
                        progress: Optional[str] = None,
                        remaining: Optional[str] = None) -> str:
    """
    生成"推一把"的回复（当 Codex 停下来但不知道为什么）
    
    Args:
        task_name: 当前任务名
        progress: 当前进度
        remaining: 剩余工作
    
    Returns:
        回复文本
    """
    parts = ["继续"]
    
    if task_name:
        parts.append(task_name)
    
    if progress:
        parts.append(f"当前进度：{progress}")
    
    if remaining:
        parts.append(f"还需完成：{remaining}")
    
    return "。".join(parts) + "。"


# ============== Phase 2: 任务编排相关 ==============

def generate_done_failed_reply(
    done_result: "DoneResult",
    task_name: Optional[str] = None
) -> str:
    """
    生成完成条件未满足的回复
    
    Args:
        done_result: 完成条件检测结果
        task_name: 任务名称
    
    Returns:
        回复文本
    """
    from .done_checker import DoneResult
    
    parts = []
    
    if task_name:
        parts.append(f"任务「{task_name}」还未完成。")
    else:
        parts.append("任务还未完成。")
    
    # 列出未满足的条件
    failed_items = done_result.get_failed_items()
    if failed_items:
        parts.append("以下条件未满足：")
        for item in failed_items[:5]:  # 最多显示 5 项
            parts.append(f"- {item.description}: {item.details}")
    
    parts.append("\n请继续完成这些要求。")
    
    return "\n".join(parts)


def generate_next_task_reply(
    next_prompt: str,
    completed_task_name: Optional[str] = None,
    on_complete_msg: Optional[str] = None
) -> str:
    """
    生成下一任务的回复（包含完成摘要和新任务 prompt）
    
    Args:
        next_prompt: 下一任务的 prompt
        completed_task_name: 刚完成的任务名
        on_complete_msg: 完成摘要消息
    
    Returns:
        回复文本
    """
    parts = []
    
    if completed_task_name:
        parts.append(f"✅ 任务「{completed_task_name}」已完成！")
        if on_complete_msg:
            parts.append(f"摘要: {on_complete_msg}")
        parts.append("")
    
    parts.append("现在开始下一个任务：")
    parts.append("")
    parts.append(next_prompt)
    
    return "\n".join(parts)


def generate_all_tasks_complete_reply(
    project_name: Optional[str] = None,
    total_tasks: int = 0
) -> str:
    """
    生成所有任务完成的回复
    
    Args:
        project_name: 项目名称
        total_tasks: 总任务数
    
    Returns:
        回复文本
    """
    if project_name:
        return f"🎉 恭喜！项目「{project_name}」的所有 {total_tasks} 个任务已全部完成！"
    else:
        return f"🎉 恭喜！所有 {total_tasks} 个任务已全部完成！"


def generate_human_review_notice(
    task_name: str,
    task_prompt: Optional[str] = None
) -> str:
    """
    生成需要人工审核的通知
    
    Args:
        task_name: 任务名称
        task_prompt: 任务描述
    
    Returns:
        通知文本
    """
    parts = [
        f"⏸ 任务「{task_name}」需要人工确认后才能开始。",
        "",
        "请使用 /approve 命令确认开始此任务。"
    ]
    
    if task_prompt:
        # 截取 prompt 的前 200 字符作为预览
        preview = task_prompt[:200] + "..." if len(task_prompt) > 200 else task_prompt
        parts.insert(1, f"任务内容预览: {preview}")
    
    return "\n".join(parts)
