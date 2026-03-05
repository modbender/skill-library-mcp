import os
import sys
import argparse

# This script is part of the 'hierarchical-memory' skill.
# Its purpose is to automate the creation of markdown files and directories
# within the local 'memory/' folder to maintain a structured context hierarchy.

def add_branch(type, name, parent_file=None):
    # Set the base path for memory files
    base_path = "/root/.openclaw/workspace/memory"
    
    if type == "domain":
        # Create a new domain file
        file_path = f"{base_path}/domains/{name.lower()}.md"
        content = f"# 🌐 DOMAIN: {name.capitalize()}\n\nDetails about {name}.\n\n---\n*Back to Root:* `MEMORY.md`"
        link_line = f"\n- **[{name.capitalize()}]** -> `memory/domains/{name.lower()}.md`"
        root_file = "/root/.openclaw/workspace/MEMORY.md"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Write the new markdown file
        with open(file_path, "w") as f:
            f.write(content)
            
        # Append a link to the root memory map
        with open(root_file, "a") as f:
            f.write(link_line)
            
    elif type == "project":
        # Create a new project file
        file_path = f"{base_path}/projects/{name.lower()}.md"
        content = f"# 🏗️ PROJECT: {name.capitalize()}\n\nStatus and details for {name}.\n\n---\n*Back to Domain:* `{parent_file}`"
        link_line = f"\n1. **[{name.capitalize()}]** -> `memory/projects/{name.lower()}.md`"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Write the new markdown file
        with open(file_path, "w") as f:
            f.write(content)
            
        # If a parent domain file is specified, append a link to it
        if parent_file:
            full_parent_path = f"/root/.openclaw/workspace/{parent_file}"
            if os.path.exists(full_parent_path):
                with open(full_parent_path, "a") as f:
                    f.write(link_line)

    print(f"✅ Created {type} branch: {name}")

if __name__ == "__main__":
    # Use argparse for a clean CLI interface
    parser = argparse.ArgumentParser(description="Add a new branch to the hierarchical memory system.")
    parser.add_argument("type", choices=["domain", "project"], help="The type of branch to create.")
    parser.add_argument("name", help="The name of the branch.")
    parser.add_argument("--parent", help="Path to parent domain file (required for projects).")
    args = parser.parse_args()
    add_branch(args.type, args.name, args.parent)
