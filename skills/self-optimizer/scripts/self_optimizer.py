#!/usr/bin/env python3
import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# OpenClaw imports (if available) - primarily for type hinting and potential future direct integration
# Not for direct execution via python3 script.py, but for when the script is imported/used within agent.
# We will pass necessary data to the script, not have it fetch data itself via default_api.


class SelfOptimizer:
    def __init__(self, logs_dir: Path, openclaw_home: Path):
        self.logs_dir = logs_dir
        self.openclaw_home = openclaw_home
        self.log_patterns = {
            "error": r"\b(Error|ERROR|exception|Exception|Fail):|\b(Failed to|error )", # Refined regex
            "restart": r"received SIGUSR1; restarting|received SIGTERM; shutting down",
            "gateway_status": r"gateway] listening on ws",
            "node_unavailable": r"remote bin probe skipped: node unavailable",
            "openrouter_403": r"403 Key limit exceeded",
            "config_change": r"config change detected; evaluating reload"
        }

    def _read_log_file(self, file_path, lines=500):
        try:
            if not os.path.exists(file_path):
                return []
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.readlines()[-lines:]
        except (FileNotFoundError, PermissionError, IOError) as e:
            # Silently return empty list for missing or unreadable files
            return []
        except Exception as e:
            # Log unexpected errors but don't fail
            print(f"Warning: Error reading log file {file_path}: {e}", file=sys.stderr)
            return []

    def analyze_logs(self, minutes_back=60):
        try:
            gateway_log_dir = self.logs_dir
            openclaw_log_dir = self.logs_dir

            gateway_log_path = os.path.join(gateway_log_dir, "gateway.log")
            openclaw_log_path = os.path.join(openclaw_log_dir, "openclaw.log") # Assuming openclaw.log can also be in same dir

            all_logs = self._read_log_file(gateway_log_path)
            all_logs.extend(self._read_log_file(openclaw_log_path))
        except Exception as e:
            # Return empty analysis if log reading fails completely
            return {
                "errors": [f"Failed to read log files: {str(e)}"],
                "restarts": 0,
                "config_changes": 0,
                "openrouter_403s": 0,
                "node_unavailable_mentions": 0,
                "suggestions": ["Log file access error. Check file permissions and paths."]
            }

        recent_logs = []
        time_cutoff = datetime.now() - timedelta(minutes=minutes_back)

        for line in all_logs:
            try:
                # Assuming log format like: 2026-02-16T21:27:45.414Z [heartbeat] started
                # Or: 2026-02-16 23:50:54 PST ...
                
                # Try parsing ISO 8601 with timezone (Z)
                match_iso = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)", line)
                if match_iso:
                    timestamp_str = match_iso.group(1)
                    log_time = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                else:
                    # Try parsing local time with timezone abbr (e.g., PST)
                    match_local = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \w{3})", line)
                    if match_local:
                        timestamp_str = match_local.group(1)
                        # Remove timezone abbreviation for parsing, as strptime doesn't handle them reliably
                        timestamp_without_tz = " ".join(timestamp_str.split(" ")[:-1])
                        # This assumes the current system's timezone for conversion, which is usually desired
                        log_time = datetime.strptime(timestamp_without_tz, "%Y-%m-%d %H:%M:%S")
                    else:
                        continue # Skip lines without a recognizable timestamp

                if log_time >= time_cutoff:
                    # Exclude the specific delivery-recovery success message
                    if not "delivery recovery complete: 0 recovered, 0 failed, 0 skipped" in line.lower():
                        recent_logs.append(line)
            except ValueError:
                # Log line might not have a perfect timestamp, skip
                continue

        analysis = {
            "errors": [],
            "restarts": 0,
            "config_changes": 0,
            "openrouter_403s": 0,
            "node_unavailable_mentions": 0,
            "suggestions": []
        }

        for line in recent_logs:
            if re.search(self.log_patterns["error"], line, re.IGNORECASE):
                analysis["errors"].append(line.strip())
            if re.search(self.log_patterns["restart"], line):
                analysis["restarts"] += 1
            if re.search(self.log_patterns["openrouter_403"], line):
                analysis["openrouter_403s"] += 1
            if re.search(self.log_patterns["node_unavailable"], line):
                analysis["node_unavailable_mentions"] += 1
            if re.search(self.log_patterns["config_change"], line):
                analysis["config_changes"] += 1
        
        # Add basic suggestions here
        if analysis["openrouter_403s"] > 0:
            analysis["suggestions"].append("OpenRouter API key might be exhausted or improperly configured. Check https://openrouter.ai/settings/keys.")
        if analysis["restarts"] >= 2: # More than one restart in the window is suspicious
            analysis["suggestions"].append("Frequent gateway restarts detected. Investigate recent configuration changes or system instability.")
        if analysis["errors"]:
            analysis["suggestions"].append(f"Found {len(analysis['errors'])} error(s) in logs. Review specific error messages for actionable insights.")
        if analysis["node_unavailable_mentions"] > 0:
            analysis["suggestions"].append(f"Node unavailable mentions detected ({analysis['node_unavailable_mentions']}). Ensure companion app is running and connected on 'ghost’s MacBook Pro'.")
        if analysis["config_changes"] >= 3:
            analysis["suggestions"].append("Multiple configuration changes detected. Reviewing `openclaw.json` for unintended changes or excessive patching might be beneficial.")

        return analysis

    def analyze_chat_history(self, chat_history_data: List[Dict[str, Any]], lookback_minutes=120):
        if not chat_history_data:
            return {"status": "No chat history data provided", "suggestions": []}

        try:
            chat_issues: Dict[str, int] = Counter()
            suggestions: List[str] = []

            problem_keywords = {
                "error": ["error", "fail", "issue", "problem", "bug"],
                "confusion": ["confused", "don't understand", "unclear", "huh?"],
                "performance": ["slow", "lag", "cost", "expensive", "quota"],
                "unavailability": ["unavailable", "not working", "disconnected"],
                "delegation": ["subagent failed", "spawn failed", "agent failed"]
            }

            time_cutoff = datetime.now() - timedelta(minutes=lookback_minutes)

            for entry in chat_history_data:
                try:
                    if not isinstance(entry, dict):
                        continue
                    if 'message' in entry and entry.get('role') == 'user': # Only analyze user messages
                        # Handle timestamp parsing gracefully
                        timestamp = entry.get('timestamp', '')
                        if not timestamp:
                            continue
                        try:
                            message_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            continue
                        if message_time < time_cutoff:
                            continue

                        text = str(entry.get('message', '')).lower()
                        for issue_type, keywords in problem_keywords.items():
                            for keyword in keywords:
                                if keyword in text:
                                    chat_issues[issue_type] += 1
                except (KeyError, AttributeError, ValueError) as e:
                    # Skip malformed entries
                    continue
        except Exception as e:
            return {
                "status": f"Error analyzing chat history: {str(e)}",
                "issues_summary": {},
                "suggestions": ["Chat history analysis failed. Check data format."]
            }

        if chat_issues["error"] > 0:
            suggestions.append(f"Recurring errors detected in chat history ({chat_issues['error']} mentions from user). Investigate common error patterns in user interactions.")
        if chat_issues["confusion"] > 0:
            suggestions.append(f"User confusion detected in chat history ({chat_issues['confusion']} mentions). Consider clarifying responses or providing more context to the user.")
        if chat_issues["performance"] > 0:
            suggestions.append(f"User concerns about performance/cost detected in chat history ({chat_issues['performance']} mentions). Optimize resource usage or suggest cheaper models for user tasks.")
        if chat_issues["unavailability"] > 0:
            suggestions.append(f"Repeated tool/service unavailability mentioned by user ({chat_issues['unavailability']} mentions). Check external service statuses or authentication for used tools.")
        if chat_issues["delegation"] > 0:
            suggestions.append(f"Sub-agent/delegation failures mentioned by user ({chat_issues['delegation']} mentions). Review agent swarm routing, config, or sub-agent skill issues.")

        return {"status": "Analyzed", "issues_summary": dict(chat_issues), "suggestions": suggestions}

    def analyze_root_folder(self):
        # Placeholder for future implementation
        return {"status": "Not yet implemented", "suggestions": []}

    def propose_improvements(self, chat_history_data: Optional[List[Dict[str, Any]]] = None):
        try:
            log_analysis = self.analyze_logs()
        except Exception as e:
            log_analysis = {
                "errors": [f"Log analysis failed: {str(e)}"],
                "restarts": 0,
                "config_changes": 0,
                "openrouter_403s": 0,
                "node_unavailable_mentions": 0,
                "suggestions": ["Log analysis encountered an error. Check system logs for details."]
            }
        
        try:
            chat_history_analysis = self.analyze_chat_history(chat_history_data=chat_history_data)
        except Exception as e:
            chat_history_analysis = {
                "status": f"Error: {str(e)}",
                "issues_summary": {},
                "suggestions": ["Chat history analysis encountered an error."]
            }
        
        try:
            root_folder_analysis = self.analyze_root_folder()
        except Exception as e:
            root_folder_analysis = {
                "status": f"Error: {str(e)}",
                "suggestions": []
            }

        proposals = []
        if log_analysis.get("suggestions"):
            proposals.extend(log_analysis["suggestions"])
        if chat_history_analysis.get("suggestions"):
            proposals.extend(chat_history_analysis["suggestions"])
        if root_folder_analysis.get("suggestions"):
            proposals.extend(root_folder_analysis["suggestions"])
        
        if not proposals:
            proposals.append("No critical issues found in recent activity. Consider optimizing frequently used skills or automating routine checks for proactive maintenance.")

        overall_report = {
            "log_analysis": log_analysis,
            "chat_history_analysis": chat_history_analysis,
            "root_folder_analysis": root_folder_analysis,
            "proposals": proposals
        }
        return overall_report


def main():
    parser = argparse.ArgumentParser(description="OpenClaw Self-Optimizer Skill.")
    parser.add_argument("command", choices=["analyze"], default="analyze", nargs="?", help="The command to run (default: analyze).")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format.")
    parser.add_argument("--chat-history-file", type=str, help="Path to a JSON file containing chat history data.")
    args = parser.parse_args()

    # Determine logs directory based on OPENCLAW_HOME
    openclaw_home = Path(os.environ.get("OPENCLAW_HOME", Path.home() / ".openclaw"))
    logs_dir = openclaw_home / "logs"

    optimizer = SelfOptimizer(logs_dir, openclaw_home)

    if args.command == "analyze":
        chat_history_data = []
        if args.chat_history_file:
            try:
                with open(args.chat_history_file, "r") as f:
                    chat_history_data = json.load(f)
            except FileNotFoundError:
                print(f"Error: Chat history file not found: {args.chat_history_file}", file=sys.stderr)
                sys.exit(1)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in chat history file: {args.chat_history_file}", file=sys.stderr)
                sys.exit(1)

        report = optimizer.propose_improvements(chat_history_data=chat_history_data)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("\\n--- OpenClaw Self-Optimization Report ---")
            print("\\nLog Analysis:")
            print(f"  Recent Errors: {len(report['log_analysis']['errors'])} detected")
            for error in report['log_analysis']['errors']:
                print(f"    - {error}")
            print(f"  Gateway Restarts: {report['log_analysis']['restarts']} detected")
            print(f"  OpenRouter 403s: {report['log_analysis']['openrouter_403s']} detected")
            print(f"  Node Unavailable Mentions: {report['log_analysis']['node_unavailable_mentions']} detected")
            print(f"  Config Changes: {report['log_analysis']['config_changes']} detected")
            
            print("\\nChat History Analysis:")
            print(f"  Status: {report['chat_history_analysis']['status']}")
            if report['chat_history_analysis']['suggestions']:
                 print("  Suggestions:")
                 for suggestion in report['chat_history_analysis']['suggestions']:
                     print(f"    - {suggestion}")         

            print("\\nRoot Folder Analysis:")
            print(f"  Status: {report['root_folder_analysis']['status']}")
            
            print("\\n--- Self-Improvement Proposals ---")
            if report['proposals']:
                for i, proposal in enumerate(report['proposals']):
                    print(f'{i + 1}. {proposal}')
            else:
                print("No specific proposals at this time.")

    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
