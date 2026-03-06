#!/usr/bin/env python3
"""
Context Restore Skill - 边界情况与错误处理测试

测试用例覆盖：
1. 输入验证测试
2. 边界情况测试
3. 错误恢复测试
4. 性能测试
"""

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))


# =============================================================================
# 测试辅助函数
# =============================================================================

def create_temp_file(content: str, suffix: str = '.json') -> str:
    """创建临时文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8') as f:
        f.write(content)
        return f.name


# =============================================================================
# 输入验证测试
# =============================================================================

class TestInputValidation(unittest.TestCase):
    """输入验证测试"""

    def test_none_input_recent_operations(self):
        """None 输入 - extract_recent_operations"""
        from restore_context import extract_recent_operations
        try:
            result = extract_recent_operations(None)
            # 当前行为：抛出 AttributeError
            self.fail("Should raise TypeError for None input")
        except (AttributeError, TypeError):
            pass  # 预期行为

    def test_none_input_key_projects(self):
        """None 输入 - extract_key_projects"""
        from restore_context import extract_key_projects
        try:
            result = extract_key_projects(None)
            self.fail("Should raise TypeError for None input")
        except (AttributeError, TypeError):
            pass

    def test_none_input_ongoing_tasks(self):
        """None 输入 - extract_ongoing_tasks"""
        from restore_context import extract_ongoing_tasks
        try:
            result = extract_ongoing_tasks(None)
            self.fail("Should raise TypeError for None input")
        except (AttributeError, TypeError):
            pass

    def test_binary_input(self):
        """二进制数据输入"""
        from restore_context import extract_recent_operations
        try:
            result = extract_recent_operations(b'\x00\x01\x02\xff')
            self.fail("Should raise TypeError for binary input")
        except TypeError:
            pass  # 预期行为

    def test_integer_input(self):
        """整数输入"""
        from restore_context import extract_recent_operations
        result = extract_recent_operations(123)
        self.assertIsInstance(result, list)


# =============================================================================
# 边界情况测试
# =============================================================================

class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def test_empty_string(self):
        """空字符串"""
        from restore_context import (
            extract_recent_operations,
            extract_key_projects,
            extract_ongoing_tasks,
            extract_memory_highlights
        )
        self.assertEqual(extract_recent_operations(''), [])
        self.assertEqual(extract_key_projects(''), [])
        self.assertEqual(extract_ongoing_tasks(''), [])
        self.assertEqual(extract_memory_highlights(''), [])

    def test_whitespace_only(self):
        """仅空白字符"""
        from restore_context import extract_recent_operations
        result = extract_recent_operations('   \n\t  \n   ')
        self.assertEqual(result, [])

    def test_newlines_only(self):
        """仅换行符"""
        from restore_context import extract_recent_operations
        result = extract_recent_operations('\n\n\n')
        self.assertEqual(result, [])

    def test_special_chars(self):
        """特殊字符"""
        from restore_context import extract_recent_operations
        content = 'Test\t\n\r\x00\x1b\\'
        result = extract_recent_operations(content)
        self.assertIsInstance(result, list)

    def test_unicode_emojis(self):
        """Unicode Emoji"""
        from restore_context import extract_recent_operations
        content = '🎉 🎊 🚀 💡 ✅'
        result = extract_recent_operations(content)
        self.assertEqual(result, ['🎉', '🎊', '🚀', '💡', '✅'])

    def test_mixed_languages(self):
        """混合语言"""
        from restore_context import extract_key_projects
        content = 'Hello 世界 مرحبا Привет'
        result = extract_key_projects(content)
        self.assertIsInstance(result, list)


# =============================================================================
# 消息计数边界测试
# =============================================================================

class TestMessageCountEdgeCases(unittest.TestCase):
    """消息计数边界测试"""

    def test_large_numbers(self):
        """超大数值"""
        from restore_context import parse_metadata
        content = '原始消息数: 99999999999999999999'
        metadata = parse_metadata(content)
        # 当前行为：尝试解析超大数
        self.assertIsNotNone(metadata.get('original_count'))

    def test_negative_numbers(self):
        """负数"""
        from restore_context import parse_metadata
        content = '原始消息数: -5\n压缩后消息数: 10'
        metadata = parse_metadata(content)
        # 当前行为：返回 None
        self.assertIsNone(metadata.get('original_count'))

    def test_zero_values(self):
        """零值"""
        from restore_context import parse_metadata
        content = '原始消息数: 0\n压缩后消息数: 0'
        metadata = parse_metadata(content)
        self.assertEqual(metadata.get('original_count'), 0)

    def test_non_numeric_values(self):
        """非数字值"""
        from restore_context import parse_metadata
        content = '原始消息数: abc\n压缩后消息数: def'
        metadata = parse_metadata(content)
        self.assertIsNone(metadata.get('original_count'))

    def test_float_values(self):
        """浮点数值"""
        from restore_context import parse_metadata
        content = '原始消息数: 100.5\n压缩后消息数: 10.7'
        metadata = parse_metadata(content)
        # 正则只匹配整数，应返回 None
        self.assertIsNone(metadata.get('original_count'))

    def test_scientific_notation(self):
        """科学计数法"""
        from restore_context import parse_metadata
        content = '原始消息数: 1e6\n压缩后消息数: 1e5'
        metadata = parse_metadata(content)
        self.assertIsNone(metadata.get('original_count'))


# =============================================================================
# 压缩率计算测试
# =============================================================================

class TestCompressionRatio(unittest.TestCase):
    """压缩率计算测试"""

    def test_normal_ratio(self):
        """正常压缩率"""
        from restore_context import calculate_compression_ratio
        ratio = calculate_compression_ratio(100, 25)
        self.assertEqual(ratio, 25.0)

    def test_zero_original(self):
        """原始消息数为零"""
        from restore_context import calculate_compression_ratio
        ratio = calculate_compression_ratio(0, 10)
        self.assertIsNone(ratio)

    def test_zero_compressed(self):
        """压缩后消息数为零"""
        from restore_context import calculate_compression_ratio
        ratio = calculate_compression_ratio(100, 0)
        self.assertEqual(ratio, 0.0)

    def test_negative_original(self):
        """负数原始消息"""
        from restore_context import calculate_compression_ratio
        ratio = calculate_compression_ratio(-100, 50)
        self.assertIsNone(ratio)

    def test_compressed_larger_than_original(self):
        """压缩后比原始大"""
        from restore_context import calculate_compression_ratio
        ratio = calculate_compression_ratio(10, 100)
        self.assertIsNone(ratio)

    def test_none_inputs(self):
        """None 输入"""
        from restore_context import calculate_compression_ratio
        self.assertIsNone(calculate_compression_ratio(None, 10))
        self.assertIsNone(calculate_compression_ratio(100, None))
        self.assertIsNone(calculate_compression_ratio(None, None))


# =============================================================================
# 文件操作测试
# =============================================================================

class TestFileOperations(unittest.TestCase):
    """文件操作测试"""

    def test_empty_file(self):
        """空文件"""
        from restore_context import load_compressed_context
        filepath = create_temp_file('')
        try:
            result = load_compressed_context(filepath)
            self.assertEqual(result, '')
        finally:
            os.unlink(filepath)

    def test_empty_json(self):
        """空 JSON 对象"""
        from restore_context import load_compressed_context
        filepath = create_temp_file('{}')
        try:
            result = load_compressed_context(filepath)
            self.assertIsInstance(result, dict)
        finally:
            os.unlink(filepath)

    def test_empty_json_array(self):
        """空 JSON 数组"""
        from restore_context import load_compressed_context
        filepath = create_temp_file('[]')
        try:
            result = load_compressed_context(filepath)
            self.assertIsInstance(result, list)
        finally:
            os.unlink(filepath)

    def test_corrupted_json(self):
        """损坏的 JSON"""
        from restore_context import load_compressed_context
        filepath = create_temp_file('{"valid": true, "incomplete":')
        try:
            result = load_compressed_context(filepath)
            self.assertIsInstance(result, str)  # 降级为文本
        finally:
            os.unlink(filepath)

    def test_unicode_bom(self):
        """Unicode BOM"""
        from restore_context import load_compressed_context
        content = '\ufeff{"key": "value"}'
        filepath = create_temp_file(content)
        try:
            result = load_compressed_context(filepath)
            self.assertIsNotNone(result)
        finally:
            os.unlink(filepath)

    def test_permission_denied(self):
        """权限拒绝 (跳过 - 需要 root)"""
        self.skipTest("Requires root privileges")


# =============================================================================
# JSON 格式处理测试
# =============================================================================

class TestJsonFormatHandling(unittest.TestCase):
    """JSON 格式处理测试"""

    def test_nested_json(self):
        """嵌套 JSON"""
        from restore_context import load_compressed_context
        data = {
            "content": "Test",
            "metadata": {
                "timestamp": "2026-02-06T23:42:00",
                "nested": {
                    "deep": "value"
                }
            }
        }
        filepath = create_temp_file(json.dumps(data))
        try:
            result = load_compressed_context(filepath)
            self.assertIsInstance(result, dict)
            self.assertEqual(result["metadata"]["nested"]["deep"], "value")
        finally:
            os.unlink(filepath)

    def test_json_with_special_chars(self):
        """含特殊字符的 JSON"""
        from restore_context import load_compressed_context
        data = {
            "content": "Test\t\n\r\x00中文🎉",
            "emoji": "✅"
        }
        filepath = create_temp_file(json.dumps(data, ensure_ascii=False))
        try:
            result = load_compressed_context(filepath)
            self.assertIsInstance(result, dict)
        finally:
            os.unlink(filepath)

    def test_json_array(self):
        """JSON 数组"""
        from restore_context import load_compressed_context
        data = ["item1", "item2", "item3"]
        filepath = create_temp_file(json.dumps(data))
        try:
            result = load_compressed_context(filepath)
            self.assertIsInstance(result, list)
        finally:
            os.unlink(filepath)


# =============================================================================
# 性能测试
# =============================================================================

class TestPerformance(unittest.TestCase):
    """性能测试"""

    def test_metadata_parsing_performance(self):
        """元数据解析性能"""
        from restore_context import parse_metadata
        content = '原始消息数: 100\n压缩后消息数: 10\n上下文压缩于 2026-02-06T23:42:00'
        content = content * 100
        
        start = time.time()
        for _ in range(100):
            parse_metadata(content)
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 2.0, f"Metadata parsing too slow: {elapsed:.2f}s")

    def test_project_extraction_performance(self):
        """项目提取性能"""
        from restore_context import extract_key_projects
        content = 'Hermes Plan 是一个数据分析助手。' * 1000
        content += 'Akasha Plan 是自主新闻系统。' * 1000
        
        start = time.time()
        for _ in range(100):
            extract_key_projects(content)
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 2.0, f"Project extraction too slow: {elapsed:.2f}s")

    def test_operations_extraction_performance(self):
        """操作提取性能"""
        from restore_context import extract_recent_operations
        content = '✅ 完成数据清洗模块\n✅ 修复登录漏洞\n✅ 添加新功能' * 100
        
        start = time.time()
        for _ in range(100):
            extract_recent_operations(content)
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 2.0, f"Operations extraction too slow: {elapsed:.2f}s")


# =============================================================================
# 报告格式化测试
# =============================================================================

class TestReportFormatting(unittest.TestCase):
    """报告格式化测试"""

    def test_minimal_report_empty_content(self):
        """空内容的 minimal 报告"""
        from restore_context import format_minimal_report
        report = format_minimal_report('')
        self.assertIn("Minimal", report)
        self.assertIn("CONTEXT RESTORE REPORT", report)

    def test_normal_report_empty_content(self):
        """空内容的 normal 报告"""
        from restore_context import format_normal_report
        report = format_normal_report('')
        self.assertIn("Normal", report)

    def test_detailed_report_empty_content(self):
        """空内容的 detailed 报告"""
        from restore_context import format_detailed_report
        report = format_detailed_report('')
        self.assertIn("Detailed", report)
        self.assertIn("Raw Content Preview", report)

    def test_report_with_unicode(self):
        """含 Unicode 的报告"""
        from restore_context import format_normal_report
        content = '🎉 测试\n✅ 完成'
        report = format_normal_report(content)
        self.assertIn("🎉", report)
        self.assertIn("✅", report)


# =============================================================================
# 错误恢复测试
# =============================================================================

class TestErrorRecovery(unittest.TestCase):
    """错误恢复测试"""

    def test_missing_json_fields(self):
        """JSON 缺少预期字段"""
        from restore_context import load_compressed_context
        # JSON 缺少 'content' 字段
        data = {"other": "value"}
        filepath = create_temp_file(json.dumps(data))
        try:
            result = load_compressed_context(filepath)
            self.assertIsInstance(result, dict)
        finally:
            os.unlink(filepath)

    def test_malformed_utf8(self):
        """损坏的 UTF-8 (跳过 - Python 会处理)"""
        self.skipTest("Python handles UTF-8 internally")

    def test_very_long_line(self):
        """非常长的行"""
        from restore_context import extract_recent_operations
        long_line = '✅ ' + 'x' * 100000
        result = extract_recent_operations(long_line)
        self.assertEqual(len(result), 1)

    def test_many_matches(self):
        """大量匹配"""
        from restore_context import extract_recent_operations
        content = '✅ 操作1\n✅ 操作2\n✅ 操作3\n✅ 操作4\n✅ 操作5\n✅ 操作6'
        result = extract_recent_operations(content)
        self.assertLessEqual(len(result), 5)  # 限制为 5


# =============================================================================
# 测试运行器
# =============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Context Restore - 边界情况与错误处理测试")
    print("=" * 70)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestInputValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestMessageCountEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestCompressionRatio))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestJsonFormatHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestReportFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorRecovery))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 统计
    print()
    print("=" * 70)
    print(f"测试结果汇总:")
    print(f"  总测试: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  跳过: {len(result.skipped)}")
    print(f"  错误: {len(result.errors)}")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
