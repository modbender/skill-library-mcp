"""
测试文件
Method Development Agent - MVP
"""
import unittest
from datetime import datetime
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Compound, ChromatographicMethod, Experiment
from utils import (
    validate_cas_number,
    calculate_resolution,
    calculate_theoretical_plates,
    assess_peak_quality
)


class TestUtils(unittest.TestCase):
    """测试工具函数"""
    
    def test_validate_cas_number(self):
        """测试CAS号验证"""
        self.assertTrue(validate_cas_number("50-78-2"))  # 阿司匹林
        self.assertTrue(validate_cas_number("1000000-00-0"))
        self.assertFalse(validate_cas_number("invalid"))
        self.assertTrue(validate_cas_number(""))  # 空值应通过
    
    def test_calculate_resolution(self):
        """测试分离度计算"""
        # 典型情况
        rs = calculate_resolution(5.0, 7.0, 0.5, 0.6)
        self.assertAlmostEqual(rs, 3.64, places=2)
        
        # 边界情况
        rs = calculate_resolution(5.0, 5.0, 1.0, 1.0)
        self.assertEqual(rs, 0.0)
    
    def test_calculate_theoretical_plates(self):
        """测试理论塔板数计算"""
        n = calculate_theoretical_plates(10.0, 1.0)
        self.assertEqual(n, 1600)
        
        # 边界情况
        n = calculate_theoretical_plates(10.0, 0.0)
        self.assertEqual(n, 0)
    
    def test_assess_peak_quality(self):
        """测试峰质量评估"""
        # 良好峰
        result = assess_peak_quality(2.5, 1.0, 5000)
        self.assertIn("良好", result)
        
        # 有问题峰
        result = assess_peak_quality(1.0, 2.5, 1000)
        self.assertIn("分离度", result)
        self.assertIn("拖尾", result)


class TestModels(unittest.TestCase):
    """测试数据模型"""
    
    def test_compound_creation(self):
        """测试化合物创建"""
        compound = Compound(
            name="Aspirin",
            cas_number="50-78-2",
            mw=180.16
        )
        self.assertEqual(compound.name, "Aspirin")
        self.assertEqual(compound.mw, 180.16)
    
    def test_method_creation(self):
        """测试方法创建"""
        method = ChromatographicMethod(
            name="Test Method",
            column_type="C18",
            flow_rate=1.0
        )
        self.assertEqual(method.column_type, "C18")
        self.assertEqual(method.flow_rate, 1.0)


class TestDatabase(unittest.TestCase):
    """测试数据库操作"""
    
    def setUp(self):
        """测试前准备"""
        from database import Database
        # 使用内存数据库进行测试
        self.db = Database(":memory:")
    
    def test_add_and_get_compound(self):
        """测试添加和获取化合物"""
        compound = Compound(
            name="Test Compound",
            cas_number="123-45-6",
            mw=200.0
        )
        compound_id = self.db.add_compound(compound)
        self.assertIsNotNone(compound_id)
        
        compounds = self.db.get_compounds()
        self.assertEqual(len(compounds), 1)
        self.assertEqual(compounds[0].name, "Test Compound")


if __name__ == '__main__':
    unittest.main()
