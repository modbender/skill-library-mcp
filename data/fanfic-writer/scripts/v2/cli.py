"""
Fanfic Writer v2.0 - Complete CLI with Interactive Confirmations
Full command line interface - each phase requires human confirmation
"""
import sys
import argparse
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent to path to maintain package structure
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from scripts.v2.workspace import WorkspaceManager
from scripts.v2.phase_runner import PhaseRunner
from scripts.v2.writing_loop import WritingLoop
from scripts.v2.safety_mechanisms import FinalIntegration, BackpatchManager
from scripts.v2.resume_manager import RunLock, ResumeManager, RuntimeConfigManager
from scripts.v2.price_table import PriceTableManager, CostBudgetManager
from scripts.v2.atomic_io import atomic_write_json
from scripts.v2.utils import get_timestamp_iso


def wait_for_confirmation(prompt: str = "确认继续? (y/n): ") -> bool:
    """Wait for user confirmation, return True if confirmed"""
    while True:
        response = input(prompt).strip().lower()
        if response in ['y', 'yes', '是', '']:
            return True
        elif response in ['n', 'no', '否', 'q', 'quit', '退出']:
            return False
        else:
            print("  请输入 y/n 或 是/否")


def cmd_init(args):
    """
    Phase 1-5: Initialize book with human confirmation at each step
    
    1. 书名、类型、字数 - 确认
    2. 目录位置 - 确认
    3. 风格指南 (Phase 2) - 确认
    4. 主线大纲 (Phase 3) - 确认
    5. 章节规划 (Phase 4) - 确认
    6. 世界观 (Phase 5) - 确认
    """
    print("\n" + "="*60)
    print("📖 阴间外卖 - 初始化向导")
    print("="*60 + "\n")
    
    # ========== Step 1: 书名、类型、字数 ==========
    print("【步骤1/6】基本配置")
    print("-" * 40)
    
    # Get book info interactively if not provided
    if not args.title:
        args.title = input("📝 书名: ").strip()
    if not args.genre:
        args.genre = input("📝 类型 (都市/玄幻/仙侠...): ").strip()
    if not args.words or args.words == 100000:
        words_input = input("📝 总字数 (默认100000): ").strip()
        if words_input:
            args.words = int(words_input)
    
    print(f"\n  书名: {args.title}")
    print(f"  类型: {args.genre}")
    print(f"  字数: {args.words:,}")
    
    if not wait_for_confirmation("\n✅ 确认基本配置? (y/n): "):
        print("❌ 已取消")
        sys.exit(0)
    
    # ========== Step 2: 目录位置 ==========
    print("\n【步骤2/6】存放目录")
    print("-" * 40)
    
    if args.base_dir:
        base_dir = Path(args.base_dir)
    else:
        default_dir = Path.home() / ".openclaw" / "novels"
        print(f"  默认目录: {default_dir}")
        custom = input("  自定义目录 (直接回车使用默认): ").strip()
        if custom:
            base_dir = Path(custom)
        else:
            base_dir = default_dir
    
    print(f"\n  存放目录: {base_dir}")
    
    if not wait_for_confirmation("\n✅ 确认存放目录? (y/n): "):
        print("❌ 已取消")
        sys.exit(0)
    
    # Create workspace and run phases 1-5 with confirmation at each step
    print("\n🚀 开始初始化...")
    workspace = WorkspaceManager(base_dir)
    runner = PhaseRunner(workspace)
    
    # Phase 1: Initialization
    print("\n" + "="*50)
    print("【Phase 1】初始化项目")
    print("="*50)
    
    results = runner.phase1_initialize(
        book_title=args.title,
        genre=args.genre,
        target_words=args.words,
        chapter_target_words=args.chapter_words or 2500,
        subgenre=args.subgenre,
        mode=args.mode,
        model=args.model,
        tone=args.tone,
        usd_cny_rate=args.usd_cny_rate
    )
    
    run_dir = results['run_dir']
    print(f"\n✅ Phase 1 完成: {run_dir}")
    
    # Phase 2: Style Guide - NEEDS CONFIRMATION
    print("\n" + "="*50)
    print("【Phase 2】生成风格指南")
    print("="*50)
    print("  正在生成写作风格指南...")
    
    runner.phase2_style_guide()
    print(f"\n  已生成: {run_dir}/0-config/style_guide.md")
    print("\n  请查看以上文件内容")
    
    if not wait_for_confirmation("\n✅ 确认风格指南? (y/n): "):
        print("❌ 已取消，请修改后重新运行")
        sys.exit(0)
    
    # Phase 3: Main Outline - NEEDS CONFIRMATION
    print("\n" + "="*50)
    print("【Phase 3】生成主线大纲")
    print("="*50)
    print("  正在生成主线大纲...")
    
    runner.phase3_main_outline()
    print(f"\n  已生成: {run_dir}/1-outline/1-main-outline.md")
    print("\n  请查看以上文件内容")
    
    if not wait_for_confirmation("\n✅ 确认主线大纲? (y/n): "):
        print("❌ 已取消，请修改后重新运行")
        sys.exit(0)
    
    # Phase 4: Chapter Planning - NEEDS CONFIRMATION
    print("\n" + "="*50)
    print("【Phase 4】生成章节规划")
    print("="*50)
    print("  正在生成章节规划...")
    
    runner.phase4_chapter_planning()
    print(f"\n  已生成: {run_dir}/2-planning/2-chapter-plan.json")
    print(f"  已生成: {run_dir}/1-outline/5-chapter-outlines.json")
    print("\n  请查看以上文件内容")
    
    if not wait_for_confirmation("\n✅ 确认章节规划? (y/n): "):
        print("❌ 已取消，请修改后重新运行")
        sys.exit(0)
    
    # Phase 5: World Building - NEEDS CONFIRMATION
    print("\n" + "="*50)
    print("【Phase 5】生成世界观设定")
    print("="*50)
    print("  正在生成世界观设定...")
    
    runner.phase5_world_building()
    print(f"\n  已生成: {run_dir}/3-world/3-world-building.md")
    print("\n  请查看以上文件内容")
    
    if not wait_for_confirmation("\n✅ 确认世界观设定? (y/n): "):
        print("❌ 已取消，请修改后重新运行")
        sys.exit(0)
    
    # Phase 5.5: Alignment Check
    print("\n" + "="*50)
    print("【Phase 5.5】对齐检查")
    print("="*50)
    runner.phase5_alignment_check()
    
    print("\n" + "="*60)
    print("🎉 初始化完成！")
    print("="*60)
    print(f"  Run ID: {results['run_id']}")
    print(f"  路径: {run_dir}")
    print("\n📝 下一步:")
    print(f"  1. 查看大纲: {run_dir}/1-outline/1-main-outline.md")
    print(f"  2. 查看世界观: {run_dir}/3-world/3-world-building.md")
    print(f"  3. 开始写作: python -m scripts.v2.cli write --run-dir \"{run_dir}\"")


def cmd_write(args):
    """
    Phase 6: Writing Loop
    Each chapter requires confirmation before moving to next
    """
    run_dir = Path(args.run_dir)
    
    if not run_dir.exists():
        print(f"❌ 目录不存在: {run_dir}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("📖 开始写作 - Phase 6")
    print("="*60)
    print(f"  目录: {run_dir}")
    print(f"  模式: {args.mode}")
    
    # Get current chapter
    state_path = run_dir / "4-state" / "4-writing-state.json"
    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    current_chapter = state.get('current_chapter', 0)
    print(f"  当前章节: {current_chapter}")
    
    # Determine chapters to write
    if args.chapters:
        if '-' in args.chapters:
            start, end = map(int, args.chapters.split('-'))
            chapters = list(range(start, end + 1))
        else:
            chapters = [int(c) for c in args.chapters.split(',')]
    else:
        # Default: write one chapter at a time
        chapters = [current_chapter + 1]
    
    print(f"  将写入章节: {chapters}")
    
    if not wait_for_confirmation("\n✅ 确认开始写作? (y/n): "):
        print("❌ 已取消")
        sys.exit(0)
    
    # Acquire lock
    run_lock = RunLock(run_dir)
    lock_success, lock_error = run_lock.acquire(mode=args.mode or "manual")
    if not lock_success:
        print(f"❌ 无法获取锁: {lock_error}")
        sys.exit(1)
    
    try:
        # Mock model for now - in real implementation, would call actual API
        def mock_model(prompt: str) -> str:
            return f"[Generated content for: {prompt[:30]}...]"
        
        loop = WritingLoop(
            run_dir=run_dir,
            model_callable=mock_model
        )
        
        for chapter_num in chapters:
            print("\n" + "="*50)
            print(f"✍️  正在写作第 {chapter_num} 章...")
            print("="*50)
            
            result = loop.write_chapter(chapter_num)
            
            print(f"\n  章节 {chapter_num} 完成:")
            print(f"    状态: {result['qc_status']}")
            print(f"    评分: {result['qc_score']}")
            
            # Show the result
            if result.get('chapter_path'):
                print(f"    保存: {result['chapter_path']}")
            
            # Ask for confirmation before next chapter
            if chapter_num < chapters[-1]:
                print("\n" + "-"*40)
                if not wait_for_confirmation(f"\n✅ 第 {chapter_num} 章完成，继续写第 {chapter_num+1} 章? (y/n): "):
                    print("❌ 已暂停")
                    break
    
    finally:
        run_lock.release()
    
    print("\n✅ 写作暂停或完成")


def main():
    parser = argparse.ArgumentParser(
        description='Fanfic Writer v2.0 - Interactive CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize new book (Phase 1-5)')
    init_parser.add_argument('--title', '-t', help='Book title')
    init_parser.add_argument('--genre', '-g', help='Genre')
    init_parser.add_argument('--words', '-w', type=int, default=100000, help='Target word count')
    init_parser.add_argument('--chapter-words', type=int, default=2500, help='Words per chapter')
    init_parser.add_argument('--subgenre', help='Subgenre')
    init_parser.add_argument('--mode', choices=['auto', 'manual'], default='manual', help='Writing mode')
    init_parser.add_argument('--model', help='Model to use')
    init_parser.add_argument('--tone', help='Tone style')
    init_parser.add_argument('--usd-cny-rate', type=float, help='USD to CNY rate')
    init_parser.add_argument('--base-dir', help='Base directory for novels')
    
    # write command  
    write_parser = subparsers.add_parser('write', help='Write chapters (Phase 6)')
    write_parser.add_argument('--run-dir', '-r', required=True, help='Run directory')
    write_parser.add_argument('--mode', choices=['auto', 'manual'], default='manual', help='Writing mode')
    write_parser.add_argument('--chapters', '-c', help='Chapter range (e.g., "1-5" or "3")')
    write_parser.add_argument('--resume', choices=['off', 'auto', 'force'], default='off', help='Resume mode')
    write_parser.add_argument('--budget', type=float, help='Cost budget in RMB')
    write_parser.add_argument('--max-chapters', type=int, default=200, help='Max chapters')
    
    # status command
    status_parser = subparsers.add_parser('status', help='Check run status')
    status_parser.add_argument('--run-dir', '-r', required=True, help='Run directory')
    
    # test command
    subparsers.add_parser('test', help='Run self-test')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'write':
        cmd_write(args)
    elif args.command == 'status':
        run_dir = Path(args.run_dir)
        if run_dir.exists():
            state_path = run_dir / "4-state" / "4-writing-state.json"
            if state_path.exists():
                with open(state_path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                print(f"  当前章节: {state.get('current_chapter', 0)}")
                print(f"  完成章节: {state.get('completed_chapters', [])}")
                print(f"  状态: {state.get('qc_status', 'N/A')}")
                print(f"  forced_streak: {state.get('forced_streak', 0)}")
        else:
            print(f"❌ 目录不存在: {run_dir}")
    elif args.command == 'test':
        print("Running tests...")
        print("✓ All modules importable")


if __name__ == '__main__':
    main()
