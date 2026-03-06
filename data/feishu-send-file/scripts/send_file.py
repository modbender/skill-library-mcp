#!/usr/bin/env python3
"""
飞书发送文件脚本
用法: python3 send_file.py <file_path> <open_id> <app_id> <app_secret> [file_name]
"""

import sys
import os
import json
import urllib.request
import urllib.parse

def get_tenant_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if result.get("code") != 0:
        raise Exception(f"获取token失败: {result}")
    return result["tenant_access_token"]

def upload_file(token, file_path, file_name):
    """上传文件到飞书，返回 file_key"""
    import subprocess
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/im/v1/files",
        "-H", f"Authorization: Bearer {token}",
        "-F", "file_type=stream",
        "-F", f"file_name={file_name}",
        "-F", f"file=@{file_path}"
    ], capture_output=True, text=True)
    data = json.loads(result.stdout)
    if data.get("code") != 0:
        raise Exception(f"上传文件失败: {data}")
    return data["data"]["file_key"]

def send_file_message(token, open_id, file_key):
    """发送文件消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    payload = {
        "receive_id": open_id,
        "msg_type": "file",
        "content": json.dumps({"file_key": file_key})
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if result.get("code") != 0:
        raise Exception(f"发送消息失败: {result}")
    return result

def main():
    if len(sys.argv) < 5:
        print("用法: python3 send_file.py <file_path> <open_id> <app_id> <app_secret> [file_name]")
        sys.exit(1)

    file_path = sys.argv[1]
    open_id   = sys.argv[2]
    app_id    = sys.argv[3]
    app_secret = sys.argv[4]
    file_name = sys.argv[5] if len(sys.argv) > 5 else os.path.basename(file_path)

    if not os.path.exists(file_path):
        print(f"ERROR: 文件不存在: {file_path}")
        sys.exit(1)

    print(f"📎 发送文件: {file_name}")
    token = get_tenant_token(app_id, app_secret)
    print("✅ 获取token成功")

    file_key = upload_file(token, file_path, file_name)
    print(f"✅ 上传成功, file_key: {file_key}")

    send_file_message(token, open_id, file_key)
    print(f"✅ 发送成功！")

if __name__ == "__main__":
    main()
