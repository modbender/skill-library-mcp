#!/usr/bin/env python3
"""
Lark Suite Wiki CLI - Manage and export Lark Wiki documents
"""
import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

LARK_API_BASE = "https://open.larksuite.com/open-apis"

class LarkWikiClient:
    def __init__(self, app_id=None, app_secret=None):
        # Try env vars first, then hardcoded defaults
        self.app_id = app_id or os.getenv("LARK_APP_ID") or "cli_a90f6c8bf8f8ded4"
        self.app_secret = app_secret or os.getenv("LARK_APP_SECRET") or "xtSodRRMmiU1R4oikynlFbBoEu3T2Wgo"
        self.token = None
        
        if not self.app_id or not self.app_secret:
            print("Error: LARK_APP_ID and LARK_APP_SECRET must be set")
            print("Run: export LARK_APP_ID='cli_xxx' && export LARK_APP_SECRET='xxx'")
            sys.exit(1)
    
    def get_token(self):
        """Get tenant access token"""
        url = f"{LARK_API_BASE}/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret
        })
        data = resp.json()
        if data.get("code") != 0:
            print(f"Error getting token: {data}")
            sys.exit(1)
        self.token = data["tenant_access_token"]
        return self.token
    
    def api_get(self, endpoint, params=None):
        """Make authenticated GET request"""
        if not self.token:
            self.get_token()
        url = f"{LARK_API_BASE}{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()
    
    def list_spaces(self):
        """List all wiki spaces"""
        result = self.api_get("/wiki/v2/spaces", {"page_size": 50})
        spaces = result.get("data", {}).get("items", [])
        
        if not spaces:
            print("No wiki spaces found. Make sure your app is authorized.")
            return
        
        print("\n📚 Wiki Spaces:")
        print("-" * 60)
        for space in spaces:
            print(f"ID: {space.get('space_id')}")
            print(f"Name: {space.get('name', 'N/A')}")
            print(f"Description: {space.get('description', 'N/A')}")
            print("-" * 60)
    
    def get_document_blocks(self, doc_id):
        """Get all blocks from document (including children)"""
        blocks = []
        page_token = None
        
        while True:
            params = {"page_size": 500, "document_revision_id": -1}
            if page_token:
                params["page_token"] = page_token
            
            result = self.api_get(f"/docx/v1/documents/{doc_id}/blocks", params)
            
            if result.get("code") != 0:
                print(f"Error getting blocks: {result.get('msg')}")
                break
            
            items = result.get("data", {}).get("items", [])
            blocks.extend(items)
            
            page_token = result.get("data", {}).get("page_token")
            if not page_token:
                break
        
        return blocks
    
    def extract_subdocs_from_blocks(self, blocks):
        """Extract subdocument links from blocks"""
        subdocs = []
        for block in blocks:
            block_type = block.get("block_type")
            
            # Check for mention_doc in various block types
            for key in ["text", "heading1", "heading2", "heading3", "heading4", "heading5", "heading6"]:
                if key in block:
                    elements = block[key].get("elements", [])
                    for elem in elements:
                        if "mention_doc" in elem:
                            doc_info = elem["mention_doc"]
                            subdocs.append({
                                "id": doc_info.get("token"),
                                "title": doc_info.get("title"),
                                "url": doc_info.get("url")
                            })
        return subdocs
    
    def read_document(self, doc_id, output_format="text"):
        """Read document content with metadata"""
        # Get document info
        result = self.api_get(f"/docx/v1/documents/{doc_id}")
        
        if result.get("code") != 0:
            print(f"Error reading document: {result.get('msg')}")
            return None
        
        doc_info = result.get("data", {}).get("document", {})
        title = doc_info.get("title", "Untitled")
        
        # Get raw content
        content_result = self.api_get(f"/docx/v1/documents/{doc_id}/raw_content")
        
        if content_result.get("code") != 0:
            print(f"Error reading content: {content_result.get('msg')}")
            return None
        
        content = content_result.get("data", {}).get("content", "")
        
        # Get blocks to find subdocuments
        blocks = self.get_document_blocks(doc_id)
        subdocs = self.extract_subdocs_from_blocks(blocks)
        
        return {
            "id": doc_id,
            "title": title,
            "content": content,
            "subdocuments": subdocs,
            "blocks": blocks
        }
    
    def build_doc_tree(self, root_doc_id, visited=None):
        """Recursively build document tree"""
        if visited is None:
            visited = set()
        
        if root_doc_id in visited:
            return None
        
        visited.add(root_doc_id)
        
        doc = self.read_document(root_doc_id)
        if not doc:
            return None
        
        tree = {
            "id": root_doc_id,
            "title": doc["title"],
            "content": doc["content"],
            "children": []
        }
        
        # Recursively get children
        for subdoc in doc.get("subdocuments", []):
            child_tree = self.build_doc_tree(subdoc["id"], visited)
            if child_tree:
                tree["children"].append(child_tree)
        
        return tree
    
    def export_document_tree(self, tree, output_dir, base_path="", index=None):
        """Export document tree to Markdown files with directory structure"""
        if not tree:
            return 0
        
        output_path = Path(output_dir)
        
        # Create safe directory/filename
        safe_title = tree["title"].replace("/", "_").replace("\\", "_").replace(":", "_")
        if index is not None:
            safe_title = f"{index:02d}_{safe_title}"
        
        # Create directory for this document
        doc_dir = output_path / base_path / safe_title
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        # Export main document
        md_file = doc_dir / f"{safe_title}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# {tree['title']}\n\n")
            f.write(tree["content"])
        
        exported = 1
        print(f"✅ Exported: {md_file}")
        
        # Export children
        for i, child in enumerate(tree.get("children", []), 1):
            exported += self.export_document_tree(
                child, 
                output_dir, 
                base_path=f"{base_path}/{safe_title}" if base_path else safe_title,
                index=i
            )
        
        return exported
    
    def load_sync_state(self, output_dir):
        """Load sync state for incremental sync"""
        state_file = Path(output_dir) / ".lark-sync-state.json"
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def save_sync_state(self, output_dir, state):
        """Save sync state"""
        state_file = Path(output_dir) / ".lark-sync-state.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    
    def sync_document(self, doc_id, output_dir, force=False):
        """Sync document with incremental update support"""
        print(f"\n🔄 Syncing document: {doc_id}")
        
        # Load previous sync state
        state = self.load_sync_state(output_dir)
        
        # Get current document info
        result = self.api_get(f"/docx/v1/documents/{doc_id}")
        if result.get("code") != 0:
            print(f"❌ Error: {result.get('msg')}")
            return 0
        
        doc_info = result.get("data", {}).get("document", {})
        current_revision = doc_info.get("revision_id", 0)
        
        # Check if update needed
        last_sync = state.get(doc_id, {})
        if not force and last_sync.get("revision") == current_revision:
            print(f"⏭️  Skipped (no changes): {doc_info.get('title')}")
            return 0
        
        # Build and export tree
        tree = self.build_doc_tree(doc_id)
        if not tree:
            return 0
        
        exported = self.export_document_tree(tree, output_dir)
        
        # Update sync state
        state[doc_id] = {
            "revision": current_revision,
            "last_sync": datetime.now().isoformat(),
            "title": doc_info.get("title")
        }
        self.save_sync_state(output_dir, state)
        
        print(f"\n📊 Sync complete: {exported} documents exported")
        return exported
    
    def export_single(self, doc_id, output_dir):
        """Export single document (flat structure)"""
        doc = self.read_document(doc_id)
        if not doc:
            return False
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        safe_title = doc["title"].replace("/", "_").replace("\\", "_")
        filename = f"{safe_title}.md"
        filepath = output_path / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {doc['title']}\n\n")
            f.write(doc["content"])
        
        print(f"✅ Exported: {filepath}")
        return True

def main():
    parser = argparse.ArgumentParser(description="Lark Suite Wiki CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # spaces
    subparsers.add_parser("spaces", help="List wiki spaces")
    
    # read
    read_parser = subparsers.add_parser("read", help="Read document")
    read_parser.add_argument("doc_id", help="Document ID or URL")
    
    # export - single document
    export_parser = subparsers.add_parser("export", help="Export single document")
    export_parser.add_argument("doc_id", help="Document ID or URL")
    export_parser.add_argument("--output", "-o", default="./lark-export", help="Output directory")
    
    # sync - batch export with tree structure
    sync_parser = subparsers.add_parser("sync", help="Sync entire wiki with subdocuments")
    sync_parser.add_argument("doc_id", help="Root document ID or URL")
    sync_parser.add_argument("--output", "-o", default="./lark-wiki", help="Output directory")
    sync_parser.add_argument("--force", "-f", action="store_true", help="Force re-export even if unchanged")
    
    # tree - show document structure
    tree_parser = subparsers.add_parser("tree", help="Show document tree structure")
    tree_parser.add_argument("doc_id", help="Root document ID or URL")
    
    args = parser.parse_args()
    
    client = LarkWikiClient()
    
    if args.command == "spaces":
        client.list_spaces()
    elif args.command == "read":
        doc = client.read_document(args.doc_id)
        if doc:
            print(f"\n📄 {doc['title']}\n")
            print(doc['content'])
            if doc.get('subdocuments'):
                print("\n📎 Subdocuments:")
                for sub in doc['subdocuments']:
                    print(f"  - {sub['title']} ({sub['id']})")
    elif args.command == "export":
        client.export_single(args.doc_id, args.output)
    elif args.command == "sync":
        count = client.sync_document(args.doc_id, args.output, force=args.force)
        if count > 0:
            print(f"\n🎉 Total exported: {count} documents")
            print(f"📁 Output: {Path(args.output).absolute()}")
    elif args.command == "tree":
        print("\n🌳 Building document tree...")
        tree = client.build_doc_tree(args.doc_id)
        if tree:
            print_tree(tree)
        else:
            print("❌ Failed to build tree")
    else:
        parser.print_help()

def print_tree(tree, indent=0, prefix=""):
    """Print tree structure"""
    connector = "└── " if indent > 0 else ""
    print(f"{'    ' * (indent - 1)}{connector}{tree['title']}")
    for i, child in enumerate(tree.get("children", [])):
        print_tree(child, indent + 1)

if __name__ == "__main__":
    main()
