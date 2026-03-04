"""
Chapter Writer - Core writing logic with segmentation
"""
import os
import json
from pathlib import Path

def get_prompt_template(prompt_name):
    """Load prompt template from prompts.md"""
    prompts_path = Path(__file__).parent.parent / "references" / "prompts.md"
    # 这里简化处理，实际使用时需要解析markdown
    # 为演示目的，返回简化版本
    return f"Template for {prompt_name}"

def generate_chapter_detailed_outline(chapter_num, chapter_title, chapter_summary, 
                                       target_words, previous_chapter_content,
                                       main_outline, worldbuilding):
    """Generate detailed outline for a chapter"""
    
    prompt = f"""
【输入】
上一章小说正文：
{previous_chapter_content}

本章初步大纲（来自章节规划）：
第{chapter_num}章 {chapter_title}
{chapter_summary}

主线大纲参考：
{main_outline}

世界观设定参考：
{worldbuilding}

【任务】
请仔细阅读正文和大纲，分析和记住剧情、人物、人物关系和性格。现在续接剧情、设定、人物性格，写第{chapter_num}章《{chapter_title}》的详细大纲。

【要求】
1. 支持写成正文字数{target_words}字以上
2. 这个大纲是提交给大语言模型让它自动生成的
3. 写的是详细大纲，不是正文
4. 遵循网文写作规律，节奏紧凑，爽点明确

【输出格式】
第{chapter_num}章 {chapter_title} 详细大纲

【章节核心逻辑】
- 本章核心冲突/目标
- 人物动机和行动逻辑
- 与前后章的衔接关系
- 情绪走向

【分幕大纲详细设定】
（将本章分为3-5幕，每幕包含字数分配）

第一幕：【幕标题】（约1200字）
环境描写：
...
人物状态：
...

【正文写作指导】
- 人物刻画要点
- 场景描写重点
- 对话风格指引
- 卡点/高潮安排
"""
    return prompt

def write_chapter_segment(chapter_title, segment_num, total_segments,
                          previous_content, detailed_outline_segment,
                          written_so_far="", target_words=2000):
    """Write one segment of a chapter"""
    
    if segment_num == 1:
        # First segment - includes previous chapter
        prompt = f"""
【输入】
上一章小说正文：
{previous_content}

本章详细大纲（第一部分）：
{detailed_outline_segment}

【任务】
仔细阅读之前的所有小说正文和详细大纲，分析和记住剧情、人物、人物关系和性格。现在续接剧情、设定、人物性格，写《{chapter_title}》的第一部分正文。

【要求】
1. 字数要求：{target_words}字以上

---------要求---------
1. 严格按照设定和大纲来写，要和前面内容接续，并且不能有矛盾和重复的地方
2. ****特别注意****不可以自行添加设定和伏笔，也不可以写超出我给的这一段剧情大概内容的剧情
3. 注意这是小说，不要用说明书式的文字来写正文，要用充满代入感的电影画面一样的描述来写
4. 不要过度使用各种修辞来描述角色的每一个动作或者言语
5. 正文中该简洁的时候简洁，该详细描述的详细描述
6. 确保你写的正文跟前文没有重复描写，重复修饰，重复情节，重复比喻这类重复问题
7. 要尽可能避免AI味，如过度表情描写和比喻描写,过度进行解释描写，不需要每个逻辑都解释的十分清晰
8. 注意阅读感受不要写的过于诗意
9. 注意文笔上，短句不要太多了，不要太过于追求精简和角色体验描述了。不能缺少适当的第三方视角描述，就是那种镜头感
10. 需要满足字数要求
"""
    else:
        # Subsequent segments
        prompt = f"""
【输入】
已生成的前文：
{written_so_far}

本章详细大纲（第{segment_num}部分）：
{detailed_outline_segment}

【任务】
现在生成了前面的正文，仔细阅读正文，分析和记住描写细节，现在续接剧情、设定、人物性格，写下面部分的正文。

【要求】
1. 字数要求：{target_words}字以上

---------要求---------
（同上...）
"""
    
    return prompt

def quality_check_prompt(previous_chapter, current_chapter):
    """Generate quality check prompt"""
    prompt = f"""
【输入】
上一章小说正文：
{previous_chapter}

最新一章小说正文：
{current_chapter}

【任务】
现在逐句阅读最新一章小说正文全文：

1. 帮我优化文笔，去除AI味
2. 在小说描写中不要过度解释，适当留白，但是也不不可以一味追求简约，要张弛有度
3. 不要过度表情、心理描写和比喻描写，注意是不要过度，不是一点不能有
4. 不要过度使用各种修辞来描述角色的每一个动作或者言语
5. 不要整个段落看起来像是在做说明
6. 整体来说不要过于追求简短描述，要松弛有度
7. 最后你不用直接修改全文，而是把有问题的地方重写贴入原文，要求替代内容可以直接复制粘贴到原文中使用
8. 注意文笔上，短句不要太多了，不要太过于追求精简和角色体验描述了。不能缺少适当的第三方视角描述
9. 检查一下逻辑是否有问题

【输出】
如果认为需要修改：
【第X段】原内容：...\n【修改建议】：...

如果认为不需要修改：
QUALITY_PASS
"""
    return prompt

def parse_detailed_outline(outline_text):
    """Parse detailed outline to extract segments"""
    segments = []
    lines = outline_text.split('\n')
    current_segment = {"title": "", "content": [], "target_words": 0}
    
    for line in lines:
        if "第一幕" in line or "第二幕" in line or "第三幕" in line or "第四幕" in line or "第五幕" in line:
            if current_segment["content"]:
                segments.append(current_segment)
            current_segment = {
                "title": line.strip(),
                "content": [],
                "target_words": extract_word_count(line)
            }
        else:
            current_segment["content"].append(line)
    
    if current_segment["content"]:
        segments.append(current_segment)
    
    return segments

def extract_word_count(line):
    """Extract word count from line like '（约1200字）'"""
    import re
    match = re.search(r'约?([\d,]+)字', line)
    if match:
        return int(match.group(1).replace(',', ''))
    return 2000  # default

def estimate_segments(total_words):
    """Estimate how many 2000-word segments needed"""
    return (total_words + 1999) // 2000  # Round up

if __name__ == "__main__":
    print("Chapter Writer Module")
    print("Usage: Import and use functions, not standalone")
