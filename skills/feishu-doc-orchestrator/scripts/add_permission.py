#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给现有飞书文档添加权限并转移所有权
"""

import sys
import json
import urllib.parse
from pathlib import Path
import requests

# 加载配置
def load_config():
    project_root = Path(__file__).parent.parent.parent.parent
    config_path = project_root / ".claude" / "feishu-config.env"
    if not config_path.exists():
        config_path = Path(".claude/feishu-config.env")

    config = {}
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"\'')
    return config

# 获取 tenant_access_token
def get_tenant_token(config):
    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    payload = {
        "app_id": config['FEISHU_APP_ID'],
        "app_secret": config['FEISHU_APP_SECRET']
    }
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    if result.get("code") == 0:
        return result["tenant_access_token"]
    else:
        raise Exception(f"获取 tenant_token 失败: {result}")

# 获取 user_access_token
def get_user_token(config):
    project_root = Path(__file__).parent.parent.parent.parent
    token_path = project_root / ".claude" / "feishu-token.json"
    if not token_path.exists():
        raise Exception("user_access_token 不存在，请先运行授权")
    
    with open(token_path, 'r', encoding='utf-8') as f:
        token_data = json.load(f)
    return token_data.get("user_access_token") or token_data.get("access_token")

# 添加协作者权限
def add_permission_member(token, config, document_id, user_id, user_type="openid", perm="full_access"):
    params = urllib.parse.urlencode({"type": "docx"})
    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/drive/v1/permissions/{document_id}/members?{params}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "member_id": user_id,
        "member_type": user_type,
        "perm": perm
    }
    
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    
    if result.get("code") == 0:
        return True, result
    else:
        return False, result

# 转移所有权
def transfer_owner(document_id, user_id, config):
    try:
        import lark_oapi as lark
        from lark_oapi.api.drive.v1 import TransferOwnerPermissionMemberRequest, Owner
    except ImportError:
        raise Exception("lark-oapi SDK 未安装，请运行: pip install lark-oapi")
    
    user_token = get_user_token(config)
    
    # 创建客户端
    client = lark.Client.builder() \
        .app_id(config.get('FEISHU_APP_ID', '')) \
        .app_secret(config.get('FEISHU_APP_SECRET', '')) \
        .build()
    
    # 创建请求选项
    request_option = lark.RequestOption.builder() \
        .user_access_token(user_token) \
        .build()
    
    # 构建转移所有权请求
    request = TransferOwnerPermissionMemberRequest.builder() \
        .token(document_id) \
        .type("docx") \
        .need_notification(True) \
        .remove_old_owner(False) \
        .stay_put(False) \
        .old_owner_perm("view") \
        .request_body(Owner.builder()
            .member_type("openid")
            .member_id(user_id)
            .build()) \
        .build()
    
    # 执行转移
    response = client.drive.v1.permission_member.transfer_owner(request, request_option)
    
    if not response.success():
        raise Exception(f"转移失败: code={response.code}, msg={response.msg}")
    
    return True

def main():
    if len(sys.argv) < 3:
        print("用法: python add_permission.py <文档ID> <用户open_id>")
        print("示例: python add_permission.py Lh6hdTak5oMOrlx96VtcHZrInfb ou_c3187510002211b7dab58e3107255adf")
        sys.exit(1)
    
    document_id = sys.argv[1]
    user_id = sys.argv[2]
    
    print("=" * 70)
    print("飞书文档权限管理")
    print("=" * 70)
    print(f"文档ID: {document_id}")
    print(f"用户ID: {user_id}")
    print()
    
    # 加载配置
    config = load_config()
    if not config:
        print("[错误] 无法加载配置")
        sys.exit(1)
    
    # 第一步：添加协作者权限
    print("[步骤 1/2] 添加协作者权限...")
    try:
        tenant_token = get_tenant_token(config)
        success, result = add_permission_member(tenant_token, config, document_id, user_id)
        if success:
            print("[OK] 协作者权限添加成功")
        else:
            print(f"[WARN] 添加协作者返回: {result}")
    except Exception as e:
        print(f"[WARN] 添加协作者失败: {e}")
    
    # 第二步：转移所有权
    print("\n[步骤 2/2] 转移文档所有权...")
    try:
        transfer_owner(document_id, user_id, config)
        print("[OK] 所有权转移成功")
        print(f"     新所有者: {user_id}")
    except Exception as e:
        print(f"[FAIL] 所有权转移失败: {e}")
        print("[提示] 可能原因:")
        print("  1. user_access_token 未配置或已过期")
        print("  2. 当前用户没有转移所有权的权限")
        print("  3. 需要先完成 OAuth 授权")
    
    print()
    print("=" * 70)
    print("操作完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
