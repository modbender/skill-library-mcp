#!/usr/bin/env python3
"""
黄金三角确定性计算引擎
Logic Engine for Logic-Hunter Skill

计算公式：C = sum(R * S) / E
- R (Reliability): 信源等级权重
- S (Support): 独立交叉证据数
- E (Entropy): 逻辑风险熵因子 (1.0-3.0)
"""

import math
import json
import sys


class LogicEngine:
    """黄金三角确定性计算引擎"""

    def __init__(self):
        self.reliability_map = {
            "primary": 1.0,    # 官方、论文、原始协议
            "secondary": 0.6,  # 主流深度报道
            "tertiary": 0.2,   # 社交媒体、传闻
            "unknown": 0.05    # 无法溯源
        }

    def calculate_confidence(self, evidence_list, logic_entropy=1.0):
        """
        计算置信度 C = sum(R * S) / E

        Args:
            evidence_list: [{'type': 'primary', 'count': 2}, ...]
            logic_entropy: 逻辑熵因子 (1.0-3.0)，越存疑数值越高

        Returns:
            float: 置信度 (0.0-0.99)
        """
        total_score = 0

        for e in evidence_list:
            r = self.reliability_map.get(e['type'], 0.05)
            s = e['count']
            total_score += (r * s)

        # 防止除以零
        if logic_entropy <= 0:
            logic_entropy = 1.0

        confidence = total_score / logic_entropy

        # 最高置信度不超过 0.99
        return round(min(confidence, 0.99), 2)

    def red_team_attack(self, hypothesis, evidence):
        """
        模拟红队对抗，返回脆弱点检测

        Args:
            hypothesis: 待验证的假设/结论
            evidence: 支撑证据列表

        Returns:
            list: 脆弱点描述列表
        """
        vulnerabilities = []

        # 检查 1：孤证风险
        if len(evidence) < 2:
            vulnerabilities.append("孤证风险：结论高度依赖单一路径")

        # 检查 2：信源多样性
        source_types = set()
        for e in evidence:
            if isinstance(e, dict):
                source_types.add(e.get('type', 'unknown'))
            else:
                source_types.add('unknown')

        if len(source_types) == 1:
            vulnerabilities.append("信源单一：所有证据来自同一类型信源")

        # 检查 3：信源质量
        primary_count = sum(1 for e in evidence if isinstance(e, dict) and e.get('type') == 'primary')
        if primary_count == 0 and len(evidence) > 0:
            vulnerabilities.append("缺乏一手信源：结论无官方/学术/原始数据支撑")

        # 检查 4：逻辑熵过高
        # 由调用方判断

        return vulnerabilities

    def classify_source(self, url, title="", snippet=""):
        """
        根据 URL 和内容特征分类信源

        Args:
            url: 来源 URL
            title: 标题
            snippet: 摘要

        Returns:
            str: 'primary' | 'secondary' | 'tertiary' | 'unknown'
        """
        url_lower = url.lower()

        # 一手信源特征
        primary_indicators = [
            '.gov', '.edu', 'arxiv.org', 'pubmed', 'doi.org',
            '.pdf', 'report', 'whitepaper', 'official',
            'sec.gov', 'patent', 'court', 'legislation'
        ]

        # 三手信源特征
        tertiary_indicators = [
            'twitter.com', 'weibo', 'reddit', 'quora',
            'blog.', 'medium.com', 'zhihu', 'toutiao',
            'forum', 'discussion', 'comment'
        ]

        # 检查一手信源
        for indicator in primary_indicators:
            if indicator in url_lower:
                return 'primary'

        # 检查三手信源
        for indicator in tertiary_indicators:
            if indicator in url_lower:
                return 'tertiary'

        # 默认为二手信源（主流媒体报道等）
        return 'secondary'

    def calculate_entropy(self, factors):
        """
        计算逻辑熵因子 (1.0-3.0)

        Args:
            factors: 风险因子字典
                - conflict_of_interest: bool (利益相关)
                - semantic_drift: bool (语义漂移)
                - time_sensitivity: bool (时效性强)
                - emotional_language: bool (情绪化语言)

        Returns:
            float: 熵因子 (1.0-3.0)
        """
        base_entropy = 1.0

        if factors.get('conflict_of_interest', False):
            base_entropy += 0.5
        if factors.get('semantic_drift', False):
            base_entropy += 0.5
        if factors.get('time_sensitivity', False):
            base_entropy += 0.3
        if factors.get('emotional_language', False):
            base_entropy += 0.2

        return min(base_entropy, 3.0)

    def generate_report(self, hypothesis, evidence_list, entropy_factors=None):
        """
        生成完整分析报告

        Args:
            hypothesis: 待验证假设
            evidence_list: 证据列表
            entropy_factors: 熵因子字典

        Returns:
            dict: 完整报告
        """
        if entropy_factors is None:
            entropy_factors = {}

        # 计算熵因子
        entropy = self.calculate_entropy(entropy_factors)

        # 计算置信度
        confidence = self.calculate_confidence(evidence_list, entropy)

        # 红队攻击
        vulnerabilities = self.red_team_attack(hypothesis, evidence_list)

        # 统计信源分布
        source_stats = {}
        for e in evidence_list:
            source_type = e.get('type', 'unknown')
            source_stats[source_type] = source_stats.get(source_type, 0) + e.get('count', 1)

        return {
            "hypothesis": hypothesis,
            "confidence": confidence,
            "entropy": entropy,
            "source_stats": source_stats,
            "vulnerabilities": vulnerabilities,
            "evidence_count": sum(e.get('count', 1) for e in evidence_list)
        }


# CLI 接口
def main():
    """命令行接口，支持直接调用"""
    if len(sys.argv) < 2:
        print("Usage: python logic_engine.py <command> [args]")
        print("Commands:")
        print("  test              Run test calculations")
        print("  calculate <json>  Calculate confidence from JSON evidence list")
        print("  redteam <json>    Run red team attack from JSON")
        sys.exit(1)

    engine = LogicEngine()
    command = sys.argv[1]

    if command == "test":
        # 测试计算
        test_evidence = [
            {'type': 'primary', 'count': 2},
            {'type': 'secondary', 'count': 3},
            {'type': 'tertiary', 'count': 1}
        ]
        confidence = engine.calculate_confidence(test_evidence, logic_entropy=1.2)
        print(f"Test confidence: {confidence}")

        # 测试红队
        vulns = engine.red_team_attack("Test hypothesis", ["single evidence"])
        print(f"Vulnerabilities: {vulns}")

    elif command == "calculate":
        if len(sys.argv) < 3:
            print("Error: Please provide JSON evidence list")
            sys.exit(1)
        evidence = json.loads(sys.argv[2])
        entropy = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
        result = engine.calculate_confidence(evidence, entropy)
        print(json.dumps({"confidence": result, "entropy": entropy}))

    elif command == "redteam":
        if len(sys.argv) < 3:
            print("Error: Please provide JSON with hypothesis and evidence")
            sys.exit(1)
        data = json.loads(sys.argv[2])
        result = engine.red_team_attack(data['hypothesis'], data['evidence'])
        print(json.dumps({"vulnerabilities": result}))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
