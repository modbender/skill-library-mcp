#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Multi-Agent - 智能任务路由器
根据任务内容自动判断任务类型并推荐模型 tier
"""

import argparse
import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple


# 最大任务字符串长度限制
MAX_TASK_LENGTH = 10000


# Tier 定义和关键词映射
# 混合模式触发信号词：用户想要多版本草稿/多角度对比
HYBRID_SIGNALS = [
    # 中文
    "几个版本", "多个版本", "多版本", "多个草稿", "多版草稿",
    "3个版本", "三个版本", "2个版本", "两个版本", "4个版本", "四个版本",
    "几个角度", "多个角度", "不同角度", "不同风格", "多种风格",
    "让我挑", "帮我挑", "我来选", "我来挑", "哪个更好",
    "对比几种", "对比几个写法", "ab对比", "a/b对比",
    "不同模型各自", "让不同ai", "让几个ai", "多个模型",
    "各写一版", "各自写", "分别写",
    "几种写法", "多种写法", "不同写法",
    # 英文
    "multiple versions", "several versions", "multi-version",
    "multiple drafts", "different angles", "different styles",
    "let me pick", "let me choose", "a/b test", "ab test",
    "compare versions", "compare drafts", "side by side",
    "each model", "different models", "multiple models",
    "3 versions", "3 drafts", "several drafts",
]

# 联网需求信号词：判断是否需要 sessions_spawn（指挥官/混合）
SEARCH_SIGNALS = [
    # 中文
    "搜索", "搜一下", "查一下", "联网", "最新", "现在", "今天",
    "最近", "实时", "新闻", "当前", "查找资料", "调研", "研究",
    "查资料", "找资料", "爬", "抓取",
    # 英文
    "search", "look up", "latest", "current", "real-time", "recent",
    "news", "find information", "research", "scrape", "fetch",
    "web", "internet", "online",
]

TIER_KEYWORDS: Dict[str, Dict] = {
    "FAST": {
        "description": "简单查询、列表、状态检查、翻译、格式转换",
        "keywords": [
            # 中文
            "查询", "列出", "状态", "翻译", "格式", "转换", "是否", "多少", "什么时候",
            "获取", "显示", "查看", "检查", "确认", "简单", "快速",
            # 英文
            "query", "list", "status", "translate", "format", "convert", "check",
            "get", "show", "display", "simple", "quick"
        ],
        "weight": 1.0,
    },
    "CODE": {
        "description": "代码相关任务：编程、调试、实现、重构",
        "keywords": [
            # 中文
            "代码", "编程", "实现功能", "函数", "bug", "修复bug", "报错",
            "重构", "程序", "爬虫", "脚本", "接口", "算法", "单元测试",
            # 英文
            "code", "programming", "implement", "function", "class", "api", "fix",
            "refactor", "script", "develop", "module", "library", "algorithm"
        ],
        "weight": 1.2,
    },
    "RESEARCH": {
        "description": "调研、搜索、收集信息、分析对比",
        "keywords": [
            # 中文
            "调研", "搜索", "查找", "收集", "整理", "分析", "对比", "比较",
            "survey", "research", "研究", "调查", "探索", "了解", "学习",
            "资料", "文献", "综述", "概览", "现状", "趋势",
            # 英文
            "research", "survey", "investigate", "explore", "study", "analyze",
            "compare", "collect", "gather", "review", "overview"
        ],
        "weight": 1.1,
    },
    "CREATIVE": {
        "description": "写作、创意、文案、报告撰写",
        "keywords": [
            # 中文（精确词，避免"写"太泛）
            "写作", "文章", "文案", "创意", "故事", "撰写", "创作",
            "润色", "改写", "手册", "指南", "教程", "博客", "推文",
            # 英文
            "writing", "creative", "story", "draft", "compose", "copywriting", "blog"
        ],
        "weight": 1.0,
    },
    "REASONING": {
        "description": "复杂推理、数学计算、逻辑分析、架构设计",
        "keywords": [
            # 中文
            "推理", "分析", "计算", "逻辑", "数学", "规划", "设计方案", "架构",
            "证明", "推导", "验证", "优化", "策略", "决策", "评估",
            "复杂", "深度", "系统性", "全面", "详细", "精确",
            # 英文
            "reasoning", "logic", "mathematical", "math", "planning", "design",
            "architecture", "optimize", "strategy", "prove", "derive", "complex"
        ],
        "weight": 1.3,
    },
}


@dataclass
class ClassificationResult:
    """分类结果"""
    tier: str
    confidence: float
    reason: str


@dataclass
class SpawnTask:
    """生成的子任务"""
    task: str
    tier: str
    model: Optional[str] = None
    reason: str = ""


class TaskRouter:
    """任务路由器 - 根据内容自动分类任务"""

    def __init__(self):
        self.tier_keywords = TIER_KEYWORDS

    def _validate_task(self, task: str) -> None:
        """验证任务字符串"""
        if not task or not isinstance(task, str):
            raise ValueError("任务不能为空")
        if len(task) > MAX_TASK_LENGTH:
            raise ValueError(f"任务长度超过限制（最大 {MAX_TASK_LENGTH} 字符）")

    def _count_keywords(self, task: str) -> Dict[str, Tuple[int, List[str]]]:
        """
        统计每个 tier 的关键词匹配数量和匹配到的关键词
        返回: {tier: (count, matched_keywords)}
        """
        task_lower = task.lower()
        results = {}

        for tier, config in self.tier_keywords.items():
            count = 0
            matched = []
            for keyword in config["keywords"]:
                # 中文关键词直接用 in 匹配，英文关键词用词边界
                kw = keyword.lower()
                if any('\u4e00' <= c <= '\u9fff' for c in kw):
                    # 中文：直接子串匹配
                    if kw in task_lower:
                        count += 1
                        matched.append(keyword)
                else:
                    # 英文：词边界匹配
                    pattern = r'\b' + re.escape(kw) + r'\b'
                    if re.search(pattern, task_lower):
                        count += 1
                        matched.append(keyword)
            results[tier] = (count, matched)

        return results

    def classify(self, task: str) -> ClassificationResult:
        """
        对单个任务进行分类

        Args:
            task: 任务描述字符串

        Returns:
            ClassificationResult 包含 tier、confidence 和 reason
        """
        self._validate_task(task)

        keyword_stats = self._count_keywords(task)

        # 计算加权分数
        scores = {}
        for tier, (count, matched) in keyword_stats.items():
            weight = self.tier_keywords[tier]["weight"]
            scores[tier] = count * weight

        # 如果没有匹配到任何关键词，默认使用 REASONING（复杂任务保险起见）
        total_matches = sum(count for count, _ in keyword_stats.values())

        if total_matches == 0:
            # 尝试基于任务长度和复杂度进行启发式判断
            if len(task) < 50:
                best_tier = "FAST"
                confidence = 0.5
                reason = "任务较短，无明确关键词，默认归类为简单查询"
            else:
                best_tier = "REASONING"
                confidence = 0.4
                reason = "未匹配到明确关键词，按复杂任务处理"
            return ClassificationResult(tier=best_tier, confidence=confidence, reason=reason)

        # 找出最高分
        best_tier = max(scores, key=scores.get)
        best_score = scores[best_tier]
        _, best_matched = keyword_stats[best_tier]

        # 计算置信度
        # 基础置信度 = 当前 tier 得分 / 总得分
        total_score = sum(scores.values())
        base_confidence = best_score / total_score if total_score > 0 else 0

        # 根据匹配数量调整置信度
        match_bonus = min(len(best_matched) * 0.1, 0.2)  # 最多加 0.2
        confidence = min(base_confidence + match_bonus, 0.95)

        # 构建原因说明
        matched_str = ", ".join(best_matched[:5])  # 最多显示5个匹配词
        if len(best_matched) > 5:
            matched_str += f" 等{len(best_matched)}个关键词"

        reason = f"包含关键词: {matched_str}"

        return ClassificationResult(
            tier=best_tier,
            confidence=round(confidence, 2),
            reason=reason
        )

    def split_task(self, task: str) -> List[str]:
        """
        尝试将复合任务拆分为多个子任务
        基于常见的连接词进行拆分

        Args:
            task: 复合任务描述

        Returns:
            子任务列表
        """
        self._validate_task(task)

        # 定义拆分模式（按优先级排序）
        split_patterns = [
            # 中文连接词
            r'[,，;；]\s*然后\s*',
            r'[,，;；]\s*接着\s*',
            r'[,，;；]\s*再\s*',
            r'[,，;；]\s*并且\s*',
            r'[,，;；]\s*同时\s*',
            r'\s+并\s*',
            r'\s+然后\s*',
            r'[,，;；]\s*',
            # 英文连接词
            r'\s*,\s*then\s+',
            r'\s*,\s*and\s+then\s+',
            r'\s+and\s+',
            r'[,;]\s*',
        ]

        subtasks = [task]

        for pattern in split_patterns:
            new_subtasks = []
            for t in subtasks:
                parts = re.split(pattern, t)
                # 过滤空字符串和过短的片段
                parts = [p.strip() for p in parts if p and len(p.strip()) > 5]
                new_subtasks.extend(parts)
            subtasks = new_subtasks
            if len(subtasks) > 1:
                break  # 成功拆分后停止

        # 如果拆分后只有一个任务且原任务较长，尝试按句子拆分
        if len(subtasks) == 1 and len(task) > 100:
            sentence_pattern = r'[。！？\.!?]\s+'
            parts = re.split(sentence_pattern, task)
            parts = [p.strip() for p in parts if p and len(p.strip()) > 10]
            if len(parts) > 1:
                subtasks = parts

        return subtasks if subtasks else [task]

    def detect_hybrid_intent(self, task: str) -> bool:
        """
        检测用户是否有「多版本草稿」意图（触发混合模式）
        """
        task_lower = task.lower()
        for signal in HYBRID_SIGNALS:
            if signal.lower() in task_lower:
                return True
        return False

    def detect_search_intent(self, task: str) -> bool:
        """
        检测用户是否需要联网搜索（触发指挥官/混合模式）
        """
        task_lower = task.lower()
        for signal in SEARCH_SIGNALS:
            if signal.lower() in task_lower:
                return True
        return False

    def recommend_mode(self, task: str) -> Dict:
        """
        根据任务内容推荐执行模式

        决策树：
          需要多版本？
            YES + 需要联网 → hybrid（混合）
            YES + 不需联网 → pipeline（流水线）
            NO  + 需要联网 → orchestrator（指挥官）
            NO  + 不需联网 → pipeline（流水线）

        Returns:
            {"mode": str, "needs_search": bool, "needs_multi_draft": bool, "reason": str}
        """
        self._validate_task(task)
        needs_search = self.detect_search_intent(task)
        needs_multi_draft = self.detect_hybrid_intent(task)

        if needs_multi_draft and needs_search:
            mode = "hybrid"
            reason = "需要联网搜索 + 多版本草稿对比 → 混合模式（先指挥官搜索，再流水线并行生成）"
        elif needs_multi_draft:
            mode = "pipeline"
            reason = "需要多版本草稿对比，无需联网 → 流水线模式（并行生成多版）"
        elif needs_search:
            mode = "orchestrator"
            reason = "需要联网搜索，只要一份结果 → 指挥官模式（sessions_spawn 并行）"
        else:
            mode = "pipeline"
            reason = "纯文本任务，无需联网 → 流水线模式"

        return {
            "mode": mode,
            "needs_search": needs_search,
            "needs_multi_draft": needs_multi_draft,
            "reason": reason,
        }

    def spawn(self, task: str, multi: bool = False) -> List[SpawnTask]:
        """
        生成任务配置

        Args:
            task: 任务描述
            multi: 是否尝试拆分为多个子任务

        Returns:
            SpawnTask 列表
        """
        self._validate_task(task)

        if multi:
            subtasks = self.split_task(task)
        else:
            subtasks = [task]

        spawn_tasks = []
        for subtask in subtasks:
            result = self.classify(subtask)
            spawn_tasks.append(SpawnTask(
                task=subtask,
                tier=result.tier,
                model=None,  # 始终返回 None，让 OpenClaw 使用用户默认模型
                reason=result.reason
            ))

        return spawn_tasks


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw Multi-Agent - 智能任务路由器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分类单个任务
  python router.py classify "调研LangChain框架"

  # 生成任务配置（单任务）
  python router.py spawn --json "写一个Python爬虫"

  # 生成任务配置（多任务拆分）
  python router.py spawn --json --multi "调研LangChain并写报告"
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # mode 命令（推荐执行模式）
    mode_parser = subparsers.add_parser(
        "mode",
        help="推荐执行模式：orchestrator / pipeline / hybrid"
    )
    mode_parser.add_argument("task", help="任务描述字符串")
    mode_parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    # classify 命令
    classify_parser = subparsers.add_parser(
        "classify",
        help="对任务进行分类，返回推荐的 tier"
    )
    classify_parser.add_argument(
        "task",
        help="任务描述字符串"
    )
    classify_parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出"
    )

    # spawn 命令
    spawn_parser = subparsers.add_parser(
        "spawn",
        help="生成任务配置"
    )
    spawn_parser.add_argument(
        "task",
        help="任务描述字符串"
    )
    spawn_parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出"
    )
    spawn_parser.add_argument(
        "--multi",
        action="store_true",
        help="尝试将复合任务拆分为多个子任务"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    router = TaskRouter()

    try:
        if args.command == "mode":
            result = router.recommend_mode(args.task)
            if args.json:
                print(json.dumps(result, ensure_ascii=False))
            else:
                mode_emoji = {"orchestrator": "🎯", "pipeline": "🔄", "hybrid": "🔀"}.get(result["mode"], "❓")
                print(f"推荐模式: {mode_emoji} {result['mode'].upper()}")
                print(f"需要联网: {'✅' if result['needs_search'] else '❌'}")
                print(f"多版草稿: {'✅' if result['needs_multi_draft'] else '❌'}")
                print(f"原因: {result['reason']}")

        elif args.command == "classify":
            result = router.classify(args.task)
            if args.json:
                print(json.dumps(asdict(result), ensure_ascii=False))
            else:
                print(f"Tier: {result.tier}")
                print(f"Confidence: {result.confidence}")
                print(f"Reason: {result.reason}")

        elif args.command == "spawn":
            tasks = router.spawn(args.task, multi=args.multi)
            if args.json:
                output = [
                    {"task": t.task, "tier": t.tier, "model": t.model, "reason": t.reason}
                    for t in tasks
                ]
                # 如果是单任务，返回对象而非数组
                if len(output) == 1 and not args.multi:
                    print(json.dumps(output[0], ensure_ascii=False))
                else:
                    print(json.dumps(output, ensure_ascii=False))
            else:
                for i, t in enumerate(tasks, 1):
                    print(f"\n任务 {i}:")
                    print(f"  Task: {t.task}")
                    print(f"  Tier: {t.tier}")
                    print(f"  Model: {t.model}")
                    print(f"  Reason: {t.reason}")

    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    import sys
    main()
