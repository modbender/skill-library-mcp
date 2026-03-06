#!/usr/bin/env python3
"""
Curate crawled content - move from raw to curated after human confirmation
"""

import argparse
import shutil
from pathlib import Path
from datetime import datetime

def curate_content(raw_filepath: Path, workspace: Path):
    """Move confirmed content from raw to curated"""
    
    # Read the raw file
    with open(raw_filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update curated status
    content = content.replace('curated: false', 'curated: true')
    content += f"\n\n---\n\n**Confirmed at**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    
    # Create curated filename
    curated_dir = workspace / "corpus" / "curated"
    curated_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract topic from frontmatter
    topic = "unknown"
    for line in content.split('\n'):
        if line.startswith('topic:'):
            topic = line.split(':', 1)[1].strip()
            break
    
    # Create curated filename: topic.md
    safe_topic = "".join(c if c.isalnum() or c in '-_' else '_' for c in topic)
    curated_filename = f"{safe_topic}.md"
    curated_filepath = curated_dir / curated_filename
    
    # Write curated file
    with open(curated_filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Optionally: move raw file to archive instead of keeping it
    archive_dir = workspace / "corpus" / "_archived_raw"
    archive_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(raw_filepath), str(archive_dir / raw_filepath.name))
    
    print(f"✅ 语料已确认并归档")
    print(f"   整理后文件: {curated_filepath}")
    print(f"   原始文件已移至: {archive_dir / raw_filepath.name}")
    
    return curated_filepath

def main():
    parser = argparse.ArgumentParser(description='Curate confirmed content')
    parser.add_argument('raw_file', help='Path to raw content file')
    parser.add_argument('--workspace', default='content-ops-workspace',
                       help='Workspace directory')
    
    args = parser.parse_args()
    
    raw_filepath = Path(args.raw_file)
    workspace = Path(args.workspace)
    
    if not raw_filepath.exists():
        print(f"❌ 文件不存在: {raw_filepath}")
        sys.exit(1)
    
    curate_content(raw_filepath, workspace)

if __name__ == '__main__':
    main()
