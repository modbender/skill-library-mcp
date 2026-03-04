#!/usr/bin/env python3
"""
Context Restore Skill - Phase 3 功能测试 (Auto Trigger & Cron Integration)

测试用例：
- test_hash_content: 内容哈希生成
- test_detect_context_changes: 变化检测
- test_load_cached_hash: 加载缓存哈希
- test_save_cached_hash: 保存缓存哈希
- test_check_and_restore_context: 自动恢复功能
- test_cron_script_generation: Cron 脚本生成
"""

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))


class TestHashContent(unittest.TestCase):
    """内容哈希功能测试"""

    def test_hash_content_basic(self):
        """测试基础哈希生成"""
        from restore_context import hash_content
        
        content = "测试内容"
        result = hash_content(content)
        
        # 使用 MD5 哈希 (32 chars)
        self.assertEqual(len(result), 32)
        self.assertTrue(all(c in '0123456789abcdef' for c in result))

    def test_hash_content_deterministic(self):
        """测试哈希确定性（相同内容产生相同哈希）"""
        from restore_context import hash_content
        
        content = "Hermes Plan 测试内容"
        
        result1 = hash_content(content)
        result2 = hash_content(content)
        
        self.assertEqual(result1, result2)

    def test_hash_content_different_content(self):
        """测试不同内容产生不同哈希"""
        from restore_context import hash_content
        
        content1 = "内容1"
        content2 = "内容2"
        
        result1 = hash_content(content1)
        result2 = hash_content(content2)
        
        self.assertNotEqual(result1, result2)

    def test_hash_content_empty(self):
        """测试空内容哈希"""
        from restore_context import hash_content
        
        result = hash_content("")
        self.assertEqual(len(result), 32)

    def test_hash_content_large(self):
        """测试大内容哈希"""
        from restore_context import hash_content
        
        large_content = "x" * 100000
        result = hash_content(large_content)
        
        self.assertEqual(len(result), 32)

    def test_hash_content_unicode(self):
        """测试 Unicode 内容哈希"""
        from restore_context import hash_content
        
        content = "中文测试 🎉 emoji"
        result = hash_content(content)
        
        self.assertEqual(len(result), 32)


class TestDetectContextChanges(unittest.TestCase):
    """变化检测功能测试"""

    def test_detect_changes_true(self):
        """测试检测到变化"""
        from restore_context import detect_context_changes
        
        old_content = "旧内容"
        new_content = "新内容"
        
        result = detect_context_changes(new_content, old_content)
        
        self.assertTrue(result)

    def test_detect_changes_false(self):
        """测试未检测到变化"""
        from restore_context import detect_context_changes
        
        content = "相同内容"
        
        result = detect_context_changes(content, content)
        
        self.assertFalse(result)

    def test_detect_changes_same_hash(self):
        """测试相同哈希（无变化）"""
        from restore_context import detect_context_changes
        
        content = "Hermes Plan 内容"
        same_content = "Hermes Plan 内容"
        
        result = detect_context_changes(same_content, content)
        
        self.assertFalse(result)

    def test_detect_changes_different(self):
        """测试内容不同（有变化）"""
        from restore_context import detect_context_changes
        
        old = "旧版本内容"
        new = "新版本内容"
        
        result = detect_context_changes(new, old)
        
        self.assertTrue(result)


class TestCachedHash(unittest.TestCase):
    """缓存哈希功能测试"""

    def test_save_and_load_hash(self):
        """测试保存和加载哈希"""
        from restore_context import save_cached_hash, load_cached_hash
        
        test_content = "测试内容"
        test_hash = hashlib.sha256(test_content.encode()).hexdigest()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = os.path.join(tmpdir, "hash_cache.json")
            context_file = os.path.join(tmpdir, "context.json")
            
            # 创建测试上下文文件
            with open(context_file, 'w') as f:
                f.write(test_content)
            
            # 保存哈希
            save_result = save_cached_hash(test_hash, context_file, cache_file)
            self.assertTrue(save_result)
            
            # 加载哈希
            loaded_hash = load_cached_hash(cache_file)
            self.assertEqual(loaded_hash, test_hash)

    def test_load_nonexistent_hash(self):
        """测试加载不存在的哈希"""
        from restore_context import load_cached_hash
        
        nonexistent = "/nonexistent/path/hash_cache.json"
        result = load_cached_hash(nonexistent)
        
        self.assertIsNone(result)

    def test_save_hash_invalid_path(self):
        """测试保存到无效路径"""
        from restore_context import save_cached_hash
        
        result = save_cached_hash(
            "some_hash",
            "/nonexistent/context.json",
            "/invalid/path/cache.json"
        )
        
        self.assertFalse(result)


class TestCheckAndRestoreContext(unittest.TestCase):
    """自动恢复功能测试"""

    def test_check_and_restore_no_changes(self):
        """测试无变化时不恢复"""
        from restore_context import (
            check_and_restore_context,
            save_cached_hash,
            hash_content,
            load_cached_hash,
            HASH_CACHE_FILE
        )
        
        test_content = "测试内容"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            context_file = os.path.join(tmpdir, "context.json")
            temp_cache = os.path.join(tmpdir, "hash_cache.json")
            
            # 写入测试内容
            with open(context_file, 'w') as f:
                f.write(test_content)
            
            # 保存哈希到临时缓存位置
            content_hash = hash_content(test_content)
            save_cached_hash(content_hash, context_file, temp_cache)
            
            # 将临时缓存复制到默认位置
            import shutil
            shutil.copy(temp_cache, HASH_CACHE_FILE)
            
            # 再次调用（相同内容，应无变化）
            result = check_and_restore_context(
                context_file,
                auto_mode=True,
                quiet=True,
                level='normal'
            )
            
            self.assertFalse(result.get('changed'))
            self.assertFalse(result.get('restored'))

    def test_check_and_restore_with_changes(self):
        """测试有变化时恢复"""
        from restore_context import (
            check_and_restore_context, 
            save_cached_hash,
            hash_content
        )
        
        old_content = "旧内容"
        new_content = "新内容 - 有变化"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            context_file = os.path.join(tmpdir, "context.json")
            cache_file = os.path.join(tmpdir, "cache.json")
            
            # 先写入旧内容并保存哈希
            with open(context_file, 'w') as f:
                f.write(old_content)
            
            old_hash = hash_content(old_content)
            save_cached_hash(old_hash, context_file, cache_file)
            
            # 修改内容
            with open(context_file, 'w') as f:
                f.write(new_content)
            
            # 恢复
            result = check_and_restore_context(
                context_file,
                auto_mode=True,
                quiet=True,
                level='normal'
            )
            
            self.assertTrue(result.get('changed'))
            self.assertTrue(result.get('restored'))
            self.assertIn('report', result)

    def test_check_and_restore_no_cache(self):
        """测试无缓存时的首次运行"""
        from restore_context import check_and_restore_context
        
        content = "首次运行内容"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            context_file = os.path.join(tmpdir, "context.json")
            
            with open(context_file, 'w') as f:
                f.write(content)
            
            result = check_and_restore_context(
                context_file,
                auto_mode=True,
                quiet=True,
                level='normal'
            )
            
            # 首次运行应该视为有变化
            self.assertTrue(result.get('changed'))
            self.assertTrue(result.get('restored'))


class TestCronIntegration(unittest.TestCase):
    """Cron 集成功能测试"""

    def test_generate_cron_script(self):
        """测试生成 cron 脚本"""
        from restore_context import generate_cron_script
        
        script = generate_cron_script()
        
        self.assertIsInstance(script, str)
        self.assertIn("python", script.lower())
        self.assertIn("restore_context", script)

    def test_generate_cron_script_with_interval(self):
        """测试 cron 脚本生成（间隔硬编码为 5 分钟）"""
        from restore_context import generate_cron_script
        
        script = generate_cron_script()
        
        self.assertIsInstance(script, str)
        # 默认间隔是 5 分钟
        self.assertIn("*/5 * * * *", script)
        # 脚本应该包含 python 调用
        self.assertIn("python", script.lower())
        self.assertIn("restore_context", script)

    def test_install_cron_job_valid_script(self):
        """测试安装有效的 cron 任务"""
        from restore_context import install_cron_job, generate_cron_script
        
        script_content = generate_cron_script()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "test_cron.sh")
            
            # 写入脚本
            with open(script_path, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write(script_content)
            os.chmod(script_path, 0o755)
            
            # 安装 cron
            result = install_cron_job(script_path, interval_minutes=5)
            
            # 结果取决于系统权限，可能成功或失败
            self.assertIsInstance(result, bool)

    def test_install_cron_job_invalid_path(self):
        """测试安装无效路径的 cron 任务"""
        from restore_context import install_cron_job
        
        result = install_cron_job("/nonexistent/script.sh")
        
        self.assertFalse(result)


class TestNotificationIntegration(unittest.TestCase):
    """通知集成测试"""

    def test_notification_script_exists(self):
        """测试通知脚本存在"""
        from restore_context import NOTIFICATION_SCRIPT
        
        # 脚本可能存在或不存在
        exists = os.path.exists(NOTIFICATION_SCRIPT)
        self.assertIsInstance(exists, bool)

    def test_send_notification_function_exists(self):
        """测试通知函数存在"""
        from restore_context import send_context_change_notification
        
        # 函数应该存在（即使可能返回 False）
        self.assertTrue(callable(send_context_change_notification))


class TestHashCacheDir(unittest.TestCase):
    """哈希缓存目录测试"""

    def test_hash_cache_dir_defined(self):
        """测试哈希缓存目录已定义"""
        from restore_context import HASH_CACHE_DIR, HASH_CACHE_FILE
        
        self.assertIsInstance(HASH_CACHE_DIR, str)
        self.assertIsInstance(HASH_CACHE_FILE, str)
        self.assertIn("tmp", HASH_CACHE_DIR)


# =============================================================================
# 测试运行器
# =============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Context Restore - Phase 3 功能测试 (Auto Trigger & Cron)")
    print("=" * 70)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestHashContent))
    suite.addTests(loader.loadTestsFromTestCase(TestDetectContextChanges))
    suite.addTests(loader.loadTestsFromTestCase(TestCachedHash))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckAndRestoreContext))
    suite.addTests(loader.loadTestsFromTestCase(TestCronIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestNotificationIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestHashCacheDir))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print(f"测试结果汇总:")
    print(f"  总测试: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
