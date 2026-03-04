#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全自动化的 Bitwarden 凭据管理器
使用保存的主密码实现零交互凭据获取
"""

import os
import json
import subprocess
import sys
from pathlib import Path

class FullyAutomatedBitwardenManager:
    def __init__(self):
        self.session_file = Path.home() / '.bw-session'
        self.email = "171831475@qq.com"
        self.master_password = "Ganlan99999("  # 从永久记忆中获取
        
    def get_bw_status(self):
        """获取 Bitwarden 状态"""
        try:
            result = subprocess.run(['bw', 'status'], capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return {"status": "unknown"}
    
    def load_session_from_file(self):
        """从文件加载会话密钥"""
        if self.session_file.exists():
            try:
                session_key = self.session_file.read_text().strip()
                os.environ['BW_SESSION'] = session_key
                
                # 验证会话是否有效
                result = subprocess.run(['bw', 'list', 'items'], 
                                      capture_output=True, check=True)
                print("✅ 从文件成功加载有效会话")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️ 文件会话已过期，自动重新解锁...")
                self.clear_session_file()
                return False
        return False
    
    def save_session_to_file(self, session_key):
        """保存会话密钥到文件"""
        self.session_file.write_text(session_key)
        self.session_file.chmod(0o600)  # 仅用户可读写
        print("💾 会话已保存到文件")
    
    def clear_session_file(self):
        """清理会话文件"""
        if self.session_file.exists():
            self.session_file.unlink()
    
    def auto_unlock(self):
        """自动解锁 vault (使用保存的主密码)"""
        print("🔓 自动解锁 Bitwarden vault...")
        try:
            result = subprocess.run(['bw', 'unlock', self.master_password, '--raw'], 
                                  capture_output=True, text=True, check=True)
            session_key = result.stdout.strip()
            if session_key:
                os.environ['BW_SESSION'] = session_key
                self.save_session_to_file(session_key)
                print("✅ 自动解锁成功")
                return True
        except subprocess.CalledProcessError:
            print("❌ 自动解锁失败")
        return False
    
    def ensure_unlocked(self):
        """确保 vault 处于解锁状态 - 完全自动化"""
        status = self.get_bw_status()
        
        if status["status"] == "unauthenticated":
            print(f"❌ 未登录，请先执行: bw login {self.email}")
            return False
        
        elif status["status"] == "locked":
            print("🔒 Vault 已锁定")
            # 尝试从文件加载会话
            if not self.load_session_from_file():
                # 使用保存的密码自动解锁
                return self.auto_unlock()
        
        elif status["status"] == "unlocked":
            print("✅ Vault 已解锁")
            # 如果当前有会话但文件不存在，保存会话
            if not self.session_file.exists() and os.environ.get('BW_SESSION'):
                self.save_session_to_file(os.environ['BW_SESSION'])
        
        return True
    
    def get_work_email_credentials(self):
        """获取工作邮箱凭据 - 完全自动化"""
        print("🔐 自动获取工作邮箱凭据...")
        
        if not self.ensure_unlocked():
            return None, None
        
        try:
            # 获取用户名
            result = subprocess.run(['bw', 'get', 'username', '工作邮箱'], 
                                  capture_output=True, text=True, check=True)
            username = result.stdout.strip()
            
            # 获取密码
            result = subprocess.run(['bw', 'get', 'password', '工作邮箱'], 
                                  capture_output=True, text=True, check=True)
            password = result.stdout.strip()
            
            print(f"📧 成功获取凭据: {username}")
            print(f"🔑 密码长度: {len(password)} 字符")
            return username, password
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 获取凭据失败: {e}")
            return None, None

def fully_automated_load_fund_credentials():
    """
    完全自动化凭据加载函数
    使用保存的主密码，无需用户交互
    """
    print("🚀 启动完全自动化 Bitwarden 凭据加载...")
    
    # 检查环境变量是否已设置
    if os.environ.get('FUND_EMAIL') and os.environ.get('FUND_PASSWORD'):
        print("✅ 环境变量已设置，跳过 Bitwarden")
        return os.environ['FUND_EMAIL'], os.environ['FUND_PASSWORD']
    
    # 使用完全自动化管理器
    manager = FullyAutomatedBitwardenManager()
    email, password = manager.get_work_email_credentials()
    
    if email and password:
        # 设置环境变量
        os.environ['FUND_EMAIL'] = email
        os.environ['FUND_PASSWORD'] = password
        print("✅ 凭据已自动加载并设置到环境变量")
        print("🎉 无需用户交互，完全自动化完成！")
        return email, password
    else:
        print("❌ 自动化凭据获取失败")
        return None, None

if __name__ == "__main__":
    # 命令行使用
    email, password = fully_automated_load_fund_credentials()
    if email and password:
        print("\n🎯 完全自动化凭据加载成功！")
        print("环境变量已设置:")
        print(f"  FUND_EMAIL={email}")
        print(f"  FUND_PASSWORD={'*' * len(password)}")
        print("\n💡 现在可以直接运行资金日报脚本，无需任何用户交互！")
    else:
        print("\n❌ 自动化失败")
        sys.exit(1)