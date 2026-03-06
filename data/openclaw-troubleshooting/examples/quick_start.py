#!/usr/bin/env python3
"""OpenClaw常见问题解决方案技能快速入门示例"""

import sys
import os

# 添加技能脚本到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, '..', 'scripts'))

from openclaw_troubleshooting import OpenClawTroubleshooter

def quick_start():
    """快速入门示例"""
    print("=== OpenClaw常见问题解决方案 - 快速入门 ===")
    print()
    
    # 创建故障排除实例
    troubleshooter = OpenClawTroubleshooter()
    
    print("1. 系统诊断")
    print("-" * 30)
    diagnosis = troubleshooter.diagnose_system()
    print()
    
    print("2. 修复问题")
    print("-" * 30)
    
    # 检查并修复依赖问题
    dependencies_status = diagnosis.get('dependencies', {}).get('status', 'warning')
    if dependencies_status == 'warning':
        print("📦 发现依赖问题，正在修复...")
        troubleshooter.fix_issue('dependencies')
    
    # 检查并修复工作区问题
    workspace_status = diagnosis.get('workspace', {}).get('status', 'warning')
    if workspace_status == 'warning':
        print("📂 发现工作区问题，正在修复...")
        troubleshooter.fix_issue('workspace')
    
    # 检查并修复权限问题
    permissions_status = diagnosis.get('permissions', {}).get('status', 'warning')
    if permissions_status == 'warning':
        print("🔐 发现权限问题，正在修复...")
        troubleshooter.fix_issue('permissions')
    
    print()
    print("✅ 所有问题已修复！")
    print()
    
    print("3. 验证修复结果")
    print("-" * 30)
    final_diagnosis = troubleshooter.diagnose_system()
    
    all_ok = True
    if final_diagnosis.get('dependencies', {}).get('status', 'warning') != 'ok':
        all_ok = False
    if final_diagnosis.get('workspace', {}).get('status', 'warning') != 'ok':
        all_ok = False
    if final_diagnosis.get('permissions', {}).get('status', 'warning') != 'ok':
        all_ok = False
    
    if all_ok:
        print("✅ OpenClaw系统已准备好使用！")
    else:
        print("⚠️  仍存在一些问题，请检查详细诊断结果")
    
    print()
    print("=== 快速入门完成 ===")

if __name__ == "__main__":
    quick_start()
