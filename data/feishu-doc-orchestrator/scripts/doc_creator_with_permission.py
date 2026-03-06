#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档创建器+权限管理器 - 合并子技能
在飞书创建文档并自动完成权限管理
输出：doc_with_permission.json
"""

import sys
import json
import urllib.parse
import time
import os
from pathlib import Path
from datetime import datetime
import requests

# 添加 feishu_auth 路径
AUTH_SCRIPT_DIR = Path(__file__).parent.parent.parent / "feishu-doc-creator" / "scripts"
if str(AUTH_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(AUTH_SCRIPT_DIR))


def load_config():
    """加载飞书配置"""
    # 修复路径 - 从脚本位置向上 5 级到达项目根目录
    project_root = Path(__file__).parent.parent.parent.parent.parent
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


def get_access_token(config, use_user_token=False):
    """获取访问令牌"""
    if use_user_token:
        # 修复路径 - 获取项目根目录
        project_root = Path(__file__).parent.parent.parent.parent.parent
        token_path = project_root / ".claude" / "feishu-token.json"

        if token_path.exists():
            with open(token_path, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
                # 支持 access_token 和 user_access_token 两种格式
                token = token_data.get("user_access_token") or token_data.get("access_token")
                if token:
                    return token

        # Token 不存在或无效，自动触发授权
        print()
        print("=" * 70)
        print("[INFO] user_access_token 不存在或已过期")
        print("[INFO] 自动启动 OAuth 授权流程...")
        print("=" * 70)
        print()

        # 运行自动授权脚本
        auto_auth_script = Path(__file__).parent / "auto_auth.py"
        if auto_auth_script.exists():
            import subprocess
            result = subprocess.run(
                [sys.executable, str(auto_auth_script)],
                capture_output=False,
                text=True
            )
            if result.returncode == 0:
                # 重新读取 token
                with open(token_path, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                return token_data.get("user_access_token") or token_data.get("access_token")
            else:
                raise Exception("自动授权失败，请检查网络连接或手动运行 auto_auth.py")
        else:
            raise Exception("auto_auth.py 不存在，请先创建此文件")

        return None
    else:
        # 获取 tenant_access_token
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
            raise Exception(f"获取 tenant_access_token 失败: {result}")


def create_document_with_user_token(user_token, config, title):
    """
    使用 user_access_token 创建飞书文档 - 文档属于用户

    修复说明：
    - 使用 user_access_token 时，可以直接在创建时指定 folder_token
    - 不需要先创建再移动，这样更可靠

    API 文档参考：
    POST /open-apis/docx/v1/documents
    {
        "folder_token": "fldcnxxxx",  // 可选，不传表示根目录
        "title": "文档标题"
    }
    """
    import requests

    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }

    # 构建请求 - 直接指定 folder_token
    payload = {
        "title": title
    }

    # 如果配置了文件夹，直接在创建时指定
    folder_token = config.get('FEISHU_DEFAULT_FOLDER', '')
    if folder_token:
        payload["folder_token"] = folder_token
        print(f"[INFO] 在指定文件夹创建文档: {folder_token}")

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        raise Exception(f"创建文档失败: code={result.get('code')}, msg={error_msg}")

    doc_id = result["data"]["document"]["document_id"]
    print(f"[OK] 文档创建成功: {doc_id}")

    if folder_token:
        print(f"[OK] 文档已创建在指定文件夹中")

    return doc_id


def create_document(token, config, title):
    """创建飞书文档（使用 tenant_access_token）"""
    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
        "folder_token": config.get('FEISHU_DEFAULT_FOLDER', '')
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if result.get("code") == 0:
        return result["data"]["document"]["document_id"]
    else:
        raise Exception(f"创建文档失败: {result}")


def create_document_with_tenant_token(tenant_token, config, title, folder_token=None):
    """
    使用 tenant_access_token 创建飞书文档 - 文档属于应用

    说明：
    - 使用 tenant_access_token 创建文档
    - 可以指定 folder_token 将文档创建在指定文件夹中
    - 文档创建后，应用拥有文档的编辑权限

    API 文档参考：
    POST /open-apis/docx/v1/documents
    {
        "folder_token": "fldcnxxxx",  // 可选，不传表示根目录
        "title": "文档标题"
    }
    """
    import requests

    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {tenant_token}",
        "Content-Type": "application/json"
    }

    # 构建请求
    payload = {
        "title": title
    }

    # 如果指定了文件夹，在创建时指定
    if folder_token:
        payload["folder_token"] = folder_token
        print(f"[INFO] 在指定文件夹创建文档: {folder_token}")

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        raise Exception(f"创建文档失败: code={result.get('code')}, msg={error_msg}")

    doc_id = result["data"]["document"]["document_id"]
    print(f"[OK] 文档创建成功: {doc_id}")

    if folder_token:
        print(f"[OK] 文档已创建在指定文件夹中")

    return doc_id


def add_permission_member(token, config, document_id, user_id, user_type, perm):
    """添加协作者权限 - 必须使用 tenant_access_token"""
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
        return result
    else:
        raise Exception(f"添加权限成员失败: {result}")


def transfer_owner(document_id, user_id):
    """转移文档所有权 - 必须使用 user_access_token 和 SDK"""
    try:
        import lark_oapi as lark
        from lark_oapi.api.drive.v1 import TransferOwnerPermissionMemberRequest, Owner
    except ImportError:
        raise Exception("lark-oapi SDK 未安装，请运行: pip install lark-oapi")

    config = load_config()
    if not config:
        raise Exception("无法加载配置文件")

    # 获取 user_access_token
    # 修复路径 - 从脚本位置向上 5 级到达项目根目录
    project_root = Path(__file__).parent.parent.parent.parent.parent
    token_path = project_root / ".claude" / "feishu-token.json"
    if not token_path.exists():
        raise Exception("user_access_token 文件不存在，请先运行授权: python auto_auth.py")

    try:
        with open(token_path, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        # 支持 access_token 和 user_access_token 两种格式
        user_token = token_data.get("user_access_token") or token_data.get("access_token")
    except Exception as e:
        raise Exception(f"读取 user_access_token 失败: {e}")

    if not user_token:
        raise Exception("user_access_token 不存在")

    # 创建使用 user_access_token 的客户端
    client = lark.Client.builder() \
        .app_id(config.get('FEISHU_APP_ID', '')) \
        .app_secret(config.get('FEISHU_APP_SECRET', '')) \
        .build()

    # 创建请求选项，设置 user_access_token
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
        raise Exception(f"转移所有权失败: code={response.code}, msg={response.msg}")

    return response


def should_use_user_token(title):
    """
    根据文档标题判断是否应该使用 user_access_token

    只有当用户明确提到以下关键词时，才使用 user_access_token：
    - "文件夹"
    - "用户"
    - "个人"
    - "我的"
    - "指定目录"
    - "特定目录"

    否则默认使用 tenant_access_token
    """
    user_token_keywords = ["文件夹", "用户", "个人", "我的", "指定目录", "特定目录", "folder", "user", "personal", "my"]
    title_lower = title.lower()

    for keyword in user_token_keywords:
        if keyword in title_lower:
            return True

    return False


def main():
    """主函数 - 命令行入口"""
    # 解析参数
    title = "未命名文档"
    output_dir = Path("output")
    force_user_token = False  # 强制使用 user_token 的标志

    if len(sys.argv) >= 2:
        title = sys.argv[1]

    if len(sys.argv) >= 3:
        output_dir = Path(sys.argv[2])

    # 检查是否强制使用 user_token（通过环境变量或参数）
    if "--user-token" in sys.argv or os.environ.get("FEISHU_USE_USER_TOKEN", "").lower() in ("1", "true", "yes"):
        force_user_token = True

    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载配置
    config = load_config()
    if not config:
        print("[feishu-doc-creator-with-permission] Error: Unable to load config")
        sys.exit(1)

    print("=" * 70)
    print("文档创建 + 权限管理（原子操作）")
    print("=" * 70)
    print(f"文档标题: {title}")
    print()

    # ========== 智能判断使用哪种 Token ==========
    # 检查是否强制使用 user_token 或标题包含关键词
    use_user_token_mode = force_user_token or should_use_user_token(title)

    if use_user_token_mode:
        print("[模式] User Token 模式（文档属于用户，可指定文件夹）")
        print("      检测到关键词: 文件夹/用户/个人/我的")
        print("      无需权限转移，文档直接属于用户")
    else:
        print("[模式] Tenant Token 模式（文档属于应用，需权限转移）")
        print("      默认模式，适合自动化批量创建")

    print()

    # 权限配置
    collaborator_id = config.get('FEISHU_AUTO_COLLABORATOR_ID')
    collaborator_type = config.get('FEISHU_AUTO_COLLABORATOR_TYPE', 'openid')
    collaborator_perm = config.get('FEISHU_AUTO_COLLABORATOR_PERM', 'full_access')

    # 结果数据
    result = {
        "title": title,
        "created_at": datetime.now().isoformat(),
        "token_mode": "user_access_token" if use_user_token_mode else "tenant_access_token",
        "permission": {
            "collaborator_added": False,
            "owner_transferred": False,
            "user_has_full_control": False,
            "collaborator_id": collaborator_id
        },
        "errors": []
    }

    # ========== 第一步：创建文档 ==========
    folder_token = config.get('FEISHU_DEFAULT_FOLDER', '')

    if use_user_token_mode:
        # User Token 模式：文档属于用户，无需权限转移
        print("[步骤 1/1] 创建文档 (user_access_token - 文档属于用户)...")
        if folder_token:
            print(f"         目标目录: {folder_token}")

        try:
            user_token = get_access_token(config, use_user_token=True)
            if not user_token:
                raise Exception("无法获取 user_access_token，请先运行授权")

            doc_id = create_document_with_user_token(user_token, config, title)
            result["document_id"] = doc_id
            result["document_url"] = f"{config.get('FEISHU_WEB_DOMAIN', 'https://feishu.cn')}/docx/{doc_id}"
            result["permission"]["user_has_full_control"] = True  # User Token 模式，用户自动有完全控制权
            print(f"[OK] 文档创建成功")
            print(f"     文档ID: {doc_id}")
        except Exception as e:
            error_msg = str(e)
            result["errors"].append(f"创建文档失败: {error_msg}")
            print(f"[FAIL] 创建文档失败: {error_msg}")
            # 保存失败结果并退出
            result_file = output_dir / "doc_with_permission.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            sys.exit(1)
    else:
        # Tenant Token 模式：文档属于应用，需要添加协作者权限和转移所有权
        print("[步骤 1/3] 创建文档 (tenant_access_token - 文档属于应用)...")
        print("         注意: Tenant Token 模式无法指定文件夹，文档将创建在根目录")

        try:
            tenant_token = get_access_token(config, use_user_token=False)
            # Tenant Token 模式不传 folder_token（无权限指定文件夹）
            doc_id = create_document_with_tenant_token(tenant_token, config, title, folder_token=None)
            result["document_id"] = doc_id
            result["document_url"] = f"{config.get('FEISHU_WEB_DOMAIN', 'https://feishu.cn')}/docx/{doc_id}"
            print(f"[OK] 文档创建成功")
            print(f"     文档ID: {doc_id}")
        except Exception as e:
            error_msg = str(e)
            result["errors"].append(f"创建文档失败: {error_msg}")
            print(f"[FAIL] 创建文档失败: {error_msg}")
            # 保存失败结果并退出
            result_file = output_dir / "doc_with_permission.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            sys.exit(1)

        # ========== 第二步：添加协作者权限 ==========
        print("\n[步骤 2/3] 添加协作者权限...")
        if collaborator_id:
            try:
                # 使用 tenant_access_token 添加协作者
                add_permission_member(tenant_token, config, doc_id, collaborator_id, collaborator_type, collaborator_perm)
                result["permission"]["collaborator_added"] = True
                result["permission"]["user_has_full_control"] = True
                print(f"[OK] 协作者添加成功")
                print(f"     协作者ID: {collaborator_id}")
                print(f"     权限: {collaborator_perm}")
            except Exception as e:
                error_msg = str(e)
                result["errors"].append(f"添加协作者失败: {error_msg}")
                print(f"[WARN] 添加协作者失败: {error_msg}")
                print(f"[INFO] 文档已创建，但协作者未添加")
        else:
            print("[SKIP] 未配置协作者ID (FEISHU_AUTO_COLLABORATOR_ID)")

    # ========== 第三步：转移所有权（Tenant Token 模式） ==========
    # 只有 Tenant Token 模式需要转移所有权
    if not use_user_token_mode and collaborator_id:
        print("\n[步骤 3/3] 转移文档所有权...")
        try:
            transfer_owner(doc_id, collaborator_id)
            result["permission"]["owner_transferred"] = True
            result["permission"]["user_has_full_control"] = True
            print(f"[OK] 所有权转移成功")
            print(f"     新所有者: {collaborator_id}")
        except Exception as e:
            error_msg = str(e)
            result["errors"].append(f"转移所有权失败: {error_msg}")
            print(f"[WARN] 所有权转移失败: {error_msg}")
            print(f"[INFO] 协作者已有编辑权限，但所有权未转移")
    elif not use_user_token_mode:
        print("\n[SKIP] 未配置协作者ID (FEISHU_AUTO_COLLABORATOR_ID)，无法转移所有权")

    # 保存结果
    result_file = output_dir / "doc_with_permission.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 打印摘要
    print()
    print("=" * 70)
    print("操作完成")
    print("=" * 70)
    print(f"文档URL: {result['document_url']}")
    print(f"Token 模式: {result['token_mode']}")
    print(f"目录位置: {folder_token if folder_token else '根目录'}")
    if use_user_token_mode:
        print(f"用户完全控制: {result['permission']['user_has_full_control']} (User Token 模式，无需权限转移)")
    else:
        print(f"协作者已添加: {result['permission']['collaborator_added']}")
        print(f"所有权已转移: {result['permission']['owner_transferred']}")
        print(f"用户完全控制: {result['permission']['user_has_full_control']}")
    print(f"\n输出文件: {result_file}")
    print(f"\n[OUTPUT] {result_file}")


if __name__ == "__main__":
    main()
