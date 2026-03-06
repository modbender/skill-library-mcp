"""
Outline Generator - Generate main plot outline and chapter plans
"""
import json
from pathlib import Path

def load_prompts(skill_dir):
    """Load prompt templates"""
    prompts_path = Path(skill_dir) / "references" / "prompts.md"
    # Simplified - in production parse the markdown
    return {}

def generate_main_outline_prompt(genre, target_words, book_title=None):
    """Generate prompt for main outline creation"""
    
    # Estimated chapter count
    chapter_count = target_words // 3000  # ~3000 words per chapter
    
    prompt = f"""
你是一位资深网文作家和编辑。请基于以下信息，生成完整的小说大纲：

题材: {genre}
总字数: {target_words} 字
预计章节数: {chapter_count} 章

【要求】
1. 大纲要有清晰的起承转合结构
2. 每个阶段要有明确的爽点和钩子
3. 主角成长弧线要清晰
4. 配角要有深度，不只是工具人
5. 世界观设定要与剧情紧密结合
6. 大纲要有可扩展性，支撑{chapter_count}章不崩

【输出格式】
# {book_title or '书名待填'}

## 一句话简介
20字内的核心卖点

## 核心卖点
- 卖点1：...
- 卖点2：...
- 卖点3：...

## 世界背景
...

## 主要角色

### 主角
- 姓名/代号：
- 身份背景：
- 性格特点：
- 核心目标：
- 成长轨迹：

### 重要配角
...

## 主线剧情

### 第一卷：【卷名】（第1-{chapter_count//4}章）
卷主题：
核心冲突：
大爽点：

#### 第一阶段：【名】（第1-{chapter_count//8}章）
...

### 第二卷：【卷名】（第{chapter_count//4+1}-{chapter_count//2}章）
...

### 第三卷：【卷名】（第{chapter_count//2+1}-{chapter_count*3//4}章）
...

### 第四卷：【卷名】（第{chapter_count*3//4+1}-{chapter_count}章）
...

## 关键转折点
1. 第X章：...
2. 第Y章：...
3. 第Z章：...

## 预计完结
{chapter_count}章，{target_words}字
"""
    return prompt, chapter_count

def generate_chapter_plan_prompt(book_title, target_words, main_outline_text):
    """Generate prompt for chapter planning"""
    
    chapter_count = target_words // 3000
    
    prompt = f"""
基于以下大纲，规划详细的章节列表：

书名: {book_title}
总字数: {target_words}
大纲: {main_outline_text}

【要求】
1. 每章控制在 2000-5000 字
2. 每章一个独立的小高潮或情节推进
3. 章节之间有连贯性，伏笔前后照应
4. 每章都要有卡点或钩子
5. 重要剧情章节字数要充足（4000+）
6. 过渡章节可以适当简短（2000-3000）

【输出格式】JSON
{{
  "chapters": [
    {{
      "number": 1,
      "title": "章节名（吸引眼球）",
      "summary": "简略内容（50-100字）",
      "target_words": 3500,
      "key_event": "本章核心事件",
      "cliffhanger": "章节卡点"
    }},
    ...
  ],
  "total_chapters": {chapter_count},
  "volume_breakdown": [
    {{"volume": 1, "name": "卷名", "chapters": "1-X", "key_plot": "卷核心剧情"}}
  ],
  "notes": "特别说明（如哪些章节是高潮、哪些是过渡）"
}}

请确保生成的JSON格式正确，可以被Python直接解析。
"""
    return prompt

def parse_chapter_plan(json_text):
    """Parse chapter plan from JSON"""
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        import re
        match = re.search(r'```json\n(.*?)\n```', json_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise

def generate_worldbuilding_prompt(book_title, main_outline):
    """Generate prompt for worldbuilding"""
    
    prompt = f"""
请基于以下小说信息，构建完整的设定体系：

书名: {book_title}
大纲: {main_outline}

【要求】
1. 设定要服务于剧情
2. 力量/技能体系要有明确规则和限制
3. 角色要有深度，有内在矛盾和成长空间
4. 势力关系要复杂但不凌乱
5. 关键道具/地点要有象征意义

【输出格式】
# {book_title} 设定集

## 一、世界观
### 时空背景
- 时间：
- 空间：
- 基本规则：

### 势力分布
...

### 力量/技能体系（如适用）
- 体系名称：
- 等级划分：
- 核心规则：
- 限制条件：

## 二、主要角色

### 主角
【基础信息】
- 姓名：
- 年龄：
- 外貌特征：
【性格】
- 表层性格：
- 深层性格：
- 性格缺陷：
【背景】
- 出身：
- 关键经历：
- 关系网：
【目标与成长】
- 短期目标：
- 长期目标：
- 成长弧线：
【经典台词】
- ...

### 重要配角1
...

### 重要配角2
...

## 三、关键设定
### 重要道具
...

### 重要地点
...

### 关键规则/设定
...
"""
    return prompt

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: outline_generator.py <genre> <target_words> <book_title>")
        sys.exit(1)
    
    genre = sys.argv[1]
    target_words = int(sys.argv[2])
    book_title = sys.argv[3]
    
    print(f"Generating outline for: {book_title}")
    print(f"Genre: {genre}, Target: {target_words} words")
    
    prompt, chapters = generate_main_outline_prompt(genre, target_words, book_title)
    print(f"\nEstimated chapters: {chapters}")
    print("\nPrompt ready for main outline generation.")
