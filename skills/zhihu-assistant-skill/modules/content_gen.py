"""
内容生成模块

功能：
- 调用豆包 API 生成知乎回答草稿
- 支持自定义提示词
- 质量评估
- API 失败时降级到模拟草稿

使用方法：
    from content_gen import ContentGenerator
    
    generator = ContentGenerator(
        api_key='your-api-key',
        model='doubao-seed-2-0-pro-260215',
        base_url='https://ark.cn-beijing.volces.com/api/v3'
    )
    
    draft = generator.generate_answer(
        question_title='为什么现在的年轻人都不爱结婚了？',
        question_detail='详细描述...',
        word_count=800
    )
"""
import os
import re
import time
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ContentGenerator:
    """
    内容生成器
    
    使用豆包 API 生成知乎回答草稿。
    当 API 调用失败时，自动降级到模拟草稿。
    
    Attributes:
        api_key: 豆包 API Key
        model: 模型名称
        base_url: API 基础 URL
        system_prompt: 系统提示词
    """
    
    def __init__(self, api_key: str = None, model: str = "doubao-seed-2-0-pro-260215", 
                 base_url: str = "https://ark.cn-beijing.volces.com/api/v3"):
        """
        初始化内容生成器
        
        Args:
            api_key: 豆包 API Key，默认从环境变量读取
            model: 模型名称
            base_url: API 基础 URL
        """
        self.api_key = api_key or os.environ.get('KIMI_API_KEY')
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/chat/completions"
        
        # 系统提示词 - 定义回答风格和格式
        self.system_prompt = """你是一位专业的知乎答主，擅长用通俗易懂的语言解释复杂问题。

回答要求：
1. 字数控制在800字左右（700-900字）
2. 结构清晰，包含：
   - 开头：直接回应问题，给出核心观点（100字左右）
   - 主体：分点论述，用例子和数据支撑（500-600字）
   - 结尾：总结升华，引发思考（100字左右）
3. 语言风格：
   - 专业但亲和，避免过于学术化
   - 适当使用口语化表达，像真人写作
   - 避免AI常用套话（如"值得注意的是"、"我们需要认识到"）
4. 内容要求：
   - 有独特见解，不泛泛而谈
   - 可以适度幽默，增加可读性
   - 如果问题有争议，呈现多角度观点

记住：你的目标是写出能获得高赞的优质回答。"""

    def generate_answer(self, question_title: str, question_detail: str = "", 
                       excerpt: str = "", word_count: int = 800) -> Optional[str]:
        """
        生成知乎回答草稿
        
        Args:
            question_title: 问题标题
            question_detail: 问题详细描述
            excerpt: 问题摘要
            word_count: 目标字数
            
        Returns:
            生成的回答草稿，失败时返回模拟草稿
        """
        # 添加延迟以避免 RPM 限制 (Tier0: 20 RPM)
        time.sleep(3)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 构建用户提示
                user_prompt = self._build_prompt(question_title, question_detail, excerpt, word_count)
                
                # 调用 API
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': self.model,
                    'messages': [
                        {'role': 'system', 'content': self.system_prompt},
                        {'role': 'user', 'content': user_prompt}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 1500
                }
                
                response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                answer = result['choices'][0]['message']['content'].strip()
                
                # 后处理
                answer = self._post_process(answer)
                
                logger.info(f"成功生成回答，字数: {len(answer)}")
                return answer
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait_time = (attempt + 1) * 5  # 5, 10, 15 秒
                    logger.warning(f"遇到速率限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"生成回答失败: {e}")
                    break
            except Exception as e:
                logger.error(f"生成回答失败: {e}")
                break
        
        # 失败时返回模拟草稿
        return self._generate_mock_answer(question_title, word_count)
    
    def _build_prompt(self, title: str, detail: str, excerpt: str, word_count: int) -> str:
        """
        构建用户提示
        
        Args:
            title: 问题标题
            detail: 问题详情
            excerpt: 问题摘要
            word_count: 目标字数
            
        Returns:
            完整的提示文本
        """
        prompt_parts = [f"问题：{title}"]
        
        if detail:
            # 限制详情长度，避免 token 超限
            detail_short = detail[:500] + "..." if len(detail) > 500 else detail
            prompt_parts.append(f"问题描述：{detail_short}")
        
        if excerpt and not detail:
            prompt_parts.append(f"问题摘要：{excerpt}")
        
        prompt_parts.append(f"\n请为这个问题写一段{word_count}字左右的优质回答。")
        
        return "\n".join(prompt_parts)
    
    def _post_process(self, text: str) -> str:
        """
        后处理生成的文本
        
        - 移除 AI 标识
        - 确保结尾有标点
        - 规范化空行
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        # 移除可能的模型标识
        text = re.sub(r'^\[?AI\]?\s*', '', text)
        
        # 确保结尾有适当的标点
        text = text.strip()
        if text and text[-1] not in '。！？.!?':
            text += '。'
        
        # 规范化空行（最多两个连续空行）
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def _generate_mock_answer(self, question_title: str, word_count: int = 800) -> str:
        """
        生成模拟回答（用于 API 失败时的降级）
        
        Args:
            question_title: 问题标题
            word_count: 目标字数
            
        Returns:
            模拟回答草稿
        """
        # 根据关键词匹配预设回答
        mock_answers = {
            "结婚": """这个问题确实戳中了很多年轻人的痛点。

先说结论：不是不想结，而是不敢轻易结。

现在的年轻人面临的压力和上一代人完全不同。房价、教育成本、职场竞争，每一项都是一座大山。结婚不再是两个人搭伙过日子那么简单，而是意味着要承担巨大的经济责任。

更重要的是，现在的年轻人更重视自我实现。我们不再接受"到了年龄就该结婚"这种逻辑，而是希望找到真正契合的伴侣。如果找不到，宁可单身也不愿意将就。

当然，这并不意味着年轻人排斥婚姻。恰恰相反，我们对婚姻的期待更高了——不再是找个人凑合过一辈子，而是希望找到能共同成长、互相成就的伴侣。

这种变化，与其说是"不爱结婚"，不如说是"更谨慎地对待婚姻"。这未必是坏事，毕竟离婚率居高不下，谨慎一点总比草率结婚再离婚要好。

你怎么看这个问题？""",
            
            "人工智能": """2024年确实是AI发展的分水岭。

从ChatGPT到各种AI工具的普及，我们见证了一场静悄悄的技术革命。但说"爆发式"可能有点夸张——AI的发展是渐进的，只是今年恰好到了大众感知的临界点。

真正值得关注的是几个趋势：

第一，AI正在从"玩具"变成"工具"。早期的AI更多是噱头，现在已经开始真正提升生产力。写代码、做设计、处理文档，AI都能帮上大忙。

第二，门槛在快速降低。不需要懂技术，普通人也能用上强大的AI能力。这种普惠性是技术扩散的关键。

第三，竞争格局在重塑。OpenAI不再是一家独大，Claude、Gemini、国内的各大模型都在快速迭代。这种竞争对消费者是好事。

当然，焦虑也是真实的。很多人担心被AI取代。我的看法是：AI确实会替代一些工作，但也会创造新的机会。关键是保持学习，让自己成为会使用AI的人，而不是被AI替代的人。

未来已来，只是分布不均。你准备好迎接AI时代了吗？"""
        }
        
        # 根据问题关键词匹配模拟回答
        for keyword, answer in mock_answers.items():
            if keyword in question_title:
                return answer
        
        # 默认回答
        return f"""这是一个很有意思的问题。

关于"{question_title}"，我的看法是：

首先，这个问题没有标准答案，不同人有不同的经历和观点。但我们可以从几个角度来分析。

从社会层面看，这种现象往往反映了更深层次的变化。可能是经济结构的调整，也可能是价值观的变迁。理解这些背景，有助于我们更好地把握问题的本质。

从个人层面看，每个人面临的具体情况不同。重要的是找到适合自己的方式，而不是盲目跟随潮流。

最后，保持开放的心态很重要。世界在不断变化，今天的答案可能不适用于明天。持续学习、保持思考，才能在这个快速变化的时代找到自己的位置。

你对这个问题有什么看法？欢迎在评论区分享你的观点。"""
    
    def estimate_quality(self, answer: str) -> dict:
        """
        评估回答质量（启发式评分）
        
        评分维度：
        - 字数（30分）
        - 段落结构（20分）
        - 列表使用（20分）
        - 例子使用（15分）
        - 数据使用（15分）
        - AI套话扣分（-5分/个）
        
        Args:
            answer: 回答文本
            
        Returns:
            质量评分字典
        """
        score = 0
        issues = []
        
        # 字数检查
        char_count = len(answer)
        if 700 <= char_count <= 900:
            score += 30
        elif 500 <= char_count < 700:
            score += 20
            issues.append("字数偏少")
        elif char_count > 900:
            score += 20
            issues.append("字数偏多")
        else:
            score += 10
            issues.append("字数不足")
        
        # 结构检查（是否有分段）
        paragraphs = [p for p in answer.split('\n') if p.strip()]
        if len(paragraphs) >= 3:
            score += 20
        else:
            score += 10
            issues.append("段落较少")
        
        # 检查是否有列表（分点论述）
        if re.search(r'[\d一二三四五六七八九十]+[、.．]', answer):
            score += 20
        
        # 检查是否有例子
        if re.search(r'(比如|例如|举个栗子|像|就像)', answer):
            score += 15
        
        # 检查是否有数据/数字
        if re.search(r'\d+%|\d+\.?\d+\s*(万|亿|个|人|次)', answer):
            score += 15
        
        # 检查AI套话
        ai_phrases = ['值得注意的是', '我们需要认识到', '不可否认的是', '总而言之']
        for phrase in ai_phrases:
            if phrase in answer:
                score -= 5
                issues.append(f"包含AI套话: {phrase}")
        
        return {
            'score': max(0, score),
            'char_count': char_count,
            'paragraph_count': len(paragraphs),
            'issues': issues,
            'is_acceptable': score >= 60
        }
