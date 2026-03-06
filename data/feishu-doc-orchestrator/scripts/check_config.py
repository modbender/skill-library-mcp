#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查飞书配置工具
"""

import os
import sys
import requests
import json
from pathlib import Path

def load_config():
    """加载配置文件"""
    config_paths = [
        Path.home() / ".openclaw" / "feishu-config.env",
        Path.home() / ".claude" / "feishu-config.env",
        Path("feishu-config.env"),
    ]
    
    config = {}
    loaded_path = None
    
    for config_path in config_paths:
        if config_path.exists():
            print(f"[配置] 找到配置文件: {config_path}")
            loaded_path = config_path
            
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip().strip('"\'')
            except Exception as e:
                print(f"[错误] 读取配置文件失败: {e}")
                return None, None
            
            break
    
    if not loaded_path:
        print("[错误] 未找到飞书配置文件")
        return None, None
    
    return config, loaded_path

def check_required_fields(config):
    """检查必需字段"""
    required = ["FEISHU_APP_ID", "FEISHU_APP_SECRET", "FEISHU_API_DOMAIN"]
    missing = []
    
    print("\n[检查] 必需配置项:")
    for field in required:
        if field in config and config[field]:
            print(f"  ✓ {field}: {config[field][:10]}...")
        else:
            print(f"  ✗ {field}: 未设置")
            missing.append(field)
    
    return missing

def check_optional_fields(config):
    """检查可选字段"""
    optional = ["FEISHU_AUTO_COLLABORATOR_ID", "FEISHU_DEFAULT_FOLDER"]
    
    print("\n[检查] 可选配置项:")
    for field in optional:
        if field in config and config[field]:
            print(f"  ✓ {field}: {config[field][:20]}...")
        else:
            print(f"  - {field}: 未设置（可选）")

def test_api_connection(config):
    """测试API连接"""
    print("\n[测试] API连接测试...")
    
    try:
        # 获取token
        url = f"{config['FEISHU_API_DOMAIN']}/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        payload = {
            "app_id": config["FEISHU_APP_ID"],
            "app_secret": config["FEISHU_APP_SECRET"]
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            token = result["tenant_access_token"]
            print(f"  ✓ Token获取成功: {token[:15]}...")
            print(f"  ✓ Token有效期: {result.get('expire', '未知')}秒")
            return True, token
        else:
            print(f"  ✗ Token获取失败: {result.get('msg', '未知错误')}")
            return False, None
    except requests.exceptions.Timeout:
        print("  ✗ 连接超时，请检查网络")
        return False, None
    except requests.exceptions.ConnectionError:
        print("  ✗ 连接错误，请检查FEISHU_API_DOMAIN配置")
        return False, None
    except Exception as e:
        print(f"  ✗ 未知错误: {e}")
        return False, None

def test_doc_permission(config, token):
    """测试文档权限"""
    print("\n[测试] 文档权限测试...")
    
    try:
        url = f"{config['FEISHU_API_DOMAIN']}/open-apis/docx/v1/documents"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("  ✓ 文档API权限正常")
            return True
        elif response.status_code == 403:
            print("  ✗ 权限不足，请检查应用权限配置")
            print("  所需权限: docx:document, docx:document.block:convert")
            return False
        else:
            print(f"  ✗ API错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ 权限测试失败: {e}")
        return False

def check_skill_files():
    """检查技能文件"""
    print("\n[检查] 技能文件...")
    
    skill_root = Path(__file__).parent.parent
    original_skill = skill_root / "original-skill"
    
    if not original_skill.exists():
        print("  ✗ 技能包未安装，请运行 install_skill.py")
        return False
    
    required_files = [
        original_skill / "feishu-doc-orchestrator" / "scripts" / "orchestrator.py",
        original_skill / "feishu-md-parser" / "scripts" / "md_parser.py",
        original_skill / "feishu-block-adder" / "scripts" / "block_adder.py",
    ]
    
    all_exists = True
    for file_path in required_files:
        if file_path.exists():
            print(f"  ✓ {file_path.relative_to(skill_root)}")
        else:
            print(f"  ✗ {file_path.relative_to(skill_root)} 未找到")
            all_exists = False
    
    return all_exists

def main():
    print("=" * 70)
    print("飞书文档创建技能 - 配置检查工具")
    print("=" * 70)
    
    # 加载配置
    config, config_path = load_config()
    if not config:
        print("\n[错误] 配置加载失败")
        return 1
    
    # 检查必需字段
    missing = check_required_fields(config)
    if missing:
        print(f"\n[错误] 缺少必需配置项: {', '.join(missing)}")
        print(f"请编辑配置文件: {config_path}")
        return 1
    
    # 检查可选字段
    check_optional_fields(config)
    
    # 测试API连接
    api_ok, token = test_api_connection(config)
    if not api_ok:
        return 1
    
    # 测试文档权限
    if not test_doc_permission(config, token):
        print("\n[警告] 文档权限测试失败，但配置检查继续")
    
    # 检查技能文件
    files_ok = check_skill_files()
    
    print("\n" + "=" * 70)
    print("配置检查完成")
    
    if missing:
        print("[状态] ❌ 配置不完整")
        return 1
    elif not api_ok:
        print("[状态] ❌ API连接失败")
        return 1
    elif not files_ok:
        print("[状态] ⚠️ 配置基本正常，但技能文件不完整")
        print("       部分功能可能受限，建议运行 install_skill.py")
        return 0
    else:
        print("[状态] ✅ 所有检查通过，技能已就绪")
        print("\n[下一步] 测试技能:")
        print("python scripts/feishu_doc_cli.py --input test.md --title \"测试文档\"")
        return 0

if __name__ == "__main__":
    sys.exit(main())