#!/usr/bin/env python3
"""
配置修改前置钩子 - 自动触发回滚机制
- 监听所有 .json 修改
- 自动备份 + 验证 + 回滚
"""

import os
import json
import hashlib
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

CONFIG_DIR = Path.home() / ".openclaw"
BACKUP_DIR = CONFIG_DIR / "backup"
LOG_FILE = CONFIG_DIR / "logs" / "config-modification.log"
CRITICAL_FILES = {
    "openclaw.json",
    "exec-approvals.json",
    "skills.json"
}

def ensure_dirs():
    """确保必要目录存在"""
    BACKUP_DIR.mkdir(exist_ok=True)
    LOG_FILE.parent.mkdir(exist_ok=True)

def log_event(level, message):
    """记录事件到日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}\n"
    
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    
    print(log_entry.strip())

def compute_hash(file_path):
    """计算文件 SHA256 哈希"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def validate_json(file_path):
    """验证 JSON 文件完整性"""
    try:
        with open(file_path) as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        log_event("ERROR", f"JSON 验证失败: {file_path} - {e}")
        return False

def create_backup(file_path):
    """创建备份（带哈希前缀，防止重复备份）"""
    ensure_dirs()
    
    file_hash = compute_hash(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.name}.{timestamp}.{file_hash[:8]}.bak"
    backup_path = BACKUP_DIR / backup_name
    
    try:
        shutil.copy2(file_path, backup_path)
        log_event("INFO", f"✅ 备份创建: {backup_name}")
        return backup_path
    except Exception as e:
        log_event("ERROR", f"备份失败: {e}")
        return None

def check_gateway_health():
    """检查 Gateway 健康状态"""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:18789/api/health"],
            timeout=3,
            capture_output=True
        )
        return result.returncode == 0
    except:
        return False

def rollback_to_backup(backup_path):
    """回滚到备份"""
    config_file = CONFIG_DIR / backup_path.name.split(".")[0]
    
    try:
        shutil.copy2(backup_path, config_file)
        log_event("INFO", f"✅ 已回滚到: {backup_path.name}")
        return True
    except Exception as e:
        log_event("ERROR", f"回滚失败: {e}")
        return False

def pre_modification_check(file_path):
    """修改前的完整检查流程"""
    log_event("INFO", f"🔍 开始前置检查: {file_path.name}")
    
    # 1. 验证源文件
    if not validate_json(file_path):
        log_event("ERROR", f"源文件 JSON 无效: {file_path}")
        return False
    
    # 2. 创建备份
    backup = create_backup(file_path)
    if not backup:
        log_event("ERROR", "备份创建失败，中止修改")
        return False
    
    # 3. 记录修改前的 Gateway 状态
    gateway_ok = check_gateway_health()
    log_event("INFO", f"修改前 Gateway 状态: {'健康' if gateway_ok else '异常'}")
    
    return backup

def post_modification_verify(file_path, backup_path):
    """修改后的验证流程"""
    log_event("INFO", f"🔍 开始后置验证: {file_path.name}")
    
    # 1. JSON 验证
    if not validate_json(file_path):
        log_event("ERROR", f"修改后 JSON 无效，触发回滚")
        rollback_to_backup(backup_path)
        return False
    
    # 2. Gateway 健康检查
    if not check_gateway_health():
        log_event("ERROR", "Gateway 修改后不健康，触发回滚")
        rollback_to_backup(backup_path)
        return False
    
    log_event("INFO", "✅ 修改验证通过")
    return True

def watch_config_files():
    """监视配置文件修改（轮询方案）
    
    轮询间隔: 3 分钟（给 Gateway 充足重启时间）
    退出条件: 连续 3 次健康检查通过 → 自动关闭回滚监视
    """
    ensure_dirs()
    
    file_hashes = {}
    consecutive_healthy = 0  # 连续健康计数器
    HEALTHY_THRESHOLD = 3    # 连续 3 次健康就退出
    POLL_INTERVAL = 180      # 3 分钟轮询间隔
    
    # 初始化文件哈希
    for file in CRITICAL_FILES:
        file_path = CONFIG_DIR / file
        if file_path.exists():
            file_hashes[str(file_path)] = compute_hash(file_path)
    
    log_event("INFO", f"开始监视 {len(file_hashes)} 个关键配置文件 (间隔 {POLL_INTERVAL}s, 连续 {HEALTHY_THRESHOLD} 次健康后退出)")
    
    # 长期监视循环
    import time
    while True:
        try:
            change_detected = False
            
            for file_path_str, old_hash in list(file_hashes.items()):
                file_path = Path(file_path_str)
                
                if not file_path.exists():
                    continue
                
                new_hash = compute_hash(file_path)
                
                if new_hash != old_hash:
                    log_event("WARN", f"⚠️ 检测到修改: {file_path.name}")
                    change_detected = True
                    consecutive_healthy = 0  # 有变更，重置计数
                    
                    # 创建备份并验证
                    backup = create_backup(file_path)
                    
                    if not post_modification_verify(file_path, backup):
                        log_event("ERROR", "修改验证失败，已回滚")
                    
                    # 更新哈希记录
                    file_hashes[file_path_str] = compute_hash(file_path)
            
            # 无变更时检查 Gateway 健康状态
            if not change_detected:
                gateway_ok = check_gateway_health()
                if gateway_ok:
                    consecutive_healthy += 1
                    log_event("INFO", f"✅ Gateway 健康 ({consecutive_healthy}/{HEALTHY_THRESHOLD})")
                else:
                    consecutive_healthy = 0
                    log_event("WARN", f"⚠️ Gateway 不健康，重置计数")
                
                # 连续 N 次健康 → 安全退出
                if consecutive_healthy >= HEALTHY_THRESHOLD:
                    log_event("INFO", f"🎉 连续 {HEALTHY_THRESHOLD} 次健康检查通过，配置稳定，自动关闭监视")
                    break
            
            time.sleep(POLL_INTERVAL)
        
        except KeyboardInterrupt:
            log_event("INFO", "监视已停止 (用户中断)")
            break
        except Exception as e:
            log_event("ERROR", f"监视循环异常: {e}")
            consecutive_healthy = 0  # 异常也重置计数
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        # 后台监视模式
        watch_config_files()
    else:
        # 单次检查模式
        ensure_dirs()
        log_event("INFO", "配置修改钩子已初始化")
