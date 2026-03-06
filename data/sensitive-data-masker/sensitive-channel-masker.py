#!/usr/bin/env python3
"""Channel 级敏感信息脱敏器。

在 Channel 消息接收时脱敏，维护临时映射表（7 天），本地可还原。
"""

import json
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

# ═══════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════

DATA_DIR = Path.home() / ".openclaw" / "data" / "sensitive-masker"
MAPPING_FILE = DATA_DIR / "sensitive-mapping.json"
CONFIG_FILE = DATA_DIR / "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "enabled": True,
    "ttl_days": 7,  # 映射表保留天数
    "auto_cleanup": True,  # 自动清理过期数据
    "log_enabled": True
}

# ═══════════════════════════════════════════════════════════════
# 数据管理
# ═══════════════════════════════════════════════════════════════

class SensitiveMappingStore:
    """敏感数据映射存储。"""
    
    def __init__(self):
        self.mapping: Dict[str, dict] = {}
        self.config = self._load_config()
        self._load_mapping()
    
    def _load_config(self) -> dict:
        """加载配置。"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 创建默认配置
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        
        return DEFAULT_CONFIG
    
    def _load_mapping(self):
        """加载映射表。"""
        if MAPPING_FILE.exists():
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                self.mapping = json.load(f)
            
            # 清理过期数据
            if self.config.get('auto_cleanup'):
                self._cleanup_expired()
    
    def _save_mapping(self):
        """保存映射表。"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.mapping, f, indent=2, ensure_ascii=False)
        
        # 设置权限
        MAPPING_FILE.chmod(0o600)
    
    def _cleanup_expired(self):
        """清理过期数据。"""
        now = datetime.now().isoformat()
        expired = []
        
        for mask_id, data in self.mapping.items():
            if data.get('expires_at', '') < now:
                expired.append(mask_id)
        
        for mask_id in expired:
            del self.mapping[mask_id]
        
        if expired:
            self._save_mapping()
            print(f"✅ 清理了 {len(expired)} 条过期数据")
    
    def add_mapping(self, original: str, data_type: str) -> str:
        """添加敏感数据映射。
        
        Args:
            original: 原始敏感数据
            data_type: 数据类型（password, api_key, etc.）
        
        Returns:
            mask_id: 脱敏标识符
        """
        # 生成唯一标识符
        mask_id = hashlib.sha256(
            f"{original}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # 计算过期时间
        expires_at = (datetime.now() + timedelta(days=self.config['ttl_days'])).isoformat()
        
        # 存储映射
        self.mapping[mask_id] = {
            "original": original,
            "data_type": data_type,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "usage_count": 0
        }
        
        self._save_mapping()
        return mask_id
    
    def get_original(self, mask_id: str) -> Optional[str]:
        """根据 mask_id 获取原始数据。
        
        Args:
            mask_id: 脱敏标识符
        
        Returns:
            原始数据，如果不存在或已过期则返回 None
        """
        data = self.mapping.get(mask_id)
        
        if not data:
            return None
        
        # 检查是否过期
        if data.get('expires_at', '') < datetime.now().isoformat():
            del self.mapping[mask_id]
            self._save_mapping()
            return None
        
        # 增加使用计数
        data['usage_count'] = data.get('usage_count', 0) + 1
        self._save_mapping()
        
        return data.get('original')
    
    def remove_mapping(self, mask_id: str) -> bool:
        """删除映射。
        
        Args:
            mask_id: 脱敏标识符
        
        Returns:
            是否成功删除
        """
        if mask_id in self.mapping:
            del self.mapping[mask_id]
            self._save_mapping()
            return True
        return False
    
    def get_stats(self) -> dict:
        """获取统计信息。"""
        now = datetime.now()
        
        total = len(self.mapping)
        by_type = {}
        expiring_soon = 0
        
        for data in self.mapping.values():
            # 按类型统计
            data_type = data.get('data_type', 'unknown')
            by_type[data_type] = by_type.get(data_type, 0) + 1
            
            # 即将过期（24 小时内）
            expires_at = datetime.fromisoformat(data.get('expires_at', ''))
            if (expires_at - now).total_seconds() < 86400:
                expiring_soon += 1
        
        return {
            "total": total,
            "by_type": by_type,
            "expiring_soon": expiring_soon,
            "ttl_days": self.config['ttl_days']
        }

# ═══════════════════════════════════════════════════════════════
# Channel 脱敏器
# ═══════════════════════════════════════════════════════════════

class ChannelSensitiveMasker:
    """Channel 级敏感信息脱敏器。"""
    
    def __init__(self):
        self.store = SensitiveMappingStore()
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> list:
        """加载脱敏规则。"""
        return [
            {
                "name": "password",
                "regex": r"(?i)(password=|password:|passwd=|pwd=)[\w@#$%^&*!]+",
                "type": "password"
            },
            {
                "name": "api_key",
                "regex": r"sk-[a-zA-Z0-9]{20,}",
                "type": "api_key"
            },
            {
                "name": "token",
                "regex": r"(?i)(token=|token:)[\w.-]+",
                "type": "token"
            },
            {
                "name": "secret",
                "regex": r"(?i)(secret=|secret:)[\w+/=]+",
                "type": "secret"
            },
            {
                "name": "db_url",
                "regex": r"(mongodb|mysql|postgresql|redis)://[^\s'\"]+",
                "type": "db_connection"
            },
        ]
    
    def mask_message(self, text: str) -> Tuple[str, list]:
        """脱敏消息。
        
        Args:
            text: 原始消息文本
        
        Returns:
            (masked_text, replacements) 脱敏后的文本和替换列表
        """
        import re
        
        replacements = []
        masked_text = text
        
        for pattern in self.patterns:
            matches = re.finditer(pattern['regex'], text)
            
            for match in matches:
                original = match.group()
                data_type = pattern['type']
                
                # 生成 mask_id
                mask_id = self.store.add_mapping(original, data_type)
                
                # 创建脱敏标记
                masked = f"[{data_type.upper()}:{mask_id}]"
                
                # 替换
                masked_text = masked_text.replace(original, masked)
                
                replacements.append({
                    "original": original[:20] + "..." if len(original) > 20 else original,
                    "masked": masked,
                    "mask_id": mask_id,
                    "type": data_type
                })
        
        return masked_text, replacements
    
    def restore_message(self, text: str) -> str:
        """还原消息中的敏感数据。
        
        Args:
            text: 包含脱敏标记的文本
        
        Returns:
            还原后的文本
        """
        import re
        
        def replace_match(match):
            full_match = match.group(0)
            # 提取 mask_id: [TYPE:mask_id]
            parts = full_match.split(':')
            if len(parts) >= 2:
                mask_id = parts[1].rstrip(']')
                original = self.store.get_original(mask_id)
                
                if original:
                    return original
            
            return full_match
        
        # 匹配 [TYPE:mask_id] 格式
        pattern = r'\[[A-Z_]+:[a-f0-9]{16}\]'
        return re.sub(pattern, replace_match, text)

# ═══════════════════════════════════════════════════════════════
# 命令行工具
# ═══════════════════════════════════════════════════════════════

def test_mask_restore(text: str):
    """测试脱敏和还原。"""
    masker = ChannelSensitiveMasker()
    
    print(f"\n原始消息:\n  {text}\n")
    
    # 脱敏
    masked, replacements = masker.mask_message(text)
    print(f"脱敏后:\n  {masked}\n")
    
    if replacements:
        print(f"检测到 {len(replacements)} 个敏感信息:")
        for r in replacements:
            print(f"  - {r['type']}: {r['original']} → {r['masked']}")
        print()
    
    # 还原
    restored = masker.restore_message(masked)
    print(f"还原后:\n  {restored}\n")
    
    # 验证
    if restored == text:
        print("✅ 还原成功！")
    else:
        print("⚠️  还原结果与原始不一致")
        print(f"  原始：{text}")
        print(f"  还原：{restored}")

def show_stats():
    """显示统计信息。"""
    store = SensitiveMappingStore()
    stats = store.get_stats()
    
    print(f"\n📊 敏感数据映射统计:")
    print(f"  总数：{stats['total']}")
    print(f"  TTL: {stats['ttl_days']} 天")
    print(f"  即将过期（24h 内）: {stats['expiring_soon']}")
    
    if stats['by_type']:
        print(f"\n  按类型:")
        for data_type, count in stats['by_type'].items():
            print(f"    - {data_type}: {count}")
    
    print()

def cleanup():
    """清理过期数据。"""
    store = SensitiveMappingStore()
    store._cleanup_expired()
    print("✅ 清理完成")

def clear_all():
    """清空所有映射。"""
    import sys
    response = input("⚠️  确定要清空所有敏感数据映射吗？(yes/no): ")
    if response.lower() == 'yes':
        MAPPING_FILE.unlink(missing_ok=True)
        print("✅ 已清空")
    else:
        print("已取消")

# ═══════════════════════════════════════════════════════════════
# OpenClaw Channel 集成
# ═══════════════════════════════════════════════════════════════

def on_channel_message(message: dict) -> dict:
    """Channel 消息接收时的钩子。
    
    在消息进入 OpenClaw 前脱敏。
    
    Args:
        message: 原始消息对象
    
    Returns:
        脱敏后的消息对象
    """
    masker = ChannelSensitiveMasker()
    
    # 脱敏消息内容
    if 'text' in message:
        message['text'], replacements = masker.mask_message(message['text'])
        
        # 记录脱敏信息（可选）
        if replacements:
            message['_masked'] = {
                "count": len(replacements),
                "types": [r['type'] for r in replacements]
            }
    
    return message

def before_task_execution(context: dict) -> dict:
    """任务执行前的钩子。
    
    还原本地需要的敏感数据。
    
    Args:
        context: 任务上下文
    
    Returns:
        还原后的上下文
    """
    masker = ChannelSensitiveMasker()
    
    # 还原上下文中的脱敏标记
    for key, value in context.items():
        if isinstance(value, str):
            context[key] = masker.restore_message(value)
    
    return context

# ═══════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print(f"用法:")
        print(f"  {sys.argv[0]} test <text>      # 测试脱敏/还原")
        print(f"  {sys.argv[0]} stats            # 显示统计")
        print(f"  {sys.argv[0]} cleanup          # 清理过期")
        print(f"  {sys.argv[0]} clear            # 清空所有")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'test' and len(sys.argv) >= 3:
        test_mask_restore(' '.join(sys.argv[2:]))
    elif cmd == 'stats':
        show_stats()
    elif cmd == 'cleanup':
        cleanup()
    elif cmd == 'clear':
        clear_all()
    else:
        print(f"未知命令：{cmd}")
        sys.exit(1)
