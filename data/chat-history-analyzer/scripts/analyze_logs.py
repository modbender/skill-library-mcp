#!/usr/bin/env python3
"""
Analyze Logs - Combined log and chat history analysis for cron jobs.

This script runs both OpenClaw log analysis and Cursor chat history analysis,
saving findings to the journal. Designed to run hourly via cron.
"""

import argparse
import json
import sys
from pathlib import Path

# Import from self-optimizer
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "self-optimizer" / "scripts"))
try:
    from self_optimizer import SelfOptimizer
except ImportError:
    print("Error: Could not import SelfOptimizer. Ensure self-optimizer skill is installed.", file=sys.stderr)
    sys.exit(1)

# Import chat history analyzer
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from chat_history_analyzer import ChatHistoryAnalyzer
except ImportError:
    print("Error: Could not import ChatHistoryAnalyzer.", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Combined log and chat history analysis for hourly cron jobs.")
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
        error_msg = f"Log analysis failed: {e}"
        results["errors"].append(error_msg)
        results["log_analysis"] = {"error": str(e)}
        if not args.json:
            print(error_msg, file=sys.stderr)
    
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
        error_msg = f"Chat history analysis failed: {e}"
        results["errors"].append(error_msg)
        results["chat_history_analysis"] = {"error": str(e)}
        if not args.json:
            print(error_msg, file=sys.stderr)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 70)
        print("CHAT HISTORY & LOG ANALYSIS REPORT")
        print("=" * 70)
        
        if results["log_analysis"] and "error" not in results["log_analysis"]:
            print("\n📋 LOG ANALYSIS:")
            print(f"  Errors: {len(results['log_analysis'].get('errors', []))}")
            print(f"  Restarts: {results['log_analysis'].get('restarts', 0)}")
            print(f"  Config Changes: {results['log_analysis'].get('config_changes', 0)}")
            print(f"  OpenRouter 403s: {results['log_analysis'].get('openrouter_403s', 0)}")
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
                print(f"  Journal Entry: {results['chat_history_analysis']['journal_file']}")
        
        if results["errors"]:
            print("\n⚠️ ERRORS:")
            for error in results["errors"]:
                print(f"  - {error}")
        
        print("\n" + "=" * 70)
        
        # Exit with error code if any analysis failed
        if results["errors"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
