#!/usr/bin/env python3
"""
Context Restore Script
======================

A utility script for restoring and presenting compressed context information.
This script reads compressed context files and generates formatted reports
at different detail levels.

Features:
- Supports both JSON and plain text compressed context formats
- Three report levels: minimal, normal, detailed
- Automatic extraction of metadata, projects, tasks, and operations
- File output capability
- Comprehensive error handling with unified error codes
- User confirmation process (--confirm flag)
- Platform format auto-adaptation (--platform flag)
  - Auto-detect platform from context content
  - Platform-specific formatting (Telegram, Discord, WhatsApp, Slack)
  - Automatic message chunking based on platform limits
- Telegram message chunking support (--telegram flag)
- Context change detection (--auto mode)
- Cron integration support

Usage:
    python3 restore_context.py                           # Normal level
    python3 restore_context.py --level minimal           # Brief info
    python3 restore_context.py --level detailed          # Full details
    python3 restore_context.py --output report.md        # Save to file
    python3 restore_context.py --confirm                 # Request user confirmation
    python3 restore_context.py --platform telegram       # Telegram optimized output
    python3 restore_context.py --platform discord        # Discord optimized output
    python3 restore_context.py --auto                    # Auto-detect and restore on changes
    python3 restore_context.py --auto --quiet            # Auto mode, quiet output

Author: OpenClaw Context Restore Module
Version: 1.4.0
"""

import argparse
import functools
import json
import os
import re
import sys
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Optional

# Import project progress module
from project_progress import (
    get_project_progress,
    get_all_project_progress,
    get_project_summary_for_context
)


# =============================================================================
# CONSTANTS
# =============================================================================

# Context restoration level constants
LEVEL_MINIMAL = "minimal"
LEVEL_NORMAL = "normal"
LEVEL_DETAILED = "detailed"

# Use absolute path for context file (修复文件路径问题)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONTEXT_FILE = os.path.normpath(os.path.join(
    SCRIPT_DIR, '..', '..', '..', 'compressed_context', 'latest_compressed.json'
))

# Period constants for timeline
PERIOD_DAILY = "daily"
PERIOD_WEEKLY = "weekly"
PERIOD_MONTHLY = "monthly"
VALID_PERIODS = [PERIOD_DAILY, PERIOD_WEEKLY, PERIOD_MONTHLY]

# Report levels as constants for API use
LEVEL_MINIMAL = 'minimal'
LEVEL_NORMAL = 'normal'
LEVEL_DETAILED = 'detailed'

# Report section separators
SEPARATOR = "=" * 60
SECTION_SEPARATOR = "-" * 60

# Emoji mappings for report sections
EMOJI = {
    'metadata': '📊',
    'operations': '🔄',
    'projects': '🚀',
    'tasks': '📋',
    'memory': '🧠',
    'content': '📄',
    'success': '✅',
    'error': '❌',
    'info': 'ℹ️',
    'watch': '👀',
    'bell': '🔔',
    'auto': '🤖'
}

# Auto mode and cron integration constants
HASH_CACHE_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'tmp', 'context_hashes')
HASH_CACHE_FILE = os.path.join(HASH_CACHE_DIR, 'latest_hash.json')
NOTIFICATION_SCRIPT = os.path.join(SCRIPT_DIR, '..', '..', 'cron', 'notify_context_change.py')

# =============================================================================
# INCREMENTAL PARSING & CACHING (性能优化 - 增量解析)
# =============================================================================

# 全局解析缓存
PARSE_CACHE = {}

# Section 解析缓存（使用 LRU）
SECTION_PARSE_CACHE = {}

# 缓存配置
CACHE_MAX_SIZE = 128  # 最大缓存条目数
CACHE_ENABLED = True  # 缓存开关


def _generate_cache_key(content_hash: str, section_type: str, level: str = 'normal') -> str:
    """生成缓存键"""
    return f"{content_hash}:{section_type}:{level}"


def parse_section_cached(section_type: str, content: str) -> dict:
    """
    缓存解析单个 section 的结果
    
    Args:
        section_type: section 类型 (metadata, operations, projects, tasks, highlights)
        content: 原始内容
        
    Returns:
        解析后的 dict
    """
    # 生成缓存键
    content_hash = hash_content(content)
    cache_key = _generate_cache_key(content_hash, section_type)
    
    # 检查缓存
    if CACHE_ENABLED and cache_key in SECTION_PARSE_CACHE:
        return SECTION_PARSE_CACHE[cache_key]
    
    # 根据类型解析
    if section_type == 'metadata':
        result = parse_metadata(content)
    elif section_type == 'operations':
        result = extract_recent_operations(content)
    elif section_type == 'projects':
        result = extract_key_projects(content)
    elif section_type == 'tasks':
        result = extract_ongoing_tasks(content)
    elif section_type == 'highlights':
        result = extract_memory_highlights(content)
    else:
        result = {}
    
    # 存入缓存
    if CACHE_ENABLED:
        # 简单缓存淘汰策略：超过最大大小则清空一半
        if len(SECTION_PARSE_CACHE) >= CACHE_MAX_SIZE:
            keys_to_remove = list(SECTION_PARSE_CACHE.keys())[:CACHE_MAX_SIZE // 2]
            for k in keys_to_remove:
                del SECTION_PARSE_CACHE[k]
        SECTION_PARSE_CACHE[cache_key] = result
    
    return result


@lru_cache(maxsize=64)
def _cached_normalize_text(content: str) -> str:
    """缓存 normalize 结果"""
    return content.lower()


def parse_with_cache(content: str, cache_key: str = None) -> dict:
    """
    解析内容并使用缓存
    
    Args:
        content: 要解析的内容
        cache_key: 可选的缓存键（如果未提供则自动生成）
        
    Returns:
        解析后的 dict
    """
    if cache_key is None:
        content_hash = hash_content(content)
        cache_key = f"full_parse:{content_hash}"
    
    # 检查缓存
    if CACHE_ENABLED and cache_key in PARSE_CACHE:
        return PARSE_CACHE[cache_key]
    
    # 解析内容
    result = {
        'metadata': parse_section_cached('metadata', content),
        'operations': parse_section_cached('operations', content),
        'projects': parse_section_cached('projects', content),
        'tasks': parse_section_cached('tasks', content),
        'highlights': parse_section_cached('highlights', content),
        'content_hash': hash_content(content)
    }
    
    # 存入缓存
    if CACHE_ENABLED:
        PARSE_CACHE[cache_key] = result
    
    return result


def clear_parse_cache():
    """清空解析缓存"""
    global PARSE_CACHE, SECTION_PARSE_CACHE
    PARSE_CACHE = {}
    SECTION_PARSE_CACHE = {}
    _cached_normalize_text.cache_clear()


def get_cache_stats() -> dict:
    """获取缓存统计信息"""
    return {
        'parse_cache_size': len(PARSE_CACHE),
        'section_cache_size': len(SECTION_PARSE_CACHE),
        'normalize_cache_info': _cached_normalize_text.cache_info(),
        'cache_enabled': CACHE_ENABLED
    }


# =============================================================================
# UNIFIED ERROR CODE SYSTEM
# =============================================================================

class ErrorCode:
    """统一错误码体系"""
    # Success
    SUCCESS = 0
    
    # File-related errors (1000-1999)
    FILE_NOT_FOUND = 1001
    PERMISSION_DENIED = 1002
    FILE_READ_ERROR = 1003
    
    # Content/Parse errors (2000-2999)
    INVALID_JSON = 2001
    EMPTY_CONTENT = 2002
    PARSE_ERROR = 2003
    INVALID_FORMAT = 2004
    
    # Input validation errors (3000-3999)
    INVALID_INPUT = 3001
    INVALID_PARAMETER = 3002
    NONE_INPUT = 3003
    
    # System errors (9000-9999)
    UNEXPECTED_ERROR = 9001
    
    @classmethod
    def get_message(cls, code: int) -> str:
        """获取错误码对应的用户友好消息"""
        messages = {
            0: "操作成功",
            1001: "文件未找到，请检查路径是否正确",
            1002: "没有权限访问该文件",
            1003: "读取文件时发生错误",
            2001: "文件格式无效，不是有效的JSON格式",
            2002: "文件内容为空",
            2003: "无法解析文件内容",
            2004: "不支持的文件格式",
            3001: "输入参数无效",
            3002: "参数值不在允许范围内",
            3003: "输入不能为空",
            9001: "发生未知错误，请稍后重试"
        }
        return messages.get(code, f"未知错误 (代码: {code})")


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class ContextLoadError(Exception):
    """上下文加载失败异常"""
    CODE = ErrorCode.FILE_READ_ERROR
    MESSAGE = ErrorCode.get_message(ErrorCode.FILE_READ_ERROR)
    
    def __init__(self, message: str = None, code: int = None, details: str = None):
        self.message = message or self.MESSAGE
        self.code = code or self.CODE
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message} (详情: {self.details})"
        return self.message
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "error": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


class ContextParseError(Exception):
    """上下文解析失败异常"""
    CODE = ErrorCode.PARSE_ERROR
    MESSAGE = ErrorCode.get_message(ErrorCode.PARSE_ERROR)
    
    def __init__(self, message: str = None, code: int = None, field: str = None):
        self.message = message or self.MESSAGE
        self.code = code or self.CODE
        self.field = field
        super().__init__(self.message)
    
    def __str__(self):
        if self.field:
            return f"{self.message} (字段: {self.field})"
        return self.message


# =============================================================================
# INPUT VALIDATION DECORATOR
# =============================================================================

def validate_input(require_str: bool = False, allow_none: bool = False):
    """
    输入验证装饰器
    
    为函数提供统一的输入验证功能：
    - 拒绝 None 输入 (除非 allow_none=True)
    - 拒绝二进制数据
    - 确保类型正确 (可选择强制为字符串)
    
    Args:
        require_str: 是否强制要求字符串输入
        allow_none: 是否允许 None 输入
        
    Returns:
        装饰器函数
        
    Example:
        @validate_input(require_str=True)
        def process_content(content: str) -> str:
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查位置参数
            for i, arg in enumerate(args):
                if arg is None:
                    if allow_none:
                        continue
                    raise ContextLoadError(
                        message=ErrorCode.get_message(ErrorCode.NONE_INPUT),
                        code=ErrorCode.NONE_INPUT,
                        details=f"{func.__name__}() 的第 {i+1} 个参数不能为空"
                    )
                if isinstance(arg, (bytes, bytearray)):
                    raise ContextLoadError(
                        message="不支持二进制输入",
                        code=ErrorCode.INVALID_INPUT,
                        details=f"{func.__name__}() 收到 bytes 类型，预期为 str"
                    )
                if require_str and not isinstance(arg, str):
                    raise ContextLoadError(
                        message=ErrorCode.get_message(ErrorCode.INVALID_INPUT),
                        code=ErrorCode.INVALID_INPUT,
                        details=f"{func.__name__}() 收到 {type(arg).__name__} 类型，预期为 str"
                    )
            
            # 检查关键字参数
            for key, value in kwargs.items():
                if value is None:
                    if allow_none:
                        continue
                    raise ContextLoadError(
                        message=ErrorCode.get_message(ErrorCode.NONE_INPUT),
                        code=ErrorCode.NONE_INPUT,
                        details=f"{func.__name__}() 的参数 '{key}' 不能为空"
                    )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# PRE-COMPILED REGEX PATTERNS (性能优化)
# =============================================================================

# =============================================================================
# PRE-COMPILED REGEX PATTERNS (性能优化)
# =============================================================================

# =============================================================================
# CONTEXT FILTERING FUNCTIONS
# =============================================================================

def filter_context(content: str, filter_pattern: str) -> str:
    """
    只保留匹配过滤条件的上下文
    
    过滤逻辑：
    - 保留包含 filter_pattern 的行/段落
    - 不区分大小写匹配
    - 保留周围的上下文行以提供更好的可读性
    
    Args:
        content: 原始上下文内容
        filter_pattern: 过滤关键词
        
    Returns:
        过滤后的内容字符串
        
    Example:
        >>> filtered = filter_context(content, "Hermes Plan")
        >>> print(filtered)  # 只包含与 Hermes Plan 相关的行
    """
    if not content or not content.strip():
        return content
    
    if not filter_pattern or not filter_pattern.strip():
        return content
    
    # 预处理：规范化过滤模式
    pattern = filter_pattern.strip()
    pattern_lower = pattern.lower()
    
    # 保留上下文的前后行数
    CONTEXT_LINES = 2
    
    lines = content.split('\n')
    filtered_indices = set()
    filtered_lines = []
    
    for i, line in enumerate(lines):
        if pattern_lower in line.lower():
            # 添加周围的上下文行
            start = max(0, i - CONTEXT_LINES)
            end = min(len(lines), i + CONTEXT_LINES + 1)
            for j in range(start, end):
                filtered_indices.add(j)
    
    # 构建过滤后的内容
    if filtered_indices:
        sorted_indices = sorted(filtered_indices)
        filtered_lines = [lines[i] for i in sorted_indices]
        return '\n'.join(filtered_lines)
    else:
        # 没有匹配时返回空字符串或原始内容的提示
        return f"[过滤: 未找到匹配 '{pattern}' 的内容]"


def filter_projects_only(content: str) -> str:
    """
    只提取项目相关信息
    
    Args:
        content: 原始上下文内容
        
    Returns:
        只包含项目相关内容的字符串
    """
    if not content or not content.strip():
        return content
    
    # 项目相关的关键词模式
    PROJECT_KEYWORDS = [
        'project', '项目',
        'hermes', 'hermès',
        'akasha',
        'morning brief', '晨间简报',
        'location', '路径',
        'status', '状态',
        'description', '描述'
    ]
    
    lines = content.split('\n')
    project_lines = []
    in_project_section = False
    
    for line in lines:
        # 检测是否进入项目部分
        lower_line = line.lower()
        if any(kw in lower_line for kw in ['🚀 **项目**', 'projects', '项目:']):
            in_project_section = True
            project_lines.append(line)
            continue
        
        # 如果已经在项目部分，保留该行直到遇到其他主要部分
        if in_project_section:
            # 检测是否离开项目部分（遇到新的主要部分）
            if any(sep in line for sep in ['---', '==='
                , '🔄 **最近操作**', 'operations'
                , '📋 **任务**', 'tasks'
                , '🧠 **记忆**', 'memory'
                , '📊 **压缩信息**', 'metadata'
            ]) and len(line.strip()) < 20:
                in_project_section = False
                continue
            project_lines.append(line)
        # 检查单行中是否包含项目信息
        elif any(kw in lower_line for kw in PROJECT_KEYWORDS):
            # 添加上下文
            project_lines.append(line)
    
    if project_lines:
        return '\n'.join(project_lines)
    else:
        return "[未找到项目相关信息]"


# Pre-compiled patterns for better performance
_METADATA_ORIGINAL_PATTERN = re.compile(r'原始消息数:\s*(\d+)')
_METADATA_COMPRESSED_PATTERN = re.compile(r'压缩后消息数:\s*(\d+)')
_METADATA_TIMESTAMP_PATTERN = re.compile(r'上下文压缩于\s*([\d\-T:.]+)')
_OPERATION_PATTERN = re.compile(r'✅\s*(.+?)(?:\n|$)')
_CRON_PATTERN = re.compile(r'(\d+)个?cron任务.*?已转为')
_SESSION_PATTERN = re.compile(r'(\d+)个活跃')
_SESSION_EN_PATTERN = re.compile(r'(\d+)\s*(?:isolated sessions)', re.IGNORECASE)
_CRON_EN_PATTERN = re.compile(r'(\d+)个?cron任务', re.IGNORECASE)
_MOLTBOOK_PATTERN = re.compile(r'(\d{1,2}):\d{2}\s*(?:Moltbook|学习)')

# Additional patterns for enhanced parsing
MESSAGE_COUNT_PATTERN = re.compile(r'原始消息数:\s*(\d+)')
COMPRESSED_COUNT_PATTERN = re.compile(r'压缩后消息数:\s*(\d+)')
TIMESTAMP_PATTERN = re.compile(r'压缩时间:\s*(\d{4}-\d{2}-\d{2})')
PROJECT_OPERATION_PATTERN = re.compile(r'• (.+)')
PROJECT_NAME_PATTERN = re.compile(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)')
TASK_PATTERN = re.compile(r'📌 (.+)')


# =============================================================================
# LRU CACHE FUNCTIONS (性能优化)
# =============================================================================

@functools.lru_cache(maxsize=32)
def _normalize_text(content: str) -> str:
    """
    缓存 lowercase 结果，避免重复调用 content.lower()
    
    Args:
        content: 原始文本内容
        
    Returns:
        小写化后的文本
        
    Performance:
        使用 LRU 缓存，maxsize=32 可缓存 32 个不同的输入结果
    """
    return content.lower()


# 便捷别名
normalize_content = _normalize_text


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_compressed_context(filepath: str) -> Any:
    """
    Load compressed context from a file.
    
    Attempts to parse the file as JSON first. If that fails, returns
    the raw text content. This allows the script to handle both
    JSON and plain text compressed context formats.
    
    Args:
        filepath: Path to the compressed context file.
        
    Returns:
        Parsed JSON object (dict/list) if valid JSON,
        raw string content if plain text,
        None if file cannot be loaded.
        
    Raises:
        ContextLoadError: When file cannot be loaded (file not found,
            permission denied, or other OS errors).
            
    Example:
        >>> result = load_compressed_context('./context.json')
        >>> if isinstance(result, dict):
        ...     print("JSON format detected")
        ... else:
        ...     print("Text format:", result[:50])
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if content is empty
        if not content or not content.strip():
            raise ContextLoadError(
                message=ErrorCode.get_message(ErrorCode.EMPTY_CONTENT),
                code=ErrorCode.EMPTY_CONTENT,
                details=f"文件 '{filepath}' 为空"
            )
        
        # Attempt to parse as JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Return raw text if not valid JSON
            return content
            
    except FileNotFoundError:
        raise ContextLoadError(
            message=ErrorCode.get_message(ErrorCode.FILE_NOT_FOUND),
            code=ErrorCode.FILE_NOT_FOUND,
            details=f"文件未找到: {filepath}"
        )
    except PermissionError:
        raise ContextLoadError(
            message=ErrorCode.get_message(ErrorCode.PERMISSION_DENIED),
            code=ErrorCode.PERMISSION_DENIED,
            details=f"权限被拒绝: {filepath}"
        )
    except OSError as e:
        raise ContextLoadError(
            message=ErrorCode.get_message(ErrorCode.FILE_READ_ERROR),
            code=ErrorCode.FILE_READ_ERROR,
            details=f"读取文件 {filepath} 时出错: {str(e)}"
        )
    except Exception as e:
        raise ContextLoadError(
            message=ErrorCode.get_message(ErrorCode.UNEXPECTED_ERROR),
            code=ErrorCode.UNEXPECTED_ERROR,
            details=f"加载上下文时发生未知错误: {str(e)}"
        )


def parse_metadata(content: str) -> dict:
    """
    Extract metadata from plain text context content.
    
    Parses the compressed context to extract key metadata such as:
    - Original message count
    - Compressed message count
    - Compression timestamp
    
    Args:
        content: Raw text content from the compressed context file.
        
    Returns:
        Dictionary containing extracted metadata fields:
        - 'original_count': Number of original messages (int or None)
        - 'compressed_count': Number of compressed messages (int or None)
        - 'timestamp': Compression timestamp string (or None)
        
    Example:
        >>> meta = parse_metadata("原始消息数: 100  压缩后消息数: 20")
        >>> print(meta['original_count'])
        100
    """
    metadata = {}
    
    # Use pre-compiled patterns for better performance
    original_match = _METADATA_ORIGINAL_PATTERN.search(content)
    if original_match:
        metadata['original_count'] = int(original_match.group(1))
    
    compressed_match = _METADATA_COMPRESSED_PATTERN.search(content)
    if compressed_match:
        metadata['compressed_count'] = int(compressed_match.group(1))
    
    timestamp_match = _METADATA_TIMESTAMP_PATTERN.search(content)
    if timestamp_match:
        metadata['timestamp'] = timestamp_match.group(1)
    
    return metadata


def extract_recent_operations(content: str, max_count: int = 5) -> list[str]:
    """
    Extract recent operations from context content.
    
    Scans the context for indicators of recent user and assistant actions,
    such as completion markers, context restoration events, and task conversions.
    
    Args:
        content: Raw text content from the compressed context file.
        max_count: Maximum number of operations to return (default: 5)
        
    Returns:
        List of strings describing recent operations.
        Operations are deduplicated and ordered by appearance.
        
    Example:
        >>> ops = extract_recent_operations("✅ Context restored\n✅ Tasks completed")
        >>> print(ops)
        ['Context restored', 'Tasks completed']
    """
    operations = []
    content_lower = normalize_content(content)  # 使用 LRU 缓存的 lowercase
    
    # Use pre-compiled pattern for ✅ operations
    matches = _OPERATION_PATTERN.findall(content)
    for match in matches:
        cleaned = match.strip()
        if cleaned and cleaned not in operations:
            operations.append(cleaned)
    
    # Check for cron task conversion
    if 'cron' in content_lower:
        cron_match = _CRON_PATTERN.search(content)
        if cron_match:
            ops_text = f"{cron_match.group(0)} isolated mode"
            if ops_text not in operations:
                operations.append(ops_text)
    
    # Check for context restoration events
    if 'context restore' in content_lower or '上下文已恢复' in content:
        restore_text = "Context restoration performed"
        if restore_text not in operations:
            operations.append(restore_text)
    
    # Check for user interaction indicators
    if 'user:' in content_lower:
        user_text = "User interaction detected"
        if user_text not in operations:
            operations.append(user_text)
    
    return operations[:max_count]


def extract_key_projects(content: str) -> list[dict]:
    """
    Extract key projects from context content.
    
    Identifies and extracts information about major projects mentioned
    in the context, including their names, descriptions, and status.
    
    Known projects:
    - Hermes Plan: Data analysis assistant
    - Akasha Plan: Autonomous news system
    - Morning Brief: Daily news briefing
    
    Args:
        content: Raw text content from the compressed context file.
        
    Returns:
        List of dictionaries, each representing a project with fields:
        - 'name': Project name (str)
        - 'description': Brief description (str)
        - 'status': Current status (str)
        - 'location': File system path (str, optional)
        
    Example:
        >>> projects = extract_key_projects("Hermes Plan - Data analysis")
        >>> print(projects[0]['name'])
        'Hermes Plan'
    """
    projects = []
    content_lower = normalize_content(content)  # 使用 LRU 缓存的 lowercase
    
    # Detect Hermes Plan - Data analysis assistant
    if 'hermès' in content_lower or 'hermes' in content_lower:
        projects.append({
            'name': 'Hermes Plan',
            'description': 'Data analysis assistant for Excel, documents, and reports',
            'status': 'Active',
            'location': '/home/athur/.openclaw/workspace/hermes-plan/'
        })
    
    # Detect Akasha Plan - Autonomous news system
    if 'akasha' in content_lower:
        projects.append({
            'name': 'Akasha Plan',
            'description': 'Autonomous news system with anchor tracking and learning',
            'status': 'Active',
            'location': '/home/athur/.openclaw/workspace/akasha-plan/'
        })
    
    # Detect Morning Brief - Daily news briefing
    if 'morning brief' in content_lower or '晨间简报' in content:
        projects.append({
            'name': 'Morning Brief',
            'description': 'Daily news briefing at 8 AM Rome time (weather + news)',
            'status': 'Active',
            'location': None
        })
    
    return projects


def extract_ongoing_tasks(content: str) -> list[dict]:
    """
    Extract ongoing tasks from context content.
    
    Identifies currently active or pending tasks based on context indicators
    such as active session counts, cron job information, and background processes.
    
    Args:
        content: Raw text content from the compressed context file.
        
    Returns:
        List of dictionaries, each representing a task with fields:
        - 'task': Task name/identifier (str)
        - 'status': Current status (str)
        - 'detail': Additional details (str)
        
    Example:
        >>> tasks = extract_ongoing_tasks("3个活跃 Isolated Sessions")
        >>> print(tasks[0]['task'])
        'Isolated Sessions'
    """
    tasks = []
    content_lower = normalize_content(content)  # 使用 LRU 缓存的 lowercase
    
    # Extract Isolated Sessions count - Chinese pattern
    session_match = _SESSION_PATTERN.search(content)
    if session_match:
        count = int(session_match.group(1))
        tasks.append({
            'task': 'Isolated Sessions',
            'status': 'Active',
            'detail': f'{count} sessions running in parallel'
        })
    else:
        # Alternative pattern for English text
        alt_match = _SESSION_EN_PATTERN.search(content)
        if alt_match:
            count = int(alt_match.group(1))
            tasks.append({
                'task': 'Isolated Sessions',
                'status': 'Active',
                'detail': f'{count} sessions running in parallel'
            })
    
    # Detect Cron tasks
    if 'cron' in content_lower:
        cron_match = _CRON_EN_PATTERN.search(content)
        if cron_match:
            count = int(cron_match.group(1))
            tasks.append({
                'task': 'Cron Tasks',
                'status': 'Running',
                'detail': f'{count} scheduled tasks (isolated mode)'
            })
        else:
            tasks.append({
                'task': 'Cron Tasks',
                'status': 'Running',
                'detail': 'Scheduled background tasks'
            })
    
    # Detect Moltbook learning
    if 'moltbook' in content_lower:
        time_match = _MOLTBOOK_PATTERN.search(content)
        if time_match:
            tasks.append({
                'task': 'Moltbook Learning',
                'status': 'Active',
                'detail': f'Daily learning at {time_match.group(1)}:00'
            })
        else:
            tasks.append({
                'task': 'Moltbook Learning',
                'status': 'Active',
                'detail': 'Daily learning schedule'
            })
    
    # Detect Main Session
    if '主会话' in content or 'main session' in content_lower:
        tasks.append({
            'task': 'Main Session',
            'status': 'Active',
            'detail': 'Primary conversation session with user'
        })
    
    return tasks


def extract_memory_highlights(content: str) -> list[str]:
    """
    Extract MEMORY.md highlights from context content.
    
    Identifies references to long-term memory sections that are
    relevant to the current context.
    
    Args:
        content: Raw text content from the compressed context file.
        
    Returns:
        List of strings describing referenced memory sections.
        
    Example:
        >>> highlights = extract_memory_highlights("Identity and Server Access")
        >>> print(highlights)
        ['• Identity: Referenced', '• Server Access: Referenced']
    """
    highlights = []
    content_lower = normalize_content(content)  # 使用 LRU 缓存的 lowercase
    
    # Known MEMORY.md sections to look for (预计算 lowercase)
    memory_sections_lower = [
        ('Identity', 'identity'),
        ('Core Capabilities', 'core capabilities'),
        ('Session Policy', 'session policy'),
        ('Key Projects', 'key projects'),
        ('Moltbook', 'moltbook'),
        ('Server Access', 'server access'),
        ('Skill Exploration', 'skill exploration'),
    ]
    
    for section_name, section_lower in memory_sections_lower:
        # Case-insensitive search for section name
        if section_lower in content_lower:
            highlights.append(f"• {section_name}: Referenced in context")
    
    return highlights


def calculate_compression_ratio(original: Optional[int], compressed: Optional[int]) -> Optional[float]:
    """
    Calculate the compression ratio as a percentage.
    
    Args:
        original: Number of original messages (int or None).
        compressed: Number of compressed messages (int or None).
        
    Returns:
        Compression ratio as a percentage (float),
        or None if either value is missing or invalid.
        
    Example:
        >>> ratio = calculate_compression_ratio(100, 25)
        >>> print(f"{ratio:.1f}%")
        25.0%
    """
    if original is None or compressed is None:
        return None
    if original <= 0:
        return None
    
    return (compressed / original) * 100


def extract_timeline(content: str, period: str = "daily", days: int = 30) -> dict:
    """
    Extract timeline of historical operations grouped by period.
    
    Parses context content and aggregates operations by date,
    creating a timeline view at the specified period granularity.
    
    Args:
        content: Raw text content from the compressed context file.
        period: Time period for aggregation.
                Valid values: "daily" | "weekly" | "monthly"
                Default: "daily"
        days: Number of days to include in timeline (default: 30).
              For weekly: approximately `days/7` periods
              For monthly: approximately `days/30` periods
        
    Returns:
        Dictionary containing:
        - 'period': The aggregation period used
        - 'total_days': Total days covered
        - 'total_operations': Total number of operations across all periods
        - 'timeline': List of period entries, each with:
            - 'period_label': Date/period identifier string
            - 'date_range': Start-end dates for weekly/monthly (optional)
            - 'operations': List of operation strings
            - 'projects': List of project names
            - 'operations_count': Number of operations
            - 'highlights': Notable highlights
        
    Example (daily):
        >>> result = extract_timeline(content, period="daily", days=7)
        >>> print(result['timeline'][0]['period_label'])
        '2026-02-07'
    
    Example (weekly):
        >>> result = extract_timeline(content, period="weekly")
        >>> print(result['timeline'][0]['period_label'])
        'Week 6 (Feb 2-8)'
    """
    import datetime
    from collections import defaultdict
    
    # Validate period
    if period not in VALID_PERIODS:
        raise ValueError(
            f"Invalid period: {period}. Must be one of: {', '.join(VALID_PERIODS)}"
        )
    
    # Pattern for finding dates in content
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
    date_matches = set(date_pattern.findall(content))
    
    # Find all dates and their surrounding content
    date_sections = {}
    for date in date_matches:
        date_index = content.find(date)
        if date_index != -1:
            # Extract section around date (150 chars before and after)
            start = max(0, date_index - 150)
            end = min(len(content), date_index + 300)
            date_sections[date] = content[start:end]
    
    # Sort dates
    sorted_dates = sorted(date_sections.keys(), reverse=True)
    
    # Filter to requested days
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    filtered_dates = []
    for d in sorted_dates:
        try:
            dt = datetime.datetime.strptime(d, "%Y-%m-%d")
            if dt >= cutoff_date:
                filtered_dates.append(d)
        except ValueError:
            continue
    
    if not filtered_dates:
        # No dates found, return single entry with all content
        # 使用缓存解析
        operations = parse_section_cached('operations', content)
        projects = parse_section_cached('projects', content)
        return {
            "period": period,
            "total_days": 0,
            "total_operations": len(operations),
            "timeline": [{
                "period_label": "Recent",
                "date_range": None,
                "operations": operations,
                "projects": [p['name'] for p in projects],
                "operations_count": len(operations),
                "highlights": []
            }]
        }
    
    # Aggregate by period
    period_groups = defaultdict(list)
    
    for date in filtered_dates:
        section = date_sections[date]
        # 使用缓存解析
        operations = parse_section_cached('operations', section)
        projects = parse_section_cached('projects', section)
        
        # Determine period key
        try:
            dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            continue
        
        if period == "daily":
            period_key = date
            period_label = date
        elif period == "weekly":
            # ISO week number
            week_num = dt.isocalendar()[1]
            year = dt.year
            # Calculate week start (Monday)
            week_start = dt - datetime.timedelta(days=dt.weekday())
            week_end = week_start + datetime.timedelta(days=6)
            period_key = f"{year}-W{week_num:02d}"
            period_label = f"Week {week_num} ({week_start.strftime('%b %d')} - {week_end.strftime('%b %d')})"
        else:  # monthly
            period_key = date[:7]  # YYYY-MM
            period_label = date[:7]
        
        period_groups[period_key].append({
            "date": date,
            "operations": operations,
            "projects": [p['name'] for p in projects],
            "section": section
        })
    
    # Build timeline result
    timeline = []
    total_operations = 0
    
    for period_key in sorted(period_groups.keys(), reverse=True):
        group_data = period_groups[period_key]
        
        # Collect unique operations and projects for this period
        all_ops = []
        all_projects = set()
        highlights = []
        
        for entry in group_data:
            all_ops.extend(entry["operations"])
            all_projects.update(entry["projects"])
        
        # Deduplicate
        all_ops = list(dict.fromkeys(all_ops))  # Preserve order, remove duplicates
        all_projects = list(all_projects)
        
        # Generate highlights from significant operations
        significant_keywords = ["completed", "restored", "created", "updated", "fixed", "deployed"]
        for op in all_ops[:3]:  # Top 3 as highlights
            op_lower = op.lower()
            if any(kw in op_lower for kw in significant_keywords):
                if op not in highlights:
                    highlights.append(op)
        
        # Use first entry's label for this period (already calculated)
        if period == "weekly":
            # Recalculate for output
            sample_date = group_data[0]["date"]
            dt = datetime.datetime.strptime(sample_date, "%Y-%m-%d")
            week_num = dt.isocalendar()[1]
            year = dt.year
            week_start = dt - datetime.timedelta(days=dt.weekday())
            week_end = week_start + datetime.timedelta(days=6)
            period_label = f"Week {week_num} ({week_start.strftime('%b %d')} - {week_end.strftime('%b %d')})"
            date_range = f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
        elif period == "monthly":
            period_label = period_key
            month_name = datetime.datetime.strptime(period_key, "%Y-%m").strftime("%B %Y")
            period_label = month_name
            first_date = min(e["date"] for e in group_data)
            last_date = max(e["date"] for e in group_data)
            date_range = f"{first_date} to {last_date}"
        else:
            period_label = period_key
            date_range = None
        
        period_entry = {
            "period_label": period_label,
            "date_range": date_range,
            "operations": all_ops,
            "projects": all_projects,
            "operations_count": len(all_ops),
            "highlights": highlights[:3]
        }
        
        timeline.append(period_entry)
        total_operations += len(all_ops)
    
    # Calculate total days covered
    if filtered_dates:
        try:
            first = datetime.datetime.strptime(filtered_dates[-1], "%Y-%m-%d")
            last = datetime.datetime.strptime(filtered_dates[0], "%Y-%m-%d")
            total_days = (last - first).days + 1
        except ValueError:
            total_days = len(filtered_dates)
    else:
        total_days = 0
    
    return {
        "period": period,
        "total_days": total_days,
        "total_operations": total_operations,
        "timeline": timeline
    }


def get_context_summary(filepath: str, period: str = "daily", days: int = 30) -> dict:
    """
    Get structured JSON summary of context for programmatic use.
    
    Extracts all relevant information from the context file and
    returns it as a structured dictionary suitable for JSON output.
    Also includes dynamically read project progress information.
    
    Args:
        filepath: Path to the compressed context file.
        period: Time period for timeline aggregation (daily/weekly/monthly).
                Default: "daily"
        days: Number of days to include in timeline. Default: 30
        
    Returns:
        Dictionary containing:
        - 'success': Boolean indicating if extraction succeeded
        - 'metadata': Context metadata (message counts, timestamp)
        - 'operations': List of recent operations
        - 'projects': List of key projects (from context text)
        - 'tasks': List of ongoing tasks
        - 'timeline': Timeline of historical operations with period aggregation
        - 'compression_ratio': Calculated compression ratio (float or None)
        - 'project_progress': Dict with real-time project progress from files
        
    Example:
        >>> summary = get_context_summary('./compressed.json', period='weekly')
        >>> print(summary['success'])
        True
        >>> print(len(summary['operations']))
        5
        >>> pp = summary['project_progress']['project_summary']
        >>> print(f"Projects: {pp['total']}, Avg: {pp['average_progress']}%")
    """
    # Load context file
    context = load_compressed_context(filepath)
    
    if context is None:
        return {
            'success': False,
            'error': f'Could not load context file from: {filepath}',
            'filepath': filepath
        }
    
    # Handle both JSON dict and text content
    if isinstance(context, dict):
        if 'content' in context:
            content = context['content']
        elif 'text' in context:
            content = context['text']
        elif 'data' in context:
            content = context['data']
        else:
            content = json.dumps(context, indent=2, ensure_ascii=False)
    else:
        content = str(context)
    
    # Extract all information
    metadata = parse_metadata(content)
    operations = extract_recent_operations(content)
    projects = extract_key_projects(content)
    tasks = extract_ongoing_tasks(content)
    timeline = extract_timeline(content, period=period, days=days)
    highlights = extract_memory_highlights(content)
    
    # Calculate compression ratio
    ratio = calculate_compression_ratio(
        metadata.get('original_count'),
        metadata.get('compressed_count')
    )
    
    # Get project progress from project directories
    project_progress_data = get_project_summary_for_context()
    
    return {
        'success': True,
        'filepath': filepath,
        'metadata': {
            'original_count': metadata.get('original_count'),
            'compressed_count': metadata.get('compressed_count'),
            'timestamp': metadata.get('timestamp'),
            'compression_ratio': ratio
        },
        'operations': operations,
        'projects': projects,
        'tasks': tasks,
        'timeline': timeline,
        'memory_highlights': highlights,
        'project_progress': project_progress_data
    }


def compare_contexts(old: str, new: str) -> dict:
    """
    Compare two versions of context and identify differences.
    
    Analyzes the changes between two context snapshots, detecting:
    - Added/removed projects
    - Modified tasks
    - Operations changes
    - Time difference in hours
    
    Args:
        old: Path to the older context file
        new: Path to the newer context file
        
    Returns:
        Dictionary containing:
        - 'success': bool - Whether comparison succeeded
        - 'added_projects': list - Projects in new but not in old
        - 'removed_projects': list - Projects in old but not in new
        - 'modified_tasks': list - Tasks with changed status/detail
        - 'operations_added': list - Operations in new but not in old
        - 'operations_removed': list - Operations in old but not in new
        - 'operations_change': dict - Count changes in operations
        - 'time_diff_hours': float - Hours between the two snapshots
        - 'message_count_change': dict - Change in original/compressed counts
        
    Example:
        >>> diff = compare_contexts('yesterday.json', 'latest.json')
        >>> print(f"Added {len(diff['added_projects'])} projects")
        >>> print(f"Time diff: {diff['time_diff_hours']:.1f} hours")
    """
    # Load both context summaries
    old_summary = get_context_summary(old)
    new_summary = get_context_summary(new)
    
    if not old_summary.get('success'):
        return {
            'success': False,
            'error': f"Failed to load old context: {old}",
            'added_projects': [],
            'removed_projects': [],
            'modified_tasks': [],
            'operations_added': [],
            'operations_removed': [],
            'operations_change': {},
            'time_diff_hours': 0,
            'message_count_change': {}
        }
    
    if not new_summary.get('success'):
        return {
            'success': False,
            'error': f"Failed to load new context: {new}",
            'added_projects': [],
            'removed_projects': [],
            'modified_tasks': [],
            'operations_added': [],
            'operations_removed': [],
            'operations_change': {},
            'time_diff_hours': 0,
            'message_count_change': {}
        }
    
    # Extract project names for comparison
    old_projects = {p['name']: p for p in old_summary.get('projects', [])}
    new_projects = {p['name']: p for p in new_summary.get('projects', [])}
    
    old_project_names = set(old_projects.keys())
    new_project_names = set(new_projects.keys())
    
    # Find added and removed projects
    added_projects = [new_projects[name] for name in new_project_names - old_project_names]
    removed_projects = [old_projects[name] for name in old_project_names - new_project_names]
    
    # Find modified projects (same name but different content)
    modified_projects = []
    for name in old_project_names & new_project_names:
        old_proj = old_projects[name]
        new_proj = new_projects[name]
        if old_proj != new_proj:
            modified_projects.append({
                'name': name,
                'old': old_proj,
                'new': new_proj
            })
    
    # Extract tasks for comparison
    old_tasks = {t['task']: t for t in old_summary.get('tasks', [])}
    new_tasks = {t['task']: t for t in new_summary.get('tasks', [])}
    
    old_task_names = set(old_tasks.keys())
    new_task_names = set(new_tasks.keys())
    
    # Find added and removed tasks
    added_tasks = [new_tasks[name] for name in new_task_names - old_task_names]
    removed_tasks = [old_tasks[name] for name in old_task_names - new_task_names]
    
    # Find modified tasks
    modified_tasks = []
    for name in old_task_names & new_task_names:
        old_task = old_tasks[name]
        new_task = new_tasks[name]
        if old_task != new_task:
            modified_tasks.append({
                'task': name,
                'old': old_task,
                'new': new_task
            })
    
    # Extract operations for comparison
    old_ops = set(old_summary.get('operations', []))
    new_ops = set(new_summary.get('operations', []))
    
    operations_added = list(new_ops - old_ops)
    operations_removed = list(old_ops - new_ops)
    
    # Calculate operations change
    old_ops_count = len(old_ops)
    new_ops_count = len(new_ops)
    
    operations_change = {
        'added_count': len(operations_added),
        'removed_count': len(operations_removed),
        'net_change': new_ops_count - old_ops_count,
        'total_old': old_ops_count,
        'total_new': new_ops_count
    }
    
    # Calculate time difference
    time_diff_hours = 0.0
    old_ts = old_summary.get('timestamp')
    new_ts = new_summary.get('timestamp')
    
    if old_ts and new_ts:
        try:
            from datetime import datetime
            # Handle various timestamp formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    old_dt = datetime.strptime(old_ts, fmt)
                    new_dt = datetime.strptime(new_ts, fmt)
                    diff = new_dt - old_dt
                    time_diff_hours = diff.total_seconds() / 3600
                    break
                except ValueError:
                    continue
        except Exception:
            time_diff_hours = 0.0
    
    # Calculate message count changes
    old_meta = old_summary.get('metadata', {})
    new_meta = new_summary.get('metadata', {})
    
    message_count_change = {
        'original_change': (new_meta.get('compressed_count') or 0) - (old_meta.get('compressed_count') or 0),
        'compressed_change': (new_meta.get('compressed_count') or 0) - (old_meta.get('compressed_count') or 0),
        'old_original': old_meta.get('original_count'),
        'new_original': new_meta.get('original_count'),
        'old_compressed': old_meta.get('compressed_count'),
        'new_compressed': new_meta.get('compressed_count')
    }
    
    return {
        'success': True,
        'added_projects': added_projects,
        'removed_projects': removed_projects,
        'modified_projects': modified_projects,
        'added_tasks': added_tasks,
        'removed_tasks': removed_tasks,
        'modified_tasks': modified_tasks,
        'operations_added': operations_added,
        'operations_removed': operations_removed,
        'operations_change': operations_change,
        'time_diff_hours': time_diff_hours,
        'message_count_change': message_count_change,
        'old_summary': {
            'timestamp': old_summary.get('timestamp'),
            'projects_count': len(old_projects),
            'tasks_count': len(old_tasks)
        },
        'new_summary': {
            'timestamp': new_summary.get('timestamp'),
            'projects_count': len(new_projects),
            'tasks_count': len(new_tasks)
        }
    }


def format_diff_report(diff: dict, old_file: str, new_file: str) -> str:
    """
    Generate a formatted diff report.
    
    Creates a human-readable report showing all differences
    between two context versions.
    
    Args:
        diff: Dictionary returned by compare_contexts()
        old_file: Path to the older context file
        new_file: Path to the newer context file
        
    Returns:
        Formatted report string
    """
    lines = []
    
    lines.append(SEPARATOR)
    lines.append("CONTEXT DIFF REPORT")
    lines.append(SEPARATOR)
    
    lines.append(f"\n📁 Old: {old_file}")
    lines.append(f"📁 New: {new_file}")
    
    if not diff.get('success'):
        lines.append(f"\n❌ Comparison failed: {diff.get('error', 'Unknown error')}")
        return '\n'.join(lines)
    
    # Time difference
    time_hours = diff.get('time_diff_hours', 0)
    if time_hours > 0:
        lines.append(f"\n⏱️  Time difference: {time_hours:.1f} hours")
    else:
        lines.append(f"\n⏱️  Time difference: N/A")
    
    # Projects section
    lines.append(f"\n🚀 Projects:")
    
    added_projects = diff.get('added_projects', [])
    removed_projects = diff.get('removed_projects', [])
    modified_projects = diff.get('modified_projects', [])
    
    if added_projects:
        lines.append(f"   ➕ Added ({len(added_projects)}):")
        for p in added_projects:
            lines.append(f"      - {p['name']}")
    
    if removed_projects:
        lines.append(f"   ➖ Removed ({len(removed_projects)}):")
        for p in removed_projects:
            lines.append(f"      - {p['name']}")
    
    if modified_projects:
        lines.append(f"   🔄 Modified ({len(modified_projects)}):")
        for m in modified_projects:
            lines.append(f"      - {m['name']}")
    
    if not any([added_projects, removed_projects, modified_projects]):
        lines.append("   (No project changes)")
    
    # Tasks section
    lines.append(f"\n📋 Tasks:")
    
    added_tasks = diff.get('added_tasks', [])
    removed_tasks = diff.get('removed_tasks', [])
    modified_tasks = diff.get('modified_tasks', [])
    
    if added_tasks:
        lines.append(f"   ➕ Added ({len(added_tasks)}):")
        for t in added_tasks:
            lines.append(f"      - {t['task']}")
    
    if removed_tasks:
        lines.append(f"   ➖ Removed ({len(removed_tasks)}):")
        for t in removed_tasks:
            lines.append(f"      - {t['task']}")
    
    if modified_tasks:
        lines.append(f"   🔄 Modified ({len(modified_tasks)}):")
        for m in modified_tasks:
            lines.append(f"      - {m['task']}")
    
    if not any([added_tasks, removed_tasks, modified_tasks]):
        lines.append("   (No task changes)")
    
    # Operations section
    lines.append(f"\n🔄 Operations:")
    
    ops_added = diff.get('operations_added', [])
    ops_removed = diff.get('operations_removed', [])
    ops_change = diff.get('operations_change', {})
    
    if ops_added:
        lines.append(f"   ➕ Added ({len(ops_added)}):")
        for op in ops_added:
            lines.append(f"      - {op}")
    
    if ops_removed:
        lines.append(f"   ➖ Removed ({len(ops_removed)}):")
        for op in ops_removed:
            lines.append(f"      - {op}")
    
    if ops_change:
        lines.append(f"   📊 Change: {ops_change.get('net_change', 0)} "
                    f"({ops_change.get('total_old', 0)} → {ops_change.get('total_new', 0)})")
    
    if not any([ops_added, ops_removed]):
        lines.append("   (No operation changes)")
    
    # Message count section
    lines.append(f"\n📊 Message Counts:")
    msg_change = diff.get('message_count_change', {})
    lines.append(f"   Old: {msg_change.get('old_original', 'N/A')} → "
                f"{msg_change.get('old_compressed', 'N/A')} (compressed)")
    lines.append(f"   New: {msg_change.get('new_original', 'N/A')} → "
                f"{msg_change.get('new_compressed', 'N/A')} (compressed)")
    
    # Summary
    lines.append(f"\n{SEPARATOR}")
    total_changes = (len(added_projects) + len(removed_projects) + 
                    len(modified_projects) + len(added_tasks) + 
                    len(removed_tasks) + len(modified_tasks) +
                    len(ops_added) + len(ops_removed))
    lines.append(f"Total changes detected: {total_changes}")
    lines.append(SEPARATOR)
    
    return '\n'.join(lines)


# =============================================================================
# PLATFORM CONSTANTS AND UTILITIES
# =============================================================================

# Platform constants
PLATFORM_UNKNOWN = "unknown"
PLATFORM_TELEGRAM = "telegram"
PLATFORM_DISCORD = "discord"
PLATFORM_WHATSAPP = "whatsapp"
PLATFORM_SLACK = "slack"

VALID_PLATFORMS = [PLATFORM_TELEGRAM, PLATFORM_DISCORD, PLATFORM_WHATSAPP, PLATFORM_SLACK]

# Platform-specific message limits
TELEGRAM_MAX_LENGTH = 4000
DISCORD_MAX_LENGTH = 2000


def detect_platform_from_context(content: str) -> str:
    """
    根据上下文中的标记检测当前平台
    
    分析内容中的特征标记来确定当前消息平台。
    
    Args:
        content: 原始内容字符串
        
    Returns:
        检测到的平台标识符 (telegram, discord, whatsapp, slack, unknown)
        
    Example:
        >>> detect_platform_from_context("telegram context data")
        'telegram'
        >>> detect_platform_from_context("discord message content")
        'discord'
    """
    if not content or not isinstance(content, str):
        return PLATFORM_UNKNOWN
    
    content_lower = content.lower()
    
    # 检查 Telegram 特征
    telegram_indicators = ['telegram', 'tg::', 'tg:', 'telega']
    for indicator in telegram_indicators:
        if indicator in content_lower:
            return PLATFORM_TELEGRAM
    
    # 检查 Discord 特征
    discord_indicators = ['discord', 'dc::', 'dc:', 'discord.gg']
    for indicator in discord_indicators:
        if indicator in content_lower:
            return PLATFORM_DISCORD
    
    # 检查 WhatsApp 特征
    whatsapp_indicators = ['whatsapp', 'wa::', 'wa:', 'whatsapp.com']
    for indicator in whatsapp_indicators:
        if indicator in content_lower:
            return PLATFORM_WHATSAPP
    
    # 检查 Slack 特征
    slack_indicators = ['slack', 'slack://']
    for indicator in slack_indicators:
        if indicator in content_lower:
            return PLATFORM_SLACK
    
    return PLATFORM_UNKNOWN


def format_for_platform(content: str, platform: str) -> str:
    """
    根据平台调整内容格式
    
    针对不同消息平台优化内容格式：
    - Telegram: Markdown 格式，支持分块
    - Discord: 特定格式，链接防展开
    - WhatsApp: 无 Markdown 表格，使用纯文本格式
    - Slack: 类似 Discord，支持更多 emoji
    
    Args:
        content: 原始内容
        platform: 目标平台标识符
        
    Returns:
        格式化后的内容字符串
        
    Example:
        >>> formatted = format_for_platform(content, "telegram")
        >>> formatted = format_for_platform(content, "discord")
    """
    if not content:
        return content
    
    if platform == PLATFORM_TELEGRAM:
        return format_for_telegram(content)
    elif platform == PLATFORM_DISCORD:
        return format_for_discord(content)
    elif platform == PLATFORM_WHATSAPP:
        return format_for_whatsapp(content)
    elif platform == PLATFORM_SLACK:
        return format_for_slack(content)
    else:
        return content


def format_for_telegram(content: str) -> str:
    """
    优化 Telegram 消息格式
    
    Telegram 支持 Markdown 格式，使用粗体/斜体标记。
    分块策略确保长消息正确发送。
    
    Args:
        content: 原始内容
        
    Returns:
        Telegram 优化格式的内容
    """
    if not content:
        return content
    
    # Telegram Markdown 不需要特殊转换，保持原样
    return content


def format_for_discord(content: str) -> str:
    """
    优化 Discord 消息格式
    
    Discord 需要：
    - 多重链接使用 < > 包裹防止 embed
    - 代码块使用 ``` 标记
    - 避免过长的纯文本块
    
    Args:
        content: 原始内容
        
    Returns:
        Discord 优化格式的内容
    """
    if not content:
        return content
    
    result = content
    
    # 转换链接为 Discord 安全格式
    import re
    
    # 找到独立的 URL (不在 <> 内部)
    url_pattern = re.compile(r'(?<!<)(https?://[^\s<>]+)(?!>)')
    
    def wrap_url(match):
        url = match.group(1)
        return f'<{url}>'
    
    result = url_pattern.sub(wrap_url, result)
    
    return result


def format_for_whatsapp(content: str) -> str:
    """
    优化 WhatsApp 消息格式
    
    WhatsApp 不支持 Markdown 表格。
    建议使用纯文本列表和 **粗体**。
    
    Args:
        content: 原始内容
        
    Returns:
        WhatsApp 友好格式的内容
    """
    if not content:
        return content
    
    result = content
    
    # 移除表格（转换为纯文本列表）
    import re
    
    lines = result.split('\n')
    result_lines = []
    in_table = False
    
    for line in lines:
        if '|' in line and not line.strip().startswith('-'):
            if not in_table:
                in_table = True
                result_lines.append('')
            cells = [c.strip() for c in line.split('|') if c.strip()]
            result_lines.append(' • '.join(cells))
        else:
            in_table = False
            result_lines.append(line)
    
    result = '\n'.join(result_lines)
    
    return result


def format_for_slack(content: str) -> str:
    """
    优化 Slack 消息格式
    
    Slack 支持 mrkdwn 格式，可以使用：
    - *粗体*
    - _斜体_
    - 链接
    - 代码块
    
    Args:
        content: 原始内容
        
    Returns:
        Slack 优化格式的内容
    """
    if not content:
        return content
    
    # Slack mrkdwn 格式与 Markdown 类似
    return content


def split_for_platform(content: str, platform: str) -> list[str]:
    """
    根据平台限制分割长消息
    
    根据不同平台的消息长度限制，分割内容。
    
    Args:
        content: 要分割的原始内容
        platform: 目标平台
        
    Returns:
        分割后的消息块列表
    """
    if not content:
        return []
    
    if platform == PLATFORM_TELEGRAM:
        max_length = TELEGRAM_MAX_LENGTH
    elif platform == PLATFORM_DISCORD:
        max_length = DISCORD_MAX_LENGTH
    else:
        max_length = TELEGRAM_MAX_LENGTH
    
    if len(content) <= max_length:
        return [content]
    
    chunks = []
    
    while len(content) > max_length:
        split_pos = content.rfind('\n', 0, max_length)
        
        if split_pos == -1:
            split_pos = max_length
        
        chunk = content[:split_pos]
        chunks.append(chunk)
        content = content[split_pos:]
    
    if content:
        chunks.append(content)
    
    return chunks


# =============================================================================
# TELEGRAM MESSAGE CHUNKING (Telegram 消息分块支持)
# =============================================================================

TELEGRAM_MAX_LENGTH = 4000


def split_for_telegram(content: str, max_length: int = TELEGRAM_MAX_LENGTH) -> list[str]:
    """
    将长消息分块以适应 Telegram 消息长度限制
    
    会在适当位置分割消息，优先在换行符处分割，
    以保持消息的可读性。
    
    Args:
        content: 要分割的原始消息内容
        max_length: 单个消息块的最大长度（默认 4000 字符）
    
    Returns:
        分割后的消息块列表
    
    Example:
        >>> chunks = split_for_telegram("长消息内容...", max_length=100)
        >>> for i, chunk in enumerate(chunks, 1):
        ...     print(f"块 {i}: {chunk[:50]}...")
    """
    if not content:
        return []
    
    if len(content) <= max_length:
        return [content]
    
    chunks = []
    
    while len(content) > max_length:
        # 尝试在最后一个换行符处分割
        split_pos = content.rfind('\n', 0, max_length)
        
        if split_pos == -1:
            # 没有找到换行符，在 max_length 处强制分割
            split_pos = max_length
        
        chunk = content[:split_pos]
        chunks.append(chunk)
        content = content[split_pos:]
    
    # 添加剩余的内容
    if content:
        chunks.append(content)
    
    return chunks


# =============================================================================
# CONTEXT CHANGE DETECTION (Phase 3 - Auto Trigger)
# =============================================================================

def hash_content(content: str) -> str:
    """
    Generate a hash for the given content for change detection.
    
    Uses MD5 hash for simplicity and speed. For production use cases
    requiring cryptographic security, consider using hashlib.sha256().
    
    Args:
        content: The text content to hash.
        
    Returns:
        Hexadecimal string representing the content hash.
        
    Example:
        >>> h1 = hash_content("hello world")
        >>> h2 = hash_content("hello world")
        >>> h1 == h2
        True
        >>> h3 = hash_content("hello world!")
        >>> h1 == h3
        False
    """
    import hashlib
    # Normalize content by stripping extra whitespace
    normalized = ' '.join(content.split())
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()


def detect_context_changes(current: str, previous: str) -> bool:
    """
    Detect if context has changed between two content versions.
    
    Compares hashes of current and previous content to determine
    if any changes have occurred.
    
    Args:
        current: The current context content.
        previous: The previous context content.
        
    Returns:
        True if content has changed, False if identical.
        
    Example:
        >>> current = "New content here"
        >>> previous = "Old content here"
        >>> detect_context_changes(current, previous)
        True
        >>> detect_context_changes("same", "same")
        False
    """
    if previous is None or previous == "":
        # No previous context means this is a new context
        return True
    
    current_hash = hash_content(current)
    previous_hash = hash_content(previous)
    
    return current_hash != previous_hash


def load_cached_hash(cache_file: str = HASH_CACHE_FILE) -> Optional[str]:
    """
    Load the previously cached context hash.
    
    Args:
        cache_file: Path to the hash cache file.
        
    Returns:
        The cached hash string, or None if not found/invalid.
    """
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('hash')
    except (json.JSONDecodeError, OSError):
        return None


def save_cached_hash(content_hash: str, context_file: str, cache_file: str = HASH_CACHE_FILE) -> bool:
    """
    Save the current context hash to cache.
    
    Creates the cache directory if it doesn't exist and saves
    the hash along with metadata.
    
    Args:
        content_hash: The hash to cache.
        context_file: The path to the context file this hash represents.
        cache_file: Path to the hash cache file.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        # Ensure cache directory exists
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        
        cache_data = {
            'hash': content_hash,
            'context_file': context_file,
            'timestamp': os.path.getmtime(context_file),
            'cached_at': json.dumps({'seconds': 0}).split(':')[0]  # ISO timestamp placeholder
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        return True
    except OSError:
        return False


# Auto mode constants (defined earlier in the file)
# HASH_CACHE_DIR, HASH_CACHE_FILE, NOTIFICATION_SCRIPT


def check_and_restore_context(
    context_file: str,
    auto_mode: bool = False,
    quiet: bool = False,
    level: str = 'normal'
) -> dict:
    """
    Check for context changes and optionally restore.
    
    This is the main function for Phase 3's auto-trigger mode.
    It checks if the context has changed since last run, and if so,
    can automatically restore the context or wait for user confirmation.
    
    Args:
        context_file: Path to the compressed context file.
        auto_mode: If True, automatically restore on changes without prompting.
        quiet: If True, suppress output except for essential messages.
        level: Report detail level ('minimal', 'normal', 'detailed').
        
    Returns:
        Dictionary with:
        - 'changed': bool - Whether context changed
        - 'restored': bool - Whether restoration was performed
        - 'report': str - The restoration report (if restored)
        - 'auto': bool - Whether auto mode was used
        
    Example:
        >>> result = check_and_restore_context('./context.json', auto_mode=True)
        >>> if result['changed']:
        ...     print(result['report'])
    """
    result = {
        'changed': False,
        'restored': False,
        'report': None,
        'auto': auto_mode
    }
    
    # Load current context
    try:
        context = load_compressed_context(context_file)
    except ContextLoadError:
        if not quiet:
            print(f"{EMOJI['error']} Failed to load context file")
        return result
    
    if context is None:
        if not quiet:
            print(f"{EMOJI['info']} No context file found")
        return result
    
    # Get content string
    if isinstance(context, dict):
        content = context.get('content', str(context))
    else:
        content = str(context)
    
    # Get previous hash
    previous_hash = load_cached_hash()
    current_hash = hash_content(content)
    
    # Check for changes
    if previous_hash is None:
        # First run - context is "new"
        result['changed'] = True
        if not quiet:
            print(f"{EMOJI['info']} First run - context initialized")
    elif current_hash != previous_hash:
        result['changed'] = True
        if not quiet:
            print(f"{EMOJI['watch']} Context changed detected")
    else:
        if not quiet:
            print(f"{EMOJI['success']} No context changes detected")
        return result
    
    # Context has changed - restore it
    if auto_mode:
        # Auto-restore without prompting
        try:
            report = restore_context(context_file, level)
            result['report'] = report
            result['restored'] = True
            
            if not quiet:
                print(f"{EMOJI['auto']} Auto-restoring context...")
                print(report)
            
            # Send notification if configured
            send_context_change_notification(context_file, auto_mode=True)
            
        except Exception as e:
            if not quiet:
                print(f"{EMOJI['error']} Auto-restore failed: {e}")
    else:
        # Require user confirmation (default behavior)
        if not quiet:
            print(f"{EMOJI['bell']} Context has changed. Run with --auto to auto-restore.")
            print(f"{EMOJI['info']} Use --confirm to manually approve restoration.")
        
        # Option to show preview
        preview = restore_context(context_file, 'minimal')
        if not quiet:
            print("\n--- Context Preview ---")
            print(preview[:200] + "..." if len(preview) > 200 else preview)
    
    # Update cache
    save_cached_hash(current_hash, context_file)
    
    return result


def send_context_change_notification(context_file: str, auto_mode: bool = False) -> bool:
    """
    Send notification about context changes.
    
    Attempts to run the notification script if it exists.
    Falls back to simple console notification if script not found.
    
    Args:
        context_file: Path to the context file that changed.
        auto_mode: Whether auto-restore was used.
        
    Returns:
        True if notification was sent, False otherwise.
    """
    if os.path.exists(NOTIFICATION_SCRIPT):
        try:
            import subprocess
            cmd = [
                'python3', NOTIFICATION_SCRIPT,
                '--file', context_file,
                '--auto' if auto_mode else '--confirm'
            ]
            subprocess.run(cmd, capture_output=True, timeout=10)
            return True
        except (subprocess.SubprocessError, OSError):
            pass
    
    # Fallback: simple notification
    print(f"{EMOJI['bell']} Context change notification sent")
    return True


def generate_cron_script() -> str:
    """
    Generate a shell script for cron integration.
    
    Creates a ready-to-use cron entry script that can be
    added to crontab for automated context monitoring.
    
    Returns:
        The generated shell script content.
    """
    script = f'''#!/bin/bash
# Context Restore Auto-Monitor
# Generated by restore_context.py Phase 3
#
# Add to crontab for automatic context monitoring:
# */5 * * * * /home/athur/.openclaw/workspace/skills/context-restore/scripts/auto_context_monitor.sh >> /var/log/context_monitor.log 2>&1
#
# Or run manually:
# bash /home/athur/.openclaw/workspace/skills/context-restore/scripts/auto_context_monitor.sh

SCRIPT_DIR="/home/athur/.openclaw/workspace/skills/context-restore/scripts"
CONTEXT_FILE="/home/athur/.openclaw/workspace/compressed_context/latest_compressed.json"
LOG_FILE="/home/athur/.openclaw/workspace/logs/context_monitor.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Run context check in auto mode
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running context check..."
python3 "$SCRIPT_DIR/restore_context.py" --auto --quiet --level normal

# Check exit code
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Context check completed"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Context check failed"
fi
'''
    return script


def install_cron_job(
    script_path: str = None,
    interval_minutes: int = 5
) -> bool:
    """
    Install a cron job for automatic context monitoring.
    
    Args:
        script_path: Path to the monitoring script.
        interval_minutes: How often to run the check (in minutes).
        
    Returns:
        True if cron job was installed successfully.
    """
    if script_path is None:
        script_path = os.path.join(SCRIPT_DIR, 'auto_context_monitor.sh')
    
    # Generate the cron script
    script_content = generate_cron_script()
    
    try:
        # Write the script
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        
        # Generate crontab entry
        interval = f"*/{interval_minutes}" if interval_minutes < 60 else f"0 */{interval_minutes // 60}"
        cron_entry = f"{interval} * * * * {script_path}"
        
        # Note: Actual cron installation requires user interaction
        # This function prepares the script and returns the cron entry
        print(f"{EMOJI['success']} Cron script created: {script_path}")
        print(f"{EMOJI['info']} To install, run:")
        print(f'  echo "{cron_entry}" >> ~/.crontab')
        print(f'  crontab ~/.crontab')
        
        return True
    except OSError as e:
        print(f"{EMOJI['error']} Failed to create cron script: {e}")
        return False


# =============================================================================
# UNIFIED OUTPUT FORMAT (统一输出格式)
# =============================================================================

def generate_normal_report(content: str) -> str:
    """
    生成统一格式的标准级别报告
    
    根据 SKILL.md 中定义的格式生成报告，
    确保示例输出与实际输出一致。
    使用 CACHED PARSING 提升性能。
    
    Args:
        content: 原始上下文内容
    
    Returns:
        格式化后的报告字符串
    """
    # 解析内容（使用缓存）
    metadata = parse_section_cached('metadata', content)
    operations = parse_section_cached('operations', content)[:5]  # 只取前5个
    projects = parse_section_cached('projects', content)
    
    # 计算压缩率
    original_count = metadata.get('original_count', 'N/A')
    compressed_count = metadata.get('compressed_count', 'N/A')
    compression_ratio = calculate_compression_ratio(
        metadata.get('original_count'),
        metadata.get('compressed_count')
    )
    # 注意：f-string 中 % 是特殊字符，所以这里不加 %
    ratio_value = f"{compression_ratio:.1f}" if compression_ratio else 'N/A'
    
    # 格式化最近操作
    ops_list = '\n'.join([f"- {op}" for op in operations]) if operations else "- 无"
    
    # 格式化项目
    proj_list = []
    for project in projects:
        name = project.get('name', 'Unknown')
        desc = project.get('description', '')
        proj_list.append(f"- **{name}** - {desc}")
    proj_str = '\n'.join(proj_list) if proj_list else "- 无"
    
    # 生成报告 - 在最终字符串中添加 % 符号
    report = f"""✅ **上下文已恢复**

📊 **压缩信息:**
- 原始消息: {original_count}
- 压缩后: {compressed_count}
- 压缩率: {ratio_value}%

🔄 **最近操作:**
{ops_list}

🚀 **项目:**
{proj_str}
"""
    return report


# =============================================================================
# REPORT FORMATTERS
# =============================================================================

def format_minimal_report(content: str) -> str:
    """
    Generate a minimal-level context restoration report.
    
    Creates a compact report containing only essential information:
    - Message count statistics
    - List of key projects
    - Summary of ongoing tasks
    
    This format is useful for quick context checks or status summaries.
    Uses INCREMENTAL PARSING - only parses metadata for speed.
    
    Args:
        content: Raw text content from the compressed context file.
        
    Returns:
        Formatted report as a single string with line separators.
        
    Example:
        >>> report = format_minimal_report(context_text)
        >>> print(report)
        ============================================================
        CONTEXT RESTORE REPORT (Minimal)
        ============================================================
        ...
    """
    lines = []
    
    # INCREMENTAL PARSING: 只解析 metadata（最快路径）
    metadata = parse_section_cached('metadata', content)
    projects = parse_section_cached('projects', content)
    tasks = parse_section_cached('tasks', content)
    
    # Header
    lines.append(SEPARATOR)
    lines.append("CONTEXT RESTORE REPORT (Minimal)")
    lines.append(SEPARATOR)
    
    # Section 1: Context Statistics
    lines.append(f"\n{EMOJI['metadata']} Context Status:")
    if metadata:
        original = metadata.get('original_count', 'N/A')
        compressed = metadata.get('compressed_count', 'N/A')
        lines.append(f"   Messages: {original} → {compressed}")
    else:
        lines.append("   Unable to parse metadata")
    
    # Section 2: Key Projects
    if projects:
        lines.append(f"\n{EMOJI['projects']} Key Projects ({len(projects)})")
        for project in projects:
            lines.append(f"   • {project['name']}")
    
    # Section 3: Ongoing Tasks
    if tasks:
        lines.append(f"\n{EMOJI['tasks']} Ongoing Tasks ({len(tasks)})")
        for task in tasks:
            lines.append(f"   • {task['task']}")
    
    # Footer
    lines.append(f"\n{SEPARATOR}")
    
    return '\n'.join(lines)


def format_normal_report(content: str) -> str:
    """
    Generate a normal-level context restoration report.
    
    Creates a balanced report with comprehensive information:
    - Compression metadata with ratio calculation
    - Recent operations and activities
    - Detailed project descriptions
    - Task status and details
    - Memory section highlights
    
    This is the default report level and provides the most useful
    information for typical use cases.
    Uses CACHED PARSING for performance.
    
    Args:
        content: Raw text content from the compressed context file.
        
    Returns:
        Formatted report as a single string with line separators.
    """
    lines = []
    
    # Parse content using cache
    metadata = parse_section_cached('metadata', content)
    operations = parse_section_cached('operations', content)
    projects = parse_section_cached('projects', content)
    tasks = parse_section_cached('tasks', content)
    highlights = parse_section_cached('highlights', content)
    
    # Header
    lines.append(SEPARATOR)
    lines.append("CONTEXT RESTORE REPORT (Normal)")
    lines.append(SEPARATOR)
    
    # Section 1: Compression Information
    lines.append(f"\n{EMOJI['metadata']} Context Compression Info:")
    if metadata:
        original = metadata.get('original_count', 'N/A')
        compressed = metadata.get('compressed_count', 'N/A')
        timestamp = metadata.get('timestamp', 'Unknown')
        
        lines.append(f"   Original messages: {original}")
        lines.append(f"   Compressed messages: {compressed}")
        lines.append(f"   Timestamp: {timestamp}")
        
        # Calculate and display compression ratio
        ratio = calculate_compression_ratio(
            metadata.get('original_count'),
            metadata.get('compressed_count')
        )
        if ratio is not None:
            lines.append(f"   Compression ratio: {ratio:.1f}%")
    else:
        lines.append("   Unable to parse metadata")
    
    # Section 2: Recent Operations
    if operations:
        lines.append(f"\n{EMOJI['operations']} Recent Operations ({len(operations)})")
        for op in operations:
            lines.append(f"   • {op}")
    
    # Section 3: Key Projects
    if projects:
        lines.append(f"\n{EMOJI['projects']} Key Projects")
        for project in projects:
            lines.append(f"\n   📁 {project['name']}")
            if project.get('description'):
                lines.append(f"      Description: {project['description']}")
            if project.get('status'):
                lines.append(f"      Status: {project['status']}")
    
    # Section 4: Ongoing Tasks
    if tasks:
        lines.append(f"\n{EMOJI['tasks']} Ongoing Tasks")
        for task in tasks:
            lines.append(f"\n   📌 {task['task']}")
            if task.get('status'):
                lines.append(f"      Status: {task['status']}")
            if task.get('detail'):
                lines.append(f"      Detail: {task['detail']}")
    
    # Section 5: Memory Highlights
    if highlights:
        lines.append(f"\n{EMOJI['memory']} MEMORY.md Highlights ({len(highlights)})")
        for highlight in highlights:
            lines.append(f"   {highlight}")
    
    # Footer
    lines.append(f"\n{SEPARATOR}")
    
    return '\n'.join(lines)


def format_detailed_report(content: str) -> str:
    """
    Generate a detailed-level context restoration report.
    
    Creates an exhaustive report containing all extracted information
    plus raw content previews for debugging and verification purposes.
    
    This format includes:
    - Complete metadata as key-value pairs
    - All operations in numbered list format
    - Full project dictionaries
    - Full task dictionaries (JSON format)
    - Memory highlights
    - Raw content preview (first 500 characters)
    
    Uses CACHED PARSING for performance.
    
    Args:
        content: Raw text content from the compressed context file.
        
    Returns:
        Formatted report as a single string with line separators.
    """
    lines = []
    
    # Parse content using cache
    metadata = parse_section_cached('metadata', content)
    operations = parse_section_cached('operations', content)
    projects = parse_section_cached('projects', content)
    tasks = parse_section_cached('tasks', content)
    highlights = parse_section_cached('highlights', content)
    
    # Header
    lines.append(SEPARATOR)
    lines.append("CONTEXT RESTORE REPORT (Detailed)")
    lines.append(SEPARATOR)
    
    # Section 1: Full Metadata
    lines.append(f"\n{EMOJI['metadata']} Context Metadata:")
    if metadata:
        for key, value in sorted(metadata.items()):
            lines.append(f"   {key}: {value}")
    else:
        lines.append("   No metadata found")
    
    # Section 2: All Operations
    if operations:
        lines.append(f"\n{EMOJI['operations']} Recent Operations ({len(operations)}):")
        for i, op in enumerate(operations, 1):
            lines.append(f"   [{i}] {op}")
    else:
        lines.append(f"\n{EMOJI['operations']} Recent Operations: None detected")
    
    # Section 3: Full Project Details
    if projects:
        lines.append(f"\n{EMOJI['projects']} Key Projects ({len(projects)}):")
        for i, project in enumerate(projects, 1):
            lines.append(f"\n   [{i}] {json.dumps(project, indent=6, ensure_ascii=False)}")
    else:
        lines.append(f"\n{EMOJI['projects']} Key Projects: None detected")
    
    # Section 4: Full Task Details
    if tasks:
        lines.append(f"\n{EMOJI['tasks']} Ongoing Tasks ({len(tasks)}):")
        for i, task in enumerate(tasks, 1):
            lines.append(f"\n   [{i}] {json.dumps(task, indent=6, ensure_ascii=False)}")
    else:
        lines.append(f"\n{EMOJI['tasks']} Ongoing Tasks: None detected")
    
    # Section 5: Memory Highlights
    if highlights:
        lines.append(f"\n{EMOJI['memory']} MEMORY.md Highlights ({len(highlights)}):")
        for highlight in highlights:
            lines.append(f"   {highlight}")
    else:
        lines.append(f"\n{EMOJI['memory']} MEMORY.md Highlights: None detected")
    
    # Section 6: Raw Content Preview
    lines.append(f"\n{EMOJI['content']} Raw Content Preview:")
    if content:
        preview_length = 500
        if len(content) > preview_length:
            lines.append(f"   [First {preview_length} chars]:")
            lines.append(f"   {content[:preview_length]}...")
        else:
            lines.append(f"   [Full content ({len(content)} chars)]:")
            lines.append(f"   {content}")
    else:
        lines.append("   No content available")
    
    # Footer
    lines.append(f"\n{SEPARATOR}")
    
    return '\n'.join(lines)


# =============================================================================
# MAIN RESTORE FUNCTION
# =============================================================================

def restore_context(filepath: str, level: str = 'normal') -> str:
    """
    Restore context from compressed file and generate a formatted report.
    
    This is the main entry point for context restoration. It loads the
    compressed context file, extracts relevant information, and generates
    a report at the specified detail level.
    
    Args:
        filepath: Path to the compressed context file.
                  Can be either JSON or plain text format.
        level: Detail level of the report.
               Valid values: 'minimal', 'normal', 'detailed'
               Default: 'normal'
        
    Returns:
        Formatted report string ready for display or output.
        
    Raises:
        ContextLoadError: When context file cannot be loaded.
        ContextParseError: When context content cannot be parsed.
        ValueError: When an invalid level is provided.
        
    Example:
        >>> report = restore_context('./compressed.json', level='normal')
        >>> print(report)
        ============================================================
        CONTEXT RESTORE REPORT (Normal)
        ...
    """
    # Validate level parameter
    valid_levels = ['minimal', 'normal', 'detailed']
    if level not in valid_levels:
        raise ValueError(
            f"无效的级别: {level}。必须是以下之一: {', '.join(valid_levels)}"
        )
    
    # Validate filepath
    if not filepath or not isinstance(filepath, str):
        raise ContextLoadError(
            message=ErrorCode.get_message(ErrorCode.INVALID_INPUT),
            code=ErrorCode.INVALID_INPUT,
            details="文件路径不能为空且必须为字符串"
        )
    
    # Load context file
    try:
        context = load_compressed_context(filepath)
    except ContextLoadError:
        # Re-raise with user-friendly message
        raise
    
    if context is None:
        raise ContextLoadError(
            message=ErrorCode.get_message(ErrorCode.EMPTY_CONTENT),
            code=ErrorCode.EMPTY_CONTENT,
            details=f"无法从 {filepath} 加载上下文"
        )
    
    # Handle both JSON dict and text content
    if isinstance(context, dict):
        # JSON format - extract content field if exists, else stringify
        # Some JSON contexts have a 'content' or 'text' key
        if 'content' in context:
            content = context['content']
        elif 'text' in context:
            content = context['text']
        elif 'data' in context:
            content = context['data']
        else:
            # Convert entire dict to string for analysis
            content = json.dumps(context, indent=2, ensure_ascii=False)
    else:
        content = str(context)
    
    # Validate content
    if not content or not content.strip():
        raise ContextParseError(
            message=ErrorCode.get_message(ErrorCode.EMPTY_CONTENT),
            code=ErrorCode.EMPTY_CONTENT,
            field="content"
        )
    
    # Generate report based on specified level
    if level == 'minimal':
        return format_minimal_report(content)
    elif level == 'detailed':
        return format_detailed_report(content)
    else:
        return format_normal_report(content)


def format_timeline_report(timeline_data: dict, content: str = None) -> str:
    """
    Generate a timeline report showing historical operations.
    
    Creates a formatted timeline view with operations aggregated
    by the specified period (daily/weekly/monthly).
    
    Args:
        timeline_data: Dictionary returned by extract_timeline()
        content: Optional raw content for additional context
        
    Returns:
        Formatted timeline report string
        
    Example:
        >>> timeline = extract_timeline(content, period='weekly')
        >>> report = format_timeline_report(timeline)
        >>> print(report)
        ============================================================
        TIMELINE REPORT (Weekly)
        ============================================================
        ...
    """
    lines = []
    
    period = timeline_data.get('period', 'daily')
    total_days = timeline_data.get('total_days', 0)
    total_ops = timeline_data.get('total_operations', 0)
    timeline = timeline_data.get('timeline', [])
    
    # Header
    period_title = period.capitalize()
    lines.append(SEPARATOR)
    lines.append(f"TIMELINE REPORT ({period_title} View)")
    lines.append(SEPARATOR)
    
    # Summary
    lines.append(f"\n📊 Summary:")
    lines.append(f"   Period: {period_title}")
    lines.append(f"   Days covered: {total_days}")
    lines.append(f"   Total operations: {total_ops}")
    lines.append(f"   Time periods: {len(timeline)}")
    
    # Timeline entries
    if timeline:
        lines.append(f"\n📅 Timeline ({len(timeline)} entries):")
        lines.append(SECTION_SEPARATOR)
        
        for i, entry in enumerate(timeline, 1):
            period_label = entry.get('period_label', 'Unknown')
            date_range = entry.get('date_range')
            ops_count = entry.get('operations_count', 0)
            projects = entry.get('projects', [])
            highlights = entry.get('highlights', [])
            
            lines.append(f"\n[{i}] {period_label}")
            if date_range:
                lines.append(f"    📆 Period: {date_range}")
            lines.append(f"    🔄 Operations: {ops_count}")
            
            if projects:
                proj_str = ', '.join(projects[:3])
                if len(projects) > 3:
                    proj_str += f" (+{len(projects) - 3} more)"
                lines.append(f"    🚀 Projects: {proj_str}")
            
            if highlights:
                lines.append(f"    ✨ Highlights:")
                for hl in highlights[:2]:
                    lines.append(f"       • {hl}")
            
            lines.append(SECTION_SEPARATOR)
    else:
        lines.append(f"\n📭 No timeline data available")
    
    # Footer
    lines.append(f"\n{SEPARATOR}")
    
    return '\n'.join(lines)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def create_arg_parser() -> argparse.ArgumentParser:
    """
    Create and configure the command-line argument parser.
    
    Sets up all arguments, defaults, and help text for the CLI interface.
    
    Returns:
        Configured argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog='restore_context.py',
        description=(
            'Context Restore Script\n'
            '======================\n\n'
            'Restore compressed context from latest_compressed.json and\n'
            'generate formatted reports at different detail levels.\n\n'
            'Examples:\n'
            '  python3 restore_context.py                    # Normal report\n'
            '  python3 restore_context.py --level minimal     # Brief summary\n'
            '  python3 restore_context.py --level detailed    # Full details\n'
            '  python3 restore_context.py --output report.md  # Save to file'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Report Levels:\n'
            '  minimal   - Basic info: messages, projects, tasks count\n'
            '  normal    - Full details with descriptions (default)\n'
            '  detailed  - Complete dump with raw content preview'
        )
    )
    
    parser.add_argument(
        '--file',
        type=str,
        default=DEFAULT_CONTEXT_FILE,
        help=(
            f'Path to compressed context file. '
            f'Default: {DEFAULT_CONTEXT_FILE}'
        )
    )
    
    parser.add_argument(
        '--level',
        type=str,
        choices=['minimal', 'normal', 'detailed'],
        default='normal',
        help=(
            'Detail level of the report. '
            'Options: minimal, normal (default), detailed'
        )
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help=(
            'Output file path. If specified, the report will be '
            'written to this file instead of stdout.'
        )
    )
    
    parser.add_argument(
        '--confirm',
        action='store_true',
        default=False,
        help=(
            'Request user confirmation before proceeding. '
            'The script will print the context report and ask '
            'for confirmation before continuing.'
        )
    )
    
    parser.add_argument(
        '--telegram',
        action='store_true',
        default=False,
        help=(
            'Optimize output for Telegram. '
            'Automatically splits long messages into chunks '
            'that fit within Telegram message limits (4000 chars).'
        )
    )
    
    parser.add_argument(
        '--platform',
        type=str,
        choices=VALID_PLATFORMS,
        default=None,
        help=(
            'Target platform for output formatting. '
            f'Options: {", ".join(VALID_PLATFORMS)} (default: auto-detect from context). '
            'Automatically applies platform-specific formatting and chunking.'
        )
    )
    
    parser.add_argument(
        '--auto-detect-platform',
        action='store_true',
        default=True,
        help=(
            'Auto-detect platform from context content. '
            'Enabled by default. Use --platform to override.'
        )
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        default=False,
        help=(
            'Output structured summary in JSON format. '
            'Useful for programmatic access by other skills.'
        )
    )
    
    parser.add_argument(
        '--timeline',
        action='store_true',
        default=False,
        help=(
            'Generate a timeline view of historical operations. '
            'Use --period to specify aggregation level (daily/weekly/monthly).'
        )
    )
    
    parser.add_argument(
        '--period', '-p',
        type=str,
        choices=['daily', 'weekly', 'monthly'],
        default='daily',
        help=(
            'Time period for timeline aggregation. '
            'Options: daily (default), weekly, monthly. '
            'Used with --timeline flag.'
        )
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help=(
            'Number of days to include in timeline view (default: 30). '
            'Used with --timeline flag.'
        )
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.4.0'
    )
    
    parser.add_argument(
        '--since',
        type=str,
        default=None,
        help='Only include operations since this date (YYYY-MM-DD format). '
             'Used with --summary for incremental context restoration.'
    )
    
    # 过滤恢复参数 (Phase 3)
    parser.add_argument(
        '--filter', '-f',
        type=str,
        default=None,
        help='Filter context to only include content matching the pattern. '
             'Example: --filter "Hermes Plan" or -f "task:"'
    )
    
    parser.add_argument(
        '--projects-only',
        action='store_true',
        default=False,
        help='Only show project-related context. '
             'Extracts and displays project information from the context.'
    )
    
    parser.add_argument(
        '--diff',
        type=str,
        nargs=2,
        metavar=('OLD_FILE', 'NEW_FILE'),
        default=None,
        help='Compare two context files and show differences. '
             'Usage: --diff yesterday.json latest.json'
    )
    
    parser.add_argument(
        '--diff-output',
        type=str,
        default=None,
        help='Output file for diff report. Used with --diff.'
    )
    
    # Phase 3: Auto trigger arguments
    parser.add_argument(
        '--auto',
        action='store_true',
        default=False,
        help=(
            'Auto mode: Automatically detect context changes and restore. '
            'When changes are detected, the context is restored without prompting. '
            'Use with --quiet for cron-compatible operation.'
        )
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        default=False,
        help=(
            'Quiet mode: Suppress non-essential output. '
            'Only essential messages and errors will be shown. '
            'Designed for use with --auto in cron jobs.'
        )
    )
    
    parser.add_argument(
        '--install-cron',
        action='store_true',
        default=False,
        help=(
            'Generate and install cron job for automatic context monitoring. '
            'Creates a monitoring script and shows crontab entry commands.'
        )
    )
    
    parser.add_argument(
        '--cron-interval',
        type=int,
        default=5,
        help='Cron interval in minutes for auto-monitoring. Default: 5. '
             'Used with --install-cron.'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        default=False,
        help=(
            'Check for context changes without restoring. '
            'Returns exit code 0 if no changes, 1 if changes detected. '
            'Useful for external monitoring scripts.'
        )
    )
    
    return parser


def _get_target_platform(args) -> str:
    """
    Determine the target platform from command-line arguments
    
    Priority:
    1. --platform explicit value
    2. --telegram flag (backwards compatibility)
    3. Auto-detect from context
    
    Args:
        args: Command-line arguments namespace
        
    Returns:
        Platform identifier string
    """
    # Priority 1: Explicit --platform
    if args.platform and args.platform in VALID_PLATFORMS:
        return args.platform
    
    # Priority 2: --telegram flag (backwards compatibility)
    if args.telegram:
        return PLATFORM_TELEGRAM
    
    # Priority 3: Auto-detect from context if enabled
    if getattr(args, 'auto_detect_platform', True):
        # Load context to detect platform
        try:
            context = load_compressed_context(args.file)
            if context:
                if isinstance(context, dict):
                    content = context.get('content', str(context))
                else:
                    content = str(context)
                detected = detect_platform_from_context(content)
                if detected != PLATFORM_UNKNOWN:
                    return detected
        except ContextLoadError:
            pass
    
    return PLATFORM_UNKNOWN


def main() -> int:
    """
    Main entry point for the script.
    
    Parses command-line arguments, generates the context restoration
    report, and handles output (stdout or file).
    
    Returns:
        Exit code: 0 for success, 1 for errors.
    """
    # Create argument parser
    parser = create_arg_parser()
    args = parser.parse_args()
    
    try:
        # Phase 3: Handle --install-cron
        if args.install_cron:
            script_path = os.path.join(SCRIPT_DIR, 'auto_context_monitor.sh')
            if install_cron_job(script_path, args.cron_interval):
                return 0
            else:
                return 1
        
        # Phase 3: Handle --check-only
        if args.check_only:
            try:
                context = load_compressed_context(args.file)
            except ContextLoadError:
                return 1
            
            if context is None:
                return 1
            
            if isinstance(context, dict):
                content = context.get('content', str(context))
            else:
                content = str(context)
            
            previous_hash = load_cached_hash()
            current_hash = hash_content(content)
            
            if previous_hash is None:
                if not args.quiet:
                    print(f"{EMOJI['info']} First run - no previous context")
                return 1  # Changes detected on first run
            elif current_hash != previous_hash:
                if not args.quiet:
                    print(f"{EMOJI['watch']} Context changed detected")
                return 1  # Changes detected
            else:
                if not args.quiet:
                    print(f"{EMOJI['success']} No changes detected")
                return 0  # No changes
        
        # Phase 3: Handle --auto mode
        if args.auto:
            result = check_and_restore_context(
                context_file=args.file,
                auto_mode=True,
                quiet=args.quiet,
                level=args.level
            )
            
            if result['changed'] and result['restored']:
                return 0
            elif result['changed'] and not result['restored']:
                if not args.quiet:
                    print(f"{EMOJI['info']} Context changed but auto-restore skipped")
                return 0
            else:
                return 0  # No changes, success
        
        # Handle --diff flag (context comparison)
        if args.diff:
            old_file, new_file = args.diff[0], args.diff[1]
            
            # Compare contexts
            diff = compare_contexts(old_file, new_file)
            
            # Generate diff report
            report = format_diff_report(diff, old_file, new_file)
            
            # Output to file or stdout
            if args.diff_output:
                try:
                    with open(args.diff_output, 'w', encoding='utf-8') as f:
                        f.write(report)
                        f.write('\n')
                    print(f"{EMOJI['success']} Diff report saved to: {args.diff_output}")
                except PermissionError:
                    print(f"{EMOJI['error']} Error: Permission denied writing to: {args.diff_output}")
                    return 1
                except OSError as e:
                    print(f"{EMOJI['error']} Error writing to file {args.diff_output}: {e}")
                    return 1
            else:
                print(report)
            
            return 0
        
        # Handle --summary flag (JSON output)
        if args.summary:
            summary = get_context_summary(args.file, period=args.period, days=args.days)
            
            # Filter by --since date if specified
            if args.since and summary.get('success'):
                since_date = args.since
                filtered_timeline = [
                    day for day in summary.get('timeline', [])
                    if day.get('date', 'unknown') >= since_date
                ]
                summary['timeline'] = filtered_timeline
                summary['filtered_since'] = since_date
            
            # Phase 3: Apply filter to summary
            if args.filter and summary.get('success'):
                filter_pattern = args.filter.lower()
                # Filter projects
                summary['projects'] = [
                    p for p in summary.get('projects', [])
                    if filter_pattern in p.get('name', '').lower()
                    or filter_pattern in p.get('description', '').lower()
                ]
                # Filter operations
                summary['operations'] = [
                    op for op in summary.get('operations', [])
                    if filter_pattern in op.lower()
                ]
                # Filter tasks
                summary['tasks'] = [
                    t for t in summary.get('tasks', [])
                    if filter_pattern in t.get('task', '').lower()
                    or filter_pattern in t.get('detail', '').lower()
                ]
                summary['filter_pattern'] = args.filter
            
            # Phase 3: Projects-only mode
            if args.projects_only and summary.get('success'):
                projects = summary.get('projects', [])
                summary = {
                    'success': True,
                    'filter_mode': 'projects-only',
                    'projects': projects,
                    'project_count': len(projects)
                }
            
            # Determine target platform
            target_platform = _get_target_platform(args)
            
            # Output JSON
            output_content = json.dumps(summary, indent=2, ensure_ascii=False)
            
            # Apply platform-specific formatting if needed
            if target_platform and target_platform != PLATFORM_UNKNOWN:
                output_content = format_for_platform(output_content, target_platform)
            
            # Handle platform-specific chunking for output
            if target_platform:
                chunks = split_for_platform(output_content, target_platform)
                for i, chunk in enumerate(chunks, 1):
                    if len(chunks) > 1:
                        print(f"[{i}/{len(chunks)}]")
                    print(chunk)
            elif args.output:
                try:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(output_content)
                        f.write('\n')
                    print(f"{EMOJI['success']} Summary saved to: {args.output}")
                except PermissionError:
                    print(f"{EMOJI['error']} Error: Permission denied writing to: {args.output}")
                    return 1
                except OSError as e:
                    print(f"{EMOJI['error']} Error writing to file {args.output}: {e}")
                    return 1
            else:
                print(output_content)
            
            return 0
        
        # Handle --timeline flag (timeline view)
        if args.timeline:
            try:
                # Validate period
                if args.period not in VALID_PERIODS:
                    print(f"{EMOJI['error']} Invalid period: {args.period}")
                    print(f"Valid options: {', '.join(VALID_PERIODS)}")
                    return 1
                
                # Load context and extract timeline
                context = load_compressed_context(args.file)
                if context is None:
                    print(f"{EMOJI['error']} Could not load context file")
                    return 1
                
                # Extract content from context
                if isinstance(context, dict):
                    if 'content' in context:
                        content = context['content']
                    elif 'text' in context:
                        content = context['text']
                    elif 'data' in context:
                        content = context['data']
                    else:
                        content = json.dumps(context, indent=2, ensure_ascii=False)
                else:
                    content = str(context)
                
                # Extract timeline with specified period
                timeline_data = extract_timeline(content, period=args.period, days=args.days)
                
                # Generate timeline report
                report = format_timeline_report(timeline_data, content)
                
                # Determine target platform and apply formatting
                target_platform = _get_target_platform(args)
                
                # Apply platform-specific formatting
                if target_platform and target_platform != PLATFORM_UNKNOWN:
                    report = format_for_platform(report, target_platform)
                
                # Handle platform-specific message chunking
                if target_platform:
                    chunks = split_for_platform(report, target_platform)
                    for i, chunk in enumerate(chunks, 1):
                        if len(chunks) > 1:
                            print(f"[{i}/{len(chunks)}]")
                        print(chunk)
                elif args.output:
                    try:
                        with open(args.output, 'w', encoding='utf-8') as f:
                            f.write(report)
                            f.write('\n')
                        print(f"{EMOJI['success']} Timeline report saved to: {args.output}")
                    except PermissionError:
                        print(f"{EMOJI['error']} Error: Permission denied writing to: {args.output}")
                        return 1
                    except OSError as e:
                        print(f"{EMOJI['error']} Error writing to file {args.output}: {e}")
                        return 1
                else:
                    print(report)
                
                return 0
                
            except ValueError as e:
                print(f"{EMOJI['error']} Parameter error: {e}")
                return 1
            except Exception as e:
                print(f"{EMOJI['error']} Error generating timeline: {e}")
                return 1
        
        # Generate report (normal text output)
        report = restore_context(args.file, args.level)
        
        # Phase 3: 应用过滤 (如果指定了 --filter)
        if args.filter:
            report = filter_context(report, args.filter)
        
        # Phase 3: 只显示项目 (如果指定了 --projects-only)
        if args.projects_only:
            report = filter_projects_only(report)
        
        # Check for error in report generation
        if report.startswith(EMOJI['error']):
            print(report)
            return 1
        
        # Determine target platform and apply formatting
        target_platform = _get_target_platform(args)
        
        # Apply platform-specific formatting
        if target_platform and target_platform != PLATFORM_UNKNOWN:
            report = format_for_platform(report, target_platform)
        
        # Handle platform-specific message chunking
        if target_platform:
            chunks = split_for_platform(report, target_platform)
            for i, chunk in enumerate(chunks, 1):
                if len(chunks) > 1:
                    print(f"[{i}/{len(chunks)}]")
                print(chunk)
            return 0
        
        # Handle user confirmation process (添加用户确认流程)
        if args.confirm:
            print(report)
            print("\n" + SEPARATOR)
            print("请确认是否继续？ (y/n)")
            print(SEPARATOR)
            
            try:
                # Try to get input (may not work in non-interactive mode)
                confirmation = input().strip().lower()
            except (EOFError, OSError):
                # Non-interactive mode, assume confirmed
                confirmation = 'y'
            
            if confirmation not in ['y', 'yes', '是', '确认']:
                print(f"{EMOJI['info']} Operation cancelled by user.")
                return 0
            
            print(f"{EMOJI['success']} Context confirmed. Proceeding with restored session.")
        
        # Output to file or stdout
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(report)
                    f.write('\n')
                print(f"{EMOJI['success']} Report saved to: {args.output}")
            except PermissionError:
                print(f"{EMOJI['error']} Error: Permission denied writing to: {args.output}")
                return 1
            except OSError as e:
                print(f"{EMOJI['error']} Error writing to file {args.output}: {e}")
                return 1
        else:
            print(report)
        
        return 0
        
    except ValueError as e:
        print(f"{EMOJI['error']} 参数错误: {e}")
        return 1
    except ContextLoadError as e:
        print(f"{EMOJI['error']} {e.message}")
        return 1
    except ContextParseError as e:
        print(f"{EMOJI['error']} {e.message}")
        return 1
    except KeyboardInterrupt:
        print(f"\n{EMOJI['info']} 操作已取消")
        return 130
    except Exception as e:
        print(f"{EMOJI['error']} 发生未知错误: {e}")
        return 1


# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    """
    Script execution entry point.
    
    Runs main() and exits with the returned status code.
    """
    sys.exit(main())
