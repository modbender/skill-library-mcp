#!/usr/bin/env python3
"""
Workflow Integrator - Process extracted notes for various downstream workflows
"""

import argparse
import json
import os
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import sys

class WorkflowIntegrator:
    def __init__(self, config_path="configs/workflows.json"):
        self.config_path = Path(config_path)
        self.script_dir = Path(__file__).parent
        self.root_dir = self.script_dir.parent
        
        self.config = self.load_config()
    
    def load_config(self):
        """Load workflow configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        
        # Default workflow configuration
        default_config = {
            "workflows": {
                "obsidian": {
                    "enabled": False,
                    "vault_path": "",
                    "subfolder": "Apple Notes",
                    "include_metadata": True,
                    "convert_attachments": True
                },
                "markdown_export": {
                    "enabled": True,
                    "output_dir": "export/markdown",
                    "single_file": False,
                    "include_toc": True
                },
                "search_index": {
                    "enabled": False,
                    "index_path": "export/search_index.json",
                    "full_text_search": True
                },
                "ai_processing": {
                    "enabled": False,
                    "summary_enabled": False,
                    "tag_extraction": False,
                    "sentiment_analysis": False
                }
            },
            "filters": {
                "min_content_length": 10,
                "exclude_empty_notes": True,
                "date_range": {
                    "enabled": False,
                    "start_date": "",
                    "end_date": ""
                }
            }
        }
        
        # Save default config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def load_latest_extraction(self):
        """Load the most recent extraction data"""
        output_dir = self.root_dir / "output" / "json"
        
        if not output_dir.exists():
            print("❌ No extraction data found. Run extract-notes.py first.")
            return None
        
        # Find the most recent JSON file
        json_files = list(output_dir.glob("notes_*.json"))
        if not json_files:
            print("❌ No extraction JSON files found.")
            return None
        
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        print(f"📖 Loading extraction data from: {latest_file}")
        
        try:
            with open(latest_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading extraction data: {e}")
            return None
    
    def filter_notes(self, notes):
        """Apply configured filters to notes"""
        filtered_notes = []
        filters = self.config.get("filters", {})
        
        min_length = filters.get("min_content_length", 10)
        exclude_empty = filters.get("exclude_empty_notes", True)
        
        for note in notes:
            content = note.get("body", "")
            
            # Skip empty notes if configured
            if exclude_empty and not content.strip():
                continue
            
            # Skip notes below minimum length
            if len(content) < min_length:
                continue
            
            # Date range filtering (if enabled)
            date_filter = filters.get("date_range", {})
            if date_filter.get("enabled", False):
                # Implementation would go here
                pass
            
            filtered_notes.append(note)
        
        print(f"🔍 Filtered {len(notes)} → {len(filtered_notes)} notes")
        return filtered_notes
    
    def export_to_obsidian(self, notes):
        """Export notes to an Obsidian vault"""
        obsidian_config = self.config["workflows"]["obsidian"]
        
        if not obsidian_config.get("enabled", False):
            print("⚠️ Obsidian export is disabled")
            return False
        
        vault_path = obsidian_config.get("vault_path", "")
        if not vault_path or not Path(vault_path).exists():
            print("❌ Obsidian vault path not configured or doesn't exist")
            return False
        
        vault_path = Path(vault_path)
        notes_dir = vault_path / obsidian_config.get("subfolder", "Apple Notes")
        notes_dir.mkdir(exist_ok=True)
        
        print(f"📁 Exporting to Obsidian vault: {vault_path}")
        
        exported_count = 0
        for note in notes:
            try:
                # Create safe filename
                title = note.get("title", "Untitled").replace("/", "-").replace(":", "-")
                filename = f"{title}.md"
                filepath = notes_dir / filename
                
                with open(filepath, 'w') as f:
                    f.write(f"# {note.get('title', 'Untitled')}\n\n")
                    
                    # Add metadata if enabled
                    if obsidian_config.get("include_metadata", True):
                        f.write("---\n")
                        f.write(f"created: {note.get('created', '')}\n")
                        f.write(f"modified: {note.get('modified', '')}\n")
                        f.write(f"folder: {note.get('folder', '')}\n")
                        f.write(f"account: {note.get('account', '')}\n")
                        f.write(f"extraction_method: {note.get('extraction_method', '')}\n")
                        f.write(f"source: Apple Notes\n")
                        f.write("---\n\n")
                    
                    # Add content
                    f.write(note.get('body', ''))
                    
                    # Add attachments info if present
                    attachments = note.get('attachments', [])
                    if attachments:
                        f.write("\n\n## Attachments\n\n")
                        for attachment in attachments:
                            f.write(f"- {attachment}\n")
                
                exported_count += 1
                
            except Exception as e:
                print(f"⚠️ Error exporting note '{note.get('title', 'Unknown')}': {e}")
        
        print(f"✅ Exported {exported_count} notes to Obsidian")
        return True
    
    def export_to_markdown(self, notes):
        """Export notes to standalone markdown files"""
        markdown_config = self.config["workflows"]["markdown_export"]
        
        if not markdown_config.get("enabled", True):
            print("⚠️ Markdown export is disabled")
            return False
        
        output_dir = self.root_dir / markdown_config.get("output_dir", "export/markdown")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📝 Exporting markdown files to: {output_dir}")
        
        if markdown_config.get("single_file", False):
            # Export all notes to a single file
            output_file = output_dir / f"apple_notes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            with open(output_file, 'w') as f:
                f.write("# Apple Notes Export\n\n")
                f.write(f"Exported on: {datetime.now().isoformat()}\n")
                f.write(f"Total notes: {len(notes)}\n\n")
                
                # Table of contents if enabled
                if markdown_config.get("include_toc", True):
                    f.write("## Table of Contents\n\n")
                    for i, note in enumerate(notes, 1):
                        title = note.get('title', f'Untitled {i}')
                        f.write(f"{i}. [{title}](#{title.lower().replace(' ', '-')})\n")
                    f.write("\n---\n\n")
                
                # Notes content
                for note in notes:
                    f.write(f"## {note.get('title', 'Untitled')}\n\n")
                    f.write(f"**Created:** {note.get('created', 'Unknown')}\n\n")
                    f.write(f"**Modified:** {note.get('modified', 'Unknown')}\n\n")
                    f.write(f"**Folder:** {note.get('folder', 'None')}\n\n")
                    f.write(note.get('body', ''))
                    f.write("\n\n---\n\n")
            
            print(f"✅ Exported to single file: {output_file}")
        
        else:
            # Export each note to its own file
            exported_count = 0
            for note in notes:
                try:
                    title = note.get("title", "Untitled").replace("/", "-").replace(":", "-")
                    filename = f"{title}.md"
                    filepath = output_dir / filename
                    
                    with open(filepath, 'w') as f:
                        f.write(f"# {note.get('title', 'Untitled')}\n\n")
                        f.write(f"- **Created:** {note.get('created', 'Unknown')}\n")
                        f.write(f"- **Modified:** {note.get('modified', 'Unknown')}\n")
                        f.write(f"- **Folder:** {note.get('folder', 'None')}\n")
                        f.write(f"- **Account:** {note.get('account', 'Unknown')}\n\n")
                        f.write(note.get('body', ''))
                    
                    exported_count += 1
                    
                except Exception as e:
                    print(f"⚠️ Error exporting note '{note.get('title', 'Unknown')}': {e}")
            
            print(f"✅ Exported {exported_count} individual markdown files")
        
        return True
    
    def create_search_index(self, notes):
        """Create a search index from notes"""
        search_config = self.config["workflows"]["search_index"]
        
        if not search_config.get("enabled", False):
            print("⚠️ Search index creation is disabled")
            return False
        
        index_path = self.root_dir / search_config.get("index_path", "export/search_index.json")
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"🔍 Creating search index...")
        
        search_index = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "total_notes": len(notes),
                "searchable_fields": ["title", "body", "folder"]
            },
            "notes": []
        }
        
        for note in notes:
            index_entry = {
                "id": note.get("id"),
                "title": note.get("title", ""),
                "created": note.get("created", ""),
                "modified": note.get("modified", ""),
                "folder": note.get("folder", ""),
                "account": note.get("account", ""),
                "preview": note.get("body", "")[:200] + "..." if len(note.get("body", "")) > 200 else note.get("body", ""),
                "word_count": len(note.get("body", "").split()),
                "char_count": len(note.get("body", ""))
            }
            
            # Full text if enabled
            if search_config.get("full_text_search", True):
                index_entry["full_text"] = note.get("body", "")
            
            search_index["notes"].append(index_entry)
        
        with open(index_path, 'w') as f:
            json.dump(search_index, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created search index: {index_path}")
        return True
    
    def run_workflows(self, notes):
        """Run all enabled workflows"""
        print(f"🔄 Running workflows on {len(notes)} notes...")
        
        # Apply filters first
        filtered_notes = self.filter_notes(notes)
        
        results = {}
        
        # Obsidian export
        if self.config["workflows"]["obsidian"]["enabled"]:
            results["obsidian"] = self.export_to_obsidian(filtered_notes)
        
        # Markdown export
        if self.config["workflows"]["markdown_export"]["enabled"]:
            results["markdown"] = self.export_to_markdown(filtered_notes)
        
        # Search index
        if self.config["workflows"]["search_index"]["enabled"]:
            results["search_index"] = self.create_search_index(filtered_notes)
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        print(f"\n✅ Completed {successful}/{len(results)} workflows successfully")
        
        return results

def main():
    parser = argparse.ArgumentParser(description="Process extracted Apple Notes through workflows")
    parser.add_argument(
        "--input",
        help="Input JSON file with extracted notes (defaults to latest)"
    )
    parser.add_argument(
        "--config",
        default="configs/workflows.json",
        help="Workflow configuration file"
    )
    parser.add_argument(
        "--workflow",
        choices=["obsidian", "markdown", "search", "all"],
        default="all",
        help="Specific workflow to run"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it"
    )
    
    args = parser.parse_args()
    
    print("🔄 Apple Notes Workflow Integrator")
    print("=================================")
    
    integrator = WorkflowIntegrator(args.config)
    
    # Load notes data
    if args.input:
        try:
            with open(args.input) as f:
                notes = json.load(f)
            print(f"📖 Loaded {len(notes)} notes from: {args.input}")
        except Exception as e:
            print(f"❌ Error loading input file: {e}")
            sys.exit(1)
    else:
        notes = integrator.load_latest_extraction()
        if not notes:
            print("❌ No notes data available")
            sys.exit(1)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        filtered_notes = integrator.filter_notes(notes)
        print(f"   Would process {len(filtered_notes)} filtered notes")
        print("   Configured workflows:")
        for workflow, config in integrator.config["workflows"].items():
            status = "✅" if config.get("enabled", False) else "⭕"
            print(f"     {status} {workflow}")
        return
    
    # Run workflows
    results = integrator.run_workflows(notes)
    
    if all(results.values()):
        print("\n🎉 All workflows completed successfully!")
    else:
        print("\n⚠️ Some workflows encountered issues")
        for workflow, success in results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {workflow}")

if __name__ == "__main__":
    main()