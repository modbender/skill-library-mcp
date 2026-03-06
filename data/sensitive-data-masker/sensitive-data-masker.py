#!/usr/bin/env python3
"""Sensitive Data Masker - 敏感信息自动检测与脱敏。

在 RAG 检索和 API 调用前自动识别并替换敏感信息，保护隐私数据。
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════

CONFIG_DIR = Path.home() / ".openclaw" / "config"
CONFIG_FILE = CONFIG_DIR / "sensitive-data.json"
LOG_FILE = CONFIG_DIR / "sensitive-data-masker.log"

# 颜色输出
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# ═══════════════════════════════════════════════════════════════
# 脱敏规则
# ═══════════════════════════════════════════════════════════════

DEFAULT_PATTERNS = [
    {
        "name": "password",
        "regex": r"(?i)(密码|password|passwd|pwd|pass)[=:\s是]+['\"]?[\w@#$%^&*!]+['\"]?",
        "replacement": "[PASSWORD:***]",
        "enabled": True
    },
    {
        "name": "api_key",
        "regex": r"(?i)(api[_-]?key|apikey)[=:\s]+['\"]?[\w-]+['\"]?",
        "replacement": "[API_KEY:***]",
        "enabled": True
    },
    {
        "name": "sk_key",
        "regex": r"sk-[a-zA-Z0-9]{20,}",
        "replacement": "[SK_KEY:***]",
        "enabled": True
    },
    {
        "name": "token",
        "regex": r"(?i)(token|access[_-]?token|auth[_-]?token)[=:\s]+['\"]?[\w.-]+['\"]?",
        "replacement": "[TOKEN:***]",
        "enabled": True
    },
    {
        "name": "secret",
        "regex": r"(?i)(secret|secret[_-]?key)[=:\s]+['\"]?[\w+/=]+['\"]?",
        "replacement": "[SECRET:***]",
        "enabled": True
    },
    {
        "name": "private_key",
        "regex": r"-----BEGIN.*PRIVATE KEY-----",
        "replacement": "[PRIVATE_KEY:***]",
        "enabled": True
    },
    {
        "name": "database_url",
        "regex": r"(mongodb|mysql|postgresql|redis)://[^\s'\"]+",
        "replacement": "[DB_CONNECTION:***]",
        "enabled": True
    },
    {
        "name": "email",
        "regex": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "replacement": "[EMAIL:***]",
        "enabled": False  # 默认不禁用，可选
    },
    {
        "name": "phone",
        "regex": r"1[3-9]\d{9}",
        "replacement": "[PHONE:***]",
        "enabled": False  # 默认不禁用，可选
    },
    {
        "name": "ip_address",
        "regex": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        "replacement": "[IP:***]",
        "enabled": False  # 默认不禁用，可选
    },
]

# ═══════════════════════════════════════════════════════════════
# 配置管理
# ═══════════════════════════════════════════════════════════════

def load_config():
    """加载配置文件。"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # 创建默认配置
    config = {
        "version": "1.0",
        "enabled": True,
        "mode": "rag_and_api",  # rag_only, api_only, rag_and_api, disabled
        "patterns": DEFAULT_PATTERNS,
        "whitelist": [],
        "log_enabled": True
    }
    
    save_config(config)
    return config

def save_config(config):
    """保存配置文件。"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # 设置权限
    CONFIG_FILE.chmod(0o600)

# ═══════════════════════════════════════════════════════════════
# 脱敏处理
# ═══════════════════════════════════════════════════════════════

class SensitiveDataMasker:
    """敏感信息脱敏器。"""
    
    def __init__(self, config=None):
        self.config = config or load_config()
        self.compiled_patterns = []
        self.detected_items = []
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式。"""
        self.compiled_patterns = []
        
        for pattern in self.config.get('patterns', []):
            if not pattern.get('enabled', True):
                continue
            
            try:
                compiled = re.compile(pattern['regex'])
                self.compiled_patterns.append({
                    'name': pattern['name'],
                    'regex': compiled,
                    'replacement': pattern['replacement']
                })
            except re.error as e:
                print(f"{YELLOW}⚠️  正则表达式错误 {pattern['name']}: {e}{NC}")
    
    def _is_whitelisted(self, text: str) -> bool:
        """检查是否在白名单中。"""
        whitelist = self.config.get('whitelist', [])
        return any(word in text for word in whitelist)
    
    def mask(self, text: str, log_detection: bool = True) -> str:
        """脱敏文本。"""
        if not self.config.get('enabled', True):
            return text
        
        self.detected_items = []
        result = text
        
        for pattern in self.compiled_patterns:
            matches = pattern['regex'].finditer(result)
            
            for match in matches:
                matched_text = match.group()
                
                # 检查白名单
                if self._is_whitelisted(matched_text):
                    continue
                
                # 记录检测到的敏感信息
                if log_detection:
                    self.detected_items.append({
                        'type': pattern['name'],
                        'original': matched_text[:20] + '...' if len(matched_text) > 20 else matched_text,
                        'position': match.start()
                    })
                
                # 替换
                result = result[:match.start()] + pattern['replacement'] + result[match.end():]
        
        return result
    
    def mask_dict(self, data: dict, log_detection: bool = True) -> dict:
        """脱敏字典（递归处理）。"""
        if not self.config.get('enabled', True):
            return data
        
        result = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.mask(value, log_detection)
            elif isinstance(value, dict):
                result[key] = self.mask_dict(value, log_detection)
            elif isinstance(value, list):
                result[key] = [
                    self.mask(item, log_detection) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    def get_detected_count(self) -> int:
        """获取检测到的敏感信息数量。"""
        return len(self.detected_items)
    
    def get_detected_items(self) -> list:
        """获取检测到的敏感信息列表。"""
        return self.detected_items

# ═══════════════════════════════════════════════════════════════
# 日志
# ═══════════════════════════════════════════════════════════════

def log_detection(text: str, detected_items: list):
    """记录脱敏日志。"""
    config = load_config()
    
    if not config.get('log_enabled', True):
        return
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Time: {datetime.now().isoformat()}\n")
        f.write(f"Detected: {len(detected_items)} items\n")
        
        for item in detected_items:
            f.write(f"  - Type: {item['type']}, Found: {item['original']}\n")
        
        f.write(f"Original (first 200 chars): {text[:200]}...\n")
        f.write(f"{'='*60}\n")

# ═══════════════════════════════════════════════════════════════
# 命令行工具
# ═══════════════════════════════════════════════════════════════

def test_mask(text: str):
    """测试脱敏效果。"""
    masker = SensitiveDataMasker()
    
    print(f"\n{BLUE}原始文本:{NC}")
    print(f"  {text}")
    print()
    
    masked = masker.mask(text)
    
    print(f"{GREEN}脱敏后:{NC}")
    print(f"  {masked}")
    print()
    
    detected = masker.get_detected_items()
    if detected:
        print(f"{YELLOW}检测到 {len(detected)} 个敏感信息:{NC}")
        for item in detected:
            print(f"  - {item['type']}: {item['original']}")
    else:
        print(f"{GREEN}✅ 未检测到敏感信息{NC}")
    
    print()

def scan_file(file_path: str):
    """扫描文件中的敏感信息。"""
    file = Path(file_path)
    
    if not file.exists():
        print(f"{RED}❌ 文件不存在：{file}{NC}")
        return
    
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    masker = SensitiveDataMasker()
    masker.mask(content)
    
    detected = masker.get_detected_items()
    
    print(f"\n{BLUE}扫描文件：{file}{NC}")
    print(f"大小：{file.stat().st_size} 字节")
    print()
    
    if detected:
        print(f"{YELLOW}⚠️  检测到 {len(detected)} 个敏感信息:{NC}")
        for item in detected:
            print(f"  - {item['type']}: {item['original']}")
    else:
        print(f"{GREEN}✅ 未检测到敏感信息{NC}")
    
    print()

def show_config():
    """显示当前配置。"""
    config = load_config()
    
    print(f"\n{BLUE}敏感信息脱敏配置:{NC}")
    print(f"  启用：{'✅' if config.get('enabled') else '❌'}")
    print(f"  模式：{config.get('mode', 'rag_and_api')}")
    print(f"  日志：{'✅' if config.get('log_enabled') else '❌'}")
    print(f"  白名单：{config.get('whitelist', [])}")
    print()
    
    print(f"{BLUE}启用的脱敏规则:{NC}")
    for pattern in config.get('patterns', []):
        if pattern.get('enabled'):
            print(f"  ✅ {pattern['name']}: {pattern['replacement']}")
        else:
            print(f"  ❌ {pattern['name']} (禁用)")
    
    print()

def enable_masker():
    """启用脱敏器。"""
    config = load_config()
    config['enabled'] = True
    save_config(config)
    print(f"{GREEN}✅ 脱敏器已启用{NC}\n")

def disable_masker():
    """禁用脱敏器。"""
    config = load_config()
    config['enabled'] = False
    save_config(config)
    print(f"{YELLOW}⚠️  脱敏器已禁用{NC}\n")

# ═══════════════════════════════════════════════════════════════
# OpenClaw 集成钩子
# ═══════════════════════════════════════════════════════════════

def before_rag(text: str) -> str:
    """RAG 检索前的脱敏钩子。"""
    config = load_config()
    
    if not config.get('enabled'):
        return text
    
    mode = config.get('mode', 'rag_and_api')
    if mode not in ['rag_only', 'rag_and_api']:
        return text
    
    masker = SensitiveDataMasker(config)
    masked = masker.mask(text)
    
    # 记录日志
    if config.get('log_enabled'):
        log_detection(text, masker.get_detected_items())
    
    return masked

def before_api_call(text: str) -> str:
    """API 调用前的脱敏钩子。"""
    config = load_config()
    
    if not config.get('enabled'):
        return text
    
    mode = config.get('mode', 'rag_and_api')
    if mode not in ['api_only', 'rag_and_api']:
        return text
    
    masker = SensitiveDataMasker(config)
    masked = masker.mask(text)
    
    # 记录日志
    if config.get('log_enabled'):
        log_detection(text, masker.get_detected_items())
    
    return masked

# ═══════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"{YELLOW}用法:{NC}")
        print(f"  {sys.argv[0]} test <text>        # 测试脱敏效果")
        print(f"  {sys.argv[0]} scan <file>        # 扫描文件")
        print(f"  {sys.argv[0]} config             # 显示配置")
        print(f"  {sys.argv[0]} enable             # 启用")
        print(f"  {sys.argv[0]} disable            # 禁用")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'test' and len(sys.argv) >= 3:
        test_mask(' '.join(sys.argv[2:]))
    elif command == 'scan' and len(sys.argv) >= 3:
        scan_file(sys.argv[2])
    elif command == 'config':
        show_config()
    elif command == 'enable':
        enable_masker()
    elif command == 'disable':
        disable_masker()
    else:
        print(f"{RED}❌ 未知命令：{command}{NC}")
        sys.exit(1)
