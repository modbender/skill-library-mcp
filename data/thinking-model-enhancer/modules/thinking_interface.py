#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
思维模型增强器 - 用户交互接口模块
Thinking Model Enhancer - User Interface Module

处理用户命令、格式化输出、提供思维模型交互接口。
"""

import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from thinking_model_core import (
    ThinkingModelCore, 
    ThinkingModel, 
    ThinkingResult,
    ProblemAnalysis,
    ProblemType,
    ConfidenceLevel,
    get_thinking_core
)
from thinking_memory import (
    ThinkingMemory, 
    ModelSnapshot,
    get_thinking_memory
)


class ThinkingInterface:
    """思维模型用户交互接口"""
    
    def __init__(self):
        """初始化交互接口"""
        self.core = get_thinking_core()
        self.memory = get_thinking_memory()
        
        # 命令模式
        self.command_patterns = {
            "启动模式": r"启动(.*?)(思维)?模式",
            "运行思考": r"运行思维(模型)?",
            "比较模型": r"比较(.*?)思维模型",
            "查询历史": r"(查询|搜索|找).*?历史",
            "显示统计": r"(显示|查看|给我).*?统计",
            "清除记忆": r"(清除|清理|删除).*?记忆",
            "帮助": r"(帮助|help|使用说明)",
        }
    
    def handle_input(self, user_input: str) -> str:
        """
        处理用户输入，返回响应
        
        Args:
            user_input: 用户输入
            
        Returns:
            响应文本
        """
        # 检测是否是帮助请求
        if self._is_help_request(user_input):
            return self.get_help_message()
        
        # 检测命令类型
        command = self._detect_command(user_input)
        
        # 处理不同类型的输入
        if command == "启动模式":
            return self._handle_start_mode(user_input)
        elif command == "运行思考":
            return self._handle_run_thinking(user_input)
        elif command == "查询历史":
            return self._handle_query_history(user_input)
        elif command == "显示统计":
            return self._handle_show_stats(user_input)
        elif command == "清除记忆":
            return self._handle_clear_memory(user_input)
        else:
            # 默认作为问题处理
            return self._handle_general_query(user_input)
    
    def _is_help_request(self, user_input: str) -> bool:
        """检测是否是帮助请求"""
        help_keywords = ["帮助", "help", "使用说明", "怎么用", "如何", "what is", "使用方法"]
        return any(kw.lower() in user_input.lower() for kw in help_keywords)
    
    def _detect_command(self, user_input: str) -> str:
        """检测用户输入的命令类型"""
        for command, pattern in self.command_patterns.items():
            if re.search(pattern, user_input):
                return command
        return "general"
    
    def _handle_start_mode(self, user_input: str) -> str:
        """处理启动模式命令"""
        # 提取模式名称
        mode_match = re.search(r"启动(.*?)(思维)?模式", user_input)
        if mode_match:
            mode_name = mode_match.group(1).strip()
        else:
            return "请指定要启动的模式，例如：启动研究型思维模式"
        
        # 映射模式名称
        mode_mapping = {
            "研究": "research_mode",
            "研究型": "research_mode",
            "诊断": "diagnostic_mode",
            "诊断型": "diagnostic_mode",
            "通用": "generic_pipeline",
            "通用型": "generic_pipeline",
        }
        
        mode_key = mode_mapping.get(mode_name)
        if not mode_key:
            return f"未知的模式: {mode_name}，可选模式：研究型、诊断型、通用型"
        
        # 获取模型
        model = self.core.builtin_models.get(mode_key)
        if not model:
            return f"模式 {mode_name} 暂不可用"
        
        lines = [
            f"✅ 已启动{model.name}！",
            f"",
            f"📋 模式说明: {model.description}",
            f"",
            f"🔄 处理阶段:",
        ]
        
        for i, stage in enumerate(model.stages, 1):
            lines.append(f"   {i}. {stage}")
        
        lines.extend([
            f"",
            f"💡 请描述您要处理的问题或任务",
        ])
        
        return "\n".join(lines)
    
    def _handle_run_thinking(self, user_input: str) -> str:
        """处理运行思维模型命令"""
        # 提取问题描述
        problem = re.sub(r"运行思维(模型)?", "", user_input).strip()
        if not problem:
            return "请描述您要处理的问题，例如：运行思维模型分析这个错误"
        
        # 执行思维模型处理
        result = self.core.execute_thinking(problem)
        
        # 格式化结果
        response = self._format_result(result)
        
        # 存储到记忆系统
        self._store_result(result)
        
        return response
    
    def _handle_query_history(self, user_input: str) -> str:
        """处理查询历史命令"""
        # 提取查询关键词
        query = re.sub(r"(查询|搜索|找)", "", user_input).strip()
        if not query:
            return "请指定要查询的问题，例如：查询历史系统修复案例"
        
        # 执行查询
        history = self.memory.query_similar_problems(query, limit=5)
        
        if not history:
            return f"未找到与「{query}」相关的历史记录"
        
        lines = [
            f"📚 找到 {len(history)} 条历史记录:",
            ""
        ]
        
        for i, record in enumerate(history, 1):
            timestamp = record.get("timestamp", "")[:16]
            success = "✅" if record.get("success") else "❌"
            rating = record.get("user_rating", "-")
            
            lines.append(f"{i}. {success} [{timestamp}] 评分: {rating}/5")
            lines.append(f"   问题: {record.get('problem_summary', 'N/A')[:50]}")
            lines.append(f"   结果: {record.get('output_summary', 'N/A')[:50]}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _handle_show_stats(self, user_input: str) -> str:
        """处理显示统计命令"""
        # 获取统计信息
        stats = self.memory.get_model_statistics()
        
        lines = [
            "📊 思维模型使用统计",
            "=" * 50,
            "",
            f"📁 快照总数: {stats['total_snapshots']}",
            f"📈 成功率: {stats['by_success']['success']}/{stats['by_success']['success'] + stats['by_success']['failed']}",
            f"   ({stats.get('success_rate', 0)*100:.1f}%)",
        ]
        
        if stats.get("by_type"):
            lines.extend(["", "📂 按模型类型:"])
            for model_type, count in sorted(stats["by_type"].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"   • {model_type}: {count}次")
        
        if stats.get("avg_rating", 0) > 0:
            lines.extend(["", f"⭐ 平均评分: {stats['avg_rating']:.1f}/5"])
        
        return "\n".join(lines)
    
    def _handle_clear_memory(self, user_input: str) -> str:
        """处理清除记忆命令"""
        # 提取天数
        days_match = re.search(r"(\d+)天", user_input)
        days = int(days_match.group(1)) if days_match else 90
        
        # 清除旧快照
        cleared = self.memory.clear_old_snapshots(days)
        
        return f"🧹 已清除 {cleared} 条超过 {days} 天的旧记录"
    
    def _handle_general_query(self, user_input: str) -> str:
        """处理一般问题查询"""
        # 分析问题
        analysis = self.core.analyze_problem(user_input)
        
        # 选择模型
        model = self.core.select_model(analysis)
        
        # 生成响应
        lines = [
            f"🧠 思维模型分析结果",
            "=" * 50,
            "",
            f"📝 问题分析:",
            f"   类型: {analysis.problem_type.value}",
            f"   复杂度: {analysis.complexity}/10",
            f"   置信度: {analysis.confidence.value}",
            "",
            f"🎯 推荐模型: {model.name}",
            f"",
            f"📌 关键发现:",
            f"   • 识别关键词: {', '.join(analysis.keywords[:5])}",
        ]
        
        if analysis.constraints:
            lines.append(f"   • 约束条件: {len(analysis.constraints)}个")
        
        if analysis.urgency:
            lines.extend(["", f"⚠️ 紧急程度: {analysis.urgency.value}"])
        
        lines.extend([
            "",
            f"🔄 处理阶段:",
        ])
        
        for i, stage in enumerate(model.stages, 1):
            lines.append(f"   {i}. {stage}")
        
        lines.extend([
            "",
            f"💡 您可以说:",
            f"   • '使用{model.name}处理这个问题'",
            f"   • '运行完整思维模型分析'",
            f"   • '查看相关历史案例'",
        ])
        
        return "\n".join(lines)
    
    def _format_result(self, result: ThinkingResult) -> str:
        """格式化思维结果"""
        return self.core.format_result(result)
    
    def _store_result(self, result: ThinkingResult):
        """存储处理结果到记忆系统"""
        snapshot = ModelSnapshot(
            snapshot_id="",
            model_type=result.selected_model,
            problem_summary=result.problem[:200],
            input_hash=hash(result.problem),
            output_summary=", ".join(result.recommendations[:3]),
            success=True,
            feedback_score=None,
            timestamp=result.timestamp,
            duration_ms=result.processing_time_ms,
            stages_used=result.stages_completed,
            key_findings=result.findings[:5]
        )
        
        self.memory.store_snapshot(snapshot)
    
    def get_welcome_message(self) -> str:
        """获取欢迎消息"""
        return """🧠 **思维模型增强器已就位！**

我可以帮你：
• 📊 分析问题类型和复杂度
• 🎯 选择合适的思维模型
• 🔍 执行结构化思考流程
• 💾 存储和查询历史案例
• 📈 追踪思维模型效果

**使用方式：**
• "启动研究型思维模式" - 用于创建技能或功能
• "启动诊断型思维模式" - 用于系统故障排除
• "分析这个问题" - 自动选择最佳模型
• "查询历史修复案例" - 查看类似问题记录
• "显示使用统计" - 查看思维模型使用情况

有什么我可以帮您思考或分析的吗？"""
    
    def get_help_message(self) -> str:
        """获取帮助消息"""
        return """🧠 **思维模型增强器 - 使用指南**

## 核心功能

### 1. 问题分析
输入任何问题，我会自动分析：
- 问题类型（创建/修复/研究/决策）
- 复杂度评估（1-10）
- 置信度评估

### 2. 思维模型选择
根据问题类型自动选择最佳模型：
- **研究型模式**: 创建技能、研究问题、调查方案
- **诊断型模式**: 系统修复、故障排除、错误诊断
- **通用管道**: 一般决策、复杂分析

### 3. 历史案例查询
查询相似问题的历史处理记录，获取经验参考

## 常用命令

| 命令 | 功能 |
|------|------|
| 启动研究型模式 | 开始研究型思维流程 |
| 启动诊断型模式 | 开始诊断型思维流程 |
| 分析这个问题 | 自动分析并选择模型 |
| 查询历史XXX | 查找相关历史案例 |
| 显示统计 | 查看使用统计数据 |
| 清除30天旧记录 | 清理历史数据 |

## 处理流程

每种模式都有多个处理阶段：
1. 问题分析 → 2. 信息收集 → 3. 方案评估 → 4. 综合决策

## 与记忆系统集成

- 自动存储每次处理结果
- 查询历史案例进行参考
- 追踪成功率持续优化

有任何问题随时问我！💡"""
    
    def batch_process(self, problems: List[str]) -> List[Dict]:
        """
        批量处理问题列表
        
        Args:
            problems: 问题列表
            
        Returns:
            处理结果列表
        """
        results = []
        
        for problem in problems:
            result = self.core.execute_thinking(problem)
            self._store_result(result)
            results.append({
                "problem": problem[:50] + "..." if len(problem) > 50 else problem,
                "model": result.selected_model,
                "confidence": result.confidence.value,
                "stages": len(result.stages_completed)
            })
        
        return results


def get_thinking_interface() -> ThinkingInterface:
    """获取思维交互接口实例"""
    return ThinkingInterface()
