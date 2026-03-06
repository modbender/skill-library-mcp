#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
思维模型增强器 - 记忆系统集成模块
Thinking Model Enhancer - Memory System Integration Module

实现与记忆系统的查询、存储和比较功能，支持历史思维模型的持久化和检索。
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import hashlib
import re


@dataclass
class ModelSnapshot:
    """思维模型快照"""
    snapshot_id: str
    model_type: str
    problem_summary: str
    input_hash: str
    output_summary: str
    success: bool
    feedback_score: Optional[int]  # 1-5 用户反馈
    timestamp: str
    duration_ms: float
    stages_used: List[str]
    key_findings: List[str]
    user_rating: Optional[int] = None
    
    def to_dict(self) -> Dict:
        return {
            "snapshot_id": self.snapshot_id,
            "model_type": self.model_type,
            "problem_summary": self.problem_summary,
            "input_hash": self.input_hash,
            "output_summary": self.output_summary,
            "success": self.success,
            "feedback_score": self.feedback_score,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "stages_used": self.stages_used,
            "key_findings": self.key_findings,
            "user_rating": self.user_rating
        }


class ThinkingMemory:
    """思维模型记忆管理器"""
    
    def __init__(self, memory_dir: Optional[str] = None):
        """
        初始化思维记忆管理器
        
        Args:
            memory_dir: 记忆存储目录
        """
        if memory_dir is None:
            self.memory_dir = Path.home() / ".claude" / "thinking_models" / "memory"
        else:
            self.memory_dir = Path(memory_dir)
        
        # 确保目录存在
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化索引文件
        self.index_file = self.memory_dir / "model_index.json"
        self._init_index()
    
    def _init_index(self):
        """初始化记忆索引"""
        if not self.index_file.exists():
            index_data = {
                "last_updated": datetime.now().isoformat(),
                "total_snapshots": 0,
                "by_type": {},
                "by_success": {"success": 0, "failed": 0},
                "avg_rating": 0,
                "frequent_problems": []
            }
            self._save_index(index_data)
    
    def _load_index(self) -> Dict:
        """加载记忆索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._init_index() or {"last_updated": "", "total_snapshots": 0}
    
    def _save_index(self, index_data: Dict):
        """保存记忆索引"""
        index_data["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def _generate_input_hash(self, input_text: str) -> str:
        """生成输入的哈希值"""
        # 标准化输入
        normalized = re.sub(r'\s+', '', input_text.lower())
        return hashlib.md5(normalized.encode()).hexdigest()[:12]
    
    def store_snapshot(self, snapshot: ModelSnapshot) -> bool:
        """
        存储思维模型快照
        
        Args:
            snapshot: ModelSnapshot 对象
            
        Returns:
            是否存储成功
        """
        try:
            # 生成快照ID（如果没有）
            if not snapshot.snapshot_id:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                snapshot.snapshot_id = f"{snapshot.model_type}_{timestamp}_{snapshot.input_hash}"
            
            # 保存快照文件
            snapshot_file = self.memory_dir / f"{snapshot.snapshot_id}.json"
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot.to_dict(), f, ensure_ascii=False, indent=2)
            
            # 更新索引
            index = self._load_index()
            index["total_snapshots"] += 1
            
            # 更新类型统计
            if snapshot.model_type not in index["by_type"]:
                index["by_type"][snapshot.model_type] = 0
            index["by_type"][snapshot.model_type] += 1
            
            # 更新成功率
            if snapshot.success:
                index["by_success"]["success"] += 1
            else:
                index["by_success"]["failed"] += 1
            
            # 更新评分
            if snapshot.user_rating:
                current_avg = index.get("avg_rating", 0)
                count = index["by_type"].get(snapshot.model_type, 1)
                index["avg_rating"] = (current_avg * (count - 1) + snapshot.user_rating) / count
            
            self._save_index(index)
            
            return True
        except Exception as e:
            print(f"存储快照失败: {e}")
            return False
    
    def query_similar_problems(self, 
                               query: str, 
                               model_type: Optional[str] = None,
                               limit: int = 5) -> List[Dict]:
        """
        查询相似问题的历史记录
        
        Args:
            query: 查询问题
            model_type: 可选，按模型类型过滤
            limit: 返回结果数量限制
            
        Returns:
            相似问题的历史记录列表
        """
        query_hash = self._generate_input_hash(query)
        query_keywords = set(re.findall(r'[\w]+', query.lower()))
        
        results = []
        
        # 遍历所有快照文件
        for snapshot_file in self.memory_dir.glob("*.json"):
            if snapshot_file.name == "model_index.json":
                continue
            
            try:
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    snapshot = json.load(f)
                
                # 按模型类型过滤
                if model_type and snapshot.get("model_type") != model_type:
                    continue
                
                # 计算相似度
                snapshot_keywords = set(re.findall(r'[\w]+', 
                    snapshot.get("problem_summary", "").lower()))
                
                # 计算关键词重叠
                overlap = len(query_keywords & snapshot_keywords)
                
                if overlap > 0:
                    results.append({
                        "snapshot": snapshot,
                        "similarity_score": overlap,
                        "match_type": "keyword_overlap"
                    })
                    
            except Exception:
                continue
        
        # 按相似度排序
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return [r["snapshot"] for r in results[:limit]]
    
    def get_model_statistics(self, model_type: Optional[str] = None) -> Dict[str, Any]:
        """
        获取模型使用统计
        
        Args:
            model_type: 可选，按模型类型过滤
            
        Returns:
            统计信息字典
        """
        index = self._load_index()
        
        stats = {
            "total_snapshots": index["total_snapshots"],
            "by_type": index["by_type"],
            "success_rate": 0,
            "avg_rating": index.get("avg_rating", 0)
        }
        
        # 计算成功率
        total = index["by_success"]["success"] + index["by_success"]["failed"]
        if total > 0:
            stats["success_rate"] = index["by_success"]["success"] / total
        
        # 如果指定了模型类型
        if model_type:
            model_stats = self._get_model_detail_stats(model_type)
            stats.update(model_stats)
        
        return stats
    
    def _get_model_detail_stats(self, model_type: str) -> Dict:
        """获取特定模型的详细统计"""
        snapshots = []
        
        for snapshot_file in self.memory_dir.glob("*.json"):
            if snapshot_file.name == "model_index.json":
                continue
            
            try:
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    snapshot = json.load(f)
                    if snapshot.get("model_type") == model_type:
                        snapshots.append(snapshot)
            except Exception:
                continue
        
        if not snapshots:
            return {"model_type": model_type, "count": 0}
        
        # 计算统计
        ratings = [s.get("user_rating") for s in snapshots if s.get("user_rating")]
        successes = [s for s in snapshots if s.get("success")]
        
        return {
            "model_type": model_type,
            "count": len(snapshots),
            "success_count": len(successes),
            "success_rate": len(successes) / len(snapshots) if snapshots else 0,
            "avg_rating": sum(ratings) / len(ratings) if ratings else 0,
            "avg_duration_ms": sum(s.get("duration_ms", 0) for s in snapshots) / len(snapshots)
        }
    
    def get_recent_snapshots(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """
        获取最近的快照
        
        Args:
            days: 天数
            limit: 数量限制
            
        Returns:
            最近的快照列表
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        results = []
        
        for snapshot_file in self.memory_dir.glob("*.json"):
            if snapshot_file.name == "model_index.json":
                continue
            
            try:
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    snapshot = json.load(f)
                    
                    if snapshot.get("timestamp", "") >= cutoff_date:
                        results.append(snapshot)
                        
            except Exception:
                continue
        
        # 按时间排序
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return results[:limit]
    
    def clear_old_snapshots(self, days: int = 90) -> int:
        """
        清理旧快照
        
        Args:
            days: 超过多少天的快照被清理
            
        Returns:
            清理的快照数量
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        cleared_count = 0
        
        for snapshot_file in self.memory_dir.glob("*.json"):
            if snapshot_file.name == "model_index.json":
                continue
            
            try:
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    snapshot = json.load(f)
                    
                if snapshot.get("timestamp", "") < cutoff_date:
                    snapshot_file.unlink()
                    cleared_count += 1
                    
            except Exception:
                continue
        
        return cleared_count
    
    def compare_with_history(self, 
                             current_problem: str,
                             model_type: str,
                             limit: int = 3) -> Dict[str, Any]:
        """
        将当前问题与历史案例比较
        
        Args:
            current_problem: 当前问题
            model_type: 使用的模型类型
            limit: 比较的历史案例数量
            
        Returns:
            比较结果
        """
        # 获取历史案例
        history = self.query_similar_problems(current_problem, model_type, limit)
        
        if not history:
            return {
                "status": "no_history",
                "message": "未找到相似历史案例",
                "recommendations": ["这是新类型的问题", "建议记录本次处理结果供未来参考"]
            }
        
        # 统计历史成功率
        successful = [h for h in history if h.get("success")]
        success_rate = len(successful) / len(history) if history else 0
        
        # 提取常见模式
        common_findings = {}
        for h in history:
            for finding in h.get("key_findings", []):
                if finding not in common_findings:
                    common_findings[finding] = 0
                common_findings[finding] += 1
        
        # 排序并获取最常见的发现
        sorted_findings = sorted(common_findings.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "status": "comparison_complete",
            "history_count": len(history),
            "historical_success_rate": success_rate,
            "common_patterns": [f for f, _ in sorted_findings[:5]],
            "previous_approaches": [h.get("output_summary", "") for h in history[:3]],
            "recommendations": self._generate_recommendations(history, success_rate)
        }
    
    def _generate_recommendations(self, history: List[Dict], success_rate: float) -> List[str]:
        """基于历史生成建议"""
        recommendations = []
        
        if success_rate > 0.7:
            recommendations.append("历史成功率较高，可以参考之前的成功模式")
        elif success_rate < 0.3:
            recommendations.append("历史成功率较低，建议尝试不同的方法")
        else:
            recommendations.append("历史成功率中等，建议结合多种方法")
        
        if history:
            first_history = history[0]
            if first_history.get("user_rating"):
                recommendations.append(f"用户对该类问题的历史评分: {first_history['user_rating']}/5")
        
        return recommendations
    
    def get_memory_summary(self) -> str:
        """获取记忆系统摘要"""
        index = self._load_index()
        
        lines = [
            "🧠 思维模型记忆系统摘要",
            "=" * 50,
            f"",
            f"📊 快照总数: {index['total_snapshots']}",
            f"📈 成功率: {index['by_success']['success']}/{index['by_success']['success'] + index['by_success']['failed']}",
        ]
        
        if index["by_type"]:
            lines.append(f"")
            lines.append(f"📂 按模型类型:")
            for model_type, count in sorted(index["by_type"].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"   • {model_type}: {count}次")
        
        if index.get("avg_rating", 0) > 0:
            lines.extend([
                f"",
                f"⭐ 平均评分: {index['avg_rating']:.1f}/5"
            ])
        
        lines.extend([
            f"",
            f"🕐 最后更新: {index['last_updated'][:19] if index['last_updated'] else '未知'}",
        ])
        
        return "\n".join(lines)


def get_thinking_memory() -> ThinkingMemory:
    """获取思维记忆实例"""
    return ThinkingMemory()
