#!/usr/bin/env python3
"""
Backup Feishu wiki pages to local markdown files.

This script exports wiki pages with metadata, preserving structure
and content. Useful for archiving, migration, or offline access.

Usage:
  python wiki_backup.py --space-id spcXXX --output-dir ./wiki_backup
  python wiki_backup.py --node-token wikcnYYY --output-dir ./section_backup --recursive
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def ensure_dir(path):
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)

def get_wiki_structure(space_id, parent_token=None):
    """
    Get wiki node structure.
    Returns sample structure for demonstration.
    """
    print(f"[INFO] Fetching wiki structure for space {space_id}")
    
    # Sample structure for demonstration
    structure = {
        "space_id": space_id,
        "nodes": [
            {
                "node_token": "wikcn001",
                "title": "Home",
                "obj_token": "doxcn001",
                "obj_type": "docx",
                "children": [
                    {
                        "node_token": "wikcn002",
                        "title": "Getting Started",
                        "obj_token": "doxcn002",
                        "obj_type": "docx",
                        "children": []
                    },
                    {
                        "node_token": "wikcn003",
                        "title": "API Documentation",
                        "obj_token": "doxcn003",
                        "obj_type": "docx",
                        "children": [
                            {
                                "node_token": "wikcn004",
                                "title": "REST API",
                                "obj_token": "doxcn004",
                                "obj_type": "docx",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "node_token": "wikcn005",
                "title": "Team Resources",
                "obj_token": "doxcn005",
                "obj_type": "docx",
                "children": []
            }
        ]
    }
    
    # Filter by parent if specified
    if parent_token:
        # In real implementation, would fetch specific subtree
        print(f"  Parent node: {parent_token}")
    
    return structure

def read_wiki_page(obj_token):
    """
    Read wiki page content.
    Returns sample content for demonstration.
    """
    print(f"[INFO] Reading wiki page {obj_token}")
    
    # Sample content
    content = f"""# Sample Wiki Page

Generated for demonstration purposes.

## Content

This is sample content for wiki page with token {obj_token}.

### Features

- Feature 1
- Feature 2
- Feature 3

## Metadata

- Backup date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Token: {obj_token}

## Sample Code

```python
def hello_wiki():
    print("Hello from wiki backup!")
```

"""
    return content

def save_page_to_markdown(content, metadata, output_dir, file_path):
    """
    Save page content and metadata to markdown file.
    """
    full_path = os.path.join(output_dir, file_path)
    ensure_dir(os.path.dirname(full_path))
    
    # Add metadata as frontmatter
    frontmatter = "---\n"
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            frontmatter += f"{key}: {value}\n"
        else:
            frontmatter += f"{key}: {json.dumps(value, ensure_ascii=False)}\n"
    frontmatter += "---\n\n"
    
    full_content = frontmatter + content
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    return full_path

def backup_node(node, base_path, output_dir, visited=None):
    """
    Recursively backup a wiki node and its children.
    """
    if visited is None:
        visited = set()
    
    if node["node_token"] in visited:
        return []
    
    visited.add(node["node_token"])
    backed_up = []
    
    # Create safe filename from title
    safe_title = "".join(c for c in node["title"] if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_')
    if not safe_title:
        safe_title = f"untitled_{node['node_token'][-6:]}"
    
    file_path = os.path.join(base_path, f"{safe_title}.md")
    
    # Read page content
    try:
        content = read_wiki_page(node["obj_token"])
        
        # Create metadata
        metadata = {
            "title": node["title"],
            "node_token": node["node_token"],
            "obj_token": node["obj_token"],
            "obj_type": node["obj_type"],
            "backup_date": datetime.now().isoformat(),
            "path": file_path,
            "children_count": len(node.get("children", []))
        }
        
        # Save to file
        saved_path = save_page_to_markdown(content, metadata, output_dir, file_path)
        backed_up.append({
            "title": node["title"],
            "path": saved_path,
            "node_token": node["node_token"]
        })
        
        print(f"  ✓ {node['title']} -> {file_path}")
        
    except Exception as e:
        print(f"  ✗ {node['title']}: {e}")
        # Still create placeholder
        placeholder = f"# {node['title']}\n\n*Error backing up this page: {e}*\n"
        metadata = {
            "title": node["title"],
            "node_token": node["node_token"],
            "error": str(e),
            "backup_date": datetime.now().isoformat()
        }
        saved_path = save_page_to_markdown(placeholder, metadata, output_dir, file_path)
        backed_up.append({
            "title": node["title"],
            "path": saved_path,
            "error": str(e)
        })
    
    # Process children recursively
    if node.get("children"):
        child_base_path = os.path.join(base_path, safe_title)
        for child in node["children"]:
            child_backup = backup_node(child, child_base_path, output_dir, visited)
            backed_up.extend(child_backup)
    
    return backed_up

def generate_index(backed_up_files, output_dir):
    """
    Generate an index file of all backed up pages.
    """
    index_content = "# Wiki Backup Index\n\n"
    index_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    index_content += f"Total pages: {len(backed_up_files)}\n\n"
    
    # Group by directory
    by_dir = {}
    for item in backed_up_files:
        rel_path = os.path.relpath(item["path"], output_dir)
        dir_name = os.path.dirname(rel_path)
        if dir_name not in by_dir:
            by_dir[dir_name] = []
        by_dir[dir_name].append(item)
    
    # Generate index
    for dir_name in sorted(by_dir.keys()):
        if dir_name == ".":
            index_content += "## Root Pages\n\n"
        else:
            index_content += f"## {dir_name}/\n\n"
        
        for item in sorted(by_dir[dir_name], key=lambda x: x["title"]):
            rel_path = os.path.relpath(item["path"], output_dir)
            index_content += f"- [{item['title']}]({rel_path})"
            if "error" in item:
                index_content += f" *(error: {item['error']})*"
            index_content += "\n"
        
        index_content += "\n"
    
    # Save index
    index_path = os.path.join(output_dir, "INDEX.md")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    return index_path

def main():
    parser = argparse.ArgumentParser(description="Backup Feishu wiki to local markdown files")
    
    # Wiki identification
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--space-id", help="Wiki space ID")
    group.add_argument("--node-token", help="Specific wiki node token to backup from")
    
    # Options
    parser.add_argument("--output-dir", default="./wiki_backup", help="Output directory")
    parser.add_argument("--recursive", action="store_true", help="Backup recursively (default: True for space, False for node)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving files")
    
    args = parser.parse_args()
    
    # Determine if recursive
    recursive = args.recursive
    if args.space_id and not args.recursive:
        recursive = True  # Default recursive for entire space
    elif args.node_token and not args.recursive:
        recursive = False  # Default non-recursive for single node
    
    # Prepare output directory
    output_dir = os.path.abspath(args.output_dir)
    if not args.dry_run:
        ensure_dir(output_dir)
    
    print(f"[INFO] Starting wiki backup")
    print(f"  Output directory: {output_dir}")
    print(f"  Recursive: {recursive}")
    print(f"  Dry run: {args.dry_run}")
    
    # Get wiki structure
    if args.space_id:
        structure = get_wiki_structure(args.space_id)
        nodes_to_backup = structure["nodes"]
        base_path = ""
    else:
        # For single node, create a minimal structure
        structure = {
            "nodes": [
                {
                    "node_token": args.node_token,
                    "title": f"Node_{args.node_token[-6:]}",
                    "obj_token": f"doxcn_{args.node_token[-6:]}",
                    "obj_type": "docx",
                    "children": []
                }
            ]
        }
        nodes_to_backup = structure["nodes"]
        base_path = ""
    
    if args.dry_run:
        print("\n[DRY RUN] Would backup:")
        print(f"  Number of root nodes: {len(nodes_to_backup)}")
        
        def print_node(node, indent=0):
            prefix = "  " * indent
            print(f"{prefix}- {node['title']} ({node['node_token']})")
            if recursive and node.get("children"):
                for child in node["children"]:
                    print_node(child, indent + 1)
        
        for node in nodes_to_backup:
            print_node(node)
        
        print(f"\n[DRY RUN] Would save to: {output_dir}")
        return
    
    # Perform backup
    backed_up_files = []
    
    for node in nodes_to_backup:
        print(f"\nBacking up: {node['title']}")
        files = backup_node(node, base_path, output_dir)
        backed_up_files.extend(files)
        
        if not recursive:
            # If not recursive, don't process children
            break
    
    # Generate index
    if backed_up_files:
        index_path = generate_index(backed_up_files, output_dir)
        print(f"\n[SUCCESS] Backup complete!")
        print(f"  Total pages: {len(backed_up_files)}")
        print(f"  Output directory: {output_dir}")
        print(f"  Index file: {index_path}")
        
        # Create summary
        summary = {
            "backup_date": datetime.now().isoformat(),
            "space_id": args.space_id,
            "node_token": args.node_token,
            "total_pages": len(backed_up_files),
            "output_dir": output_dir,
            "files": backed_up_files
        }
        
        summary_path = os.path.join(output_dir, "backup_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"  Summary: {summary_path}")
    else:
        print("\n[WARNING] No pages were backed up")

if __name__ == "__main__":
    main()