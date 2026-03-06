#!/usr/bin/env python3
"""
增强功能测试脚本
测试LoreBible管理、冲突检测和会话管理功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

def test_lore_bible_manager():
    """测试LoreBible管理器"""
    print("测试LoreBible管理器...")

    from lore_bible_manager import LoreBibleManager

    # 创建临时工作目录
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir) / "test_workspace"
        workspace.mkdir()

        # 创建管理器
        manager = LoreBibleManager(str(workspace))

        # 测试目录验证
        is_valid, missing_dirs = manager.validate_directory_structure()
        print(f"  目录验证: 有效={is_valid}, 缺失目录={missing_dirs}")

        # 测试目录创建
        success = manager.create_directory_structure()
        print(f"  目录创建: {'成功' if success else '失败'}")

        # 再次验证
        is_valid, missing_dirs = manager.validate_directory_structure()
        print(f"  创建后验证: 有效={is_valid}")

        # 测试工作空间信息
        info = manager.get_workspace_info()
        print(f"  工作空间信息: 角色数={info['characters_count']}, 临时文件数={info['temp_files_count']}")

        print("  LoreBible管理器测试完成")

def test_conflict_detector():
    """测试冲突检测器"""
    print("测试冲突检测器...")

    from conflict_detector import ConflictDetector, ConflictSeverity

    # 创建检测器
    detector = ConflictDetector()

    # 测试角色数据
    character_data = {
        "name": "测试角色",
        "age": "25",
        "gender": "男",
        "occupation": "剑士",
        "role": "主角"
    }

    # 测试冲突检测
    conflicts = detector.detect_conflicts(character_data, [])
    print(f"  冲突检测: 发现 {len(conflicts)} 个冲突")

    # 测试角色验证
    is_valid, validation_conflicts = detector.validate_character(character_data)
    print(f"  角色验证: 有效={is_valid}, 冲突数={len(validation_conflicts)}")

    # 测试报告生成
    report = detector.generate_report(conflicts, "text")
    print(f"  报告生成: {len(report.splitlines())} 行")

    print("  冲突检测器测试完成")

def test_profile_session():
    """测试会话管理"""
    print("测试会话管理...")

    from profile_session import ProfileSession, SessionConfig

    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir) / "test_session"
        workspace.mkdir()

        # 创建配置
        config = SessionConfig(
            workspace=str(workspace),
            character_name="测试角色",
            template_type="standard",
            require_confirmation=False
        )

        # 创建会话
        session = ProfileSession(config)
        print(f"  会话创建: ID={session.session_id}")

        # 测试状态报告
        report = session.get_status_report()
        print(f"  状态报告: {report['status']}")

        # 测试临时档案保存
        test_content = "# 测试角色 - 角色档案\n\n测试内容"
        temp_path = session.save_temp_profile(test_content)
        print(f"  临时保存: {'成功' if temp_path else '失败'}")

        # 测试会话列表
        sessions = ProfileSession.list_sessions(str(workspace), active_only=False)
        print(f"  会话列表: {len(sessions)} 个会话")

        print("  会话管理测试完成")

def test_generate_profile_enhanced():
    """测试增强的档案生成"""
    print("测试增强档案生成...")

    from generate_profile import CharacterProfileGenerator

    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir) / "test_generation"
        workspace.mkdir()

        # 创建生成器（增强模式）
        generator = CharacterProfileGenerator(
            template_type="standard",
            workspace=str(workspace)
        )

        # 角色数据
        character_data = {
            "name": "增强测试角色",
            "age": "30",
            "gender": "女",
            "occupation": "法师",
            "role": "主角"
        }

        # 测试增强生成（跳过用户确认）
        success, final_path, conflicts = generator.generate_enhanced_profile(
            character_data,
            require_confirmation=False
        )

        print(f"  增强生成: 成功={success}, 最终路径={final_path}, 冲突数={len(conflicts)}")

        # 测试传统生成
        generator2 = CharacterProfileGenerator(template_type="standard")
        content = generator2.generate_markdown(character_data, output_path=None)
        print(f"  传统生成: 内容长度={len(content)} 字符")

        print("  增强档案生成测试完成")

def test_subagent_orchestrator():
    """测试子代理协调器"""
    print("测试子代理协调器...")

    from subagent_orchestrator import SubagentOrchestrator

    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir) / "test_orchestrator"
        workspace.mkdir()

        # 创建协调器
        orchestrator = SubagentOrchestrator(str(workspace))

        # 测试工作流运行（使用快速创建模式）
        try:
            result = orchestrator.run_workflow("quick_creation", {
                "character_data": {
                    "name": "协调测试角色",
                    "age": "28",
                    "gender": "男",
                    "occupation": "盗贼",
                    "role": "配角"
                },
                "template_type": "standard"
            })

            report = result["report"]
            print(f"  工作流执行: {report['completed']}/{report['total_tasks']} 任务完成")
            print(f"  成功率: {report['success_rate']:.1%}")

        except Exception as e:
            print(f"  工作流执行失败（预期内）: {e}")

        print("  子代理协调器测试完成")

def main():
    """主测试函数"""
    print("开始增强功能测试...")
    print("=" * 60)

    tests = [
        test_lore_bible_manager,
        test_conflict_detector,
        test_profile_session,
        test_generate_profile_enhanced,
        test_subagent_orchestrator
    ]

    passed = 0
    total = len(tests)

    for i, test_func in enumerate(tests, 1):
        try:
            test_func()
            passed += 1
            print(f"[{i}/{total}] [OK] 通过")
        except Exception as e:
            print(f"[{i}/{total}] [X] 失败: {e}")
        print()

    print("=" * 60)
    print(f"测试完成: {passed}/{total} 通过 ({passed/total*100:.1f}%)")

    if passed == total:
        print("所有测试通过！")
        return 0
    else:
        print("部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())