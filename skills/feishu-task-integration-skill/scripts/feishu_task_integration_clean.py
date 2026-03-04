#!/usr/bin/env python3
"""
飞书任务API集成 (清理版)
移除了所有个人信息和敏感配置
"""

import json
import requests
import os
from datetime import datetime, date
import sys

class FeishuTaskManager:
    def __init__(self):
        # 从配置文件加载凭证
        self.load_config()
        self.tenant_access_token = None
        self.user_access_token = None
        
        # 用户信息
        self.current_user_id = None
        self.assignee_user_id = None
        
        self.load_user_info()
    
    def load_config(self):
        """从配置文件加载凭证"""
        config_file = 'feishu_config.json'
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.app_id = config.get('app_id')
                    self.app_secret = config.get('app_secret')
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            self.app_id = None
            self.app_secret = None
    
    def load_user_info(self):
        """加载用户信息"""
        config_file = 'feishu_config.json'
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_user_id = config.get('current_user_id')
                    self.assignee_user_id = config.get('assignee_user_id')
                    
                    if self.current_user_id:
                        print(f"✅ 已加载当前用户ID: {self.current_user_id}")
                    if self.assignee_user_id:
                        print(f"✅ 已加载负责人用户ID: {self.assignee_user_id}")
        except Exception as e:
            print(f"读取用户信息失败: {e}")
    
    def get_tenant_access_token(self):
        """获取租户访问令牌"""
        if not self.app_id or not self.app_secret:
            print("❌ 缺少应用凭证")
            return False
            
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            if result.get('code') == 0:
                self.tenant_access_token = result['tenant_access_token']
                return True
            else:
                print(f"获取tenant_access_token失败: {result}")
                return False
        except Exception as e:
            print(f"获取tenant_access_token异常: {e}")
            return False
    
    def create_task(self, title, description="", due_date=None, followers=None, assignees=None):
        """创建任务
        
        Args:
            title: 任务标题
            description: 任务描述
            due_date: 截止日期（时间戳）
            followers: 关注人列表
            assignees: 负责人列表
        """
        if not self.tenant_access_token:
            if not self.get_tenant_access_token():
                return None
        
        url = "https://open.feishu.cn/open-apis/task/v2/tasks"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "summary": title,
            "description": description
        }
        
        if due_date:
            data["due"] = {"timestamp": due_date}
        
        # 根据飞书API示例，使用members字段设置负责人
        members = []
        
        # 使用指定的负责人用户ID
        if self.assignee_user_id:
            members.append({
                "id": self.assignee_user_id,
                "type": "user",
                "role": "assignee"
            })
        elif self.current_user_id:
            members.append({
                "id": self.current_user_id,
                "type": "user", 
                "role": "assignee"
            })
        
        if members:
            data["members"] = members
        
        print(f"📋 创建任务: {title}")
        print(f"   负责人: {len(members)}")
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            if result.get('code') == 0:
                task_data = result['data']['task']
                task_id = task_data.get('task_id') or task_data.get('id') or task_data.get('guid')
                if task_id:
                    print(f"✅ 任务创建成功，ID: {task_id}")
                    return task_id
                else:
                    print(f"❌ 无法获取任务ID，响应数据: {task_data}")
                    return None
            else:
                print(f"❌ 创建任务失败: {result}")
                return None
        except Exception as e:
            print(f"❌ 创建任务异常: {e}")
            return None
    
    def complete_task(self, task_id):
        """完成任务
        
        Args:
            task_id: 可以是task_id（t开头）或guid（uuid格式）
        """
        if not self.tenant_access_token:
            if not self.get_tenant_access_token():
                return False
        
        # 如果task_id是task_id格式（t开头），需要转换为guid
        task_guid = task_id
        if task_id.startswith('t'):
            print(f"⚠️  需要task_id到guid的映射")
            return False
        
        url = f"https://open.feishu.cn/open-apis/task/v2/tasks/{task_guid}"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }
        
        import time
        data = {
            "task": {
                "completed_at": str(int(time.time() * 1000))  # 当前时间戳（毫秒）
            },
            "update_fields": ["completed_at"]
        }
        
        try:
            response = requests.patch(url, headers=headers, json=data)
            response_text = response.text
            print(f"完成任务API响应: {response_text}")
            
            if response.status_code != 200:
                print(f"HTTP错误: {response.status_code}")
                return False
            
            try:
                result = response.json()
                if result.get('code') == 0:
                    print("✅ 任务完成成功")
                    return True
                else:
                    print(f"完成任务失败: {result}")
                    return False
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                return False
        except Exception as e:
            print(f"完成任务异常: {e}")
            return False

def main():
    manager = FeishuTaskManager()
    
    if len(sys.argv) < 2:
        print("Usage: feishu_task_integration.py [create|complete] [args...]")
        return
    
    action = sys.argv[1]
    
    if action == 'create' and len(sys.argv) > 2:
        title = sys.argv[2]
        task_id = manager.create_task(title)
        if task_id:
            print(f"任务创建成功，ID: {task_id}")
        else:
            print("任务创建失败")
    
    elif action == 'complete' and len(sys.argv) > 2:
        task_id = sys.argv[2]
        if manager.complete_task(task_id):
            print(f"任务 {task_id} 已完成")
        else:
            print(f"任务 {task_id} 完成失败")
    
    else:
        print("无效的命令")

if __name__ == '__main__':
    main()