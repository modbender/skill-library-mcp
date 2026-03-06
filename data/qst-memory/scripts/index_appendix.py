#!/usr/bin/env python3
"""
附錄索引處理腳本
提取 QST 附錄中的關鍵概念並索引到記憶系統
"""

import re
import argparse
from pathlib import Path
from datetime import datetime

# 關鍵概念提取規則
KEY_PATTERNS = {
    '意識旋量孤子': r'意識.*?旋量.*?孤子|spinor.*?soliton',
    '夸克渦旋': r'夸克.*?渦旋|quark.*?vortex',
    '三旋鈕': r'三旋鈕|three.*?knob',
    '本體層': r'本體層|ontological.*?layer',
    '顯現層': r'顯現層|phenomenal.*?layer',
}


def extract_key_memories(content: str, source_file: str) -> list:
    """提取關鍵記憶"""
    memories = []
    
    for concept_name, pattern in KEY_PATTERNS.items():
        matches = list(re.finditer(pattern, content, re.IGNORECASE | re.DOTALL))
        for i, match in enumerate(matches[:3]):  # 每個概念最多3條
            start = max(0, match.start() - 200)
            end = min(len(content), match.end() + 200)
            context = content[start:end]
            
            memories.append({
                'concept': concept_name,
                'source': source_file,
                'context': context.strip(),
                'timestamp': datetime.now().isoformat()
            })
    
    return memories


def index_appendix(file_path: str, category: str = "QST_Physics"):
    """索引附錄文件"""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    content = path.read_text(encoding='utf-8')
    print(f"📖 讀取附錄: {path.name} ({len(content)} 字符)")
    
    # 提取關鍵記憶
    memories = extract_key_memories(content, path.name)
    print(f"🔍 發現 {len(memories)} 條關鍵記憶")
    
    # 生成索引文件
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"appendix_index_{path.stem}.md"
    
    lines = [
        f"# 附錄索引: {path.name}",
        f"- 生成時間: {datetime.now().isoformat()}",
        f"- 記憶數: {len(memories)}",
        "",
        "## 關鍵記憶",
        ""
    ]
    
    for i, mem in enumerate(memories, 1):
        lines.extend([
            f"### #{i} - {mem['concept']}",
            f"- 來源: {mem['source']}",
            f"- 分類: {category}",
            "",
            "```",
            mem['context'],
            "```",
            "",
            "---",
            ""
        ])
    
    output_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✅ 索引已保存: {output_file}")
    
    # 同時保存到 QST 記憶庫
    from qst_memory import save_memory
    for mem in memories:
        save_memory(
            content=mem['context'],
            category=category,
            source=f"appendix:{mem['source']}"
        )
    print(f"✅ 已導入 {len(memories)} 條到 QST 記憶庫")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="索引 QST 附錄文件")
    parser.add_argument("file", help="附錄文件路徑")
    parser.add_argument("--category", default="QST_Physics", help="分類")
    args = parser.parse_args()
    
    index_appendix(args.file, args.category)
