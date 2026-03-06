#!/usr/bin/env python3
"""
输出管理器 — 缓冲中间输出，只在结束时输出摘要

解决问题：
    脚本中大量 print(..., flush=True) 会导致 agent 将每次输出作为独立回复发送给用户。
    OutputManager 将中间输出重定向到日志文件，只在脚本结束时输出一段简洁摘要到 stdout。

用法：
    from output_manager import OutputManager

    out = OutputManager(verbose=False)  # 默认静默模式
    out.print("步骤 1: ...")            # 写入日志文件，不打印到 stdout
    out.print("步骤 2: ...")

    # 脚本结束时输出摘要
    out.summary(
        success=True,
        title="歌曲创建完成",
        details={"标题": "xxx", "文件": ["/path/to/file.mp3"]},
    )
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path


class OutputManager:
    """
    控制脚本输出行为：
    - verbose=True  → 保持原有行为（实时 print 到 stdout + 写日志）
    - verbose=False → 静默模式（只写日志，stdout 不输出中间过程，结束时输出摘要）
    """

    def __init__(self, log_prefix: str = "suno", verbose: bool = False, log_dir: str = "/tmp"):
        self.verbose = verbose
        self._buffer = []

        # 创建带时间戳的日志文件
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = os.path.join(log_dir, f"{log_prefix}_{ts}.log")
        Path(self.log_path).parent.mkdir(parents=True, exist_ok=True)
        self._log_file = open(self.log_path, "w", encoding="utf-8")

    def print(self, *args, **kwargs):
        """替代内置 print()，根据模式决定输出目标"""
        # 始终写入日志文件
        msg = " ".join(str(a) for a in args)
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_file.write(f"[{ts}] {msg}\n")
        self._log_file.flush()

        # 缓存消息
        self._buffer.append(msg)

        # verbose 模式同时输出到 stdout
        if self.verbose:
            kwargs.setdefault("flush", True)
            print(*args, **kwargs)

    def summary(self, success: bool, title: str, details: dict = None):
        """
        在脚本结尾输出唯一一次结果摘要到 stdout。

        Args:
            success: 是否成功
            title: 摘要标题, e.g. "歌曲创建完成"
            details: 键值对字典, e.g. {"标题": "...", "文件": [...]}
        """
        icon = "✅" if success else "❌"
        lines = [f"\n{icon} {title}"]

        if details:
            for key, value in details.items():
                if isinstance(value, list):
                    lines.append(f"   {key}:")
                    for item in value:
                        lines.append(f"     📁 {item}")
                else:
                    lines.append(f"   {key}: {value}")

        lines.append(f"   📋 详细日志: {self.log_path}")

        output = "\n".join(lines)
        print(output, flush=True)

        # 也写入日志
        self._log_file.write(f"\n{'='*60}\n{output}\n{'='*60}\n")
        self._log_file.flush()

    def close(self):
        """关闭日志文件"""
        if self._log_file and not self._log_file.closed:
            self._log_file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
