# 配置文件管理
## 技能配置、环境变量和用户设置管理

## 🎯 配置管理概述

### 1. 配置层级体系
```
多层配置架构:
• 默认配置: 技能内置的默认值
• 环境配置: 环境变量覆盖
• 用户配置: 用户自定义配置
• 运行时配置: 程序运行时动态配置
• 会话配置: 单个会话的临时配置
```

### 2. 配置管理原则
```
配置管理最佳实践:
• 安全性: 敏感信息加密存储
• 可维护性: 配置结构清晰易懂
• 可扩展性: 支持动态添加配置
• 兼容性: 向后兼容配置变更
• 可测试性: 支持配置单元测试
```

## ⚙️ 配置文件设计

### 1. 配置文件格式
#### JSON配置示例：
```json
{
  "chinese_toolkit": {
    "version": "1.0.0",
    "api": {
      "baidu_translate": {
        "enabled": true,
        "app_id": "${BAIDU_APP_ID}",
        "app_key": "${BAIDU_APP_KEY}",
        "endpoint": "https://fanyi-api.baidu.com/api/trans/vip/translate"
      },
      "tencent_cloud": {
        "enabled": false,
        "secret_id": "${TENCENT_SECRET_ID}",
        "secret_key": "${TENCENT_SECRET_KEY}"
      }
    },
    "local_services": {
      "ocr": {
        "enabled": true,
        "language": "chi_sim",
        "timeout": 30
      },
      "translation": {
        "enabled": true,
        "cache_size": 1000,
        "cache_ttl": 3600
      }
    },
    "performance": {
      "max_workers": 4,
      "timeout": 30,
      "retry_attempts": 3
    },
    "logging": {
      "level": "INFO",
      "file": "chinese_toolkit.log",
      "max_size_mb": 10
    }
  }
}
```

#### YAML配置示例：
```yaml
chinese_toolkit:
  version: "1.0.0"
  
  api:
    baidu_translate:
      enabled: true
      app_id: "${BAIDU_APP_ID}"
      app_key: "${BAIDU_APP_KEY}"
      endpoint: "https://fanyi-api.baidu.com/api/trans/vip/translate"
    
    tencent_cloud:
      enabled: false
      secret_id: "${TENCENT_SECRET_ID}"
      secret_key: "${TENCENT_SECRET_KEY}"
  
  local_services:
    ocr:
      enabled: true
      language: "chi_sim"
      timeout: 30
    
    translation:
      enabled: true
      cache_size: 1000
      cache_ttl: 3600
  
  performance:
    max_workers: 4
    timeout: 30
    retry_attempts: 3
  
  logging:
    level: "INFO"
    file: "chinese_toolkit.log"
    max_size_mb: 10
```

### 2. 配置验证模式
#### 使用Pydantic进行配置验证：
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class APIConfig(BaseModel):
    enabled: bool = True
    app_id: Optional[str] = None
    app_key: Optional[str] = None
    endpoint: str
    timeout: int = 30
    
    @validator('app_id', 'app_key')
    def check_api_keys(cls, v, values):
        if values.get('enabled') and not v:
            raise ValueError("API密钥不能为空")
        return v

class LocalServiceConfig(BaseModel):
    enabled: bool = True
    cache_size: int = Field(1000, ge=0, le=10000)
    cache_ttl: int = Field(3600, ge=0, le=86400)

class ChineseToolkitConfig(BaseModel):
    version: str
    api: Dict[str, APIConfig]
    local_services: Dict[str, LocalServiceConfig]
    performance: Dict[str, int]
    logging: Dict[str, str]
    
    class Config:
        env_prefix = "CHINESE_TOOLKIT_"
        env_file = ".env"
```

## 🔧 配置管理实现

### 1. 配置加载器
#### 多源配置加载：
```python
# config_loader.py
import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class ConfigLoader:
    def __init__(self, config_name: str = "chinese_toolkit"):
        self.config_name = config_name
        self.config = {}
        self._load_environment()
    
    def _load_environment(self):
        """加载环境变量"""
        load_dotenv()
        
        # 加载环境变量配置
        env_config = {}
        for key, value in os.environ.items():
            if key.startswith(f"{self.config_name.upper()}_"):
                config_key = key[len(self.config_name) + 1:].lower()
                env_config[config_key] = value
        
        self.config.update(self._parse_env_config(env_config))
    
    def _parse_env_config(self, env_config: Dict) -> Dict:
        """解析环境变量配置"""
        parsed = {}
        for key, value in env_config.items():
            keys = key.split('__')
            current = parsed
            
            for i, k in enumerate(keys):
                if i == len(keys) - 1:
                    # 尝试转换类型
                    if value.lower() in ['true', 'false']:
                        current[k] = value.lower() == 'true'
                    elif value.isdigit():
                        current[k] = int(value)
                    else:
                        current[k] = value
                else:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
        
        return parsed
    
    def load_file(self, file_path: str) -> Dict:
        """从文件加载配置"""
        path = Path(file_path)
        
        if not path.exists():
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix == '.json':
                file_config = json.load(f)
            elif path.suffix in ['.yaml', '.yml']:
                file_config = yaml.safe_load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {path.suffix}")
        
        # 合并配置（文件配置优先级高于环境变量）
        self._merge_config(self.config, file_config)
        return self.config
    
    def _merge_config(self, base: Dict, update: Dict) -> None:
        """递归合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        current = self.config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        current = self.config
        
        for i, k in enumerate(keys):
            if i == len(keys) - 1:
                current[k] = value
            else:
                if k not in current:
                    current[k] = {}
                current = current[k]
```

### 2. 配置热重载
#### 监控配置文件变化：
```python
# config_watcher.py
import time
import threading
from pathlib import Path
from typing import Callable, Optional
import hashlib

class ConfigWatcher:
    def __init__(self, config_file: str, callback: Callable):
        self.config_file = Path(config_file)
        self.callback = callback
        self.last_hash = self._get_file_hash()
        self.watching = False
        self.thread = None
    
    def _get_file_hash(self) -> str:
        """获取文件哈希值"""
        if not self.config_file.exists():
            return ""
        
        with open(self.config_file, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _watch_loop(self):
        """监控循环"""
        while self.watching:
            current_hash = self._get_file_hash()
            
            if current_hash != self.last_hash:
                self.last_hash = current_hash
                self.callback(self.config_file)
            
            time.sleep(5)  # 每5秒检查一次
    
    def start(self):
        """开始监控"""
        if not self.watching:
            self.watching = True
            self.thread = threading.Thread(target=self._watch_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        """停止监控"""
        self.watching = False
        if self.thread:
            self.thread.join(timeout=2)
```

## 🔐 安全配置管理

### 1. 敏感信息加密
#### 使用加密存储：
```python
# secure_config.py
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os

class SecureConfig:
    def __init__(self, password: str, salt: Optional[bytes] = None):
        self.password = password.encode()
        self.salt = salt or os.urandom(16)
        self.fernet = self._create_fernet()
    
    def _create_fernet(self) -> Fernet:
        """创建Fernet加密器"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return Fernet(key)
    
    def encrypt_config(self, config: Dict) -> str:
        """加密配置"""
        config_json = json.dumps(config).encode()
        encrypted = self.fernet.encrypt(config_json)
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_config(self, encrypted_config: str) -> Dict:
        """解密配置"""
        encrypted = base64.urlsafe_b64decode(encrypted_config.encode())
        decrypted = self.fernet.decrypt(encrypted)
        return json.loads(decrypted.decode())
    
    def save_secure(self, config: Dict, file_path: str):
        """保存加密配置"""
        encrypted = self.encrypt_config(config)
        
        # 保存盐值和加密数据
        data = {
            'salt': base64.urlsafe_b64encode(self.salt).decode(),
            'encrypted_config': encrypted
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f)
    
    def load_secure(self, file_path: str) -> Dict:
        """加载加密配置"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        self.salt = base64.urlsafe_b64decode(data['salt'].encode())
        self.fernet = self._create_fernet()
        
        return self.decrypt_config(data['encrypted_config'])
```

### 2. 密钥管理
#### 使用密钥管理服务：
```python
# key_manager.py
import keyring
import json
from typing import Optional

class KeyManager:
    def __init__(self, service_name: str = "chinese_toolkit"):
        self.service_name = service_name
    
    def store_api_key(self, api_name: str, key_data: Dict):
        """存储API密钥"""
        keyring.set_password(
            self.service_name,
            api_name,
            json.dumps(key_data)
        )
    
    def get_api_key(self, api_name: str) -> Optional[Dict]:
        """获取API密钥"""
        key_json = keyring.get_password(self.service_name, api_name)
        if key_json:
            return json.loads(key_json)
        return None
    
    def delete_api_key(self, api_name: str):
        """删除API密钥"""
        keyring.delete_password(self.service_name, api_name)
    
    def list_api_keys(self) -> List[str]:
        """列出所有API密钥"""
        # 注意：keyring可能不支持直接列出，这里使用自定义存储
        import sqlite3
        import os
        
        # 查找keyring数据库
        keyring_path = os.path.expanduser("~/.local/share/python_keyring/keyring_pass.cfg")
        if os.path.exists(keyring_path):
            conn = sqlite3.connect(keyring_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username FROM credentials WHERE service_name = ?",
                (self.service_name,)
            )
            return [row[0] for row in cursor.fetchall()]
        return []
```

## 📊 配置分析和优化

### 1. 配置使用分析
#### 跟踪配置使用情况：
```python
# config_analytics.py
import time
from collections import defaultdict
from typing import Dict, List
import json

class ConfigAnalytics:
    def __init__(self):
        self.access_count = defaultdict(int)
        self.access_time = defaultdict(list)
        self.config_values = {}
    
    def track_access(self, config_key: str, value: Any):
        """跟踪配置访问"""
        self.access_count[config_key] += 1
        self.access_time[config_key].append(time.time())
        self.config_values[config_key] = value
    
    def get_usage_report(self) -> Dict:
        """获取使用报告"""
        report = {
            'total_accesses': sum(self.access_count.values()),
            'most_accessed': [],
            'least_accessed': [],
            'access_patterns': {}
        }
        
        # 计算最常访问的配置
        sorted_access = sorted(
            self.access_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        report['most_accessed'] = sorted_access[:10]
        report['least_accessed'] = sorted_access[-10:] if len(sorted_access) > 10 else []
        
        # 分析访问模式
        for key, times in self.access_time.items():
            if len(times) > 1:
                intervals = [times[i+1] - times[i] for i in range(len(times)-1)]
                report['access_patterns'][key] = {
                    'count': len(times),
                    'avg_interval': sum(intervals) / len(intervals),
                    'min_interval': min(intervals),
                    'max_interval': max(intervals)
                }
        
        return report
    
    def suggest_optimizations(self) -> List[Dict]:
        """提供优化建议"""
        suggestions = []
        report = self.get_usage_report()
        
        # 建议1: 缓存频繁访问的配置
        for key, count in report['most_accessed']:
            if count > 100:
                suggestions.append({
                    'type': 'cache',
                    'config_key': key,
                    'reason': f'频繁访问 ({count}次)',
                    'recommendation': '添加内存缓存'
                })
        
        # 建议2: 合并相关配置
        related_keys = defaultdict(list)
        for key in self.config_values.keys():
            prefix = key.split('.')[0]
            related_keys[prefix].append(key)
        
        for prefix, keys in related_keys.items():
            if len(keys) > 5:
                suggestions.append({
                    'type': 'consolidate',
                    'config_prefix': prefix,
                    'reason': f'相关配置过多 ({len(keys)}个)',
                    'recommendation': '考虑合并相关配置'
                })
        
        return suggestions
```

### 2. 配置性能优化
#### 配置缓存策略：
```python
# config_cache.py
import time
from functools import lru_cache
from typing import Any, Callable

class ConfigCache:
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str, loader: Callable[[], Any]) -> Any:
        """获取配置值，支持缓存"""
        current_time = time.time()
        
        # 检查缓存是否有效
        if (key in self.cache and 
            key in self.timestamps and
            current_time - self.timestamps[key] < self.ttl):
            return self.cache[key]
        
        # 加载新值
        value = loader()
        self.cache[key] = value
        self.timestamps[key] = current_time
        return value
    
    def invalidate(self, key: str = None):
        """使缓存失效"""
        if key:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)
        else:
            self.cache.clear()
            self.timestamps.clear()
    
    @lru_cache(maxsize=128)
    def get_cached(self, key: str) -> Any:
        """使用LRU缓存获取配置"""
        # 这里假设配置已经加载到内存中
        return self._get_from_source(key)
    
    def _get_from_source(self, key: str) -> Any:
        """从源获取配置（模拟）"""
        # 实际实现中应该从配置文件或数据库读取
        time.sleep(0.01)  # 模拟IO延迟
        return f"value_for_{key}"
```

## 🔄 配置迁移和版本管理

### 1. 配置版本迁移
#### 自动配置迁移：
```python
# config_migration.py
import json
from typing import Dict, Any
from pathlib import Path

class ConfigMigrator:
    def __init__(self, migrations_dir: str = "migrations"):
        self.migrations_dir = Path(migrations_dir)
        self.migrations = self._load_migrations()
    
    def _load_migrations(self) -> Dict[str, Callable]:
        """加载迁移脚本"""
        migrations = {}
        
        if self.migrations_dir.exists():
            for migration_file in self.migrations_dir.glob("*.py"):
                migration_name = migration_file.stem
                
                # 动态导入迁移模块
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    migration_name,
                    migration_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'migrate'):
                    migrations[migration_name] = module.migrate
        
        return migrations
    
    def migrate_config(self, config: Dict, from_version: str, to_version: str) -> Dict:
        """迁移配置"""
        # 获取需要应用的迁移
        migrations_to_apply = self._get_migrations_between(from_version, to_version)
        
        # 按顺序应用迁移
        migrated_config = config.copy()
        for migration_name in migrations_to_apply:
            if migration_name in self.migrations:
                migrated_config = self.migrations[migration_name](migrated_config)
        
        return migrated_config
    
    def _get_migrations_between(self, from_version: str, to_version: str) -> List[str]:
        """获取两个版本之间的迁移列表"""
        # 这里需要实现版本比较和迁移顺序逻辑
        # 简化实现：假设迁移文件名包含版本信息
        migration_files = sorted(self.migrations_dir.glob("*.py"))
        migrations = []
        
        for migration_file in migration_files:
            # 提取版本信息（例如：v1_0_to_v1_1.py）
            version_part = migration_file.stem
            if version_part.startswith('v'):
                migrations.append(version_part)
        
        return migrations

### 2. 配置备份和恢复
#### 自动配置备份：
```python
# config_backup.py
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List

class ConfigBackup:
    def __init__(self, backup_dir: str = "backups", max_backups: int = 10):
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, config_file: str, description: str = ""):
        """创建配置备份"""
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{config_path.stem}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        # 复制文件
        shutil.copy2(config_path, backup_path)
        
        # 创建元数据文件
        metadata = {
            'original_file': str(config_path),
            'backup_time': timestamp,
            'description': description,
            'file_size': config_path.stat().st_size,
            'checksum': self._calculate_checksum(config_path)
        }
        
        metadata_path = backup_path.with_suffix('.meta.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # 清理旧备份
        self._cleanup_old_backups()
        
        return str(backup_path)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        import hashlib
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _cleanup_old_backups(self):
        """清理旧备份"""
        backups = list(self.backup_dir.glob("*.bak"))
        if len(backups) > self.max_backups:
            # 按修改时间排序，删除最旧的
            backups.sort(key=lambda x: x.stat().st_mtime)
            for backup in backups[:-self.max_backups]:
                backup.unlink()
                # 同时删除元数据文件
                meta_file = backup.with_suffix('.meta.json')
                if meta_file.exists():
                    meta_file.unlink()
    
    def list_backups(self) -> List[Dict]:
        """列出所有备份"""
        backups = []
        for backup_file in self.backup_dir.glob("*.bak"):
            meta_file = backup_file.with_suffix('.meta.json')
            metadata = {}
            
            if meta_file.exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            backups.append({
                'backup_file': str(backup_file),
                'metadata': metadata
            })
        
        return sorted(backups, key=lambda x: x['metadata'].get('backup_time', ''), reverse=True)
    
    def restore_backup(self, backup_file: str, target_file: str = None):
        """恢复备份"""
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_file}")
        
        # 读取元数据获取原始文件名
        meta_file = backup_path.with_suffix('.meta.json')
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            original_file = metadata.get('original_file', target_file)
        else:
            original_file = target_file
        
        if not original_file:
            raise ValueError("需要指定目标文件或备份包含原始文件名")
        
        # 恢复文件
        shutil.copy2(backup_path, original_file)
        return original_file
```

## 🚀 最佳实践

### 1. 配置管理最佳实践
```
设计原则:
• 单一职责: 每个配置项有明确的目的
• 最小权限: 只暴露必要的配置项
• 默认安全: 默认配置应该是安全的
• 明确文档: 每个配置项都有详细说明

实现原则:
• 类型安全: 使用类型提示和验证
• 环境隔离: 不同环境使用不同配置
• 版本控制: 配置变更可追溯
• 自动化测试: 配置变更自动测试
```

### 2. 配置部署策略
```
开发环境:
• 使用本地配置文件
• 包含示例配置
• 支持环境变量覆盖
• 提供快速启动配置

测试环境:
• 使用独立的配置文件
• 包含测试专用配置
• 支持配置验证
• 自动化配置部署

生产环境:
• 使用加密配置文件
• 支持热重载
• 包含监控和告警
• 支持回滚机制
```

### 3. 配置监控和告警
```
监控指标:
• 配置加载时间
• 配置访问频率
• 配置变更次数
• 配置错误率

告警规则:
• 配置加载失败
• 配置验证错误
• 敏感配置变更
• 配置性能下降
```

---
**配置文件管理指南版本**: 1.0.0
**最后更新**: 2026-02-23
**适用对象**: 技能开发者、系统管理员

**优秀配置，稳定运行！** ⚙️🔧

**安全第一，性能至上！** 🛡️🚀