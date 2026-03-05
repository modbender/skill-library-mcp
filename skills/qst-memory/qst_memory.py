#!/usr/bin/env python3
"""
QST Memory System v1.5
樹狀分類 + 混合搜索 + 自動分類 + 記憶衰減

============================================
🌳 樹狀分類：34 分類 (6 根 → 18 L2 → 10 L3)
🔍 三種搜索：Tree / Selection Rule / Semantic
🤖 自動分類：智能推斷分類
🧹 記憶衰減：自動清理過期記憶
============================================

Usage:
    python qst_memory.py search "暗物質"
    python qst_memory.py search "ARM芯片" --hybrid
    python qst_memory.py save "重要決定：採用 FSCA v7"
    python qst_memory.py classify "QST暗物質計算"
    python qst_memory.py cleanup --dry-run
    python qst_memory.py stats
"""

import argparse
import sys
from pathlib import Path

# 添加腳本目錄到路徑
SCRIPT_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from tree_search import tree_search as ts
from bfs_search import bfs_search as bs
from semantic_search import semantic_search as ss
from semantic_search_v15 import semantic_search_enhanced
from hybrid_search import hybrid_search
from auto_classify import auto_classify, suggest_category
from save_memory import save_memory
from stats_panel import stats_panel
from cleanup import cleanup_memories, print_status


def cmd_search(args):
    """搜索命令"""
    if args.method == "tree":
        result = ts(args.query, args.path)
    elif args.method == "bfs":
        result = bs(args.query, args.root)
    elif args.method == "semantic":
        result = ss(args.query, args.expand)
    elif args.method == "enhanced":
        context = args.context.split(",") if args.context else None
        result = semantic_search_enhanced(
            args.query,
            context=context,
            expand=args.expand,
            min_relevance=args.min_relevance
        )
    elif args.method == "hybrid":
        methods = [m.strip() for m in args.methods.split(",")]
        context = args.context.split(",") if args.context else None
        result = hybrid_search(args.query, methods=methods, context=context)
    else:
        # 默認使用混合搜索
        result = hybrid_search(args.query)
    
    # 顯示路徑
    path = result.get('path', result.get('primary', 'Root'))
    if isinstance(path, list):
        path_display = ' → '.join(path)
    elif isinstance(path, str):
        path_display = path
    else:
        path_display = 'Root'
    
    print(f"\n📁 Path: {path_display}")
    print(f"🔗 Related: {', '.join(result.get('related', [])[:5])}")
    print(f"🔑 Keywords: {', '.join(result.get('keywords', [])[:5])}")
    print(f"📊 Found: {result.get('count', len(result.get('results', [])))} memories\n")
    
    for i, r in enumerate(result.get('results', result.get('memories', []))[:5], 1):
        content = r if isinstance(r, str) else r.get('content', str(r))
        print(f"--- Memory {i} ---")
        print(content[:200] + "..." if len(content) > 200 else content)
        print()


def cmd_save(args):
    """保存記憶命令"""
    # 獲取內容
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = args.content
    
    # 保存記憶
    result = save_memory(
        content,
        category=args.category,
        weight=args.weight,
        auto_classify=not args.no_auto_classify,
        auto_weight=not args.no_auto_weight
    )
    
    if result["success"]:
        print(f"\n✅ 記憶已保存！")
        print(f"   分類: {result['category']}")
        print(f"   權重: [{result['weight']}]")
        print(f"   索引: #{result['index']}")
        if result.get('auto_classified'):
            print(f"   自動分類: ✅ ({result['reasoning']})")
    else:
        print(f"\n❌ 保存失敗！")


def cmd_classify(args):
    """自動分類命令"""
    # 獲取內容
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = args.content
    
    result = auto_classify(content)
    
    print(f"\n📊 分類結果")
    print(f"{'='*50}")
    print(f"🏷️ 建議分類: {result['suggested_category']}")
    print(f"📈 置信度: {result['confidence']}")
    print(f"🎯 分數: {result['primary_score']}")
    print(f"💡 推理: {result['reasoning']}")
    
    print(f"\n🔑 關鍵詞: {', '.join(result['keywords'][:10])}")
    
    if result.get('alternatives'):
        print(f"\n🔄 備選:")
        for alt in result['alternatives']:
            print(f"  • {alt['category']} ({alt['score']}) - {alt['confidence']}")


def cmd_suggest(args):
    """建議分類命令"""
    keywords = [k.strip() for k in args.keywords.split(",")]
    
    config_file = Path(__file__).parent / "config.yaml"
    import yaml
    config = yaml.safe_load(config_file.read_text()) if config_file.exists() else {}
    
    suggestion = suggest_category(" ".join(keywords), config)
    
    print(f"\n💡 建議: {suggestion['reasoning']}")
    
    if suggestion.get('suggested_parent'):
        print(f"📁 父分類: {suggestion['suggested_parent']}")
    
    if suggestion.get('suggested_name'):
        print(f"🏷️ 建議名稱: {suggestion['suggested_name']}")


def cmd_cleanup(args):
    """清理命令"""
    if args.status:
        print_status()
    elif args.dry_run:
        report = cleanup_memories(dry_run=True)
        print(f"\n🧹 預覽清理")
        print(f"{'='*50}")
        print(f"總記憶: {report['summary']['total']}")
        print(f"保留: {report['summary']['kept']}")
        print(f"歸檔: {report['summary']['archived']}")
        print(f"刪除: {report['summary']['deleted']}")
    elif args.run:
        report = cleanup_memories(dry_run=False)
        print(f"\n🧹 清理完成")
        print(f"{'='*50}")
        print(f"歸檔: {report['summary']['archived']}")
        print(f"刪除: {report['summary']['deleted']}")
    else:
        print("\n用法:")
        print("  python qst_memory.py cleanup --status   # 查看狀態")
        print("  python qst_memory.py cleanup --dry-run  # 預覽清理")
        print("  python qst_memory.py cleanup --run      # 執行清理")


def cmd_stats(args):
    """統計命令"""
    output = "json" if args.json else "text"
    result = stats_panel(output)
    
    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)


def main():
    parser = argparse.ArgumentParser(
        description="QST Memory System v1.5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
============================================
🌳 Tree-Based Classification (34 categories)
🔍 Multi-Mode Search (Tree/BFS/Semantic/Enhanced/Hybrid)
🤖 Auto-Classification with AI inference
🧹 Memory Decay & Cleanup System
============================================

Examples:
  search:
    python qst_memory.py search "暗物質"
    python qst_memory.py search "ARM芯片" --method enhanced
    python qst_memory.py search "ARM芯片" --method hybrid --context "技術討論"
  
  save memory:
    python qst_memory.py save "採用 FSCA v7 作為暗物質理論"
    python qst_memory.py save --file memory.txt --weight I
  
  auto-classify:
    python qst_memory.py classify "QST暗物質使用FSCA理論"
    python qst_memory.py classify --file content.txt
  
  cleanup:
    python qst_memory.py cleanup --status
    python qst_memory.py cleanup --dry-run
    python qst_memory.py cleanup --run
  
  stats:
    python qst_memory.py stats
    python qst_memory.py stats --json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索記憶")
    search_parser.add_argument("query", help="搜索查詢")
    search_parser.add_argument("--method", "-m", 
                              choices=["tree", "bfs", "semantic", "enhanced", "hybrid"],
                              default="hybrid", help="搜索方法")
    search_parser.add_argument("--path", help="樹狀路徑 (tree 方法)")
    search_parser.add_argument("--root", help="根分類 (bfs 方法)")
    search_parser.add_argument("--expand", action="store_true",
                              help="擴展相關分類 (semantic/enhanced 方法)")
    search_parser.add_argument("--min-relevance", type=float, default=0.1,
                             help="最小相關度 (enhanced 方法)")
    search_parser.add_argument("--methods", default="tree,selection,semantic",
                             help="混合搜索方法 (hybrid 方法)")
    search_parser.add_argument("--context", "-c", help="上下文 (comma-separated)")
    
    # save 命令
    save_parser = subparsers.add_parser("save", help="保存記憶")
    save_parser.add_argument("content", nargs="?", help="記憶內容")
    save_parser.add_argument("--file", "-f", help="文件路徑")
    save_parser.add_argument("--category", "-c", help="指定分類")
    save_parser.add_argument("--weight", "-w", choices=["C", "I", "N"], help="權重")
    save_parser.add_argument("--no-auto-classify", action="store_true", help="禁用自動分類")
    save_parser.add_argument("--no-auto-weight", action="store_true", help="禁用自動權重")
    
    # classify 命令
    classify_parser = subparsers.add_parser("classify", help="自動分類")
    classify_parser.add_argument("content", nargs="?", help="要分類的內容")
    classify_parser.add_argument("--file", "-f", help="文件路徑")
    
    # suggest 命令
    suggest_parser = subparsers.add_parser("suggest", help="建議分類")
    suggest_parser.add_argument("--keywords", required=True, help="關鍵詞 (逗號分隔)")
    
    # cleanup 命令
    cleanup_parser = subparsers.add_parser("cleanup", help="清理記憶")
    cleanup_parser.add_argument("--status", action="store_true", help="查看狀態")
    cleanup_parser.add_argument("--dry-run", action="store_true", help="預覽清理")
    cleanup_parser.add_argument("--run", action="store_true", help="執行清理")
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="統計面板")
    stats_parser.add_argument("--json", action="store_true", help="JSON 輸出")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 分發命令
    if args.command == "search":
        cmd_search(args)
    elif args.command == "save":
        cmd_save(args)
    elif args.command == "classify":
        cmd_classify(args)
    elif args.command == "suggest":
        cmd_suggest(args)
    elif args.command == "cleanup":
        cmd_cleanup(args)
    elif args.command == "stats":
        cmd_stats(args)


if __name__ == "__main__":
    main()
