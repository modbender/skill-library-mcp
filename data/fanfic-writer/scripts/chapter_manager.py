"""
Chapter Content Manager
Handles chapter file operations and content integrity
"""
import os
import re
from pathlib import Path
from datetime import datetime

def get_chapter_path(book_dir, chapter_num, chapter_title=None):
    """Get path for a chapter file"""
    chapters_dir = Path(book_dir) / "chapters"
    
    # Convert title to safe filename
    if chapter_title:
        safe_title = "".join(c for c in chapter_title if c.isalnum() or c in "-_").strip()
        filename = f"第{chapter_num:03d}章_{safe_title}.txt"
    else:
        filename = f"第{chapter_num:03d}章.txt"
    
    return chapters_dir / filename

def save_chapter(book_dir, chapter_num, chapter_title, content, is_draft=False):
    """Save a chapter to file"""
    if is_draft:
        save_dir = Path(book_dir) / "drafts"
    else:
        save_dir = Path(book_dir) / "chapters"
    
    save_dir.mkdir(exist_ok=True)
    
    # Construct filename
    safe_title = "".join(c for c in chapter_title if c.isalnum() or c in "-_").strip() if chapter_title else ""
    if safe_title:
        filename = f"第{chapter_num:03d}章_{safe_title}.txt"
    else:
        filename = f"第{chapter_num:03d}章.txt"
    
    filepath = save_dir / filename
    
    # Write with metadata header
    metadata = f"""[Chapter Metadata]
Number: {chapter_num}
Title: {chapter_title}
Word Count: {len(content)}
Created: {datetime.now().isoformat()}
Status: {'draft' if is_draft else 'final'}
[End Metadata]

---

{content}
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(metadata)
    
    return filepath

def load_chapter(book_dir, chapter_num):
    """Load a chapter from file"""
    chapters_dir = Path(book_dir) / "chapters"
    
    # Find chapter file
    pattern = f"第{chapter_num:03d}章*.txt"
    matches = list(chapters_dir.glob(pattern))
    
    if not matches:
        # Try drafts
        drafts_dir = Path(book_dir) / "drafts"
        matches = list(drafts_dir.glob(pattern))
    
    if not matches:
        raise FileNotFoundError(f"Chapter {chapter_num} not found")
    
    filepath = matches[0]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract metadata and content
    metadata_match = re.search(r'\[Chapter Metadata\](.+?)\[End Metadata\]', content, re.DOTALL)
    if metadata_match:
        metadata_text = metadata_match.group(1)
        main_content = content[metadata_match.end():].strip()
        # Remove --- separator
        if main_content.startswith('---'):
            main_content = main_content[3:].strip()
    else:
        metadata_text = ""
        main_content = content
    
    # Parse metadata
    metadata = {}
    for line in metadata_text.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    
    return {
        'filepath': str(filepath),
        'metadata': metadata,
        'content': main_content,
        'word_count': len(main_content)
    }

def load_previous_chapters(book_dir, current_chapter, count=3):
    """Load previous N chapters for context"""
    chapters = []
    for i in range(max(1, current_chapter - count), current_chapter):
        try:
            chapter = load_chapter(book_dir, i)
            chapters.append(chapter)
        except FileNotFoundError:
            continue
    return chapters

def list_chapters(book_dir):
    """List all chapters in the book"""
    chapters_dir = Path(book_dir) / "chapters"
    chapters = []
    
    for f in sorted(chapters_dir.glob("第*.txt")):
        # Parse chapter number from filename
        match = re.match(r'第(\d+)章', f.stem)
        if match:
            chapter_num = int(match.group(1))
            # Get title from filename after chapter number
            title = f.stem.split('_', 1)[1] if '_' in f.stem else ""
            
            # Get actual content for word count
            try:
                chapter_data = load_chapter(book_dir, chapter_num)
                word_count = chapter_data['word_count']
            except:
                word_count = 0
            
            chapters.append({
                'number': chapter_num,
                'title': title,
                'filename': f.name,
                'word_count': word_count
            })
    
    return sorted(chapters, key=lambda x: x['number'])

def count_total_words(book_dir):
    """Count total words across all chapters"""
    chapters = list_chapters(book_dir)
    return sum(c['word_count'] for c in chapters)

def merge_chapters(book_dir, output_format='txt'):
    """Merge all chapters into final book"""
    chapters = list_chapters(book_dir)
    
    if not chapters:
        raise ValueError("No chapters found")
    
    # Load book config
    import json
    config_path = Path(book_dir) / "0-book-config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    book_title = config.get('title', 'Untitled')
    
    # Build merged content
    lines = [f"# {book_title}", "", "---", ""]
    
    for chapter in chapters:
        try:
            chapter_data = load_chapter(book_dir, chapter['number'])
            lines.append(f"\n第{chapter['number']}章 {chapter['title']}\n")
            lines.append(chapter_data['content'])
            lines.append("\n---\n")
        except Exception as e:
            lines.append(f"\n[Error loading chapter {chapter['number']}: {e}]\n")
    
    merged_content = '\n'.join(lines)
    
    # Save to final directory
    final_dir = Path(book_dir) / "final"
    final_dir.mkdir(exist_ok=True)
    
    safe_title = "".join(c for c in book_title if c.isalnum() or c == '-').strip()
    output_path = final_dir / f"{safe_title}.txt"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(merged_content)
    
    return output_path, len(merged_content)

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: chapter_manager.py <command> [args]")
        print("  list <book_dir> - List all chapters")
        print("  merge <book_dir> - Merge into final book")
        print("  count <book_dir> - Count total words")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        chapters = list_chapters(sys.argv[2])
        for c in chapters:
            print(f"第{c['number']}章: {c['title']} ({c['word_count']} words)")
    
    elif cmd == "merge":
        path, words = merge_chapters(sys.argv[2])
        print(f"Merged to: {path}")
        print(f"Total words: {words}")
    
    elif cmd == "count":
        words = count_total_words(sys.argv[2])
        print(f"Total words written: {words}")
