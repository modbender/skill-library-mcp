#!/usr/bin/env python3
"""
Apple Notes Monitor - Real-time monitoring and extraction
"""

import argparse
import json
import time
import subprocess
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

class NotesMonitor:
    def __init__(self, config_path="configs/monitor.json", extractor_config="configs/extractor.json"):
        self.config_path = Path(config_path)
        self.extractor_config_path = Path(extractor_config)
        self.script_dir = Path(__file__).parent
        self.root_dir = self.script_dir.parent
        
        self.config = self.load_config()
        self.running = False
        self.last_check = datetime.now()
        self.known_notes = {}
        
        # Set up signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Load existing notes state
        self.load_known_notes()
        
    def load_config(self):
        """Load monitor configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        
        # Default configuration
        return {
            "monitoring": {
                "enabled": True,
                "check_interval_minutes": 30,
                "detect_changes": True,
                "auto_extract_new": True
            },
            "triggers": {
                "new_note_threshold": 1,
                "modification_threshold": 5,
                "batch_processing": True
            },
            "notifications": {
                "enabled": True,
                "methods": ["console"],
                "webhook_url": None
            }
        }
    
    def load_known_notes(self):
        """Load the state of previously seen notes"""
        state_file = self.root_dir / "output" / "monitor_state.json"
        if state_file.exists():
            try:
                with open(state_file) as f:
                    state = json.load(f)
                    self.known_notes = state.get("known_notes", {})
                    self.last_check = datetime.fromisoformat(
                        state.get("last_check", datetime.now().isoformat())
                    )
                print(f"📊 Loaded state: {len(self.known_notes)} known notes")
            except Exception as e:
                print(f"⚠️ Error loading monitor state: {e}")
                self.known_notes = {}
        else:
            print("🔄 Starting fresh monitoring session")
    
    def save_state(self):
        """Save the current monitoring state"""
        state_file = self.root_dir / "output" / "monitor_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "known_notes": self.known_notes,
            "last_check": self.last_check.isoformat(),
            "monitor_version": "1.0"
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_current_notes_state(self):
        """Get the current state of all notes via AppleScript"""
        applescript = '''
        tell application "Notes"
            set noteList to {}
            repeat with eachNote in every note
                try
                    set noteTitle to the name of eachNote
                    set noteModified to the modification date of eachNote
                    set noteCreated to the creation date of eachNote
                    
                    -- Create a simple hash of the note content for change detection
                    set noteBody to the body of eachNote
                    set noteSize to length of noteBody
                    
                    set noteInfo to noteTitle & "|" & (noteCreated as string) & "|" & (noteModified as string) & "|" & (noteSize as string)
                    set end of noteList to noteInfo
                end try
            end repeat
            
            return noteList as string
        end tell
        '''
        
        try:
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"❌ Error getting notes state: {result.stderr}")
                return {}
            
            # Parse the result
            current_state = {}
            for line in result.stdout.strip().split(', '):
                if '|' in line:
                    try:
                        title, created, modified, size = line.split('|')
                        note_id = hashlib.md5((title + created).encode()).hexdigest()
                        current_state[note_id] = {
                            'title': title,
                            'created': created,
                            'modified': modified,
                            'size': int(size),
                            'last_seen': datetime.now().isoformat()
                        }
                    except ValueError:
                        continue
            
            return current_state
            
        except subprocess.TimeoutExpired:
            print("⏰ Timeout getting notes state")
            return {}
        except Exception as e:
            print(f"❌ Error getting notes state: {e}")
            return {}
    
    def detect_changes(self, current_state):
        """Detect new and modified notes"""
        new_notes = []
        modified_notes = []
        
        for note_id, note_info in current_state.items():
            if note_id not in self.known_notes:
                # New note
                new_notes.append({
                    'id': note_id,
                    'title': note_info['title'],
                    'type': 'new'
                })
            else:
                # Check if modified
                known_note = self.known_notes[note_id]
                if (note_info['modified'] != known_note['modified'] or 
                    note_info['size'] != known_note['size']):
                    modified_notes.append({
                        'id': note_id,
                        'title': note_info['title'],
                        'type': 'modified',
                        'old_modified': known_note['modified'],
                        'new_modified': note_info['modified']
                    })
        
        return new_notes, modified_notes
    
    def notify(self, message, level="info"):
        """Send notifications based on configuration"""
        if not self.config.get("notifications", {}).get("enabled", False):
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        methods = self.config.get("notifications", {}).get("methods", ["console"])
        
        if "console" in methods:
            if level == "info":
                print(f"ℹ️ {formatted_message}")
            elif level == "warning":
                print(f"⚠️ {formatted_message}")
            elif level == "success":
                print(f"✅ {formatted_message}")
            else:
                print(formatted_message)
        
        # Add webhook support if configured
        webhook_url = self.config.get("notifications", {}).get("webhook_url")
        if webhook_url and "webhook" in methods:
            try:
                import requests
                payload = {
                    "message": formatted_message,
                    "level": level,
                    "timestamp": datetime.now().isoformat()
                }
                requests.post(webhook_url, json=payload, timeout=5)
            except Exception as e:
                print(f"⚠️ Webhook notification failed: {e}")
    
    def trigger_extraction(self, reason="scheduled"):
        """Trigger a note extraction"""
        self.notify(f"Triggering extraction: {reason}")
        
        try:
            # Run the main extraction script
            extractor_script = self.script_dir / "extract-notes.py"
            result = subprocess.run([
                sys.executable, str(extractor_script),
                "--method", "auto",
                "--config", str(self.extractor_config_path)
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                self.notify("Extraction completed successfully", "success")
                return True
            else:
                self.notify(f"Extraction failed: {result.stderr}", "warning")
                return False
                
        except subprocess.TimeoutExpired:
            self.notify("Extraction timed out", "warning")
            return False
        except Exception as e:
            self.notify(f"Error during extraction: {e}", "warning")
            return False
    
    def check_notes(self):
        """Check for note changes and trigger actions"""
        if not self.config.get("monitoring", {}).get("enabled", True):
            return
        
        current_state = self.get_current_notes_state()
        if not current_state:
            self.notify("Failed to get current notes state", "warning")
            return
        
        if not self.known_notes:
            # First run - just record the current state
            self.known_notes = current_state
            self.notify(f"Initial monitoring setup: tracking {len(current_state)} notes")
            self.save_state()
            return
        
        # Detect changes
        new_notes, modified_notes = self.detect_changes(current_state)
        
        # Update known state
        self.known_notes = current_state
        self.last_check = datetime.now()
        self.save_state()
        
        # Report changes
        if new_notes:
            self.notify(f"Found {len(new_notes)} new notes")
            for note in new_notes[:3]:  # Show first 3
                self.notify(f"  📝 New: {note['title']}")
        
        if modified_notes:
            self.notify(f"Found {len(modified_notes)} modified notes")
            for note in modified_notes[:3]:  # Show first 3
                self.notify(f"  📝 Modified: {note['title']}")
        
        # Trigger extraction if thresholds are met
        auto_extract = self.config.get("monitoring", {}).get("auto_extract_new", True)
        new_threshold = self.config.get("triggers", {}).get("new_note_threshold", 1)
        mod_threshold = self.config.get("triggers", {}).get("modification_threshold", 5)
        
        if auto_extract and (len(new_notes) >= new_threshold or len(modified_notes) >= mod_threshold):
            changes = len(new_notes) + len(modified_notes)
            self.trigger_extraction(f"{changes} note changes detected")
    
    def run_daemon(self):
        """Run the monitoring daemon"""
        self.running = True
        interval_minutes = self.config.get("monitoring", {}).get("check_interval_minutes", 30)
        
        print(f"🔄 Starting Notes monitoring daemon")
        print(f"   Check interval: {interval_minutes} minutes")
        print(f"   Press Ctrl+C to stop")
        
        self.notify("Notes monitoring started")
        
        while self.running:
            try:
                self.check_notes()
                
                # Sleep for the configured interval
                for _ in range(interval_minutes * 60):  # Convert to seconds
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.notify(f"Error during monitoring cycle: {e}", "warning")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down monitor...")
        self.running = False
        self.save_state()
        self.notify("Notes monitoring stopped")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Monitor Apple Notes for changes")
    parser.add_argument(
        "--daemon", "-d",
        action="store_true",
        help="Run as a background daemon"
    )
    parser.add_argument(
        "--check-once",
        action="store_true",
        help="Perform one check and exit"
    )
    parser.add_argument(
        "--config",
        default="configs/monitor.json",
        help="Monitor configuration file"
    )
    parser.add_argument(
        "--extract-config",
        default="configs/extractor.json",
        help="Extraction configuration file"
    )
    
    args = parser.parse_args()
    
    monitor = NotesMonitor(args.config, args.extract_config)
    
    if args.check_once:
        print("🔍 Performing one-time check...")
        monitor.check_notes()
        print("✅ Check completed")
    elif args.daemon:
        monitor.run_daemon()
    else:
        print("📖 Use --daemon to run as a monitoring daemon")
        print("    Use --check-once to perform a single check")
        print("    See --help for more options")

if __name__ == "__main__":
    main()