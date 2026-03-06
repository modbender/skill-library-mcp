#!/usr/bin/env python3
"""
Layer 2: Intent Analyzer
- 分析 Codex 输出语义
- 识别意图 (ERROR/CHOICE/CONFIRM/TASK_COMPLETE/REVIEW/DEFAULT)
"""

import re
from enum import Enum
from typing import Optional


class Intent(Enum):
    ERROR = "error"              # P1: 遇到错误
    CHOICE = "choice"            # P2: 需要选择
    CONFIRM = "confirm"          # P3: 需要确认
    TASK_COMPLETE = "complete"   # P4: 任务完成
    REVIEW = "review"            # P5: Review 标记
    DEFAULT = "default"          # P6: 默认（Codex 停下来了但不知道为什么）


# P1: 错误关键词
ERROR_KEYWORDS = [
    "error", "Error", "ERROR",
    "错误", "失败", "报错",
    "failed", "Failed", "FAILED",
    "Cannot", "cannot", "can't", "Can't",
    "TypeError", "SyntaxError", "ImportError", "ModuleNotFoundError",
    "ReferenceError", "RuntimeError", "ValueError", "KeyError",
    "AttributeError", "NameError", "IndentationError",
    "Exception", "Traceback",
    "编译失败", "构建失败", "build failed",
    "npm ERR", "yarn error", "pnpm ERR",
]

# 已解决关键词（用于排除误判）
RESOLVED_KEYWORDS = [
    "已修复", "已解决", "修复了", "解决了",
    "fixed", "Fixed", "FIXED",
    "resolved", "Resolved", "RESOLVED",
    "已处理", "处理完成",
    "successfully", "Successfully",
    "通过", "passed", "Passed",
]

# P2: 选择模式（需要组合条件）
CHOICE_PATTERNS = [
    r"方案[一二三ABCD123].*(方案[一二三ABCD123]|或者|还是)",  # "方案A...方案B" 或 "方案A...或者..."
    r"(选择|选项|方案)\s*[：:]\s*\n",                        # "选择：\n 1. ..."
    r"(还是|或者).*(呢|吗|？|\?)",                           # "还是...呢？"
    r"(should I|would you prefer|which one|which option)",  # 英文选择
    r"(请选择|你选择|你决定|你来决定)",                      # 中文选择请求
    r"(Option [A-D]|option [a-d]).*(Option [A-D]|option [a-d])",  # Option A ... Option B
    # 注意: 去掉了过于宽泛的 "\d+\.\s+.+\n\d+\.\s+" 编号列表模式
    # 编号列表太常见（修改记录、步骤说明等），容易误判为选择
]

# P3: 确认关键词
CONFIRM_KEYWORDS = [
    "是否继续", "要不要", "确认", "确定",
    "proceed", "Proceed",
    "continue?", "Continue?",
    "shall I", "Shall I",
    "should I proceed", "Should I proceed",
    "可以吗", "好吗", "行吗",
    "是否", "是否要",
    "要继续吗", "继续吗",
    "你确定", "确定要",
    "需要修改的吗", "需要调整的吗", "需要改的吗",
    "有什么需要", "还有什么",
    "what do you think", "What do you think",
    "any feedback", "Any feedback",
    "let me know", "Let me know",
]

# P4: 完成关键词
COMPLETION_KEYWORDS = [
    "完成", "已完成", "全部完成",
    "done", "Done", "DONE",
    "completed", "Completed", "COMPLETED",
    "已实现", "实现完成",
    "all tasks", "All tasks",
    "所有任务", "任务完成",
    "已经完成", "都完成了",
    "finished", "Finished",
    "成功完成", "顺利完成",
    "所有测试通过", "tests passing", "tests passed",
    "已解决", "已修复",
    "继续下一步",
]

# P5: Review 标记（需要明确的 review 结构标记，而非普通提及 "review"）
REVIEW_MARKERS = [
    "[BLOCK]", "[CHANGES]", "[FINDING]",
    "[P0]", "[P1]", "[P2]", "[P3]",
    "[BUG]", "[ISSUE]", "[WARNING]",
    "[CRITICAL]", "[HIGH]", "[MEDIUM]", "[LOW]",
    "::code-comment",  # Codex Desktop review 格式
    "priority=",       # Codex review 的 priority 标注
    "新发现",
    "review",          # 通用（_has_review 用小写匹配）
    "优化建议", "改进建议",
    "审查结果", "代码审查",
]


def _is_in_quote_or_comment(text: str, keyword: str) -> bool:
    """
    简单启发式：检查关键词是否在引用块或代码注释中
    """
    lines = text.split('\n')
    for line in lines:
        if keyword in line:
            stripped = line.strip()
            # 检查是否在引用块中 (> 开头)
            if stripped.startswith('>'):
                return True
            # 检查是否在代码注释中
            if stripped.startswith('//') or stripped.startswith('#') or stripped.startswith('*'):
                return True
            # 检查是否在 markdown 代码块中
            if stripped.startswith('```'):
                return True
    return False


def _has_error(text: str) -> bool:
    """检查是否有错误（且未解决）"""
    found_error = False
    
    # 检查错误关键词
    for error in ERROR_KEYWORDS:
        if error in text:
            # 排除引用/注释中的误判
            if not _is_in_quote_or_comment(text, error):
                # 检查同一句中是否已解决
                # 找包含该错误关键词的所有行
                error_resolved = True
                for line in text.split('\n'):
                    if error in line:
                        # 该行是否也包含解决关键词？
                        line_resolved = any(r in line for r in RESOLVED_KEYWORDS)
                        if not line_resolved:
                            error_resolved = False
                            break
                
                if not error_resolved:
                    found_error = True
                    break
    
    if not found_error:
        return False
    
    # 全局检查：如果文本整体是"修复完成"的语气
    for resolved in RESOLVED_KEYWORDS:
        if resolved in text:
            # 如果解决关键词出现在错误关键词之前，认为已修复
            for error in ERROR_KEYWORDS:
                if error in text:
                    resolved_pos = text.find(resolved)
                    error_pos = text.find(error)
                    if resolved_pos < error_pos:
                        return False
    
    return True


def _has_choice(text: str) -> bool:
    """检查是否需要选择"""
    for pattern in CHOICE_PATTERNS:
        if re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
            return True
    return False


def _has_confirm(text: str) -> bool:
    """检查是否需要确认"""
    for keyword in CONFIRM_KEYWORDS:
        if keyword in text:
            return True
    return False


def _has_completion(text: str) -> bool:
    """检查是否任务完成（排除进度报告中的部分完成）"""
    import re
    
    # 如果文本中有明确的"未完成"信号，说明是进度报告
    has_incomplete = bool(re.search(r'(未开始|未完成|0%|\d+%.*未)', text))
    # "完成 50%" 这种百分比模式是进度报告
    has_partial = bool(re.search(r'完成\s*\d+%', text))
    
    if has_incomplete and has_partial:
        # 明确是进度报告（有完成也有未完成）
        return False
    
    for keyword in COMPLETION_KEYWORDS:
        if keyword in text:
            return True
    
    return False


def _has_review(text: str) -> bool:
    """检查是否有 Review 标记"""
    import re
    text_lower = text.lower()
    
    for marker in REVIEW_MARKERS:
        marker_lower = marker.lower()
        
        # "review" 需要特殊处理：排除 "for review"、"ready for review" 等
        if marker_lower == "review":
            # 匹配 "review 结果"、"review 后"、"code review"、行首 "review:" 等
            # 排除 "for review"、"ready for review"
            if re.search(r'(?<!for\s)(?<!for )\breview\s*(结果|后|发现|建议|:)', text_lower):
                return True
            if re.search(r'(code|代码)\s*review', text_lower):
                return True
            continue
        
        if marker_lower in text_lower:
            return True
    
    return False


def analyze_intent(text: Optional[str]) -> Intent:
    """
    分析 Codex 输出文本，返回意图
    
    按优先级顺序匹配:
    P1 错误 → P2 选择 → P3 确认 → P4 Review → P5 完成 → P6 默认
    
    注意：Review 优先于完成——review 报告里经常包含"已完成"等词，
    但核心意图是 review 反馈而非单纯完成通知。
    
    Args:
        text: Codex 的输出文本
    
    Returns:
        识别出的意图
    """
    if not text:
        return Intent.DEFAULT
    
    # P1: 错误处理
    if _has_error(text):
        return Intent.ERROR
    
    # P2: 选择处理
    if _has_choice(text):
        return Intent.CHOICE
    
    # P3: 确认处理
    if _has_confirm(text):
        return Intent.CONFIRM
    
    # P4: Review 标记（优先于完成——review 里常含"完成"等词）
    if _has_review(text):
        return Intent.REVIEW
    
    # P5: 任务完成
    if _has_completion(text):
        return Intent.TASK_COMPLETE
    
    # P6: 默认
    return Intent.DEFAULT


def get_intent_description(intent: Intent) -> str:
    """获取意图的中文描述"""
    descriptions = {
        Intent.ERROR: "遇到错误",
        Intent.CHOICE: "需要选择",
        Intent.CONFIRM: "需要确认",
        Intent.TASK_COMPLETE: "任务完成",
        Intent.REVIEW: "Review 标记",
        Intent.DEFAULT: "等待输入",
    }
    return descriptions.get(intent, "未知")
