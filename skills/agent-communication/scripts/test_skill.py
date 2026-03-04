#!/usr/bin/env python3
"""
Agent Communication Skill 测试脚本
测试所有核心功能
"""

import subprocess
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

def run_command(cmd: list) -> dict:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            ["python3"] + cmd,
            capture_output=True,
            text=True,
            cwd=SCRIPTS_DIR
        )
        if result.returncode == 0:
            return {"success": True, "output": result.stdout}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_send_message():
    """测试发送消息"""
    print("\n=== 测试发送消息 ===")
    result = run_command([
        "send.py", "--to", "dev", "--message", "测试消息", "--priority", "high"
    ])
    print(f"结果: {result}")
    return result.get("success", False)

def test_broadcast():
    """测试广播消息"""
    print("\n=== 测试广播消息 ===")
    result = run_command([
        "broadcast.py", "--message", "项目启动", "--agents", "pm,dev,test"
    ])
    print(f"结果: {result}")
    return result.get("success", False)

def test_status():
    """测试状态查询"""
    print("\n=== 测试状态查询 ===")
    # 更新状态
    run_command(["status.py", "--agent", "dev", "--update", "online"])
    # 查询状态
    result = run_command(["status.py", "--agent", "dev"])
    print(f"结果: {result}")
    return result.get("success", False)

def test_workspace():
    """测试共享工作空间"""
    print("\n=== 测试共享工作空间 ===")
    # 写入数据
    write_result = run_command([
        "workspace.py", "--write", "--key", "test_task",
        "--value", '{"id":1,"title":"测试任务"}'
    ])
    print(f"写入: {write_result}")
    
    # 读取数据
    read_result = run_command([
        "workspace.py", "--read", "--key", "test_task"
    ])
    print(f"读取: {read_result}")
    
    return write_result.get("success", False) and read_result.get("success", False)

def main():
    print("🧪 Agent Communication Skill 测试")
    print("=" * 50)
    
    tests = [
        ("发送消息", test_send_message),
        ("广播消息", test_broadcast),
        ("状态查询", test_status),
        ("共享工作空间", test_workspace)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{name}: {status}")
        except Exception as e:
            results.append((name, False))
            print(f"{name}: ❌ 错误 - {e}")
    
    print("\n" + "=" * 50)
    passed = sum(1 for _, s in results if s)
    total = len(results)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())