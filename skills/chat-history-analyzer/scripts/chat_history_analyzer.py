#!/usr/bin/env python3
"""
Chat History Analyzer - Extracts and analyzes Cursor IDE chat history.

Extracts chat history from Cursor's SQLite databases, analyzes the last hour
for key discoveries, obstacles, and solutions, and saves findings to the journal.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


class ChatHistoryAnalyzer:
    def __init__(self, openclaw_home: Path):
        self.openclaw_home = openclaw_home
        self.journal_dir = openclaw_home / "journal"
        self.cursor_storage = Path.home() / "Library" / "Application Support" / "Cursor" / "User"
        self.global_db = self.cursor_storage / "globalStorage" / "state.vscdb"
        self.workspace_storage = self.cursor_storage / "workspaceStorage"
        
    def extract_chat_history(self, hours_back: float = 1.0) -> List[Dict[str, Any]]:
        """Extract chat history from Cursor's SQLite databases."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        all_messages = []
        
        # Try global storage first
        if self.global_db.exists():
            try:
                conn = sqlite3.connect(str(self.global_db))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Query for chat history keys
                cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%chat%' OR key LIKE '%ai%' OR key LIKE '%history%'")
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
                        elif isinstance(value, dict):
                            if 'messages' in value:
                                all_messages.extend(self._extract_messages_from_conversation(value, cutoff_time))
                            elif 'role' in value or 'message' in value:
                                msg = self._normalize_message(value, cutoff_time)
                                if msg:
                                    all_messages.append(msg)
                    except (json.JSONDecodeError, KeyError, TypeError):
                        continue
                
                conn.close()
            except sqlite3.Error as e:
                print(f"Error reading global database: {e}", file=sys.stderr)
        
        # Try workspace-specific databases
        if self.workspace_storage.exists():
            for workspace_dir in self.workspace_storage.iterdir():
                workspace_db = workspace_dir / "state.vscdb"
                if workspace_db.exists():
                    try:
                        conn = sqlite3.connect(str(workspace_db))
                        conn.row_factory = sqlite3.Row
                        cursor = conn.cursor()
                        
                        cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%chat%' OR key LIKE '%ai%' OR key LIKE '%history%'")
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
                                elif isinstance(value, dict):
                                    if 'messages' in value:
                                        all_messages.extend(self._extract_messages_from_conversation(value, cutoff_time))
                                    elif 'role' in value or 'message' in value:
                                        msg = self._normalize_message(value, cutoff_time)
                                        if msg:
                                            all_messages.append(msg)
                            except (json.JSONDecodeError, KeyError, TypeError):
                                continue
                        
                        conn.close()
                    except sqlite3.Error:
                        continue
        
        # Sort by timestamp
        all_messages.sort(key=lambda x: x.get('timestamp', 0))
        return all_messages
    
    def _extract_messages_from_conversation(self, conversation: Dict[str, Any], cutoff_time: datetime) -> List[Dict[str, Any]]:
        """Extract messages from a conversation object."""
        messages = []
        if 'messages' in conversation:
            for msg in conversation['messages']:
                normalized = self._normalize_message(msg, cutoff_time)
                if normalized:
                    messages.append(normalized)
        return messages
    
    def _normalize_message(self, msg: Dict[str, Any], cutoff_time: datetime) -> Optional[Dict[str, Any]]:
        """Normalize a message object and filter by time."""
        try:
            # Try to extract timestamp
            timestamp = None
            if 'timestamp' in msg:
                ts_val = msg['timestamp']
                if isinstance(ts_val, (int, float)):
                    timestamp = datetime.fromtimestamp(ts_val / 1000 if ts_val > 1e10 else ts_val, tz=timezone.utc)
                elif isinstance(ts_val, str):
                    try:
                        timestamp = datetime.fromisoformat(ts_val.replace('Z', '+00:00'))
                    except ValueError:
                        pass
            elif 'createdAt' in msg:
                ts_val = msg['createdAt']
                if isinstance(ts_val, (int, float)):
                    timestamp = datetime.fromtimestamp(ts_val / 1000 if ts_val > 1e10 else ts_val, tz=timezone.utc)
            
            # If no timestamp found, skip (we can't filter it)
            if timestamp is None:
                return None
            
            # Filter by cutoff time
            if timestamp < cutoff_time:
                return None
            
            # Extract role and content
            role = msg.get('role', msg.get('author', 'unknown'))
            content = msg.get('content', msg.get('message', msg.get('text', '')))
            
            if not content:
                return None
            
            return {
                'role': role,
                'content': content if isinstance(content, str) else json.dumps(content),
                'timestamp': timestamp.isoformat(),
                'timestamp_epoch': timestamp.timestamp()
            }
        except (KeyError, ValueError, TypeError):
            return None
    
    def analyze_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze messages for discoveries, obstacles, and solutions."""
        discoveries = []
        obstacles = []
        solutions = []
        
        # Patterns for identifying different types of content
        discovery_patterns = [
            r'\b(found|discovered|learned|realized|figured out|understood|noticed)\b',
            r'\b(insight|discovery|finding|realization)\b',
            r'\b(works|working|success|succeeded|fixed|resolved)\b',
            r'\b(created|built|implemented|added|made)\b',
        ]
        
        obstacle_patterns = [
            r'\b(error|failed|failure|issue|problem|bug|broken)\b',
            r'\b(can\'t|cannot|couldn\'t|unable to|stuck|blocked)\b',
            r'\b(confused|don\'t understand|unclear|doesn\'t work)\b',
            r'\b(timeout|disconnected|unauthorized|403|404|500)\b',
        ]
        
        solution_patterns = [
            r'\b(solution|fix|resolved|fixed|solved|workaround)\b',
            r'\b(changed|updated|modified|replaced|switched)\b',
            r'\b(installed|configured|set up|enabled)\b',
            r'\b(should|need to|try|use|instead)\b',
        ]
        
        for msg in messages:
            content = msg.get('content', '').lower()
            role = msg.get('role', '').lower()
            
            # Skip very short messages
            if len(content) < 20:
                continue
            
            # Check for discoveries (usually in assistant or user messages about success)
            for pattern in discovery_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if role in ['assistant', 'user']:
                        discoveries.append({
                            'content': msg['content'][:500],  # Truncate long messages
                            'timestamp': msg['timestamp'],
                            'role': msg['role']
                        })
                    break
            
            # Check for obstacles (usually in user messages or error reports)
            for pattern in obstacle_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if role in ['user', 'system']:
                        obstacles.append({
                            'content': msg['content'][:500],
                            'timestamp': msg['timestamp'],
                            'role': msg['role']
                        })
                    break
            
            # Check for solutions (usually in assistant messages or follow-up user messages)
            for pattern in solution_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if role in ['assistant', 'user']:
                        solutions.append({
                            'content': msg['content'][:500],
                            'timestamp': msg['timestamp'],
                            'role': msg['role']
                        })
                    break
        
        return {
            'discoveries': discoveries[:10],  # Limit to top 10
            'obstacles': obstacles[:10],
            'solutions': solutions[:10],
            'total_messages': len(messages),
            'analysis_time': datetime.now(timezone.utc).isoformat()
        }
    
    def save_to_journal(self, analysis: Dict[str, Any]) -> Path:
        """Save analysis results to journal directory."""
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a dated journal entry
        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        journal_file = self.journal_dir / f"chat_analysis_{today}_{timestamp}.md"
        
        with open(journal_file, 'w') as f:
            f.write(f"# Chat History Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Analysis Period:** Last hour\n")
            f.write(f"**Total Messages Analyzed:** {analysis['total_messages']}\n\n")
            
            if analysis['discoveries']:
                f.write("## 🔍 Key Discoveries\n\n")
                for i, disc in enumerate(analysis['discoveries'], 1):
                    f.write(f"{i}. **{disc['role'].title()}** ({disc['timestamp'][:19]}):\n")
                    f.write(f"   {disc['content']}\n\n")
            
            if analysis['obstacles']:
                f.write("## ⚠️ Obstacles Encountered\n\n")
                for i, obs in enumerate(analysis['obstacles'], 1):
                    f.write(f"{i}. **{obs['role'].title()}** ({obs['timestamp'][:19]}):\n")
                    f.write(f"   {obs['content']}\n\n")
            
            if analysis['solutions']:
                f.write("## ✅ Solutions Found\n\n")
                for i, sol in enumerate(analysis['solutions'], 1):
                    f.write(f"{i}. **{sol['role'].title()}** ({sol['timestamp'][:19]}):\n")
                    f.write(f"   {sol['content']}\n\n")
            
            if not analysis['discoveries'] and not analysis['obstacles'] and not analysis['solutions']:
                f.write("## No significant discoveries, obstacles, or solutions found in the last hour.\n\n")
        
        return journal_file


def main():
    parser = argparse.ArgumentParser(description="Analyze Cursor IDE chat history and save findings to journal.")
    parser.add_argument("--hours", type=float, default=1.0, help="Hours of history to analyze (default: 1.0)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--openclaw-home", type=str, help="OpenClaw home directory (default: ~/.openclaw)")
    args = parser.parse_args()
    
    openclaw_home = Path(args.openclaw_home) if args.openclaw_home else Path.home() / ".openclaw"
    
    analyzer = ChatHistoryAnalyzer(openclaw_home)
    
    try:
        messages = analyzer.extract_chat_history(hours_back=args.hours)
        analysis = analyzer.analyze_messages(messages)
        journal_file = analyzer.save_to_journal(analysis)
        
        if args.json:
            output = {
                'messages_analyzed': analysis['total_messages'],
                'discoveries_count': len(analysis['discoveries']),
                'obstacles_count': len(analysis['obstacles']),
                'solutions_count': len(analysis['solutions']),
                'journal_file': str(journal_file),
                'analysis': analysis
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"Analyzed {analysis['total_messages']} messages from the last {args.hours} hour(s)")
            print(f"Found {len(analysis['discoveries'])} discoveries, {len(analysis['obstacles'])} obstacles, {len(analysis['solutions'])} solutions")
            print(f"Saved to: {journal_file}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
