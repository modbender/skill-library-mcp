#!/usr/bin/env python3
"""Initialize a new MV project directory with standard structure."""

import argparse
import os
import yaml

def init_project(name: str, base_dir: str):
    project_dir = os.path.join(base_dir, name)
    
    dirs = [
        "lyrics",
        "audio",
        "video/scenes",
        "analysis",
        "edit/src/data",
        "edit/public/scenes",
        "output",
    ]
    
    for d in dirs:
        os.makedirs(os.path.join(project_dir, d), exist_ok=True)
    
    # Create scene_list.yaml template
    scene_template = {
        "project": name,
        "scenes": [
            {
                "id": "intro",
                "prompt": "TODO: Describe the intro scene",
                "duration": 8,
                "notes": ""
            },
            {
                "id": "verse1",
                "prompt": "TODO: Describe verse 1 scene",
                "duration": 8,
                "notes": ""
            },
        ]
    }
    
    scene_path = os.path.join(project_dir, "video", "scene_list.yaml")
    with open(scene_path, "w") as f:
        yaml.dump(scene_template, f, default_flow_style=False, allow_unicode=True)
    
    # Create empty lyrics files
    for fname in ["lyrics_raw.txt", "lyrics_formatted.txt"]:
        path = os.path.join(project_dir, "lyrics", fname)
        with open(path, "w") as f:
            f.write(f"# {name} - Lyrics\n# Edit this file\n")
    
    # Create .gitkeep in empty dirs
    for d in ["audio", "output"]:
        gitkeep = os.path.join(project_dir, d, ".gitkeep")
        if not os.listdir(os.path.join(project_dir, d)):
            open(gitkeep, "w").close()
    
    print(f"✅ Project '{name}' initialized at {project_dir}")
    print(f"   📁 {project_dir}/")
    for d in dirs:
        print(f"   ├── {d}/")
    print(f"\nNext: Edit lyrics/ and video/scene_list.yaml")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize MV project directory")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--dir", default=".", help="Base directory for the project")
    args = parser.parse_args()
    init_project(args.name, args.dir)
