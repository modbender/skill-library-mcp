"""
壓力測試與邊界條件測試
用於找出潛在問題
"""

import pytest
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer import PageAnalyzer, RegionType, BoundingBox
from processor import RegionProcessor
from utils.ollama_client import OllamaClient


class TestStress:
    """壓力測試"""
    
    def test_large_image(self, tmp_path):
        """測試大圖片處理"""
        # 建立大圖片（1000x1000）
        test_img = tmp_path / "large.png"
        img = Image.new('RGB', (1000, 1000), color='blue')
        img.save(str(test_img))
        
        analyzer = PageAnalyzer()
        # 應該能正常分析
        analysis = analyzer.analyze_page(
            str(test_img),
            page_number=1,
            auto_detect=False  # 避免實際调用 Ollama
        )
        
        assert analysis.page_number == 1
        assert len(analysis.regions) == 1
    
    def test_very_small_image(self, tmp_path):
        """測試極小圖片處理"""
        # 建立 1x1 像素的圖片
        test_img = tmp_path / "tiny.png"
        img = Image.new('RGB', (1, 1), color='red')
        img.save(str(test_img))
        
        analyzer = PageAnalyzer()
        analysis = analyzer.analyze_page(
            str(test_img),
            page_number=1,
            auto_detect=False
        )
        
        assert analysis.page_number == 1
    
    def test_many_regions(self, tmp_path):
        """測試多區域分割"""
        test_img = tmp_path / "test.png"
        img = Image.new('RGB', (300, 900), color='green')  # 300x900，分成 3 個 300x300
        img.save(str(test_img))
        
        analyzer = PageAnalyzer()
        # 強制分成 5 個區域
        analysis = analyzer.analyze_page(
            str(test_img),
            page_number=1,
            auto_detect=True,
            mixed_mode=True,
            num_regions=5
        )
        
        # 應該有 5 個區域
        assert len(analysis.regions) == 5
        
        # 檢查每個區域的高度應該是 180 (900/5)
        for region in analysis.regions:
            assert region.bbox.height == 180


class TestEdgeCases:
    """邊界條件測試"""
    
    def test_empty_bbox(self):
        """測試空邊界框"""
        bbox = BoundingBox(0, 0, 0, 0)
        assert bbox.area == 0
        assert bbox.to_crop_tuple() == (0, 0, 0, 0)
    
    def test_negative_coordinates(self, tmp_path):
        """測試負坐標（應該被處理）"""
        test_img = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='white')
        img.save(str(test_img))
        
        # 建立有負坐標的區域（不應該發生，但要測試容錯）
        bbox = BoundingBox(-10, -10, 100, 100)
        
        analyzer = PageAnalyzer()
        # 應該能處理，不會崩潰
        region = analyzer.detect_region_type(str(test_img), bbox)
        assert region in [RegionType.TEXT, RegionType.TABLE, RegionType.FIGURE]
    
    def test_very_large_bbox(self, tmp_path):
        """測試超大邊界框"""
        test_img = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='white')
        img.save(str(test_img))
        
        # 建立超出圖片的邊界框
        bbox = BoundingBox(0, 0, 10000, 10000)
        
        analyzer = PageAnalyzer()
        # 應該能處理，不會崩潰
        region = analyzer.detect_region_type(str(test_img), bbox)
        assert region in [RegionType.TEXT, RegionType.TABLE, RegionType.FIGURE]


class TestPromptLoading:
    """測試提示詞加載"""
    
    def test_all_prompts_exist(self):
        """測試所有提示詞都存在"""
        from prompts import TEXT_PROMPT, TABLE_PROMPT, FIGURE_PROMPT, MIXED_PROMPT
        
        assert TEXT_PROMPT is not None
        assert TABLE_PROMPT is not None
        assert FIGURE_PROMPT is not None
        assert MIXED_PROMPT is not None
        
        assert len(TEXT_PROMPT) > 0
        assert len(TABLE_PROMPT) > 0
        assert len(FIGURE_PROMPT) > 0
        assert len(MIXED_PROMPT) > 0
    
    def test_prompt_content(self):
        """測試提示詞內容"""
        from prompts import load_prompt
        
        # 測試加載所有提示詞
        for name in ["text", "table", "figure", "mixed"]:
            prompt = load_prompt(name)
            assert isinstance(prompt, str)
            assert len(prompt) > 0


class TestIntegration:
    """整合測試"""
    
    def test_full_pipeline_mock(self, tmp_path):
        """測試完整流程（使用假圖片，不調用 Ollama）"""
        # 建立測試圖片
        test_img = tmp_path / "test.png"
        img = Image.new('RGB', (200, 600), color='gray')
        img.save(str(test_img))
        
        # 1. 分析
        analyzer = PageAnalyzer()
        analysis = analyzer.analyze_page(
            str(test_img),
            page_number=1,
            auto_detect=False  # 不調用 Ollama
        )
        
        assert analysis.page_number == 1
        assert len(analysis.regions) == 1
        
        # 2. 處理（這裡不實際調用 OCR，只測試流程）
        # processor 需要 Ollama client，所以跳過實際 OCR
        
        # 3. 整合
        from integrator import MarkdownIntegrator
        integrator = MarkdownIntegrator(save_images=False)
        
        # 手動設置內容以測試整合
        analysis.regions[0].content = "測試內容"
        analysis.regions[0].region_type = RegionType.TEXT
        
        output_md = tmp_path / "output.md"
        integrator.integrate([analysis], str(output_md), metadata={"test": True})
        
        # 檢查輸出
        assert output_md.exists()
        content = output_md.read_text()
        assert "測試內容" in content
        assert "PDF 轉 Markdown" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
