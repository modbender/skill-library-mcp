#!/usr/bin/env python3
"""
Scribe - Comprehensive note-taking for OpenClaw

Scans OpenClaw logs, config files, chat history, cursor history, behavior,
desires, tastes, drafts and takes daily/weekly notes with summaries.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import re
import os


class Scribe:
    def __init__(self, openclaw_home: Path):
        self.openclaw_home = openclaw_home
        self.workspace_dir = openclaw_home / "workspace"
        self.logs_dir = openclaw_home / "logs"
        self.notes_dir = self.workspace_dir / "Notes"
        self.daily_notes_dir = self.notes_dir / "daily"
        self.weekly_notes_dir = self.notes_dir / "weekly"
        self.memory_dir = self.workspace_dir / "memory"
        self.config_path = openclaw_home / "openclaw.json"
        self.cursor_storage = Path.home() / "Library" / "Application Support" / "Cursor" / "User"
        self.global_db = self.cursor_storage / "globalStorage" / "state.vscdb"
        self.workspace_storage = self.cursor_storage / "workspaceStorage"
        
        # Ensure directories exist
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.daily_notes_dir.mkdir(parents=True, exist_ok=True)
        self.weekly_notes_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
    def scan_logs(self, days_back: int = 1) -> Dict[str, Any]:
        """Scan OpenClaw logs for activity patterns."""
        log_data = {
            "errors": [],
            "warnings": [],
            "activities": [],
            "gateway_events": [],
            "subagent_spawns": []
        }
        
        if not self.logs_dir.exists():
            return log_data
        
        cutoff_time = datetime.now() - timedelta(days=days_back)
        
        for log_file in self.logs_dir.glob("*.log"):
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        # Try to extract timestamp if present
                        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})', line)
                        if timestamp_match:
                            try:
                                log_time = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                            except:
                                try:
                                    log_time = datetime.strptime(timestamp_match.group(1), '%Y-%m-%dT%H:%M:%S')
                                except:
                                    log_time = None
                        else:
                            log_time = None
                        
                        # Categorize log entries
                        line_lower = line.lower()
                        if 'error' in line_lower or 'exception' in line_lower or 'traceback' in line_lower:
                            log_data["errors"].append({
                                "file": log_file.name,
                                "line": line.strip(),
                                "timestamp": log_time.isoformat() if log_time else None
                            })
                        elif 'warning' in line_lower or 'warn' in line_lower:
                            log_data["warnings"].append({
                                "file": log_file.name,
                                "line": line.strip(),
                                "timestamp": log_time.isoformat() if log_time else None
                            })
                        elif 'gateway' in line_lower:
                            log_data["gateway_events"].append({
                                "file": log_file.name,
                                "line": line.strip(),
                                "timestamp": log_time.isoformat() if log_time else None
                            })
                        elif 'spawn' in line_lower or 'subagent' in line_lower:
                            log_data["subagent_spawns"].append({
                                "file": log_file.name,
                                "line": line.strip(),
                                "timestamp": log_time.isoformat() if log_time else None
                            })
            except Exception as e:
                log_data["errors"].append({
                    "file": log_file.name,
                    "error": f"Failed to read log file: {e}"
                })
        
        return log_data
    
    def scan_config(self) -> Dict[str, Any]:
        """Scan openclaw.json config file for settings and preferences."""
        config_data = {
            "exists": False,
            "model_preferences": {},
            "gateway_settings": {},
            "agent_settings": {},
            "tools_settings": {}
        }
        
        if not self.config_path.exists():
            return config_data
        
        config_data["exists"] = True
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Extract model preferences
            if "agents" in config and "defaults" in config["agents"]:
                defaults = config["agents"]["defaults"]
                if "model" in defaults:
                    config_data["model_preferences"]["default"] = defaults["model"]
                if "models" in defaults:
                    config_data["model_preferences"]["aliases"] = defaults["models"]
            
            # Extract gateway settings
            if "gateway" in config:
                config_data["gateway_settings"] = config["gateway"]
            
            # Extract agent settings
            if "agents" in config:
                config_data["agent_settings"] = config["agents"]
            
            # Extract tools settings
            if "tools" in config:
                config_data["tools_settings"] = config["tools"]
                
        except Exception as e:
            config_data["error"] = str(e)
        
        return config_data
    
    def scan_chat_history(self, hours_back: float = 24.0) -> List[Dict[str, Any]]:
        """Extract chat history from Cursor's SQLite databases."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        all_messages = []
        
        # Try global storage
        if self.global_db.exists():
            try:
                conn = sqlite3.connect(str(self.global_db))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%chat%' OR key LIKE '%ai%' OR key LIKE '%history%' OR key LIKE '%conversation%'")
                rows = cursor.fetchall()
                
                for row in rows:
                    try:
                        value = json.loads(row['value'])
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict) and 'messages' in item:
                                    all_messages.extend(self._extract_messages_from_conversation(item, cutoff_time))
                                elif isinstance(item, dict) and ('role' in item or 'message' in item):
                                    msg = self._normalize_message(item, cutoff_time)
                                    if msg:
                                        all_messages.append(msg)
                        elif isinstance(value, dict) and 'messages' in value:
                            all_messages.extend(self._extract_messages_from_conversation(value, cutoff_time))
                    except:
                        pass
                
                conn.close()
            except Exception as e:
                pass
        
        # Try workspace-specific databases
        if self.workspace_storage.exists():
            for workspace_dir in self.workspace_storage.iterdir():
                db_path = workspace_dir / "state.vscdb"
                if db_path.exists():
                    try:
                        conn = sqlite3.connect(str(db_path))
                        conn.row_factory = sqlite3.Row
                        cursor = conn.cursor()
                        
                        cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%chat%' OR key LIKE '%ai%' OR key LIKE '%history%'")
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            try:
                                value = json.loads(row['value'])
                                if isinstance(value, dict) and 'messages' in value:
                                    all_messages.extend(self._extract_messages_from_conversation(value, cutoff_time))
                            except:
                                pass
                        
                        conn.close()
                    except:
                        pass
        
        return all_messages
    
    def _extract_messages_from_conversation(self, conversation: Dict, cutoff_time: datetime) -> List[Dict]:
        """Extract messages from a conversation object."""
        messages = []
        if 'messages' in conversation:
            for msg in conversation['messages']:
                normalized = self._normalize_message(msg, cutoff_time)
                if normalized:
                    messages.append(normalized)
        return messages
    
    def _normalize_message(self, msg: Any, cutoff_time: datetime) -> Optional[Dict]:
        """Normalize a message object to a standard format."""
        if not isinstance(msg, dict):
            return None
        
        # Extract timestamp
        timestamp = None
        if 'timestamp' in msg:
            timestamp = msg['timestamp']
        elif 'createdAt' in msg:
            timestamp = msg['createdAt']
        elif 'time' in msg:
            timestamp = msg['time']
        
        if timestamp:
            try:
                if isinstance(timestamp, (int, float)):
                    msg_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                else:
                    msg_time = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                if msg_time < cutoff_time:
                    return None
            except:
                pass
        
        # Extract role and content
        role = msg.get('role', msg.get('author', 'unknown'))
        content = msg.get('content', msg.get('message', msg.get('text', '')))
        
        if not content:
            return None
        
        return {
            "role": role,
            "content": str(content)[:500],  # Truncate long messages
            "timestamp": timestamp
        }
    
    def scan_memory_files(self, days_back: int = 7) -> Dict[str, Any]:
        """Scan memory files for behavior patterns and context."""
        memory_data = {
            "daily_notes": [],
            "memories": []
        }
        
        if not self.memory_dir.exists():
            return memory_data
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Scan daily memory files
        for memory_file in self.memory_dir.glob("*.md"):
            if memory_file.name == "MEMORY.md":
                # Read long-term memory
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        memory_data["memories"].append({
                            "file": memory_file.name,
                            "content": content[:2000],  # Truncate for summary
                            "size": len(content)
                        })
                except Exception as e:
                    pass
            else:
                # Daily note file (YYYY-MM-DD.md)
                try:
                    file_date_match = re.match(r'(\d{4}-\d{2}-\d{2})', memory_file.name)
                    if file_date_match:
                        file_date = datetime.strptime(file_date_match.group(1), '%Y-%m-%d')
                        if file_date >= cutoff_date:
                            with open(memory_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                memory_data["daily_notes"].append({
                                    "date": file_date_match.group(1),
                                    "content": content[:2000],
                                    "size": len(content)
                                })
                except Exception as e:
                    pass
        
        return memory_data
    
    def scan_drafts(self) -> List[Dict[str, Any]]:
        """Scan for draft files (tweets, blog posts, etc.)."""
        drafts = []
        
        # Check workspace for draft files
        draft_patterns = [
            "**/*draft*.txt",
            "**/*draft*.md",
            "**/blog/**/*.md",
            "**/tweet*.txt"
        ]
        
        for pattern in draft_patterns:
            for draft_file in self.workspace_dir.glob(pattern):
                try:
                    with open(draft_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        drafts.append({
                            "path": str(draft_file.relative_to(self.workspace_dir)),
                            "content": content[:1000],  # Truncate
                            "size": len(content),
                            "modified": datetime.fromtimestamp(draft_file.stat().st_mtime).isoformat()
                        })
                except:
                    pass
        
        return drafts
    
    def scan_behavior_files(self) -> Dict[str, Any]:
        """Scan for behavior, desires, and taste files."""
        behavior_data = {
            "behavior": {},
            "desires": {},
            "tastes": {}
        }
        
        # Look for common behavior/desire files
        behavior_files = {
            "behavior": ["BEHAVIOR.md", "behavior.md", "workspace/BEHAVIOR.md"],
            "desires": ["DESIRES.md", "desires.md", "workspace/DESIRES.md"],
            "tastes": ["TASTES.md", "tastes.md", "workspace/TASTES.md", "PREFERENCES.md"]
        }
        
        for category, file_patterns in behavior_files.items():
            for pattern in file_patterns:
                file_path = self.workspace_dir / pattern if pattern.startswith("workspace/") else self.openclaw_home / pattern
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            behavior_data[category][pattern] = {
                                "content": content[:2000],
                                "size": len(content)
                            }
                    except:
                        pass
        
        return behavior_data
    
    def generate_summary(self, data: Dict[str, Any], period: str = "daily") -> str:
        """Generate a summary at the top of the note file."""
        summary_lines = []
        summary_lines.append(f"# {period.capitalize()} Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary_lines.append("")
        
        # Log summary
        if "logs" in data:
            logs = data["logs"]
            summary_lines.append(f"- **Logs**: {len(logs.get('errors', []))} errors, {len(logs.get('warnings', []))} warnings")
            summary_lines.append(f"- **Gateway Events**: {len(logs.get('gateway_events', []))} events")
            summary_lines.append(f"- **Subagent Activity**: {len(logs.get('subagent_spawns', []))} spawns")
        
        # Chat history summary
        if "chat_history" in data:
            chat_count = len(data["chat_history"])
            summary_lines.append(f"- **Chat Messages**: {chat_count} messages")
        
        # Memory summary
        if "memory" in data:
            memory = data["memory"]
            summary_lines.append(f"- **Daily Notes**: {len(memory.get('daily_notes', []))} files")
            summary_lines.append(f"- **Memory Files**: {len(memory.get('memories', []))} files")
        
        # Drafts summary
        if "drafts" in data:
            draft_count = len(data["drafts"])
            summary_lines.append(f"- **Drafts**: {draft_count} draft files")
        
        # Config summary
        if "config" in data and data["config"].get("exists"):
            summary_lines.append("- **Config**: Loaded successfully")
        
        summary_lines.append("")
        summary_lines.append("---")
        summary_lines.append("")
        
        return "\n".join(summary_lines)
    
    def generate_daily_note(self) -> Path:
        """Generate a daily note file."""
        today = datetime.now().strftime('%Y-%m-%d')
        note_file = self.daily_notes_dir / f"{today}.md"
        
        # Collect all data
        data = {
            "logs": self.scan_logs(days_back=1),
            "config": self.scan_config(),
            "chat_history": self.scan_chat_history(hours_back=24),
            "memory": self.scan_memory_files(days_back=1),
            "drafts": self.scan_drafts(),
            "behavior": self.scan_behavior_files()
        }
        
        # Generate note content
        content_lines = []
        content_lines.append(self.generate_summary(data, "daily"))
        content_lines.append("# Daily Note")
        content_lines.append("")
        
        # Logs section
        content_lines.append("## Logs")
        logs = data["logs"]
        if logs.get("errors"):
            content_lines.append(f"### Errors ({len(logs['errors'])})")
            for error in logs["errors"][:10]:  # Limit to 10
                content_lines.append(f"- {error.get('line', error.get('error', 'Unknown error'))[:200]}")
        if logs.get("warnings"):
            content_lines.append(f"### Warnings ({len(logs['warnings'])})")
            for warning in logs["warnings"][:10]:
                content_lines.append(f"- {warning.get('line', 'Unknown warning')[:200]}")
        content_lines.append("")
        
        # Chat history section
        content_lines.append("## Chat History")
        chat_history = data["chat_history"]
        if chat_history:
            content_lines.append(f"Found {len(chat_history)} messages in the last 24 hours.")
            # Group by role
            by_role = {}
            for msg in chat_history:
                role = msg.get("role", "unknown")
                if role not in by_role:
                    by_role[role] = []
                by_role[role].append(msg)
            for role, messages in by_role.items():
                content_lines.append(f"### {role.capitalize()} ({len(messages)} messages)")
                for msg in messages[:5]:  # Show first 5
                    content_lines.append(f"- {msg.get('content', '')[:150]}")
        else:
            content_lines.append("No recent chat history found.")
        content_lines.append("")
        
        # Memory section
        content_lines.append("## Memory Files")
        memory = data["memory"]
        if memory.get("daily_notes"):
            content_lines.append(f"### Daily Notes ({len(memory['daily_notes'])})")
            for note in memory["daily_notes"]:
                content_lines.append(f"- **{note['date']}**: {note['content'][:200]}...")
        content_lines.append("")
        
        # Drafts section
        content_lines.append("## Drafts")
        drafts = data["drafts"]
        if drafts:
            for draft in drafts:
                content_lines.append(f"### {draft['path']}")
                content_lines.append(f"- Size: {draft['size']} bytes")
                content_lines.append(f"- Modified: {draft['modified']}")
                content_lines.append(f"- Preview: {draft['content'][:200]}...")
        else:
            content_lines.append("No drafts found.")
        content_lines.append("")
        
        # Behavior section
        content_lines.append("## Behavior & Preferences")
        behavior = data["behavior"]
        if behavior.get("behavior"):
            content_lines.append("### Behavior Files")
            for file_path, file_data in behavior["behavior"].items():
                content_lines.append(f"- **{file_path}**: {file_data['content'][:200]}...")
        if behavior.get("desires"):
            content_lines.append("### Desires")
            for file_path, file_data in behavior["desires"].items():
                content_lines.append(f"- **{file_path}**: {file_data['content'][:200]}...")
        if behavior.get("tastes"):
            content_lines.append("### Tastes")
            for file_path, file_data in behavior["tastes"].items():
                content_lines.append(f"- **{file_path}**: {file_data['content'][:200]}...")
        content_lines.append("")
        
        # Config section
        content_lines.append("## Configuration")
        config = data["config"]
        if config.get("exists"):
            if config.get("model_preferences"):
                content_lines.append("### Model Preferences")
                if "default" in config["model_preferences"]:
                    content_lines.append(f"- Default: {config['model_preferences']['default']}")
                if "aliases" in config["model_preferences"]:
                    content_lines.append(f"- Aliases: {len(config['model_preferences']['aliases'])} configured")
        else:
            content_lines.append("Config file not found or not readable.")
        content_lines.append("")
        
        # Write file
        content = "\n".join(content_lines)
        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return note_file
    
    def generate_weekly_note(self) -> Path:
        """Generate a weekly note file."""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        note_file = self.weekly_notes_dir / f"{week_start.strftime('%Y-%m-%d')}.md"
        
        # Collect all data for the week
        data = {
            "logs": self.scan_logs(days_back=7),
            "config": self.scan_config(),
            "chat_history": self.scan_chat_history(hours_back=168),  # 7 days
            "memory": self.scan_memory_files(days_back=7),
            "drafts": self.scan_drafts(),
            "behavior": self.scan_behavior_files()
        }
        
        # Generate note content
        content_lines = []
        content_lines.append(self.generate_summary(data, "weekly"))
        content_lines.append(f"# Weekly Note - {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
        content_lines.append("")
        
        # Weekly summary
        content_lines.append("## Weekly Summary")
        content_lines.append("")
        
        # Logs summary
        logs = data["logs"]
        total_errors = len(logs.get("errors", []))
        total_warnings = len(logs.get("warnings", []))
        total_gateway_events = len(logs.get("gateway_events", []))
        total_spawns = len(logs.get("subagent_spawns", []))
        
        content_lines.append(f"- **Total Errors**: {total_errors}")
        content_lines.append(f"- **Total Warnings**: {total_warnings}")
        content_lines.append(f"- **Gateway Events**: {total_gateway_events}")
        content_lines.append(f"- **Subagent Spawns**: {total_spawns}")
        content_lines.append("")
        
        # Chat history summary
        chat_history = data["chat_history"]
        content_lines.append(f"## Chat Activity ({len(chat_history)} messages)")
        if chat_history:
            by_role = {}
            for msg in chat_history:
                role = msg.get("role", "unknown")
                if role not in by_role:
                    by_role[role] = []
                by_role[role].append(msg)
            for role, messages in by_role.items():
                content_lines.append(f"- **{role.capitalize()}**: {len(messages)} messages")
        content_lines.append("")
        
        # Memory summary
        memory = data["memory"]
        content_lines.append(f"## Memory Activity ({len(memory.get('daily_notes', []))} daily notes)")
        for note in memory.get("daily_notes", []):
            content_lines.append(f"- **{note['date']}**: {note['size']} bytes")
        content_lines.append("")
        
        # Drafts summary
        drafts = data["drafts"]
        content_lines.append(f"## Drafts ({len(drafts)} files)")
        for draft in drafts:
            content_lines.append(f"- **{draft['path']}**: {draft['size']} bytes (modified: {draft['modified']})")
        content_lines.append("")
        
        # Trends and patterns
        content_lines.append("## Trends & Patterns")
        content_lines.append("")
        if total_errors > 0:
            content_lines.append(f"- ⚠️ **Error Rate**: {total_errors} errors this week")
        if total_spawns > 0:
            content_lines.append(f"- 🤖 **Subagent Activity**: {total_spawns} spawns this week")
        if len(chat_history) > 0:
            content_lines.append(f"- 💬 **Chat Activity**: {len(chat_history)} messages this week")
        content_lines.append("")
        
        # Write file
        content = "\n".join(content_lines)
        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return note_file


def main():
    parser = argparse.ArgumentParser(description="Scribe - Comprehensive note-taking for OpenClaw")
    parser.add_argument("--mode", choices=["daily", "weekly", "both"], default="daily",
                       help="Generate daily, weekly, or both notes")
    parser.add_argument("--openclaw-home", type=str,
                       help="OpenClaw home directory (default: ~/.openclaw)")
    parser.add_argument("--json", action="store_true",
                       help="Output results in JSON format")
    args = parser.parse_args()
    
    openclaw_home = Path(args.openclaw_home) if args.openclaw_home else Path.home() / ".openclaw"
    
    scribe = Scribe(openclaw_home)
    
    results = {
        "daily_note": None,
        "weekly_note": None,
        "errors": []
    }
    
    try:
        if args.mode in ["daily", "both"]:
            daily_file = scribe.generate_daily_note()
            results["daily_note"] = str(daily_file)
        
        if args.mode in ["weekly", "both"]:
            weekly_file = scribe.generate_weekly_note()
            results["weekly_note"] = str(weekly_file)
    except Exception as e:
        results["errors"].append(str(e))
        if not args.json:
            print(f"Error: {e}", file=sys.stderr)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if results["daily_note"]:
            print(f"Daily note generated: {results['daily_note']}")
        if results["weekly_note"]:
            print(f"Weekly note generated: {results['weekly_note']}")
        if results["errors"]:
            print(f"Errors: {results['errors']}", file=sys.stderr)


if __name__ == "__main__":
    main()
