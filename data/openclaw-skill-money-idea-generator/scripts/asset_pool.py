#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资产池管理
保存灵感、跟踪执行、记录收益
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class AssetPool:
    """资产池管理器"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser('~/.openclaw/workspace/memory/money-ideas')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.ideas_file = os.path.join(self.data_dir, 'ideas.json')
        self.execution_file = os.path.join(self.data_dir, 'executions.json')
        self.revenue_file = os.path.join(self.data_dir, 'revenue.json')
        
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        self.ideas = self._load_json(self.ideas_file, [])
        self.executions = self._load_json(self.execution_file, [])
        self.revenues = self._load_json(self.revenue_file, [])
    
    def _load_json(self, filepath: str, default):
        """加载 JSON 文件"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def _save_json(self, filepath: str, data):
        """保存 JSON 文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # === 灵感池 ===
    
    def add_idea(self, idea: Dict) -> str:
        """
        添加灵感到资产池
        
        Args:
            idea: 灵感信息
            
        Returns:
            灵感 ID
        """
        idea_id = f"idea-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        idea['id'] = idea_id
        idea['created_at'] = datetime.now().isoformat()
        idea['status'] = 'pending'  # pending, in_progress, completed, failed
        idea['score'] = 0  # 潜力分数
        idea['tags'] = idea.get('tags', [])
        
        self.ideas.append(idea)
        self._save_json(self.ideas_file, self.ideas)
        
        return idea_id
    
    def get_idea(self, idea_id: str) -> Optional[Dict]:
        """获取灵感"""
        for idea in self.ideas:
            if idea['id'] == idea_id:
                return idea
        return None
    
    def list_ideas(self, status: str = None, limit: int = 10) -> List[Dict]:
        """
        列出灵感
        
        Args:
            status: 状态筛选
            limit: 数量限制
            
        Returns:
            灵感列表
        """
        ideas = self.ideas
        
        if status:
            ideas = [i for i in ideas if i.get('status') == status]
        
        # 按创建时间倒序
        ideas = sorted(ideas, key=lambda x: x.get('created_at', ''), reverse=True)
        
        return ideas[:limit]
    
    def update_idea_status(self, idea_id: str, status: str, notes: str = None):
        """更新灵感状态"""
        for idea in self.ideas:
            if idea['id'] == idea_id:
                idea['status'] = status
                idea['updated_at'] = datetime.now().isoformat()
                if notes:
                    idea['notes'] = notes
                self._save_json(self.ideas_file, self.ideas)
                return True
        return False
    
    # === 执行跟踪 ===
    
    def start_execution(self, idea_id: str) -> str:
        """
        开始执行灵感
        
        Args:
            idea_id: 灵感 ID
            
        Returns:
            执行 ID
        """
        exec_id = f"exec-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        execution = {
            'id': exec_id,
            'idea_id': idea_id,
            'started_at': datetime.now().isoformat(),
            'status': 'in_progress',
            'steps': [],
            'logs': [],
        }
        
        self.executions.append(execution)
        self._save_json(self.execution_file, self.executions)
        
        # 更新灵感状态
        self.update_idea_status(idea_id, 'in_progress')
        
        return exec_id
    
    def add_execution_step(self, exec_id: str, step: str, status: str = 'completed'):
        """添加执行步骤"""
        for execution in self.executions:
            if execution['id'] == exec_id:
                execution['steps'].append({
                    'step': step,
                    'status': status,
                    'timestamp': datetime.now().isoformat(),
                })
                self._save_json(self.execution_file, self.executions)
                return True
        return False
    
    def add_execution_log(self, exec_id: str, log: str):
        """添加执行日志"""
        for execution in self.executions:
            if execution['id'] == exec_id:
                execution['logs'].append({
                    'log': log,
                    'timestamp': datetime.now().isoformat(),
                })
                self._save_json(self.execution_file, self.executions)
                return True
        return False
    
    def complete_execution(self, exec_id: str, success: bool = True, notes: str = None):
        """完成执行"""
        for execution in self.executions:
            if execution['id'] == exec_id:
                execution['status'] = 'success' if success else 'failed'
                execution['completed_at'] = datetime.now().isoformat()
                if notes:
                    execution['notes'] = notes
                self._save_json(self.execution_file, self.executions)
                
                # 更新灵感状态
                idea_id = execution['idea_id']
                self.update_idea_status(idea_id, 'completed' if success else 'failed', notes)
                
                return True
        return False
    
    # === 收益记录 ===
    
    def add_revenue(self, idea_id: str, amount: float, source: str, notes: str = None) -> str:
        """
        记录收益
        
        Args:
            idea_id: 灵感 ID
            amount: 金额
            source: 收入来源
            notes: 备注
            
        Returns:
            记录 ID
        """
        rev_id = f"rev-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        revenue = {
            'id': rev_id,
            'idea_id': idea_id,
            'amount': amount,
            'source': source,
            'notes': notes,
            'recorded_at': datetime.now().isoformat(),
        }
        
        self.revenues.append(revenue)
        self._save_json(self.revenue_file, self.revenues)
        
        return rev_id
    
    def get_revenue_stats(self, idea_id: str = None) -> Dict:
        """
        获取收益统计
        
        Args:
            idea_id: 灵感 ID（可选，不传则统计全部）
            
        Returns:
            统计数据
        """
        revenues = self.revenues
        
        if idea_id:
            revenues = [r for r in revenues if r['idea_id'] == idea_id]
        
        total = sum(r['amount'] for r in revenues)
        count = len(revenues)
        avg = total / count if count > 0 else 0
        
        # 按来源统计
        by_source = {}
        for r in revenues:
            source = r['source']
            by_source[source] = by_source.get(source, 0) + r['amount']
        
        return {
            'total': total,
            'count': count,
            'average': avg,
            'by_source': by_source,
        }
    
    # === 统计分析 ===
    
    def get_overview(self) -> Dict:
        """获取资产池概览"""
        # 灵感统计
        idea_stats = {
            'total': len(self.ideas),
            'pending': len([i for i in self.ideas if i.get('status') == 'pending']),
            'in_progress': len([i for i in self.ideas if i.get('status') == 'in_progress']),
            'completed': len([i for i in self.ideas if i.get('status') == 'completed']),
            'failed': len([i for i in self.ideas if i.get('status') == 'failed']),
        }
        
        # 成功率
        finished = idea_stats['completed'] + idea_stats['failed']
        success_rate = idea_stats['completed'] / finished if finished > 0 else 0
        
        # 收益统计
        revenue_stats = self.get_revenue_stats()
        
        # 执行统计
        exec_stats = {
            'total': len(self.executions),
            'in_progress': len([e for e in self.executions if e.get('status') == 'in_progress']),
            'success': len([e for e in self.executions if e.get('status') == 'success']),
            'failed': len([e for e in self.executions if e.get('status') == 'failed']),
        }
        
        return {
            'ideas': idea_stats,
            'success_rate': success_rate,
            'revenue': revenue_stats,
            'executions': exec_stats,
        }


# 测试
if __name__ == '__main__':
    pool = AssetPool()
    
    # 测试添加灵感
    idea_id = pool.add_idea({
        'name': 'OpenClaw 部署服务',
        'description': '帮助用户部署 OpenClaw',
        'type': 'deployment_service',
        'tags': ['AI', '自动化'],
    })
    print(f"添加灵感: {idea_id}")
    
    # 测试开始执行
    exec_id = pool.start_execution(idea_id)
    print(f"开始执行: {exec_id}")
    
    # 添加步骤
    pool.add_execution_step(exec_id, '在闲鱼发布服务')
    pool.add_execution_step(exec_id, '收到第一个客户咨询')
    
    # 完成执行
    pool.complete_execution(exec_id, success=True, notes='第一个客户成功交付')
    
    # 记录收益
    pool.add_revenue(idea_id, 299, '闲鱼', 'OpenClaw 部署服务')
    
    # 查看统计
    overview = pool.get_overview()
    print("\n=== 资产池概览 ===")
    print(json.dumps(overview, indent=2, ensure_ascii=False))