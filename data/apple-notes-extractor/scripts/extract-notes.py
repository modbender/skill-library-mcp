#!/usr/bin/env python3
"""
Apple Notes Extraction System
Main orchestration script for extracting Apple Notes content
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import sqlite3
import hashlib

class AppleNotesExtractor:
    def __init__(self, output_dir="output", config_path="configs/extractor.json"):
        self.output_dir = Path(output_dir)
        self.config_path = Path(config_path)
        self.script_dir = Path(__file__).parent
        self.root_dir = self.script_dir.parent
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "json").mkdir(exist_ok=True)
        (self.output_dir / "markdown").mkdir(exist_ok=True)
        (self.output_dir / "attachments").mkdir(exist_ok=True)
        
        self.config = self.load_config()
        
    def load_config(self):
        """Load extraction configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            "methods": {
                "simple": {
                    "enabled": True,
                    "timeout": 30,
                    "include_metadata": True
                },
                "full": {
                    "enabled": True,
                    "timeout": 300,
                    "extract_attachments": True,
                    "preserve_formatting": True
                }
            },
            "output": {
                "formats": ["json", "markdown"],
                "compress_attachments": False,
                "max_note_size_mb": 10
            },
            "privacy": {
                "exclude_patterns": ["password", "secret", "private"],
                "encrypt_sensitive": False
            }
        }
        
        # Save default config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        return default_config
    
    def extract_simple(self):
        """Extract notes using AppleScript/JXA method"""
        print("🔍 Extracting notes using simple method...")
        
        applescript = '''
        tell application "Notes"
            set noteList to {}
            repeat with eachNote in every note
                try
                    set noteTitle to the name of eachNote
                    set noteBody to the body of eachNote
                    set noteCreated to the creation date of eachNote
                    set noteModified to the modification date of eachNote
                    set noteAccount to the name of the account of eachNote
                    set noteFolder to ""
                    try
                        set noteFolder to the name of the folder of eachNote
                    end try
                    
                    set noteData to "NOTESEP_START" & return & ¬
                        "TITLE: " & noteTitle & return & ¬
                        "CREATED: " & noteCreated & return & ¬
                        "MODIFIED: " & noteModified & return & ¬
                        "ACCOUNT: " & noteAccount & return & ¬
                        "FOLDER: " & noteFolder & return & ¬
                        "BODY_START" & return & ¬
                        noteBody & return & ¬
                        "BODY_END" & return & ¬
                        "NOTESEP_END" & return
                    
                    set end of noteList to noteData
                end try
            end repeat
            
            return (noteList as string)
        end tell
        '''
        
        try:
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                timeout=self.config["methods"]["simple"]["timeout"]
            )
            
            if result.returncode != 0:
                print(f"❌ AppleScript error: {result.stderr}")
                return False
                
            return self.process_simple_output(result.stdout)
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Simple extraction timed out after {self.config['methods']['simple']['timeout']} seconds")
            return False
        except Exception as e:
            print(f"❌ Error during simple extraction: {e}")
            return False
    
    def process_simple_output(self, raw_output):
        """Process the raw AppleScript output into structured data"""
        notes = []
        note_blocks = raw_output.split("NOTESEP_START")
        
        for block in note_blocks[1:]:  # Skip first empty block
            if "NOTESEP_END" not in block:
                continue
                
            try:
                # Extract note data
                lines = block.split('\n')
                note_data = {}
                body_started = False
                body_lines = []
                
                for line in lines:
                    if line.startswith("TITLE: "):
                        note_data['title'] = line[7:]
                    elif line.startswith("CREATED: "):
                        note_data['created'] = line[9:]
                    elif line.startswith("MODIFIED: "):
                        note_data['modified'] = line[10:]
                    elif line.startswith("ACCOUNT: "):
                        note_data['account'] = line[9:]
                    elif line.startswith("FOLDER: "):
                        note_data['folder'] = line[8:]
                    elif line == "BODY_START":
                        body_started = True
                    elif line == "BODY_END":
                        body_started = False
                    elif body_started:
                        body_lines.append(line)
                
                note_data['body'] = '\n'.join(body_lines)
                note_data['extraction_method'] = 'simple'
                note_data['extraction_date'] = datetime.now().isoformat()
                note_data['id'] = hashlib.md5(
                    (note_data.get('title', '') + note_data.get('created', '')).encode()
                ).hexdigest()
                
                # Check for sensitive content
                if not self.is_sensitive_note(note_data):
                    notes.append(note_data)
                    
            except Exception as e:
                print(f"⚠️ Error processing note block: {e}")
                continue
        
        # Save results
        self.save_notes(notes, "simple")
        print(f"✅ Extracted {len(notes)} notes using simple method")
        return True
    
    def extract_full(self):
        """Extract notes using the comprehensive Ruby parser"""
        print("🔍 Extracting notes using full method (Ruby parser)...")
        
        # Check if Ruby parser is available
        parser_path = self.root_dir / "tools" / "apple_cloud_notes_parser"
        if not parser_path.exists():
            print("📦 Ruby parser not found, installing...")
            if not self.install_ruby_parser():
                print("❌ Failed to install Ruby parser")
                return False
        
        try:
            # Run the Ruby parser
            output_file = self.output_dir / "full_extraction.json"
            cmd = [
                "ruby", str(parser_path / "notes_cloud_ripper.rb"),
                "--export-json", str(output_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config["methods"]["full"]["timeout"],
                cwd=str(parser_path)
            )
            
            if result.returncode != 0:
                print(f"❌ Ruby parser error: {result.stderr}")
                return False
            
            return self.process_full_output(output_file)
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Full extraction timed out after {self.config['methods']['full']['timeout']} seconds")
            return False
        except Exception as e:
            print(f"❌ Error during full extraction: {e}")
            return False
    
    def install_ruby_parser(self):
        """Install the Apple Cloud Notes Parser"""
        tools_dir = self.root_dir / "tools"
        tools_dir.mkdir(exist_ok=True)
        
        try:
            # Clone the repository
            subprocess.run([
                "git", "clone",
                "https://github.com/threeplanetssoftware/apple_cloud_notes_parser.git"
            ], cwd=str(tools_dir), check=True)
            
            # Install Ruby dependencies
            parser_dir = tools_dir / "apple_cloud_notes_parser"
            subprocess.run([
                "bundle", "install"
            ], cwd=str(parser_dir), check=True)
            
            print("✅ Ruby parser installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Ruby parser: {e}")
            return False
    
    def process_full_output(self, output_file):
        """Process the Ruby parser JSON output"""
        if not output_file.exists():
            print(f"❌ Full extraction output file not found: {output_file}")
            return False
        
        try:
            with open(output_file) as f:
                data = json.load(f)
            
            # Process and normalize the data
            notes = []
            for note in data.get('notes', []):
                processed_note = {
                    'id': note.get('Z_PK', str(hash(note.get('ZTITLE', '')))),
                    'title': note.get('ZTITLE', ''),
                    'body': note.get('ZBODY', ''),
                    'created': note.get('ZCREATIONDATE'),
                    'modified': note.get('ZMODIFICATIONDATE'),
                    'folder': note.get('ZFOLDER', {}).get('ZTITLE', ''),
                    'account': note.get('ZACCOUNT', {}).get('ZNAME', ''),
                    'extraction_method': 'full',
                    'extraction_date': datetime.now().isoformat(),
                    'attachments': note.get('attachments', [])
                }
                
                # Check for sensitive content
                if not self.is_sensitive_note(processed_note):
                    notes.append(processed_note)
            
            self.save_notes(notes, "full")
            print(f"✅ Extracted {len(notes)} notes using full method")
            return True
            
        except Exception as e:
            print(f"❌ Error processing full extraction output: {e}")
            return False
    
    def is_sensitive_note(self, note):
        """Check if a note contains sensitive content based on configuration"""
        exclude_patterns = self.config.get("privacy", {}).get("exclude_patterns", [])
        
        content = f"{note.get('title', '')} {note.get('body', '')}".lower()
        
        for pattern in exclude_patterns:
            if pattern.lower() in content:
                print(f"🔒 Skipping sensitive note: {note.get('title', 'Untitled')}")
                return True
        
        return False
    
    def save_notes(self, notes, method):
        """Save notes in configured output formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        if "json" in self.config["output"]["formats"]:
            json_file = self.output_dir / "json" / f"notes_{method}_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(notes, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved JSON: {json_file}")
        
        # Save as Markdown
        if "markdown" in self.config["output"]["formats"]:
            md_file = self.output_dir / "markdown" / f"notes_{method}_{timestamp}.md"
            with open(md_file, 'w') as f:
                f.write(f"# Apple Notes Export - {method.title()} Method\n\n")
                f.write(f"Extracted on: {datetime.now().isoformat()}\n")
                f.write(f"Total notes: {len(notes)}\n\n")
                f.write("---\n\n")
                
                for note in notes:
                    f.write(f"## {note.get('title', 'Untitled')}\n\n")
                    f.write(f"- **Created:** {note.get('created', 'Unknown')}\n")
                    f.write(f"- **Modified:** {note.get('modified', 'Unknown')}\n")
                    f.write(f"- **Folder:** {note.get('folder', 'None')}\n")
                    f.write(f"- **Account:** {note.get('account', 'Unknown')}\n")
                    if note.get('attachments'):
                        f.write(f"- **Attachments:** {len(note['attachments'])}\n")
                    f.write("\n")
                    f.write(note.get('body', ''))
                    f.write("\n\n---\n\n")
            
            print(f"📝 Saved Markdown: {md_file}")
        
        # Update index
        self.update_index(notes, method)
    
    def update_index(self, notes, method):
        """Update the master index of extracted notes"""
        index_file = self.output_dir / "index.json"
        
        if index_file.exists():
            with open(index_file) as f:
                index = json.load(f)
        else:
            index = {"notes": {}, "metadata": {}}
        
        # Update notes in index
        for note in notes:
            note_id = note['id']
            if note_id not in index["notes"]:
                index["notes"][note_id] = []
            
            # Add this extraction
            index["notes"][note_id].append({
                "method": method,
                "extraction_date": note["extraction_date"],
                "title": note.get("title", ""),
                "size": len(note.get("body", "")),
                "has_attachments": bool(note.get("attachments"))
            })
        
        # Update metadata
        index["metadata"]["last_extraction"] = datetime.now().isoformat()
        index["metadata"]["total_notes"] = len(index["notes"])
        index["metadata"]["methods_used"] = list(set(
            index["metadata"].get("methods_used", []) + [method]
        ))
        
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        print(f"📊 Updated index: {len(index['notes'])} unique notes tracked")

def main():
    parser = argparse.ArgumentParser(description="Extract Apple Notes content")
    parser.add_argument(
        "--method", 
        choices=["simple", "full", "auto"],
        default="auto",
        help="Extraction method to use"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for extracted content"
    )
    parser.add_argument(
        "--config",
        default="configs/extractor.json",
        help="Configuration file path"
    )
    
    args = parser.parse_args()
    
    print("🍎 Apple Notes Extraction System")
    print("================================")
    
    extractor = AppleNotesExtractor(args.output_dir, args.config)
    
    success = False
    
    if args.method == "simple":
        success = extractor.extract_simple()
    elif args.method == "full":
        success = extractor.extract_full()
    elif args.method == "auto":
        print("🤖 Auto-selecting best extraction method...")
        # Try simple first, fall back to full if needed
        if extractor.extract_simple():
            print("✅ Simple extraction completed successfully")
            success = True
        else:
            print("⚠️ Simple extraction failed, trying full method...")
            success = extractor.extract_full()
    
    if success:
        print("\n✅ Extraction completed successfully!")
        print(f"📁 Output saved to: {extractor.output_dir}")
    else:
        print("\n❌ Extraction failed")
        sys.exit(1)

if __name__ == "__main__":
    main()