#!/usr/bin/env python3
"""
Hybrid Deep Search Router
智能路由: 根据查询复杂度自动选择 Brave API 或 OpenAI Codex
"""

import re
import json
import os
from typing import Dict, Tuple, Literal

class QueryRouter:
    """查询路由器 - 分析查询复杂度并选择最优搜索方案"""

    # 复杂查询关键词
    COMPLEX_KEYWORDS = [
        "compare", "comparison", "vs", "versus",
        "analyze", "analysis", "analyzing",
        "explain", "explanation", "detailed",
        "why", "how", "what are the", "what is the difference",
        "comprehensive", "thorough", "in-depth", "deep",
        "evaluate", "assessment", "review",
        "pros and cons", "advantages", "disadvantages",
        "relationship", "connection", "impact",
        "framework", "architecture", "implementation",
        "best practices", "strategies", "approaches"
    ]

    # 简单查询关键词
    SIMPLE_KEYWORDS = [
        "what is", "who is", "when was", "where is",
        "list of", "definition of", "meaning of",
        "latest", "current", "recent",
        "news", "update", "release",
        "version", "download", "install"
    ]

    def __init__(self):
        self.min_complexity_score = 3  # 低于此分数使用 Brave
        self.max_query_length = 100     # 短查询倾向 Brave

    def analyze(self, query: str) -> Dict:
        """
        分析查询复杂度

        Returns:
            Dict with:
            - complexity_score: 0-10 分数
            - recommended_mode: 'quick' or 'codex'
            - confidence: 0.0-1.0 置信度
            - reasons: 决策原因列表
        """
        query_lower = query.lower().strip()

        # 计算复杂度分数
        complexity_score = self._calculate_complexity(query_lower)

        # 决策
        recommended_mode, confidence, reasons = self._make_decision(
            complexity_score, query_lower, query
        )

        return {
            "query": query,
            "complexity_score": complexity_score,
            "recommended_mode": recommended_mode,
            "confidence": confidence,
            "reasons": reasons
        }

    def _calculate_complexity(self, query: str) -> int:
        """计算复杂度分数 (0-10)"""

        score = 0

        # 1. 关键词匹配 (最多 +6 分)
        for keyword in self.COMPLEX_KEYWORDS:
            if keyword in query:
                score += 2

        # 2. 查询长度 (最多 +2 分)
        length = len(query.split())
        if length > 15:
            score += 2
        elif length > 8:
            score += 1

        # 3. 疑问句模式 (最多 +1 分)
        if re.search(r'(why|how|what).*\?.*\?', query):
            score += 1

        # 4. 技术术语 (最多 +1 分)
        tech_terms = ['api', 'framework', 'architecture', 'algorithm',
                     'implementation', 'integration', 'deployment']
        for term in tech_terms:
            if term in query:
                score += 1
                break

        # 5. 简单关键词惩罚 (最多 -2 分)
        for keyword in self.SIMPLE_KEYWORDS:
            if keyword in query:
                score -= 1

        # 限制分数范围
        score = max(0, min(10, score))

        return score

    def _make_decision(
        self,
        complexity_score: int,
        query_lower: str,
        query: str
    ) -> Tuple[Literal['quick', 'codex'], float, list]:
        """决策逻辑"""

        reasons = []
        confidence = 0.8

        # 默认决策
        recommended_mode = 'quick'  # Brave API

        # 复杂度决策
        if complexity_score >= self.min_complexity_score:
            recommended_mode = 'codex'
            reasons.append(f"复杂度分数 {complexity_score}/10 达到阈值")
            confidence = 0.85
        else:
            reasons.append(f"复杂度分数 {complexity_score}/10 低于阈值")

        # 查询长度调整
        if len(query.split()) <= 3 and complexity_score < 3:
            recommended_mode = 'quick'
            reasons.append("短查询适合快速搜索")
            confidence = 0.9

        # 关键词覆盖调整
        if any(kw in query_lower for kw in ["compare", "vs", "versus"]):
            recommended_mode = 'codex'
            reasons.append("检测到对比查询,需要深度分析")
            confidence = 0.95

        # 简单事实查询调整
        if any(kw in query_lower for kw in ["what is", "who is", "when was"]):
            if complexity_score < 3:
                recommended_mode = 'quick'
                reasons.append("简单事实查询,适合快速搜索")
                confidence = 0.92

        # 短查询且没有复杂关键词
        if len(query.split()) <= 5 and complexity_score < 2:
            recommended_mode = 'quick'
            reasons.append("短简单查询")
            confidence = 0.95

        return recommended_mode, confidence, reasons

    def print_analysis(self, analysis: Dict):
        """打印分析结果 (用户友好的格式)"""
        print(f"\n{'='*60}")
        print(f"📊 查询分析")
        print(f"{'='*60}")
        print(f"查询内容: {analysis['query']}")
        print(f"\n复杂度评分: {analysis['complexity_score']}/10")
        print(f"推荐模式: {analysis['recommended_mode'].upper()}")
        print(f"置信度: {analysis['confidence']*100:.1f}%")
        print(f"\n决策原因:")
        for i, reason in enumerate(analysis['reasons'], 1):
            print(f"  {i}. {reason}")

        mode_emoji = "🚀" if analysis['recommended_mode'] == 'codex' else "⚡"
        mode_name = "OpenAI Codex" if analysis['recommended_mode'] == 'codex' else "Brave API"
        print(f"\n{mode_emoji} 将使用: {mode_name}")
        print(f"{'='*60}\n")

def main():
    """测试路由器"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 router.py \"查询内容\"")
        print("\n测试示例:")
        print("  python3 router.py \"what is OpenClaw?\"")
        print("  python3 router.py \"compare LangChain vs LlamaIndex in detail\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    router = QueryRouter()
    analysis = router.analyze(query)
    router.print_analysis(analysis)

if __name__ == "__main__":
    main()
