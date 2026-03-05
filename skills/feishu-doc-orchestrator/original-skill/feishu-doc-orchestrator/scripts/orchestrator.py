#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文档创建 - 主编排脚本
编排 5 个子技能协作完成文档创建
使用文件传递数据，节省 Token
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


# 子技能脚本路径
SCRIPT_DIR = Path(__file__).parent.parent.parent
SUB_SKILLS = {
    "parser": SCRIPT_DIR / "feishu-md-parser" / "scripts" / "md_parser.py",
    "creator_with_permission": SCRIPT_DIR / "feishu-doc-creator-with-permission" / "scripts" / "doc_creator_with_permission.py",
    "block_adder": SCRIPT_DIR / "feishu-block-adder" / "scripts" / "block_adder.py",
    "verifier": SCRIPT_DIR / "feishu-doc-verifier" / "scripts" / "doc_verifier.py",
    "logger": SCRIPT_DIR / "feishu-logger" / "scripts" / "logger.py"
}


def run_step(name, script, args):
    """运行单个步骤"""
    print(f"\n{'='*70}")
    print(f"[步骤] {name}")
    print(f"{'='*70}")

    cmd = [sys.executable, str(script)] + args
    print(f"命令: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    # 打印输出
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"[FAIL] {name} 失败，退出码: {result.returncode}")
        return False

    print(f"[OK] {name} 完成")
    return True


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python orchestrator.py <markdown文件> [文档标题] [运行名称]")
        print()
        print("参数说明:")
        print("  markdown文件  - 要转换的 Markdown 文件路径")
        print("  文档标题      - 飞书文档标题（可选，默认使用文件名）")
        print("  运行名称      - 本次运行的文件夹名称（可选，默认使用时间戳）")
        print()
        print("示例:")
        print("  python orchestrator.py input.md")
        print("  python orchestrator.py input.md \"我的文档\"")
        print("  python orchestrator.py input.md \"我的文档\" \"test-run-01\"")
        print()
        print("工作流目录结构:")
        print("  workflow/run-2026-02-10-143022/")
        print("  ├── step1_parse/")
        print("  ├── step2_create_with_permission/")
        print("  ├── step3_add_blocks/")
        print("  └── step4_verify/")
        sys.exit(1)

    md_file = Path(sys.argv[1])
    if not md_file.exists():
        print(f"错误: 文件不存在: {md_file}")
        sys.exit(1)

    # 文档标题
    if len(sys.argv) >= 3:
        doc_title = sys.argv[2]
    else:
        doc_title = md_file.stem  # 使用文件名作为标题

    # 运行名称（用于创建独立子文件夹）
    if len(sys.argv) >= 4:
        run_name = sys.argv[3]
    else:
        # 默认使用时间戳：run-YYYY-MM-DD-HHMMSS
        run_name = datetime.now().strftime("run-%Y-%m-%d-%H%M%S")

    # 工作流基础目录（在项目根目录下）
    project_root = Path(__file__).parent.parent.parent.parent  # 上升到项目根目录
    workflow_base_dir = project_root / "workflow" / "feishu-doc-runs"

    # 本次运行的工作流目录
    workflow_dir = workflow_base_dir / run_name

    # 输出目录（日志文件保存位置）
    output_dir = project_root / "workflow" / "feishu-logs"

    print("="*70)
    print("Feishu Document Creation - Orchestrator Workflow (5 Steps)")
    print("="*70)
    print(f"输入文件: {md_file}")
    print(f"文档标题: {doc_title}")
    print(f"运行名称: {run_name}")
    print(f"工作流目录: {workflow_dir}")
    print(f"日志目录: {output_dir}")
    print()

    # 确保工作流目录和输出目录存在
    workflow_base_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建工作流目录
    step_dirs = {
        "parse": workflow_dir / "step1_parse",
        "create_with_permission": workflow_dir / "step2_create_with_permission",
        "add_blocks": workflow_dir / "step3_add_blocks",
        "verify": workflow_dir / "step4_verify"
    }

    for step_dir in step_dirs.values():
        step_dir.mkdir(parents=True, exist_ok=True)

    # 记录开始时间
    start_time = datetime.now()

    # ========== 第一步：Markdown 解析 ==========
    if not run_step(
        "第一步：Markdown 解析",
        SUB_SKILLS["parser"],
        [str(md_file), str(step_dirs["parse"])]
    ):
        sys.exit(1)

    blocks_file = step_dirs["parse"] / "blocks.json"
    if not blocks_file.exists():
        print(f"[FAIL] blocks.json 未生成: {blocks_file}")
        sys.exit(1)

    # ========== 第二步：文档创建+权限管理（原子操作）==========
    if not run_step(
        "第二步：文档创建+权限管理（原子操作）",
        SUB_SKILLS["creator_with_permission"],
        [doc_title, str(step_dirs["create_with_permission"])]
    ):
        sys.exit(1)

    doc_info_file = step_dirs["create_with_permission"] / "doc_with_permission.json"
    if not doc_info_file.exists():
        print(f"[FAIL] doc_with_permission.json 未生成: {doc_info_file}")
        sys.exit(1)

    # 读取文档信息
    with open(doc_info_file, 'r', encoding='utf-8') as f:
        doc_info = json.load(f)
    doc_url = doc_info["document_url"]
    permission = doc_info.get("permission", {})

    print(f"\n[权限状态]")
    print(f"  协作者添加: {permission.get('collaborator_added', False)}")
    print(f"  所有权转移: {permission.get('owner_transferred', False)}")
    print(f"  用户完全控制: {permission.get('user_has_full_control', False)}")

    # ========== 第三步：块添加 ==========
    if not run_step(
        "第三步：块添加",
        SUB_SKILLS["block_adder"],
        [str(blocks_file), str(doc_info_file), str(step_dirs["add_blocks"])]
    ):
        print("[WARN] 块添加失败，但继续执行后续步骤")

    # ========== 第四步：文档验证 ==========
    if not run_step(
        "第四步：文档验证",
        SUB_SKILLS["verifier"],
        [str(doc_info_file), str(step_dirs["verify"])]
    ):
        print("[WARN] 文档验证失败，但继续执行后续步骤")

    # ========== 第五步：日志记录 ==========
    if not run_step(
        "第五步：日志记录",
        SUB_SKILLS["logger"],
        [str(workflow_dir), str(output_dir)]
    ):
        print("[WARN] 日志记录失败")

    # 完成
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*70)
    print("文档创建完成！")
    print("="*70)
    print(f"文档 URL: {doc_url}")
    print(f"耗时: {duration:.2f} 秒")
    print(f"运行目录: {workflow_dir}")
    print()
    print("权限状态:")
    print(f"  协作者添加: {'[OK]' if permission.get('collaborator_added') else '[FAIL]'}")
    print(f"  所有权转移: {'[OK]' if permission.get('owner_transferred') else '[FAIL]'}")
    print(f"  用户完全控制: {'[OK]' if permission.get('user_has_full_control') else '[FAIL]'}")
    print()
    print("日志文件:")
    print(f"  - {output_dir / 'CREATED_DOCS.md'}")
    print(f"  - {output_dir / 'created_docs.json'}")
    print()
    print("本次运行工作流文件:")
    print(f"  - {workflow_dir / 'step1_parse/blocks.json'}")
    print(f"  - {workflow_dir / 'step2_create_with_permission/doc_with_permission.json'}")
    print(f"  - {workflow_dir / 'step3_add_blocks/add_result.json'}")
    print(f"  - {workflow_dir / 'step4_verify/verify_result.json'}")
    print()
    print(f"[提示] 所有工作流数据保存在: {workflow_base_dir}")
    print(f"[提示] 日志文件保存在: {output_dir}")


if __name__ == "__main__":
    main()
