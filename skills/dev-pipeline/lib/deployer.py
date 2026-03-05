"""
部署模块
"""

import subprocess
import os
from pathlib import Path


class Deployer:
    """部署到服务器"""
    
    def __init__(self, config):
        self.config = config
        self.deploy_config = config.get("deploy", {})
    
    def deploy(self, project_root):
        """执行部署"""
        host = self.deploy_config.get("host")
        user = self.deploy_config.get("user")
        ssh_key = self.deploy_config.get("ssh_key")
        remote_path = self.deploy_config.get("remote_path")
        
        if not all([host, user, ssh_key, remote_path]):
            raise ValueError("部署配置不完整，需要 host, user, ssh_key, remote_path")
        
        # 展开 ~
        ssh_key = os.path.expanduser(ssh_key)
        
        print(f"部署到 {user}@{host}:{remote_path}")
        
        # 1. 执行 pre_deploy
        pre_deploy = self.deploy_config.get("pre_deploy", [])
        for cmd in pre_deploy:
            print(f"执行: {cmd}")
            result = subprocess.run(cmd, shell=True, cwd=project_root, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"pre_deploy 失败: {result.stderr}")
        
        # 2. 同步代码到服务器
        print("同步代码...")
        rsync_cmd = [
            "rsync", "-avz", "--delete",
            "-e", f"ssh -i {ssh_key}",
            "--exclude", ".git",
            "--exclude", "node_modules",
            "--exclude", "versions",
            "--exclude", ".dev-pipeline",
            f"{project_root}/",
            f"{user}@{host}:{remote_path}/"
        ]
        
        result = subprocess.run(rsync_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"rsync 失败: {result.stderr}")
        
        # 3. 在服务器上执行命令
        server_commands = []
        
        # 如果有 package.json，执行 npm install
        if (project_root / "package.json").exists():
            server_commands.append(f"cd {remote_path} && npm install")
        
        # 执行 post_deploy
        post_deploy = self.deploy_config.get("post_deploy", [])
        for cmd in post_deploy:
            server_commands.append(f"cd {remote_path} && {cmd}")
        
        for cmd in server_commands:
            print(f"服务器执行: {cmd}")
            ssh_cmd = [
                "ssh", "-i", ssh_key,
                f"{user}@{host}",
                cmd
            ]
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"服务器命令失败: {result.stderr}")
        
        # 4. 健康检查
        port = self.deploy_config.get("port")
        if port:
            print(f"健康检查: http://{host}:{port}/api/health")
            # 简单检查，实际可能需要更复杂的逻辑
        
        print("部署完成！")
