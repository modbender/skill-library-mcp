#!/usr/bin/env python3
"""
Agent 群聊协作系统 - 决策投票模块
负责决策提议的创建、投票、结果统计等
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import db
    from agent_manager import AgentManager
    from message_manager import MessageManager
except ImportError:
    from .database import db
    from .agent_manager import AgentManager
    from .message_manager import MessageManager


class DecisionStatus:
    """决策状态常量"""
    PROPOSED = "proposed"
    DISCUSSING = "discussing"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class VoteType:
    """投票类型常量"""
    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"


class Decision:
    """决策类"""
    
    def __init__(self, id: int = None, decision_db_id: int = None, decision_id: str = "",
                 title: str = "", description: str = "", group_id: Optional[int] = None,
                 proposer_id: int = None, status: str = "proposed", votes_for: int = 0,
                 votes_against: int = 0, decided_at: Optional[str] = None,
                 created_at: str = "", **kwargs):
        self.id = id if id is not None else decision_db_id
        self.decision_id = decision_id
        self.title = title
        self.description = description
        self.group_id = group_id
        self.proposer_id = proposer_id
        self.status = status
        self.votes_for = votes_for
        self.votes_against = votes_against
        self.decided_at = decided_at
        self.created_at = created_at
        
        # 额外字段
        self.proposer_name: Optional[str] = kwargs.get('proposer_name')
        self.group_name: Optional[str] = kwargs.get('group_name')
        self.votes: List[Dict] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'decision_id': self.decision_id,
            'title': self.title,
            'description': self.description,
            'group_id': self.group_id,
            'group_name': self.group_name,
            'proposer_id': self.proposer_id,
            'proposer_name': self.proposer_name,
            'status': self.status,
            'votes_for': self.votes_for,
            'votes_against': self.votes_against,
            'decided_at': self.decided_at,
            'created_at': self.created_at,
            'votes': self.votes
        }
    
    @property
    def total_votes(self) -> int:
        """获取总投票数"""
        return self.votes_for + self.votes_against
    
    @property
    def pass_rate(self) -> float:
        """获取通过率"""
        total = self.total_votes
        if total == 0:
            return 0.0
        return (self.votes_for / total) * 100
    
    def __repr__(self):
        return f"Decision({self.decision_id}: {self.title})"


class DecisionManager:
    """决策管理器"""
    
    _decision_counter = 0
    
    @staticmethod
    def generate_decision_id() -> str:
        """生成决策唯一标识"""
        DecisionManager._decision_counter += 1
        return f"DEC-{datetime.now().strftime('%Y%m%d')}-{DecisionManager._decision_counter:03d}"
    
    @staticmethod
    def create(title: str, description: str, proposer_id: int,
               group_id: Optional[int] = None) -> Optional[Decision]:
        """创建决策提议"""
        decision_id = DecisionManager.generate_decision_id()
        
        try:
            db_id = db.insert(
                """INSERT INTO decisions (decision_id, title, description, group_id, proposer_id,
                    status, votes_for, votes_against, created_at)
                   VALUES (?, ?, ?, ?, ?, 'proposed', 0, 0, ?)""",
                (decision_id, title, description, group_id, proposer_id, datetime.now().isoformat())
            )
            
            # 发送决策提议消息
            proposer = AgentManager.get_by_id(proposer_id)
            if proposer:
                content = f"📊 新决策提议\n\n**{title}**\n{description}\n\n请投票: for/against/abstain\n决策ID: {decision_id}"
                MessageManager.send_message(
                    from_agent_id=proposer_id,
                    content=content,
                    group_id=group_id,
                    msg_type="decision"
                )
            
            return DecisionManager.get_by_id(db_id)
        except Exception as e:
            print(f"创建决策提议失败: {e}")
            return None
    
    @staticmethod
    def get_by_id(decision_db_id: int) -> Optional[Decision]:
        """通过 ID 获取决策"""
        row = db.fetch_one(
            """SELECT d.*, 
                      a.name as proposer_name,
                      g.name as group_name
               FROM decisions d
               LEFT JOIN agents a ON d.proposer_id = a.id
               LEFT JOIN groups g ON d.group_id = g.id
               WHERE d.id = ?""",
            (decision_db_id,)
        )
        if row:
            decision = Decision(**row)
            decision.proposer_name = row.get('proposer_name')
            decision.group_name = row.get('group_name')
            decision.votes = DecisionManager.get_votes(decision_db_id)
            return decision
        return None
    
    @staticmethod
    def get_by_decision_id(decision_id: str) -> Optional[Decision]:
        """通过决策标识获取决策"""
        row = db.fetch_one(
            """SELECT d.*, 
                      a.name as proposer_name,
                      g.name as group_name
               FROM decisions d
               LEFT JOIN agents a ON d.proposer_id = a.id
               LEFT JOIN groups g ON d.group_id = g.id
               WHERE d.decision_id = ?""",
            (decision_id,)
        )
        if row:
            decision = Decision(**row)
            decision.proposer_name = row.get('proposer_name')
            decision.group_name = row.get('group_name')
            decision.votes = DecisionManager.get_votes(row['id'])
            return decision
        return None
    
    @staticmethod
    def get_all(status: Optional[str] = None, group_id: Optional[int] = None) -> List[Decision]:
        """获取所有决策提议"""
        query = """SELECT d.*, 
                          a.name as proposer_name,
                          g.name as group_name
                   FROM decisions d
                   LEFT JOIN agents a ON d.proposer_id = a.id
                   LEFT JOIN groups g ON d.group_id = g.id"""
        params = []
        conditions = []
        
        if status:
            conditions.append("d.status = ?")
            params.append(status)
        if group_id:
            conditions.append("d.group_id = ?")
            params.append(group_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY d.created_at DESC"
        
        rows = db.fetch_all(query, tuple(params))
        decisions = []
        for row in rows:
            decision = Decision(**row)
            decision.proposer_name = row.get('proposer_name')
            decision.group_name = row.get('group_name')
            decision.votes = DecisionManager.get_votes(row['id'])
            decisions.append(decision)
        return decisions
    
    @staticmethod
    def vote(decision_db_id: int, agent_id: int, vote: str, comment: str = "") -> bool:
        """投票"""
        valid_votes = ['for', 'against', 'abstain']
        if vote not in valid_votes:
            print(f"无效的投票选项: {vote}. 请使用 for/against/abstain")
            return False
        
        decision = DecisionManager.get_by_id(decision_db_id)
        if not decision:
            print("决策不存在")
            return False
        
        if decision.status not in ['proposed', 'discussing']:
            print(f"决策已关闭，无法投票 (当前状态: {decision.status})")
            return False
        
        # 检查是否已经投过票
        existing = db.fetch_one(
            "SELECT id FROM decision_votes WHERE decision_id = ? AND agent_id = ?",
            (decision_db_id, agent_id)
        )
        
        if existing:
            # 更新投票
            db.execute(
                "UPDATE decision_votes SET vote = ?, comment = ? WHERE id = ?",
                (vote, comment, existing['id'])
            )
        else:
            # 新增投票
            db.execute(
                """INSERT INTO decision_votes (decision_id, agent_id, vote, comment, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (decision_db_id, agent_id, vote, comment, datetime.now().isoformat())
            )
        
        # 更新决策的投票计数
        if vote == 'for':
            db.execute(
                "UPDATE decisions SET votes_for = votes_for + 1 WHERE id = ?",
                (decision_db_id,)
            )
        elif vote == 'against':
            db.execute(
                "UPDATE decisions SET votes_against = votes_against + 1 WHERE id = ?",
                (decision_db_id,)
            )
        
        # 发送投票通知
        agent = AgentManager.get_by_id(agent_id)
        vote_text = {'for': '✅ 赞成', 'against': '❌ 反对', 'abstain': '⚪ 弃权'}.get(vote, vote)
        
        content = f"🗳️ {agent.name if agent else 'Agent'} 投票: {vote_text}\n决策: {decision.title}"
        if comment:
            content += f"\n意见: {comment}"
        
        MessageManager.send_message(
            from_agent_id=agent_id,
            content=content,
            group_id=decision.group_id,
            msg_type="chat"
        )
        
        return True
    
    @staticmethod
    def update_status(decision_db_id: int, new_status: str, updater_id: int) -> bool:
        """更新决策状态"""
        valid_status = ['proposed', 'discussing', 'approved', 'rejected', 'implemented']
        if new_status not in valid_status:
            print(f"无效的状态: {new_status}")
            return False
        
        decision = DecisionManager.get_by_id(decision_db_id)
        if not decision:
            return False
        
        decided_at = datetime.now().isoformat() if new_status in ['approved', 'rejected'] else None
        
        affected = db.execute(
            "UPDATE decisions SET status = ?, decided_at = ? WHERE id = ?",
            (new_status, decided_at, decision_db_id)
        )
        
        if affected > 0:
            status_text = {
                'proposed': '提议中',
                'discussing': '讨论中',
                'approved': '已通过',
                'rejected': '已否决',
                'implemented': '已实施'
            }.get(new_status, new_status)
            
            updater = AgentManager.get_by_id(updater_id)
            content = f"📊 决策状态更新\n\n**{decision.title}**\n新状态: {status_text}"
            
            MessageManager.send_message(
                from_agent_id=updater_id,
                content=content,
                group_id=decision.group_id,
                msg_type="decision"
            )
            
            return True
        return False
    
    @staticmethod
    def get_votes(decision_db_id: int) -> List[Dict]:
        """获取决策的所有投票"""
        rows = db.fetch_all(
            """SELECT dv.*, a.name as agent_name
               FROM decision_votes dv
               JOIN agents a ON dv.agent_id = a.id
               WHERE dv.decision_id = ?
               ORDER BY dv.created_at""",
            (decision_db_id,)
        )
        return [dict(row) for row in rows]
    
    @staticmethod
    def has_voted(decision_db_id: int, agent_id: int) -> bool:
        """检查 Agent 是否已经投票"""
        result = db.fetch_one(
            "SELECT 1 FROM decision_votes WHERE decision_id = ? AND agent_id = ?",
            (decision_db_id, agent_id)
        )
        return result is not None
    
    @staticmethod
    def delete(decision_db_id: int) -> bool:
        """删除决策"""
        affected = db.execute("DELETE FROM decisions WHERE id = ?", (decision_db_id,))
        return affected > 0
    
    @staticmethod
    def format_decision_for_display(decision: Decision, show_votes: bool = False) -> str:
        """格式化决策用于显示"""
        status_emoji = {
            'proposed': '📝',
            'discussing': '💬',
            'approved': '✅',
            'rejected': '❌',
            'implemented': '🚀'
        }.get(decision.status, '⚪')
        
        lines = [
            f"{status_emoji} [{decision.decision_id}] {decision.title}",
            f"   提案人: {decision.proposer_name} | 状态: {decision.status}",
            f"   投票: ✅ {decision.votes_for} 票 | ❌ {decision.votes_against} 票 | 通过率: {decision.pass_rate:.1f}%"
        ]
        
        if decision.description:
            lines.append(f"   描述: {decision.description[:60]}{'...' if len(decision.description) > 60 else ''}")
        
        if show_votes and decision.votes:
            lines.append("   投票详情:")
            for v in decision.votes:
                vote_emoji = {'for': '✅', 'against': '❌', 'abstain': '⚪'}.get(v['vote'], '⚪')
                lines.append(f"     {vote_emoji} {v['agent_name']}: {v['vote']}")
        
        return "\n".join(lines)
