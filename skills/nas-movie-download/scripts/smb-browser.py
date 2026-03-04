#!/usr/bin/env python3
"""
SMB Browser and Subtitle Downloader
用于浏览 SMB 共享文件夹并下载字幕
"""

import os
import sys
import subprocess
from pathlib import Path

# SMB 配置
SMB_CONFIG = {
    "username": "13917908083",
    "password": "Roger0808",
    "server": "Z4ProPlus-X6L8._smb._tcp.local",
    "share": "super8083",
    "path": "qb/downloads"
}

def install_smbprotocol():
    """安装 smbprotocol 库"""
    try:
        import smbprotocol
        return True
    except ImportError:
        print("正在安装 smbprotocol 库...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "smbprotocol"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("安装成功!")
            return True
        else:
            print(f"安装失败: {result.stderr}")
            return False

def try_mount_cifs():
    """尝试使用 mount.cifs 挂载"""
    mount_point = os.path.expanduser("~/smb_downloads")
    os.makedirs(mount_point, exist_ok=True)
    
    # 构建挂载命令
    server = SMB_CONFIG["server"]
    share = SMB_CONFIG["share"]
    path = SMB_CONFIG["path"]
    username = SMB_CONFIG["username"]
    password = SMB_CONFIG["password"]
    
    mount_cmd = [
        "mount", "-t", "cifs",
        f"//{server}/{share}/{path}",
        mount_point,
        "-o", f"username={username},password={password},vers=3.0,uid={os.getuid()},gid={os.getgid()}"
    ]
    
    print(f"尝试挂载: {' '.join(mount_cmd)}")
    result = subprocess.run(mount_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"挂载成功! 目录: {mount_point}")
        return mount_point
    else:
        print(f"挂载失败: {result.stderr}")
        return None

def list_smb_files():
    """列出 SMB 共享中的文件"""
    try:
        from smbprotocol.connection import Connection
        from smbprotocol.session import Session
        from smbprotocol.tree import TreeConnect
        from smbprotocol.open import Open, FilePipePrinterAccessMask, CreateDisposition, CreateOptions
        from smbprotocol.file_information import FileInformationClass
        
        server = SMB_CONFIG["server"]
        username = SMB_CONFIG["username"]
        password = SMB_CONFIG["password"]
        share = SMB_CONFIG["share"]
        path = SMB_CONFIG["path"]
        
        # 建立连接
        conn = Connection(server, server)
        conn.connect()
        
        # 创建会话
        session = Session(conn, username, password)
        session.connect()
        
        # 连接共享
        tree = TreeConnect(session, f"\\\\{server}\\{share}")
        tree.connect()
        
        # 打开目录
        dir_open = Open(tree, path)
        dir_open.create(
            desired_access=FilePipePrinterAccessMask.FILE_LIST_DIRECTORY,
            file_attributes=0,
            share_access=0,
            create_disposition=CreateDisposition.FILE_OPEN,
            create_options=CreateOptions.FILE_DIRECTORY_FILE
        )
        
        # 列出文件
        files = dir_open.query_directory(
            pattern="*",
            file_information_class=FileInformationClass.FILE_NAMES_INFORMATION
        )
        
        print("\\n文件列表:")
        for file_info in files:
            print(f"  - {file_info['file_name']}")
        
        dir_open.close()
        tree.disconnect()
        session.disconnect()
        conn.disconnect()
        
        return files
        
    except Exception as e:
        print(f"SMB 访问失败: {e}")
        return None

def main():
    print("=" * 50)
    print("SMB 字幕下载工具")
    print("=" * 50)
    
    # 方法1: 尝试 mount.cifs
    print("\\n方法1: 尝试挂载 SMB 共享...")
    mount_point = try_mount_cifs()
    
    if mount_point and os.path.exists(mount_point):
        print(f"\\n挂载成功! 列出文件:")
        subprocess.run(["ls", "-la", mount_point])
        return mount_point
    
    # 方法2: 使用 Python smbprotocol
    print("\\n方法2: 尝试使用 Python smbprotocol 库...")
    if install_smbprotocol():
        files = list_smb_files()
        if files:
            return files
    
    print("\\n所有方法都失败了。请检查:")
    print("1. SMB 服务是否运行")
    print("2. 用户名密码是否正确")
    print("3. 网络连接是否正常")
    return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\\n成功访问 SMB 共享!")
    else:
        print(f"\\n无法访问 SMB 共享")
        sys.exit(1)
