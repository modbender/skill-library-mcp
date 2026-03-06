#!/usr/bin/env python3
"""
ClawPressor - Session Context Compressor for OpenClaw
Compresses OpenClaw session files using intelligent summarization.
Reduces token usage by ~85-96% while preserving essential context.

Usage:
    python3 compress.py --dry-run    # Preview compression
    python3 compress.py --apply      # Apply compression
    python3 compress.py --restore    # Restore from backup
"""

import json
import os
import sys
import glob
import argparse
from datetime import datetime
from pathlib import Path

# Sumy imports for intelligent summarization
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lex_rank import LexRankSummarizer
    HAS_SUMY = True
except ImportError:
    HAS_SUMY = False
    print("⚠️  Sumy not installed. Falling back to truncation mode.")
    print("   Install with: pip install sumy")

# Configuration
DEFAULT_SESSION_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")
STATS_FILE = os.path.expanduser("~/.openclaw/workspace/memory/compression-stats.json")
MESSAGES_TO_KEEP = 5  # Always keep last N messages intact
SENTENCES_PER_SUMMARY = 5  # Number of sentences in summary
TOKENS_PER_CHAR = 0.25  # Rough estimate: 4 chars ≈ 1 token


class SessionCompressor:
    """Compresses OpenClaw session files using NLP summarization."""
    
    def __init__(self, lang="french"):
        self.lang = lang
        if HAS_SUMY:
            try:
                self.tokenizer = Tokenizer(lang)
                self.summarizer = LexRankSummarizer()
            except Exception as e:
                print(f"⚠️  Tokenizer error: {e}")
                print("   Using fallback mode.")
                self.tokenizer = None
                self.summarizer = None
        else:
            self.tokenizer = None
            self.summarizer = None
    
    def find_latest_session(self, session_dir=None):
        """Find the most recently modified session file."""
        if session_dir is None:
            session_dir = DEFAULT_SESSION_DIR
        
        jsonl_files = glob.glob(os.path.join(session_dir, "*.jsonl"))
        if not jsonl_files:
            return None
        
        # Sort by modification time (most recent first)
        jsonl_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        return jsonl_files[0]
    
    def load_session(self, filepath):
        """Load session file as list of JSON objects."""
        messages = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        messages.append(msg)
                    except json.JSONDecodeError:
                        continue
        return messages
    
    def summarize_text(self, text, num_sentences=SENTENCES_PER_SUMMARY):
        """Summarize text using Sumy LexRank algorithm."""
        if not HAS_SUMY or not self.tokenizer or not self.summarizer:
            # Fallback: truncate
            return text[:500] + "..." if len(text) > 500 else text
        
        try:
            parser = PlaintextParser.from_string(text, self.tokenizer)
            summary = self.summarizer(parser.document, num_sentences)
            return " ".join([str(s) for s in summary])
        except Exception as e:
            # Fallback on error
            return text[:500] + "..." if len(text) > 500 else text
    
    def extract_content(self, message):
        """Extract text content from a message."""
        content = ""
        
        # Try different content fields
        if 'content' in message:
            c = message['content']
            if isinstance(c, str):
                content = c
            elif isinstance(c, list):
                # Handle content as list of objects
                for item in c:
                    if isinstance(item, dict) and 'text' in item:
                        content += item['text'] + " "
        
        # Add tool calls info if present
        if 'tool_calls' in message:
            for tc in message['tool_calls']:
                if 'function' in tc:
                    fn = tc['function']
                    content += f" [Tool: {fn.get('name', 'unknown')}]"
        
        # Add tool results
        if 'tool_call_id' in message and 'content' in message:
            content += f" [Tool Result]"
        
        return content.strip()
    
    def compress_session(self, messages, keep_last=MESSAGES_TO_KEEP):
        """
        Compress session by summarizing old messages.
        Keeps last N messages intact for immediate context.
        """
        if len(messages) <= keep_last + 2:
            return messages, 0, 0
        
        # Split messages
        to_summarize = messages[:-keep_last]
        to_keep = messages[-keep_last:]
        
        # Extract all content from old messages
        all_content = []
        role_content = {}
        
        for msg in to_summarize:
            role = msg.get('role', 'unknown')
            content = self.extract_content(msg)
            
            if content:
                if role not in role_content:
                    role_content[role] = []
                role_content[role].append(content)
        
        # Create summary for each role
        summary_parts = []
        for role in ['system', 'user', 'assistant', 'tool']:
            if role in role_content:
                role_text = " ".join(role_content[role])
                if role_text:
                    summary = self.summarize_text(role_text, SENTENCES_PER_SUMMARY)
                    summary_parts.append(f"[{role.upper()}] {summary}")
        
        # Create compacted message
        compacted_content = "\n\n".join(summary_parts)
        compacted_message = {
            "role": "system",
            "content": f"[CONTEXT COMPACTED - Previous {len(to_summarize)} messages summarized]\n\n{compacted_content}",
            "_compacted": True,
            "_original_count": len(to_summarize),
            "_timestamp": datetime.now().isoformat()
        }
        
        # Build new message list
        new_messages = [compacted_message] + to_keep
        
        return new_messages, len(messages), len(new_messages)
    
    def save_session(self, filepath, messages, backup=True, compression_stats=None):
        """Save messages back to JSONL file."""
        if backup:
            backup_path = filepath + ".backup"
            if os.path.exists(filepath):
                os.rename(filepath, backup_path)
                print(f"💾 Backup created: {backup_path}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for msg in messages:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')
        
        # Log compression stats if provided
        if compression_stats:
            self.log_compression(
                compression_stats['original_count'],
                compression_stats['new_count'],
                compression_stats['before_stats'],
                compression_stats['after_stats']
            )
    
    def restore_backup(self, filepath):
        """Restore session from backup file."""
        backup_path = filepath + ".backup"
        if not os.path.exists(backup_path):
            print(f"❌ No backup found at {backup_path}")
            return False
        
        os.rename(backup_path, filepath)
        print(f"✅ Restored from backup: {filepath}")
        return True
    
    def get_stats(self, messages):
        """Get statistics about the session."""
        total_chars = sum(len(json.dumps(m)) for m in messages)
        roles = {}
        for m in messages:
            role = m.get('role', 'unknown')
            roles[role] = roles.get(role, 0) + 1
        
        return {
            'message_count': len(messages),
            'total_chars': total_chars,
            'total_kb': total_chars / 1024,
            'estimated_tokens': int(total_chars * TOKENS_PER_CHAR),
            'roles': roles
        }
    
    def log_compression(self, original_count, new_count, before_stats, after_stats):
        """Log compression stats to tracking file."""
        try:
            # Load existing stats
            stats = {'compressions': [], 'daily_summary': {}}
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
            
            # Calculate gains
            today = datetime.now().strftime('%Y-%m-%d')
            messages_saved = original_count - new_count
            chars_saved = before_stats['total_chars'] - after_stats['total_chars']
            tokens_saved = before_stats['estimated_tokens'] - after_stats['estimated_tokens']
            
            # Log this compression
            compression_entry = {
                'timestamp': datetime.now().isoformat(),
                'date': today,
                'messages_before': original_count,
                'messages_after': new_count,
                'messages_saved': messages_saved,
                'kb_before': round(before_stats['total_kb'], 2),
                'kb_after': round(after_stats['total_kb'], 2),
                'kb_saved': round(chars_saved / 1024, 2),
                'tokens_saved': tokens_saved
            }
            stats['compressions'].append(compression_entry)
            
            # Update daily summary
            if today not in stats['daily_summary']:
                stats['daily_summary'][today] = {
                    'compressions_count': 0,
                    'total_messages_saved': 0,
                    'total_kb_saved': 0,
                    'total_tokens_saved': 0
                }
            
            daily = stats['daily_summary'][today]
            daily['compressions_count'] += 1
            daily['total_messages_saved'] += messages_saved
            daily['total_kb_saved'] += round(chars_saved / 1024, 2)
            daily['total_tokens_saved'] += tokens_saved
            
            # Save stats
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            # Update Google Sheet if configured
            self._update_gsheet(compression_entry)
            
            return compression_entry
        except Exception as e:
            print(f"⚠️  Could not log stats: {e}")
            return None
    
    def _update_gsheet(self, compression_entry):
        """Update Google Sheet with new compression data if configured."""
        try:
            gsheets_id_file = os.path.expanduser("~/.openclaw/workspace/memory/gsheets_compression_id.txt")
            
            if not os.path.exists(gsheets_id_file):
                return  # No sheet configured, skip silently
            
            with open(gsheets_id_file, 'r') as f:
                spreadsheet_id = f.read().strip()
            
            # Import Google API
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
            except ImportError:
                return  # Google libs not available
            
            # Load credentials
            creds_file = os.path.expanduser("~/.openclaw/workspace/config/google_credentials.json")
            if not os.path.exists(creds_file):
                return
            
            with open(creds_file, 'r') as f:
                creds_data = json.load(f)
            
            creds = Credentials.from_authorized_user_info(creds_data)
            service = build('sheets', 'v4', credentials=creds)
            
            # Append to details sheet
            row = [
                compression_entry['timestamp'][:19],
                compression_entry['date'],
                compression_entry['messages_before'],
                compression_entry['messages_after'],
                compression_entry['kb_before'],
                compression_entry['kb_after'],
                compression_entry['tokens_saved']
            ]
            
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Détails par Compression!A:G',
                valueInputOption='RAW',
                body={'values': [row]}
            ).execute()
            
            # Update daily summary sheet
            # First, find if this date already exists
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Résumé Quotidien!A:A'
            ).execute()
            
            values = result.get('values', [])
            date_row = None
            for i, row_vals in enumerate(values):
                if row_vals and row_vals[0] == compression_entry['date']:
                    date_row = i + 1
                    break
            
            if date_row:
                # Update existing row
                range_name = f'Résumé Quotidien!A{date_row}:E{date_row}'
                stats = self.get_daily_stats(days=1)
                if stats and compression_entry['date'] in stats:
                    day = stats[compression_entry['date']]
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=range_name,
                        valueInputOption='RAW',
                        body={'values': [[
                            compression_entry['date'],
                            day['compressions_count'],
                            day['total_messages_saved'],
                            day['total_tokens_saved'],
                            round(day['total_kb_saved'], 2)
                        ]]}
                    ).execute()
            else:
                # Append new row
                stats = self.get_daily_stats(days=1)
                if stats and compression_entry['date'] in stats:
                    day = stats[compression_entry['date']]
                    service.spreadsheets().values().append(
                        spreadsheetId=spreadsheet_id,
                        range='Résumé Quotidien!A:E',
                        valueInputOption='RAW',
                        body={'values': [[
                            compression_entry['date'],
                            day['compressions_count'],
                            day['total_messages_saved'],
                            day['total_tokens_saved'],
                            round(day['total_kb_saved'], 2)
                        ]]}
                    ).execute()
            
            print(f"   📊 Google Sheet updated")
            
        except Exception as e:
            # Silently fail - don't break compression if sheet update fails
            pass
    
    def get_daily_stats(self, days=7):
        """Get compression stats for the last N days."""
        try:
            if not os.path.exists(STATS_FILE):
                return None
            
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            
            # Get last N days
            daily = stats.get('daily_summary', {})
            sorted_days = sorted(daily.keys(), reverse=True)[:days]
            
            return {day: daily[day] for day in sorted_days}
        except Exception as e:
            print(f"⚠️  Could not read stats: {e}")
            return None


def format_number(n):
    """Format large numbers with separators."""
    return f"{n:,}".replace(",", " ")


def main():
    parser = argparse.ArgumentParser(
        description="ClawPressor - Compress OpenClaw session context",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dry-run           # Preview compression without changes
  %(prog)s --apply             # Compress the session
  %(prog)s --restore           # Restore from backup
  %(prog)s --session FILE      # Target specific session file
  %(prog)s --stats             # Show daily compression stats
        """
    )
    parser.add_argument('--session', '-s', help='Path to specific session file')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Preview only, no changes')
    parser.add_argument('--apply', '-a', action='store_true', help='Apply compression')
    parser.add_argument('--restore', '-r', action='store_true', help='Restore from backup')
    parser.add_argument('--stats', action='store_true', help='Show compression statistics')
    parser.add_argument('--keep', '-k', type=int, default=MESSAGES_TO_KEEP, 
                        help=f'Number of recent messages to keep (default: {MESSAGES_TO_KEEP})')
    
    args = parser.parse_args()
    
    compressor = SessionCompressor()
    
    # Handle stats display
    if args.stats:
        daily_stats = compressor.get_daily_stats(days=7)
        if not daily_stats:
            print("📊 No compression stats yet.")
            print(f"   Stats file: {STATS_FILE}")
            sys.exit(0)
        
        print("📈 Compression Statistics (Last 7 Days)")
        print("=" * 50)
        
        total_compressions = 0
        total_tokens_saved = 0
        total_kb_saved = 0
        
        for date, day_stats in sorted(daily_stats.items(), reverse=True):
            count = day_stats['compressions_count']
            tokens = day_stats['total_tokens_saved']
            kb = day_stats['total_kb_saved']
            
            total_compressions += count
            total_tokens_saved += tokens
            total_kb_saved += kb
            
            print(f"\n📅 {date}:")
            print(f"   Compressions: {count}")
            print(f"   Messages saved: {day_stats['total_messages_saved']}")
            print(f"   KB saved: {kb:.1f} KB")
            print(f"   Tokens saved: ~{format_number(tokens)}")
        
        print("\n" + "=" * 50)
        print(f"📊 TOTAL (7 days):")
        print(f"   {total_compressions} compressions")
        print(f"   {total_kb_saved:.1f} KB saved")
        print(f"   ~{format_number(total_tokens_saved)} tokens saved")
        print(f"   💰 Est. savings: ${total_tokens_saved * 0.000003:.2f} - ${total_tokens_saved * 0.000015:.2f}")
        sys.exit(0)
    
    # Find session file
    if args.session:
        session_file = args.session
    else:
        session_file = compressor.find_latest_session()
    
    if not session_file or not os.path.exists(session_file):
        print("❌ No session file found!")
        print(f"   Searched in: {DEFAULT_SESSION_DIR}")
        sys.exit(1)
    
    print(f"🎯 Session: {os.path.basename(session_file)}")
    print(f"   Path: {session_file}")
    
    # Handle restore
    if args.restore:
        if compressor.restore_backup(session_file):
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Load session
    messages = compressor.load_session(session_file)
    
    if not messages:
        print("❌ Session file is empty!")
        sys.exit(1)
    
    # Get before stats
    before_stats = compressor.get_stats(messages)
    print(f"\n📊 Current session: {before_stats['message_count']} messages, {before_stats['total_kb']:.1f} KB")
    print(f"   Estimated tokens: ~{format_number(before_stats['estimated_tokens'])}")
    
    # Compress
    new_messages, original_count, new_count = compressor.compress_session(messages, args.keep)
    
    # Get after stats
    after_stats = compressor.get_stats(new_messages)
    reduction = (1 - new_count / original_count) * 100 if original_count > 0 else 0
    tokens_saved = before_stats['estimated_tokens'] - after_stats['estimated_tokens']
    
    print(f"\n📈 Compression preview:")
    print(f"   Messages: {original_count} → {new_count} ({reduction:.1f}% reduction)")
    print(f"   Size: {before_stats['total_kb']:.1f} KB → {after_stats['total_kb']:.1f} KB")
    print(f"   Tokens saved: ~{format_number(tokens_saved)}")
    
    if new_count < original_count:
        print(f"\n📝 Summary preview:")
        summary_msg = new_messages[0]
        preview = summary_msg.get('content', '')[:300]
        print(f"   {preview}...")
    
    # Apply or dry-run
    if args.apply:
        compression_stats = {
            'original_count': original_count,
            'new_count': new_count,
            'before_stats': before_stats,
            'after_stats': after_stats
        }
        compressor.save_session(session_file, new_messages, backup=True, compression_stats=compression_stats)
        print(f"\n✅ Compression applied!")
        print(f"   💾 Backup saved as: {session_file}.backup")
        print(f"   📊 Logged: {format_number(tokens_saved)} tokens saved")
    else:
        print(f"\n🔍 DRY RUN - No changes made")
        print(f"   Use --apply to compress the session")


if __name__ == "__main__":
    main()
