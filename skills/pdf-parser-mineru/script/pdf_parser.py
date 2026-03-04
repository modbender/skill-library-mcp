#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Parser Skill - 基于 MinerU 的 PDF 解析工具

支持将 PDF 转换为 Markdown 或 JSON 格式
"""

import json
import os
import re
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


class PDFParser:
    """PDF 解析器封装类"""

    def __init__(self):
        self.mineru_cmd = self._find_mineru()

    def _find_mineru(self) -> str:
        """查找 mineru 命令"""
        # 优先使用 mineru 命令
        if shutil.which("mineru"):
            return "mineru"
        if os.path.exists('/home/research/miniconda3/bin/mineru'):
            return '/home/research/miniconda3/bin/mineru'
        # 检查是否在虚拟环境中
        venv_path = sys.prefix
        mineru_in_venv = os.path.join(venv_path, "bin", "mineru")
        if os.path.exists(mineru_in_venv):
            return mineru_in_venv

        raise RuntimeError(
            "未找到 mineru 命令。请先安装 MinerU:\n"
            "pip install --upgrade pip\n"
            "pip install uv\n"
            "uv pip install -U 'mineru[all]'"
        )

    def _build_command(
        self,
        tool_name: str,
        file_path: str,
        output_dir: str,
        backend: str = "hybrid-auto-engine",
        language: Optional[str] = None,
        enable_formula: bool = True,
        enable_table: bool = True,
        start_page: int = 0,
        end_page: int = -1,
    ) -> list:
        """构建 mineru 命令"""
        cmd = [
            self.mineru_cmd,
            "-p", file_path,
            "-o", output_dir,
            "-b", backend,
        ]

        # 添加语言参数
        if language:
            cmd.extend(["-l", language])

        # 添加公式开关
        cmd.extend(["-f", str(enable_formula).lower()])

        # 添加表格开关
        cmd.extend(["-t", str(enable_table).lower()])

        # 添加设备参数（强制使用 CPU，避免 MPS 限制）
        cmd.extend(["-d", "cpu"])

        # 添加页码范围
        if end_page != -1:
            cmd.extend(["-s", str(start_page)])
            cmd.extend(["-e", str(end_page)])

        return cmd

    def parse_to_markdown(
        self,
        file_path: str,
        output_dir: str,
        backend: str = "hybrid-auto-engine",
        language: Optional[str] = None,
        enable_formula: bool = True,
        enable_table: bool = True,
        start_page: int = 0,
        end_page: int = -1,
    ) -> Dict[str, Any]:
        """
        将 PDF 解析为 Markdown 格式

        Args:
            file_path: PDF 文件路径
            output_dir: 输出目录
            backend: 解析后端
            language: OCR 语言
            enable_formula: 是否启用公式识别
            enable_table: 是否启用表格提取
            start_page: 起始页码
            end_page: 结束页码

        Returns:
            包含解析结果的字典
        """
        # 验证输入文件
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"输入文件不存在: {file_path}"
            }

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 构建命令
        cmd = self._build_command(
            "pdf_to_markdown",
            file_path,
            output_dir,
            backend,
            language,
            enable_formula,
            enable_table,
            start_page,
            end_page,
        )

        try:
            # 设置环境变量以强制使用 CPU（避免 MPS 设备限制）
            env = os.environ.copy()
            env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
            env["MPS_DEVICE"] = "cpu"

            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 1小时超时
                env=env,
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"MinerU 执行失败: {result.stderr}",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }

            # 查找输出的 markdown 文件
            output_files = list(Path(output_dir).rglob("*.md"))
            if not output_files:
                return {
                    "success": False,
                    "error": "未找到输出的 Markdown 文件"
                }

            # 读取第一个 markdown 文件
            md_file = output_files[0]
            with open(md_file, "r", encoding="utf-8") as f:
                md_content = f.read()

            # 统计信息
            images = list(Path(output_dir).rglob("*.png")) + list(Path(output_dir).rglob("*.jpg"))
            tables = len(re.findall(r"\\|.*\\|", md_content))
            formula_count = len(re.findall(r"\\$.*\\$|\\$\\$.*\\$\\$", md_content))

            return {
                "success": True,
                "output_path": str(md_file),
                "output_dir": output_dir,
                "markdown_content": md_content,
                "images": [str(img) for img in images],
                "tables": tables,
                "formula_count": formula_count,
                "file_size": os.path.getsize(file_path),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "解析超时（超过1小时），请尝试减少页数或使用更快的后端"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"解析过程中发生错误: {str(e)}",
                "exception": str(e),
            }

    def parse_to_json(
        self,
        file_path: str,
        output_dir: str,
        backend: str = "hybrid-auto-engine",
        language: Optional[str] = None,
        enable_formula: bool = True,
        enable_table: bool = True,
        start_page: int = 0,
        end_page: int = -1,
    ) -> Dict[str, Any]:
        """
        将 PDF 解析为 JSON 格式

        Args:
            file_path: PDF 文件路径
            output_dir: 输出目录
            backend: 解析后端
            language: OCR 语言
            enable_formula: 是否启用公式识别
            enable_table: 是否启用表格提取
            start_page: 起始页码
            end_page: 结束页码

        Returns:
            包含解析结果的字典
        """
        # 验证输入文件
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"输入文件不存在: {file_path}"
            }

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 构建命令
        cmd = self._build_command(
            "pdf_to_json",
            file_path,
            output_dir,
            backend,
            language,
            enable_formula,
            enable_table,
            start_page,
            end_page,
        )

        try:
            # 设置环境变量以强制使用 CPU（避免 MPS 设备限制）
            env = os.environ.copy()
            env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
            env["MPS_DEVICE"] = "cpu"

            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 1小时超时
                env=env,
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"MinerU 执行失败: {result.stderr}",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }

            # 查找输出的 JSON 文件
            output_files = list(Path(output_dir).rglob("*.json"))
            if not output_files:
                # 如果没有 JSON 文件，尝试读取其他文件
                all_files = list(Path(output_dir).rglob("*"))
                return {
                    "success": False,
                    "error": f"未找到输出的 JSON 文件。找到的文件: {[str(f) for f in all_files]}"
                }

            # 读取第一个 JSON 文件
            json_file = output_files[0]
            with open(json_file, "r", encoding="utf-8") as f:
                json_content = json.load(f)

            return {
                "success": True,
                "output_path": str(json_file),
                "output_dir": output_dir,
                "json_content": json_content,
                "file_size": os.path.getsize(file_path),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "解析超时（超过1小时），请尝试减少页数或使用更快的后端"
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON 解析失败: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"解析过程中发生错误: {str(e)}",
                "exception": str(e),
            }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "缺少参数。使用方法: python pdf_parser.py '{\"name\": \"tool_name\", \"arguments\": {...}}'"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    try:
        # 解析输入参数
        input_data = json.loads(sys.argv[1])
        tool_name = input_data.get("name")
        args = input_data.get("arguments", {})

        # 创建解析器
        parser = PDFParser()

        # 根据工具名称调用相应方法
        if tool_name == "pdf_to_markdown":
            result = parser.parse_to_markdown(**args)
        elif tool_name == "pdf_to_json":
            result = parser.parse_to_json(**args)
        else:
            result = {
                "success": False,
                "error": f"未知的工具名称: {tool_name}。支持的工具: pdf_to_markdown, pdf_to_json"
            }

        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"JSON 解析失败: {str(e)}"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"执行失败: {str(e)}",
            "exception": str(e)
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
