#!/usr/bin/env python3
"""
OpenClaw故障排除工具版本升级脚本
"""

import os
import sys
import subprocess
import json
from datetime import datetime

class OpenClawVersionUpdater:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_dir = os.path.abspath(os.path.join(self.script_dir, '..'))
        self.skill_file = os.path.join(self.project_dir, 'openclaw-troubleshooting.skill')
        self.skill_dir = self.project_dir
        self.current_version = "1.0.0"
        self.new_version = "1.1.0"
    
    def read_skill_file(self):
        """读取技能文件"""
        try:
            with open(self.skill_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ 读取技能文件失败: {e}")
            return None
    
    def write_skill_file(self, content):
        """写入技能文件"""
        try:
            with open(self.skill_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ 技能文件更新成功")
            return True
        except Exception as e:
            print(f"❌ 写入技能文件失败: {e}")
            return False
    
    def update_version(self):
        """更新技能版本"""
        print(f"🔄 升级OpenClaw故障排除工具从 {self.current_version} 到 {self.new_version}")
        
        skill_content = self.read_skill_file()
        if not skill_content:
            return False
        
        # 更新版本号
        updated_content = skill_content.replace(
            'version: 1.0.0', 
            f'version: {self.new_version}'
        )
        
        # 更新发布时间
        updated_content = updated_content.replace(
            'created_at: 2026-02-19', 
            f'created_at: {datetime.now().strftime("%Y-%m-%d")}'
        )
        
        # 更新描述信息
        updated_content = updated_content.replace(
            'description: OpenClaw故障排除工具',
            'description: OpenClaw故障排除工具 - 系统诊断、依赖检查、自动修复'
        )
        
        return self.write_skill_file(updated_content)
    
    def test_skill(self):
        """测试技能功能"""
        print("🧪 测试OpenClaw故障排除工具功能")
        
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(self.script_dir, 'openclaw_troubleshooting.py'), 'diagnose', 'system'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ 技能诊断功能正常")
                return True
            else:
                print(f"❌ 技能诊断功能失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    def publish_skill(self):
        """发布技能到ClawHub"""
        print("🚀 发布OpenClaw故障排除工具到ClawHub")
        
        try:
            result = subprocess.run(
                ['clawhub', 'publish', self.skill_dir, '--version', self.new_version, '--test'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ 技能发布成功")
                print(result.stdout)
                return True
            else:
                print(f"❌ 技能发布失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 发布过程失败: {e}")
            return False
    
    def run_upgrade(self):
        """执行完整升级流程"""
        print("=== OpenClaw故障排除工具版本升级 ===")
        
        # 更新技能文件
        if not self.update_version():
            return False
        
        # 测试技能功能
        if not self.test_skill():
            return False
        
        # 发布技能
        if not self.publish_skill():
            print("⚠️ 技能发布失败，但技能文件已更新")
            return False
        
        print("🎉 OpenClaw故障排除工具版本升级完成!")
        return True

def main():
    updater = OpenClawVersionUpdater()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = updater.test_skill()
    else:
        success = updater.run_upgrade()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
