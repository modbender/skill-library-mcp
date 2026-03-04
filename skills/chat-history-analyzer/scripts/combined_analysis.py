#!/usr/bin/env python3
"""
Combined Analysis Script - Runs both log analysis and chat history analysis.

This script combines self-optimizer log analysis with chat history analysis
for a comprehensive hourly review.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directories to path to import self_optimizer
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "self-optimizer" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from self_optimizer import SelfOptimizer
from chat_history_analyzer import ChatHistoryAnalyzer


def main():
    parser = argparse.ArgumentParser(description="Combined log and chat history analysis.")
    parser.add_argument("--hours", type=float, default=1.0, help="Hours of chat history to analyze (default: 1.0)")
    parser.add_argument("--minutes", type=int, default=60, help="Minutes of logs to analyze (default: 60)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--openclaw-home", type=str, help="OpenClaw home directory (default: ~/.openclaw)")
    args = parser.parse_args()
    
    openclaw_home = Path(args.openclaw_home) if args.openclaw_home else Path.home() / ".openclaw"
    logs_dir = openclaw_home / "logs"
    
    results = {
        "log_analysis": None,
        "chat_history_analysis": None,
        "errors": []
    }
    
    # Run log analysis
    try:
        optimizer = SelfOptimizer(logs_dir, openclaw_home)
        log_analysis = optimizer.analyze_logs(minutes_back=args.minutes)
        results["log_analysis"] = log_analysis
    except Exception as e:
        results["errors"].append(f"Log analysis failed: {e}")
        results["log_analysis"] = {"error": str(e)}
    
    # Run chat history analysis
    try:
        analyzer = ChatHistoryAnalyzer(openclaw_home)
        messages = analyzer.extract_chat_history(hours_back=args.hours)
        chat_analysis = analyzer.analyze_messages(messages)
        journal_file = analyzer.save_to_journal(chat_analysis)
        results["chat_history_analysis"] = {
            **chat_analysis,
            "journal_file": str(journal_file)
        }
    except Exception as e:
        results["errors"].append(f"Chat history analysis failed: {e}")
        results["chat_history_analysis"] = {"error": str(e)}
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 60)
        print("COMBINED ANALYSIS REPORT")
        print("=" * 60)
        
        if results["log_analysis"] and "error" not in results["log_analysis"]:
            print("\n📋 LOG ANALYSIS:")
            print(f"  Errors: {len(results['log_analysis'].get('errors', []))}")
            print(f"  Restarts: {results['log_analysis'].get('restarts', 0)}")
            print(f"  Config Changes: {results['log_analysis'].get('config_changes', 0)}")
            if results['log_analysis'].get('suggestions'):
                print("  Suggestions:")
                for suggestion in results['log_analysis']['suggestions']:
                    print(f"    - {suggestion}")
        
        if results["chat_history_analysis"] and "error" not in results["chat_history_analysis"]:
            print("\n💬 CHAT HISTORY ANALYSIS:")
            print(f"  Messages Analyzed: {results['chat_history_analysis'].get('total_messages', 0)}")
            print(f"  Discoveries: {len(results['chat_history_analysis'].get('discoveries', []))}")
            print(f"  Obstacles: {len(results['chat_history_analysis'].get('obstacles', []))}")
            print(f"  Solutions: {len(results['chat_history_analysis'].get('solutions', []))}")
            if results['chat_history_analysis'].get('journal_file'):
                print(f"  Saved to: {results['chat_history_analysis']['journal_file']}")
        
        if results["errors"]:
            print("\n⚠️ ERRORS:")
            for error in results["errors"]:
                print(f"  - {error}")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
