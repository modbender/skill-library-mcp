"""Merge Book - Combine all chapters into final book with full book quality check"""
import json
from pathlib import Path
from datetime import datetime

def merge_chapters(book_dir, output_filename=None):
    book_dir = Path(book_dir)
    chapters_dir = book_dir / "chapters"
    final_dir = book_dir / "final"
    final_dir.mkdir(exist_ok=True)
    
    with open(book_dir / "0-book-config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    chapter_files = sorted(chapters_dir.glob("第*.txt"))
    if not chapter_files:
        return None
    
    merged = [f"《{config['title']}》", "", f"共{len(chapter_files)}章", "="*60, ""]
    total = 0
    for cf in chapter_files:
        with open(cf, 'r', encoding='utf-8') as f:
            c = f.read()
        total += len(c)
        merged.extend([f"\n{'='*60}\n", c, ""])
    
    merged.extend(["="*60, f"总字数: {total:,}", ""])
    
    out = output_filename or f"{config['title']}_完整版.txt"
    out_path = final_dir / out
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(merged))
    
    config.update({"status": "merged", "completed_words": total, "completed_at": datetime.now().isoformat()})
    with open(book_dir / "0-book-config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"Merged: {out_path}")
    return out_path, total

def full_book_quality_check(book_dir):
    """整书质量检查：设定一致性、大纲符合度、剧情逻辑、人物性格、伏笔回收"""
    book_dir = Path(book_dir)
    
    with open(book_dir / "0-book-config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    with open(book_dir / "1-main-outline.md", 'r', encoding='utf-8') as f:
        outline = f.read()
    with open(book_dir / "3-world-building.md", 'r', encoding='utf-8') as f:
        world = f.read()
    with open(book_dir / "2-chapter-plan.json", 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    chapters = []
    for cf in sorted((book_dir / "chapters").glob("第*.txt")):
        with open(cf, 'r', encoding='utf-8') as f:
            chapters.append(f"=== {cf.name} ===\n{f.read()}")
    
    prompt = f"""【整书质量检查】书名：《{config['title']}》
大纲：{outline[:3000]}...
设定：{world[:3000]}...
章节：{len(plan.get('chapters',[]))}章
正文：{''.join(chapters)[:5000]}...（后续省略）

检查：1设定一致性 2大纲符合度 3剧情逻辑 4人物性格 5伏笔回收
输出JSON: {{"status": "PASS/NEEDS_REVISION", "issues": []}}"""
    
    check_file = book_dir / "final" / "full_book_check_prompt.txt"
    check_file.parent.mkdir(exist_ok=True)
    with open(check_file, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    result = {"book_title": config['title'], "status": "pending", "prompt_file": str(check_file),
              "dimensions": {k: {"status": "pending", "issues": []} for k in 
              ["setting", "outline", "logic", "character", "foreshadowing"]}}
    
    res_file = book_dir / "final" / "full_book_check.json"
    with open(res_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"整书检查提示词: {check_file}")
    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: merge_book.py <book_dir> [check]")
        sys.exit(1)
    merge_chapters(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2] == "check":
        full_book_quality_check(sys.argv[1])
