#!/usr/bin/env python3
"""
Layer 3: Done Checker
- 检查任务的完成条件 (done_when)
- 支持三种条件类型: files, files_glob, commands
"""

import glob as glob_module
import logging
import os
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# 命令执行超时（秒）
COMMAND_TIMEOUT = 60


@dataclass
class CheckResult:
    """单个检查结果"""
    check_type: str  # "file", "glob", "command"
    description: str
    passed: bool
    details: str = ""


@dataclass
class DoneResult:
    """完成条件检测结果"""
    passed: bool
    results: List[CheckResult] = field(default_factory=list)
    summary: str = ""
    
    def get_failed_items(self) -> List[CheckResult]:
        """获取所有失败的检查项"""
        return [r for r in self.results if not r.passed]


def check_file_condition(
    file_spec: Dict[str, Any],
    project_dir: str,
    default_min_size: int = 1
) -> CheckResult:
    """
    检查单个文件条件
    
    Args:
        file_spec: 文件规格 {path, min_size?, contains?}
        project_dir: 项目目录
        default_min_size: 默认最小文件大小
    
    Returns:
        CheckResult
    """
    rel_path = file_spec.get("path", "")
    full_path = os.path.join(project_dir, rel_path)
    min_size = file_spec.get("min_size", default_min_size)
    contains = file_spec.get("contains", [])
    
    # 检查文件是否存在
    if not os.path.exists(full_path):
        return CheckResult(
            check_type="file",
            description=f"文件: {rel_path}",
            passed=False,
            details=f"文件不存在"
        )
    
    # 检查文件大小
    try:
        file_size = os.path.getsize(full_path)
    except OSError as e:
        return CheckResult(
            check_type="file",
            description=f"文件: {rel_path}",
            passed=False,
            details=f"无法读取文件大小: {e}"
        )
    
    if file_size < min_size:
        return CheckResult(
            check_type="file",
            description=f"文件: {rel_path}",
            passed=False,
            details=f"文件大小 {file_size} 字节 < 最小要求 {min_size} 字节"
        )
    
    # 检查文件内容（如果指定了 contains）
    if contains:
        try:
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            missing_keywords = [kw for kw in contains if kw not in content]
            if missing_keywords:
                return CheckResult(
                    check_type="file",
                    description=f"文件: {rel_path}",
                    passed=False,
                    details=f"缺少关键词: {', '.join(missing_keywords)}"
                )
        except IOError as e:
            return CheckResult(
                check_type="file",
                description=f"文件: {rel_path}",
                passed=False,
                details=f"无法读取文件内容: {e}"
            )
    
    return CheckResult(
        check_type="file",
        description=f"文件: {rel_path}",
        passed=True,
        details=f"存在，大小 {file_size} 字节"
    )


def check_glob_condition(
    glob_spec: Dict[str, Any],
    project_dir: str,
    default_min_size: int = 1
) -> CheckResult:
    """
    检查文件 glob 模式条件
    
    Args:
        glob_spec: glob 规格 {pattern, min_count?, min_file_size?}
        project_dir: 项目目录
        default_min_size: 默认最小文件大小
    
    Returns:
        CheckResult
    """
    pattern = glob_spec.get("pattern", "")
    min_count = glob_spec.get("min_count", 1)
    min_file_size = glob_spec.get("min_file_size", default_min_size)
    
    # 构建完整的 glob 路径
    full_pattern = os.path.join(project_dir, pattern)
    
    # 查找匹配文件
    matches = glob_module.glob(full_pattern, recursive=True)
    
    # 过滤掉目录和小于 min_file_size 的文件
    valid_files = []
    for match in matches:
        if os.path.isfile(match):
            try:
                if os.path.getsize(match) >= min_file_size:
                    valid_files.append(match)
            except OSError:
                continue
    
    if len(valid_files) < min_count:
        return CheckResult(
            check_type="glob",
            description=f"Glob: {pattern}",
            passed=False,
            details=f"找到 {len(valid_files)} 个文件 < 要求的 {min_count} 个"
        )
    
    return CheckResult(
        check_type="glob",
        description=f"Glob: {pattern}",
        passed=True,
        details=f"找到 {len(valid_files)} 个文件 >= {min_count}"
    )


def check_command_condition(
    cmd_spec: Dict[str, Any],
    project_dir: str
) -> CheckResult:
    """
    检查命令执行条件
    
    Args:
        cmd_spec: 命令规格 {cmd, expect_exit?}
        project_dir: 项目目录
    
    Returns:
        CheckResult
    """
    cmd = cmd_spec.get("cmd", "")
    expect_exit = cmd_spec.get("expect_exit", 0)
    
    # 替换 {project_dir} 占位符
    cmd = cmd.replace("{project_dir}", project_dir)
    
    # 显示简化的命令（用于日志）
    short_cmd = cmd if len(cmd) <= 50 else cmd[:47] + "..."
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            timeout=COMMAND_TIMEOUT,
            cwd=project_dir
        )
        
        if result.returncode == expect_exit:
            return CheckResult(
                check_type="command",
                description=f"命令: {short_cmd}",
                passed=True,
                details=f"exit code = {result.returncode}"
            )
        else:
            # 获取 stderr 的前 200 字符
            stderr = result.stderr.decode('utf-8', errors='replace')[:200]
            return CheckResult(
                check_type="command",
                description=f"命令: {short_cmd}",
                passed=False,
                details=f"exit code = {result.returncode}，期望 {expect_exit}。错误: {stderr}"
            )
    
    except subprocess.TimeoutExpired:
        return CheckResult(
            check_type="command",
            description=f"命令: {short_cmd}",
            passed=False,
            details=f"超时（>{COMMAND_TIMEOUT}秒）"
        )
    except Exception as e:
        return CheckResult(
            check_type="command",
            description=f"命令: {short_cmd}",
            passed=False,
            details=f"执行失败: {e}"
        )


def check_done_conditions(
    done_when: Optional[Dict[str, Any]],
    project_dir: str,
    default_min_size: int = 100
) -> DoneResult:
    """
    检查任务完成条件
    
    Args:
        done_when: 完成条件配置 {files?, files_glob?, commands?}
        project_dir: 项目目录
        default_min_size: 默认最小文件大小
    
    Returns:
        DoneResult 包含所有检查结果
    """
    if not done_when:
        # 没有完成条件，默认通过
        return DoneResult(
            passed=True,
            results=[],
            summary="无完成条件"
        )
    
    results: List[CheckResult] = []
    
    # 1. 检查指定文件
    for file_spec in done_when.get("files", []):
        result = check_file_condition(file_spec, project_dir, default_min_size)
        results.append(result)
        logger.debug(f"文件检查: {result.description} -> {result.passed}")
    
    # 2. 检查文件 glob
    for glob_spec in done_when.get("files_glob", []):
        result = check_glob_condition(glob_spec, project_dir, default_min_size)
        results.append(result)
        logger.debug(f"Glob检查: {result.description} -> {result.passed}")
    
    # 3. 执行验证命令
    for cmd_spec in done_when.get("commands", []):
        result = check_command_condition(cmd_spec, project_dir)
        results.append(result)
        logger.debug(f"命令检查: {result.description} -> {result.passed}")
    
    # 汇总结果
    all_passed = all(r.passed for r in results)
    
    if all_passed:
        summary = f"全部 {len(results)} 项检查通过"
    else:
        failed = [r for r in results if not r.passed]
        summary = f"{len(failed)}/{len(results)} 项检查失败"
    
    return DoneResult(
        passed=all_passed,
        results=results,
        summary=summary
    )


def format_done_result(result: DoneResult) -> str:
    """
    格式化 DoneResult 为人类可读的字符串
    
    Args:
        result: DoneResult 对象
    
    Returns:
        格式化的字符串
    """
    lines = [f"完成条件检测: {'✅ 全部通过' if result.passed else '❌ 有失败项'}"]
    lines.append(f"摘要: {result.summary}")
    
    if result.results:
        lines.append("")
        lines.append("详细结果:")
        for r in result.results:
            status = "✅" if r.passed else "❌"
            lines.append(f"  {status} [{r.check_type}] {r.description}")
            if r.details:
                lines.append(f"      {r.details}")
    
    return "\n".join(lines)
