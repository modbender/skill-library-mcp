"""
记忆存储模块

功能：
- 管理已回答问题列表（去重）
- 管理待审核队列（增删改查）
- 记录操作日志
- 数据持久化到 JSON 文件

数据文件：
- data/answered.json: 已回答问题ID列表
- data/pending.json: 待审核队列
- logs/operation.log: 操作日志（JSON Lines 格式）

使用方法：
    from memory_store import MemoryStore
    
    memory = MemoryStore(data_dir='./data', log_dir='./logs')
    
    # 检查是否已回答
    if memory.is_answered('123456'):
        print('已回答过')
    
    # 添加到待审核队列
    pending_id = memory.add_pending(question, draft)
    
    # 更新状态
    memory.update_pending_status(pending_id, 'published')
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MemoryStore:
    """
    记忆存储管理器
    
    负责管理所有数据的持久化存储，包括：
    - 已回答问题的去重
    - 待审核队列的管理
    - 操作日志的记录
    
    Attributes:
        data_dir: 数据文件存储目录
        log_dir: 日志文件存储目录
        answered_file: 已回答问题列表文件路径
        pending_file: 待审核队列文件路径
        log_file: 操作日志文件路径
    """
    
    def __init__(self, data_dir: str = "./data", log_dir: str = "./logs"):
        """
        初始化存储管理器
        
        Args:
            data_dir: 数据文件存储目录，默认 ./data
            log_dir: 日志文件存储目录，默认 ./logs
        """
        self.data_dir = Path(data_dir)
        self.log_dir = Path(log_dir)
        
        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 文件路径
        self.answered_file = self.data_dir / "answered.json"
        self.pending_file = self.data_dir / "pending.json"
        self.log_file = self.log_dir / "operation.log"
        
        # 内存缓存
        self._answered_cache: set = set()
        self._pending_cache: List[Dict] = []
        
        self._load_data()
    
    def _load_data(self):
        """从磁盘加载数据到内存缓存"""
        # 加载已回答问题
        if self.answered_file.exists():
            try:
                with open(self.answered_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._answered_cache = set(data.get('question_ids', []))
                logger.info(f"已加载 {len(self._answered_cache)} 条已回答问题记录")
            except Exception as e:
                logger.error(f"加载已回答问题失败: {e}")
                self._answered_cache = set()
        
        # 加载待审核队列
        if self.pending_file.exists():
            try:
                with open(self.pending_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._pending_cache = data.get('items', [])
                logger.info(f"已加载 {len(self._pending_cache)} 条待审核记录")
            except Exception as e:
                logger.error(f"加载待审核队列失败: {e}")
                self._pending_cache = []
    
    def _save_answered(self):
        """保存已回答问题列表到磁盘"""
        try:
            data = {
                'question_ids': list(self._answered_cache),
                'updated_at': datetime.now().isoformat()
            }
            with open(self.answered_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存已回答问题失败: {e}")
    
    def _save_pending(self):
        """保存待审核队列到磁盘"""
        try:
            data = {
                'items': self._pending_cache,
                'updated_at': datetime.now().isoformat()
            }
            with open(self.pending_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存待审核队列失败: {e}")
    
    # ========== 已回答问题管理 ==========
    
    def is_answered(self, question_id: str) -> bool:
        """
        检查问题是否已回答过
        
        Args:
            question_id: 问题ID
            
        Returns:
            True 如果已回答，False 否则
        """
        return question_id in self._answered_cache
    
    def add_answered(self, question_id: str, title: str = ""):
        """
        标记问题为已回答
        
        Args:
            question_id: 问题ID
            title: 问题标题（用于日志）
        """
        self._answered_cache.add(question_id)
        self._save_answered()
        self.log_operation("ANSWERED", f"问题已回答: {title} (ID: {question_id})")
        logger.info(f"标记问题为已回答: {question_id}")
    
    def get_answered_count(self) -> int:
        """获取已回答问题数量"""
        return len(self._answered_cache)
    
    # ========== 待审核队列管理 ==========
    
    def add_pending(self, question: Dict, draft: str) -> str:
        """
        添加待审核项
        
        Args:
            question: 问题信息字典，包含 id, title, url, heat 等
            draft: 生成的回答草稿
            
        Returns:
            pending_id: 待审核项唯一ID
        """
        # 生成唯一ID：P + 时间戳 + 问题ID
        pending_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}_{question['id']}"
        
        item = {
            'id': pending_id,
            'question_id': question['id'],
            'title': question['title'],
            'url': question['url'],
            'heat': question.get('heat', 0),
            'draft': draft,
            'status': 'pending',  # pending / approved / rejected / published
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'feishu_message_id': None  # 飞书消息ID
        }
        
        self._pending_cache.append(item)
        self._save_pending()
        
        self.log_operation("PENDING_ADD", f"添加待审核: {question['title']}")
        logger.info(f"添加待审核项: {pending_id}")
        
        return pending_id
    
    def get_pending(self, status: str = 'pending') -> List[Dict]:
        """
        获取待审核列表
        
        Args:
            status: 筛选状态（pending/approved/rejected/published/all）
            
        Returns:
            待审核项列表
        """
        if status == 'all':
            return self._pending_cache.copy()
        return [item for item in self._pending_cache if item['status'] == status]
    
    def get_pending_by_id(self, pending_id: str) -> Optional[Dict]:
        """
        通过ID获取待审核项
        
        Args:
            pending_id: 待审核项ID
            
        Returns:
            待审核项字典，不存在返回 None
        """
        for item in self._pending_cache:
            if item['id'] == pending_id:
                return item
        return None
    
    def update_pending_status(self, pending_id: str, status: str, feishu_msg_id: str = None) -> bool:
        """
        更新待审核项状态
        
        Args:
            pending_id: 待审核项ID
            status: 新状态（approved/rejected/published）
            feishu_msg_id: 飞书消息ID（可选）
            
        Returns:
            True 如果更新成功，False 否则
        """
        for item in self._pending_cache:
            if item['id'] == pending_id:
                item['status'] = status
                item['updated_at'] = datetime.now().isoformat()
                if feishu_msg_id:
                    item['feishu_message_id'] = feishu_msg_id
                
                self._save_pending()
                self.log_operation("PENDING_UPDATE", f"更新状态: {pending_id} -> {status}")
                logger.info(f"更新待审核项状态: {pending_id} -> {status}")
                return True
        
        logger.warning(f"待审核项不存在: {pending_id}")
        return False
    
    def remove_pending(self, pending_id: str) -> bool:
        """
        删除待审核项
        
        Args:
            pending_id: 待审核项ID
            
        Returns:
            True 如果删除成功，False 否则
        """
        for i, item in enumerate(self._pending_cache):
            if item['id'] == pending_id:
                self._pending_cache.pop(i)
                self._save_pending()
                self.log_operation("PENDING_REMOVE", f"删除: {pending_id}")
                return True
        return False
    
    # ========== 操作日志 ==========
    
    def log_operation(self, action: str, detail: str):
        """
        记录操作日志
        
        Args:
            action: 操作类型，如 ANSWERED, PENDING_ADD, PUBLISH 等
            detail: 详细信息
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'detail': detail
        }
        
        # 追加到日志文件（JSON Lines 格式）
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"写入日志失败: {e}")
    
    def get_logs(self, limit: int = 100, action_filter: str = None) -> List[Dict]:
        """
        获取操作日志
        
        Args:
            limit: 返回最近 N 条
            action_filter: 按操作类型筛选
            
        Returns:
            日志条目列表
        """
        logs = []
        
        if not self.log_file.exists():
            return logs
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if action_filter and entry.get('action') != action_filter:
                            continue
                        logs.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"读取日志失败: {e}")
        
        # 返回最近的 N 条
        return logs[-limit:]
    
    # ========== 统计信息 ==========
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计字典，包含各状态数量
        """
        pending = self.get_pending('pending')
        approved = self.get_pending('approved')
        published = self.get_pending('published')
        rejected = self.get_pending('rejected')
        
        return {
            'answered_count': len(self._answered_cache),
            'pending_count': len(pending),
            'approved_count': len(approved),
            'published_count': len(published),
            'rejected_count': len(rejected),
            'total_drafts': len(self._pending_cache)
        }


if __name__ == '__main__':
    # 测试代码
    store = MemoryStore()
    
    # 测试添加待审核
    test_question = {
        'id': '123456',
        'title': '测试问题',
        'url': 'https://zhihu.com/question/123456',
        'heat': 100.5
    }
    pending_id = store.add_pending(test_question, "这是测试回答草稿")
    print(f"添加待审核项: {pending_id}")
    
    # 测试获取统计
    stats = store.get_stats()
    print(f"统计: {json.dumps(stats, ensure_ascii=False, indent=2)}")
