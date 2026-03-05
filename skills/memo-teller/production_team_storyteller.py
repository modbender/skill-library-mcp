import os
import json
from datetime import datetime

# 技能元数据定义
SKILL_NAME = "LegacyStoryAgent"
DESCRIPTION = "专门用于协助老一辈回忆生产队往事，记录口述历史，并将其转化为自媒体/短剧剧本。"

class LegacyStoryAgent:
    def __init__(self, data_dir="./father_stories"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def get_interview_hooks(self, theme="通用"):
        """
        根据不同主题，提供能够诱导老人开口的‘钩子’问题。
        """
        hooks = {
            "工分与劳动": ["爸，那时候干一天活能挣几个工分？", "队里力气最大的人是谁？他有什么出名的事吗？"],
            "饮食与生活": ["那时候最馋什么？过年才能吃到什么？", "您还记得第一件的确良衣服是怎么来的吗？"],
            "情感与社交": ["您和妈结婚的时候，队里是怎么闹洞房的？", "那时候看露天电影要跑多少里地？"],
            "突发事件": ["那时候遇到大旱或者洪水，大家是怎么自救的？", "有没有哪个知青让您印象特别深？"]
        }
        return hooks.get(theme, hooks["通用"])

    def save_raw_memory(self, content, tags):
        """
        保存原始口述记录，带上时间戳和标签，方便后续翻查。
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.data_dir}/memory_{timestamp}.json"
        data = {
            "timestamp": timestamp,
            "content": content,
            "tags": tags,
            "status": "raw"
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return f"已存入素材库，编号：{timestamp}"

    def draft_short_drama_script(self, story_content):
        """
        将杂乱的口述转化为短剧脚本逻辑（包含：视觉、对白、冲突点）。
        """
        # 这里模拟 AI 转换逻辑
        script_template = f"""
        【短剧脚本建议】
        场景：生产队大晒场 / 破旧祖屋内部
        视觉重点：阳光穿过烟雾、粗糙的手、旧式农具
        核心冲突点：{story_content[:20]}... 
        剧本梗概：
        1. 开场（Hook）：展示一个现在见不到的细节（如：摇动的老式风车）。
        2. 发展：老人（主角）面临的一个困境（如：丢了公分票）。
        3. 反转/情感：在那段艰苦日子里体现的人性光辉。
        4. 结尾：画面拉回现实，老人在阳光下微笑。
        """
        return script_template

# 注册给 MoltClaw 的接口
def get_tools():
    return [
        {
            "name": "suggest_interview_questions",
            "description": "当不知道该问爸爸什么时，调用此工具获取诱导式问题。",
            "parameters": {"theme": "string"}
        },
        {
            "name": "record_story_segment",
            "description": "记录爸爸讲的一段具体故事。",
            "parameters": {"content": "string", "tags": "list"}
        },
        {
            "name": "transform_to_script",
            "description": "将选中的故事素材转化为适合自媒体发布的短剧脚本。",
            "parameters": {"story_content": "string"}
        }
    ]