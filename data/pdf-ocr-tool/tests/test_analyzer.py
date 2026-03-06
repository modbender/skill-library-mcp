"""
測試頁面分析模組
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer import PageAnalyzer, PageAnalysis, Region, RegionType, BoundingBox
from utils.ollama_client import OllamaClient


class TestBoundingBox:
    """測試 BoundingBox 資料結構"""
    
    def test_init(self):
        """測試初始化"""
        bbox = BoundingBox(x=10, y=20, width=100, height=200)
        assert bbox.x == 10
        assert bbox.y == 20
        assert bbox.width == 100
        assert bbox.height == 200
    
    def test_area(self):
        """測試面積計算"""
        bbox = BoundingBox(x=0, y=0, width=10, height=20)
        assert bbox.area == 200
    
    def test_to_crop_tuple(self):
        """測試轉換為裁剪 tuple"""
        bbox = BoundingBox(x=10, y=20, width=100, height=200)
        result = bbox.to_crop_tuple()
        assert result == (10, 20, 110, 220)


class TestRegion:
    """測試 Region 資料結構"""
    
    def test_init(self):
        """測試初始化"""
        bbox = BoundingBox(0, 0, 100, 100)
        region = Region(bbox=bbox, region_type=RegionType.TEXT)
        
        assert region.bbox == bbox
        assert region.region_type == RegionType.TEXT
        assert region.confidence == 1.0
        assert region.content is None
    
    def test_to_dict(self):
        """測試轉換為字典"""
        bbox = BoundingBox(0, 0, 100, 100)
        region = Region(
            bbox=bbox,
            region_type=RegionType.TABLE,
            confidence=0.9,
            page_number=1
        )
        
        result = region.to_dict()
        assert "bbox" in result
        assert result["region_type"] == "table"
        assert result["confidence"] == 0.9
        assert result["page_number"] == 1


class TestPageAnalysis:
    """測試 PageAnalysis 資料結構"""
    
    def test_init(self):
        """測試初始化"""
        analysis = PageAnalysis(
            page_number=1,
            image_path="/test.png"
        )
        
        assert analysis.page_number == 1
        assert analysis.image_path == "/test.png"
        assert len(analysis.regions) == 0
        assert analysis.full_text is None
    
    def test_to_dict(self):
        """測試轉換為字典"""
        bbox = BoundingBox(0, 0, 100, 100)
        region = Region(bbox=bbox, region_type=RegionType.TEXT)
        
        analysis = PageAnalysis(
            page_number=1,
            image_path="/test.png",
            regions=[region],
            detected_type="text"
        )
        
        result = analysis.to_dict()
        assert result["page_number"] == 1
        assert len(result["regions"]) == 1
        assert result["detected_type"] == "text"


class TestPageAnalyzer:
    """測試 PageAnalyzer 類別"""
    
    def test_init_default(self):
        """測試預設初始化"""
        analyzer = PageAnalyzer()
        assert analyzer.min_region_height == 100
        assert analyzer.detection_model == "glm-ocr:q8_0"
    
    def test_init_custom(self):
        """測試自訂初始化"""
        client = OllamaClient()
        analyzer = PageAnalyzer(
            ollama_client=client,
            min_region_height=200,
            detection_model="test-model"
        )
        assert analyzer.ollama_client == client
        assert analyzer.min_region_height == 200
        assert analyzer.detection_model == "test-model"
    
    def test_analyze_page_no_auto_detect(self, tmp_path):
        """測試不自動檢測模式"""
        # 建立真實的測試圖片（1x1 像素）
        from PIL import Image
        test_img = tmp_path / "test.png"
        img = Image.new('RGB', (1, 1), color='red')
        img.save(str(test_img))
        
        analyzer = PageAnalyzer()
        analysis = analyzer.analyze_page(
            str(test_img),
            page_number=1,
            auto_detect=False
        )
        
        assert analysis.page_number == 1
        assert len(analysis.regions) == 1
        assert analysis.regions[0].region_type == RegionType.MIXED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
