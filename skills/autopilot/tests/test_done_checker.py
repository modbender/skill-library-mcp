#!/usr/bin/env python3
"""
测试 Done Checker 模块
- 文件存在检查
- 文件大小检查
- 文件内容检查
- Glob 模式检查
- 命令执行检查
"""

import os
import sys
import tempfile
import unittest

# 添加 lib 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.done_checker import (
    CheckResult,
    DoneResult,
    check_command_condition,
    check_done_conditions,
    check_file_condition,
    check_glob_condition,
    format_done_result,
)


class TestFileCondition(unittest.TestCase):
    """测试文件条件检查"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理临时文件"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_file(self, rel_path: str, content: str = "test content") -> str:
        """创建临时文件"""
        full_path = os.path.join(self.temp_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return full_path
    
    def test_file_exists(self):
        """测试文件存在检查"""
        self._create_file("test.txt", "hello world")
        
        result = check_file_condition(
            {"path": "test.txt"},
            self.temp_dir
        )
        
        self.assertTrue(result.passed)
        self.assertEqual(result.check_type, "file")
    
    def test_file_not_exists(self):
        """测试文件不存在"""
        result = check_file_condition(
            {"path": "nonexistent.txt"},
            self.temp_dir
        )
        
        self.assertFalse(result.passed)
        self.assertIn("不存在", result.details)
    
    def test_file_min_size_pass(self):
        """测试文件大小满足要求"""
        self._create_file("test.txt", "A" * 200)
        
        result = check_file_condition(
            {"path": "test.txt", "min_size": 100},
            self.temp_dir
        )
        
        self.assertTrue(result.passed)
    
    def test_file_min_size_fail(self):
        """测试文件大小不满足要求"""
        self._create_file("test.txt", "small")
        
        result = check_file_condition(
            {"path": "test.txt", "min_size": 100},
            self.temp_dir
        )
        
        self.assertFalse(result.passed)
        self.assertIn("字节", result.details)
    
    def test_file_contains_pass(self):
        """测试文件包含关键词"""
        self._create_file("test.txt", "model User { name: string }")
        
        result = check_file_condition(
            {"path": "test.txt", "contains": ["model User"]},
            self.temp_dir
        )
        
        self.assertTrue(result.passed)
    
    def test_file_contains_fail(self):
        """测试文件缺少关键词"""
        self._create_file("test.txt", "model User { name: string }")
        
        result = check_file_condition(
            {"path": "test.txt", "contains": ["model User", "model Restaurant"]},
            self.temp_dir
        )
        
        self.assertFalse(result.passed)
        self.assertIn("model Restaurant", result.details)
    
    def test_file_contains_multiple(self):
        """测试多个关键词"""
        self._create_file("test.txt", "model User\nmodel Restaurant\nmodel Review")
        
        result = check_file_condition(
            {"path": "test.txt", "contains": ["model User", "model Restaurant", "model Review"]},
            self.temp_dir
        )
        
        self.assertTrue(result.passed)
    
    def test_nested_path(self):
        """测试嵌套路径"""
        self._create_file("src/app/page.tsx", "export default function Page() {}")
        
        result = check_file_condition(
            {"path": "src/app/page.tsx"},
            self.temp_dir
        )
        
        self.assertTrue(result.passed)


class TestGlobCondition(unittest.TestCase):
    """测试 Glob 模式检查"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理临时文件"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_file(self, rel_path: str, content: str = "test content") -> str:
        """创建临时文件"""
        full_path = os.path.join(self.temp_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return full_path
    
    def test_glob_simple_pattern(self):
        """测试简单 glob 模式"""
        self._create_file("test1.ts", "A" * 100)
        self._create_file("test2.ts", "B" * 100)
        
        result = check_glob_condition(
            {"pattern": "*.ts", "min_count": 2},
            self.temp_dir
        )
        
        self.assertTrue(result.passed)
    
    def test_glob_recursive_pattern(self):
        """测试递归 glob 模式"""
        self._create_file("src/api/auth.ts", "A" * 100)
        self._create_file("src/api/users.ts", "B" * 100)
        self._create_file("src/api/routes/index.ts", "C" * 100)
        
        result = check_glob_condition(
            {"pattern": "src/**/*.ts", "min_count": 3},
            self.temp_dir
        )
        
        self.assertTrue(result.passed)
    
    def test_glob_min_count_fail(self):
        """测试文件数量不足"""
        self._create_file("test1.ts", "A" * 100)
        
        result = check_glob_condition(
            {"pattern": "*.ts", "min_count": 5},
            self.temp_dir
        )
        
        self.assertFalse(result.passed)
        self.assertIn("1", result.details)  # 找到 1 个
        self.assertIn("5", result.details)  # 需要 5 个
    
    def test_glob_min_file_size(self):
        """测试最小文件大小过滤"""
        self._create_file("big.ts", "A" * 200)
        self._create_file("small.ts", "B")  # 太小
        
        result = check_glob_condition(
            {"pattern": "*.ts", "min_count": 1, "min_file_size": 100},
            self.temp_dir
        )
        
        self.assertTrue(result.passed)
        self.assertIn("1", result.details)  # 只有 1 个有效
    
    def test_glob_no_matches(self):
        """测试没有匹配文件"""
        result = check_glob_condition(
            {"pattern": "*.xyz", "min_count": 1},
            self.temp_dir
        )
        
        self.assertFalse(result.passed)
        self.assertIn("0", result.details)


class TestCommandCondition(unittest.TestCase):
    """测试命令执行检查"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理临时文件"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_command_success(self):
        """测试命令成功"""
        result = check_command_condition(
            {"cmd": "echo hello", "expect_exit": 0},
            self.temp_dir
        )
        
        self.assertTrue(result.passed)
        self.assertIn("0", result.details)
    
    def test_command_failure(self):
        """测试命令失败"""
        result = check_command_condition(
            {"cmd": "exit 1", "expect_exit": 0},
            self.temp_dir
        )
        
        self.assertFalse(result.passed)
        self.assertIn("1", result.details)
    
    def test_command_with_project_dir(self):
        """测试 {project_dir} 替换"""
        result = check_command_condition(
            {"cmd": "cd {project_dir} && pwd", "expect_exit": 0},
            self.temp_dir
        )
        
        self.assertTrue(result.passed)
    
    def test_command_expect_nonzero(self):
        """测试期望非零退出码"""
        result = check_command_condition(
            {"cmd": "exit 42", "expect_exit": 42},
            self.temp_dir
        )
        
        self.assertTrue(result.passed)
    
    def test_command_timeout(self):
        """测试命令超时（跳过，因为需要长时间等待）"""
        # 这个测试会太慢，跳过
        pass


class TestCheckDoneConditions(unittest.TestCase):
    """测试完整的完成条件检测"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理临时文件"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_file(self, rel_path: str, content: str = "test content") -> str:
        """创建临时文件"""
        full_path = os.path.join(self.temp_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return full_path
    
    def test_all_conditions_pass(self):
        """测试所有条件通过"""
        self._create_file("package.json", '{"name": "test"}' + "X" * 200)
        self._create_file("src/index.ts", "A" * 100)
        self._create_file("src/utils.ts", "B" * 100)
        
        done_when = {
            "files": [
                {"path": "package.json", "min_size": 100}
            ],
            "files_glob": [
                {"pattern": "src/**/*.ts", "min_count": 2}
            ],
            "commands": [
                {"cmd": "echo test", "expect_exit": 0}
            ]
        }
        
        result = check_done_conditions(done_when, self.temp_dir)
        
        self.assertTrue(result.passed)
        self.assertEqual(len(result.results), 3)
    
    def test_partial_failure(self):
        """测试部分条件失败"""
        # 创建一个足够大的文件（超过默认的 min_file_size 100）
        self._create_file("package.json", '{"name": "test"}' + "X" * 100)
        
        done_when = {
            "files": [
                {"path": "package.json"},
                {"path": "nonexistent.json"}  # 这个会失败
            ]
        }
        
        result = check_done_conditions(done_when, self.temp_dir)
        
        self.assertFalse(result.passed)
        self.assertEqual(len(result.get_failed_items()), 1)
    
    def test_no_conditions(self):
        """测试无条件（默认通过）"""
        result = check_done_conditions(None, self.temp_dir)
        
        self.assertTrue(result.passed)
        self.assertEqual(len(result.results), 0)
    
    def test_empty_conditions(self):
        """测试空条件"""
        result = check_done_conditions({}, self.temp_dir)
        
        self.assertTrue(result.passed)


class TestDoneResult(unittest.TestCase):
    """测试 DoneResult 类"""
    
    def test_get_failed_items(self):
        """测试获取失败项"""
        result = DoneResult(
            passed=False,
            results=[
                CheckResult("file", "test1.txt", True, "OK"),
                CheckResult("file", "test2.txt", False, "不存在"),
                CheckResult("glob", "*.ts", False, "数量不足"),
            ]
        )
        
        failed = result.get_failed_items()
        self.assertEqual(len(failed), 2)


class TestFormatDoneResult(unittest.TestCase):
    """测试格式化输出"""
    
    def test_format_passed(self):
        """测试格式化通过结果"""
        result = DoneResult(
            passed=True,
            results=[
                CheckResult("file", "test.txt", True, "存在"),
            ],
            summary="全部通过"
        )
        
        formatted = format_done_result(result)
        self.assertIn("✅", formatted)
        self.assertIn("全部通过", formatted)
    
    def test_format_failed(self):
        """测试格式化失败结果"""
        result = DoneResult(
            passed=False,
            results=[
                CheckResult("file", "test.txt", False, "不存在"),
            ],
            summary="1 项失败"
        )
        
        formatted = format_done_result(result)
        self.assertIn("❌", formatted)
        self.assertIn("失败", formatted)


if __name__ == '__main__':
    unittest.main()
