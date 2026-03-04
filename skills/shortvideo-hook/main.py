#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短视频黄金 3 秒钩子生成器 v1.1
自动生成高完播、高停留、高流量的短视频开头钩子
优化版：修复计数逻辑，增加主题相关钩子
"""

import json
import random
import re
import sys
import io
from datetime import datetime
from pathlib import Path

# 修复 Windows 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ===== 钩子模板库（扩充版） =====
HOOK_TEMPLATES = {
    "悬念型": [
        "每天只做 3 件事，我的{result}反而提升了 10 倍",
        "99% 的人都不知道的{topic}秘密",
        "如果早点知道这个，我能少走 10 年弯路",
        "最后一个方法，99% 的人都没听过",
        "说出来你可能不信，但我真的做到了",
        "这个{topic}技巧，我只告诉内部员工",
        "偷偷用了这个方法，同事都以为我开挂了",
        "老板问我：你是怎么做到{result}的？",
        "千万别让太多人知道这个{topic}技巧",
        "我打赌，这个方法你一定没见过",
        "用了这个技巧，{result}提升了 300%",
        "同行都在偷偷用的{topic}秘籍",
        "3 天后删除，这个{topic}技巧太狠了",
        "被问爆了！都是关于{topic}的",
        "震惊！原来{topic}还可以这样做",
    ],
    "痛点型": [
        "你是不是也经常{pain}，却一事无成？",
        "为什么你总是感觉{pain}？",
        "明明很努力，为什么还是{pain}？",
        "别再无效努力了，这才是问题的根源",
        "我知道你现在很{pain}，因为我也经历过",
        "{topic}做不好，90% 是因为这个问题",
        "还在为{topic}发愁？这个方法救了我",
        "我懂你的{pain}，曾经我也这样",
        "别再{pain}了，试试这个方法",
        "{pain}的根本原因，不是你不努力",
        "为什么别人{result}，你却还在{pain}？",
        "停止{pain}！这才是正确做法",
        "{topic}总是做不好？问题在这里",
        "别再{pain}了，值得吗？",
        "你的{topic}方法，可能从一开始就错了",
    ],
    "利益型": [
        "学会这招，每天多出 2 小时自由时间",
        "我用这个方法，{time}从 0 到 1 掌握了{topic}",
        "照着做，你也能快速上手{topic}",
        "3 个步骤，让你的{result}提升 300%",
        "今天分享的这个工具，能帮你省下一半时间",
        "用这个技巧，{time}内看到明显效果",
        "亲测有效！{time}内{result}翻倍",
        "零基础也能学会的{topic}方法",
        "手把手教你{topic}，{time}见效",
        "这个{topic}工具，让我工作效率翻倍",
        "免费分享！{topic}的实战秘籍",
        "用了这个方法，{time}少工作 3 小时",
        "{topic}这样做，{result}翻倍",
        "简单 3 步，{time}掌握{topic}",
        "这个{topic}技巧，价值 10 万块",
    ],
    "反差型": [
        "以前我{before}，现在{after}",
        "从{before}到{after}，我只做了一件事",
        "月薪 3 千到 3 万，我只改变了一个习惯",
        "别人都在内卷，我却选择了躺平，结果...",
        "所有人都说做不到，但我偏要试试",
        "{topic}小白{time}逆袭，你敢信？",
        "曾经{before}，如今{after}",
        "不花一分钱，{time}后{after}",
        "没基础、没人脉，我{time}后{after}",
        "放弃{before}，选择{after}，我错了么？",
        "从{before}到{after}，我的{topic}之路",
        "同事都在加班，我{after}，还被表扬了",
        "零基础{time}后{after}，怎么做到的？",
        "不报培训班，{time}自学{topic}",
        "都说{before}，我偏要{after}",
    ],
    "故事型": [
        "3 年前我还是个{topic}小白，现在...",
        "我的老板问我：你是怎么做到{result}的？",
        "昨天有个粉丝跟我说，我的视频改变了他",
        "今天遇到一件事，让我感触很深",
        "说出来不怕你笑话，我曾经也{before}",
        "有个{topic}问题，困扰了我 3 年",
        "直到遇到这个方法，我才明白",
        "一个{topic}故事，送给正在努力的你",
        "从{before}到{after}，这是我的真实经历",
        "如果你也{pain}，请花 3 分钟看完",
        "我的{topic}血泪史，看完少走弯路",
        "因为{topic}，我差点放弃了",
        "一个{topic}技巧，改变了我的人生",
        "今天分享一个{topic}的真实案例",
        "这个故事，送给所有{topic}的人",
    ],
}

# 主题关键词替换
TOPIC_KEYWORDS = {
    "AI": ["AI 工具", "人工智能", "AI 技巧", "智能助手"],
    "时间管理": ["效率", "时间利用", "工作效率", "生产力"],
    "电商": ["销量", "转化", "流量", "订单"],
    "美妆": ["妆容", "护肤", "化妆技巧", "变美"],
    "健身": ["身材", "减脂", "增肌", "体能"],
    "编程": ["代码", "开发效率", "技术能力", "项目"],
    "自媒体": ["粉丝", "播放量", "内容质量", "影响力"],
    "职场": ["升职", "加薪", "工作能力", "人际关系"],
    "理财": ["收益", "财富", "投资回报", "被动收入"],
    "学习": ["成绩", "知识储备", "学习能力", "记忆力"],
}

# 结果词
RESULT_WORDS = ["效率", "收入", "能力", "成绩", "质量", "速度", "效果", "业绩"]

# 时间词
TIME_WORDS = ["1 周", "1 个月", "3 个月", "半年", "1 年", "30 天", "100 天"]

# 痛苦场景
PAIN_SCENARIOS = ["迷茫", "焦虑", "困惑", "瓶颈", "停滞不前", "没有进步", "赚不到钱", "没时间"]

# 前后对比
BEFORE_AFTER = [
    ("熬夜加班", "准点下班"),
    ("月薪 3 千", "月薪 3 万"),
    ("拖延症晚期", "效率达人"),
    ("小白", "高手"),
    ("没人脉", "资源不断"),
    ("没基础", "专家"),
    ("负债累累", "财务自由"),
    ("996", "work-life balance"),
]

# 平台专属优化前缀
PLATFORM_PREFIX = {
    "抖音": ["注意看！", "惊呆了！", "太真实了！", "绝了！", "一定要看到最后！"],
    "小红书": ["姐妹们！", "亲测有效！", "真心推荐！", "宝藏分享！", "好用到哭！"],
    "快手": ["老铁们！", "没毛病！", "安排！", "整起！", "杠杠的！"],
    "视频号": ["朋友们！", "重要提醒！", "值得关注！", "干货分享！", "建议收藏！"],
}


class ShortVideoHookGenerator:
    """短视频钩子生成器"""

    def __init__(self):
        self.usage_count = 0
        self.daily_limit = 10  # 免费版每日限制
        self.last_reset_date = datetime.now().strftime("%Y-%m-%d")
        self.data_file = Path(__file__).parent / "data" / "usage.json"
        self.load_usage()

    def load_usage(self):
        """加载使用记录"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    today = datetime.now().strftime("%Y-%m-%d")
                    if data.get("date") == today:
                        self.usage_count = data.get("count", 0)
                        self.last_reset_date = today
            except:
                pass

    def save_usage(self):
        """保存使用记录"""
        self.data_file.parent.mkdir(exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump({
                "date": self.last_reset_date,
                "count": self.usage_count
            }, f, ensure_ascii=False, indent=2)

    def check_daily_limit(self):
        """检查每日使用限制"""
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self.last_reset_date:
            self.usage_count = 0
            self.last_reset_date = today
            self.save_usage()
        
        return self.usage_count < self.daily_limit

    def get_topic_keywords(self, topic):
        """获取主题相关关键词"""
        for key, keywords in TOPIC_KEYWORDS.items():
            if key in topic:
                return keywords
        return [topic]

    def generate_hook(self, template, topic):
        """根据模板生成钩子"""
        keywords = self.get_topic_keywords(topic)
        keyword = random.choice(keywords)
        result = random.choice(RESULT_WORDS)
        time = random.choice(TIME_WORDS)
        pain = random.choice(PAIN_SCENARIOS)
        
        before_after = random.choice(BEFORE_AFTER)
        before = before_after[0]
        after = before_after[1]
        
        # 替换模板中的变量
        hook = template
        hook = hook.replace("{topic}", topic)
        hook = hook.replace("{result}", result)
        hook = hook.replace("{time}", time)
        hook = hook.replace("{pain}", pain)
        hook = hook.replace("{before}", before)
        hook = hook.replace("{after}", after)
        
        # 优化：有些模板需要更自然的表达
        if "做到效果" in hook:
            hook = hook.replace("做到效果", f"掌握{topic}")
        if "3 个月高手" in hook:
            hook = hook.replace("3 个月高手", f"{time}成为高手")
        
        return hook

    def generate(self, topic, hook_type=None, platform=None):
        """
        生成钩子文案
        
        Args:
            topic: 主题
            hook_type: 钩子类型 (悬念型/痛点型/利益型/反差型/故事型)
            platform: 平台 (抖音/小红书/快手/视频号)
        
        Returns:
            dict: 生成的钩子列表
        """
        # 检查限制
        if not self.check_daily_limit():
            remaining = self.daily_limit - self.usage_count
            return {
                "error": f"免费版每日限制 10 条，今日已用完",
                "remaining": remaining,
                "upgrade": "发送 /shortvideo-hook 升级 了解付费版权益"
            }

        results = []
        
        # 如果指定了类型，只生成该类型
        if hook_type:
            types_to_generate = [hook_type]
        else:
            types_to_generate = list(HOOK_TEMPLATES.keys())

        # 计算每种类型生成的数量
        hooks_per_type = max(2, 10 // len(types_to_generate))
        
        for h_type in types_to_generate:
            if h_type not in HOOK_TEMPLATES:
                continue
            
            templates = HOOK_TEMPLATES[h_type]
            # 随机选择模板并生成钩子
            selected_templates = random.sample(templates, min(hooks_per_type, len(templates)))
            
            for template in selected_templates:
                # 检查是否超出限制
                if self.usage_count >= self.daily_limit:
                    break
                
                hook = self.generate_hook(template, topic)
                
                # 添加平台前缀
                if platform and platform in PLATFORM_PREFIX:
                    prefix = random.choice(PLATFORM_PREFIX[platform])
                    hook = f"{prefix} {hook}"
                
                results.append(f"【{h_type}】{hook}")
                self.usage_count += 1
            
            if self.usage_count >= self.daily_limit:
                break
        
        self.save_usage()

        return {
            "topic": topic,
            "hook_type": hook_type or "全部",
            "platform": platform or "通用",
            "hooks": results,
            "usage": f"今日已使用 {self.usage_count}/{self.daily_limit} 次",
            "remaining": self.daily_limit - self.usage_count,
            "tip": "发送 /shortvideo-hook 生成 <主题> 平台=<平台> 获取专属优化版本"
        }

    def get_stats(self):
        """获取使用统计"""
        return {
            "usage_count": self.usage_count,
            "daily_limit": self.daily_limit,
            "remaining": max(0, self.daily_limit - self.usage_count),
            "last_reset": self.last_reset_date,
            "available_types": list(HOOK_TEMPLATES.keys()),
            "supported_platforms": list(PLATFORM_PREFIX.keys())
        }


# 全局实例
generator = ShortVideoHookGenerator()


def main(command, args):
    """
    主函数
    
    Args:
        command: 命令 (生成/类型/模板/统计/升级)
        args: 参数字典
    """
    if command == "生成":
        topic = args.get("topic", "通用主题")
        hook_type = args.get("类型")
        platform = args.get("平台")
        
        result = generator.generate(topic, hook_type, platform)
        
        if "error" in result:
            output = f"⚠️ {result['error']}\n\n"
            output += f"💡 提示：每日 0 点重置次数\n"
            output += f"\n📊 剩余次数：{result.get('remaining', 0)}"
            return output
        
        output = f"🎯 为你生成 {len(result['hooks'])} 个「{topic}」主题钩子：\n\n"
        for i, hook in enumerate(result["hooks"], 1):
            output += f"{i}. {hook}\n"
        
        output += f"\n💡 提示：{result['tip']}"
        output += f"\n📊 {result['usage']}"
        output += f"\n⏰ 剩余次数：{result['remaining']}"
        
        return output
    
    elif command == "类型":
        types_info = "📋 钩子类型说明：\n\n"
        for h_type, templates in HOOK_TEMPLATES.items():
            types_info += f"【{h_type}】\n"
            types_info += f"  特点：{h_type.replace('型', '')}内容，吸引用户继续观看\n"
            types_info += f"  模板数：{len(templates)} 个\n"
            types_info += f"  示例：{templates[0].replace('{topic}', 'XX').replace('{result}', 'XX')}\n\n"
        return types_info
    
    elif command == "模板":
        return "🔥 爆款模板库正在更新中...\n\n付费用户可获取实时更新的爆款模板库（100+ 模板）"
    
    elif command == "统计":
        stats = generator.get_stats()
        output = "📊 使用统计：\n\n"
        output += f"今日已用：{stats['usage_count']}/{stats['daily_limit']} 次\n"
        output += f"剩余次数：{stats['remaining']} 次\n"
        output += f"可用类型：{', '.join(stats['available_types'])}\n"
        output += f"支持平台：{', '.join(stats['supported_platforms'])}\n"
        output += f"\n💡 提示：每日 0 点重置次数"
        return output
    
    elif command == "关于":
        about_info = """
🎬 短视频黄金 3 秒钩子生成器 v1.1

开源项目 - 完全免费

【功能特点】
- 5 大钩子类型：悬念/痛点/利益/反差/故事
- 4 大平台适配：抖音/快手/视频号/小红书
- 75+ 专业模板
- 智能主题关键词关联
- 每日免费 10 条，0 点重置

【开源地址】
GitHub: https://github.com/openclaw/skills

【问题反馈】
欢迎提交 Issue 或 Pull Request！
"""
        return about_info
    
    else:
        return """
🎬 短视频黄金 3 秒钩子生成器 v1.1

用法：
/shortvideo-hook 生成 <主题>
/shortvideo-hook 生成 <主题> 类型=悬念型
/shortvideo-hook 生成 <主题> 平台=抖音
/shortvideo-hook 类型
/shortvideo-hook 统计
/shortvideo-hook 升级

示例：
/shortvideo-hook 生成 AI 工具教程
/shortvideo-hook 生成 时间管理 类型=痛点型
/shortvideo-hook 生成 电商带货 平台=小红书
"""


if __name__ == "__main__":
    # 测试
    print(main("生成", {"topic": "时间管理"}))
