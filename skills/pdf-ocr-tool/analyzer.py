# Page Analyzer (進階版 - 混合內容處理)

"""頁面分析模組 - 支援混合內容的智能分割與識別"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum

try:
    from .utils.ollama_client import OllamaClient
    from .utils.image_utils import get_image_size
except ImportError:
    from utils.ollama_client import OllamaClient
    from utils.image_utils import get_image_size


class RegionType(Enum):
    """區域類型列舉。"""
    TEXT = "text"
    TABLE = "table"
    FIGURE = "figure"
    MIXED = "mixed"


@dataclass
class BoundingBox:
    """邊界框資料結構。"""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def area(self) -> int:
        """計算區域面積。"""
        return self.width * self.height
    
    def to_crop_tuple(self) -> Tuple[int, int, int, int]:
        """轉換為裁剪用的 tuple (left, upper, right, lower)。"""
        return (self.x, self.y, self.x + self.width, self.y + self.height)


@dataclass
class Region:
    """區域資料結構。"""
    bbox: BoundingBox
    region_type: RegionType
    confidence: float = 1.0
    content: Optional[str] = None
    image_path: Optional[str] = None
    page_number: int = 0
    
    def to_dict(self) -> dict:
        """轉換為字典。"""
        return {
            "bbox": {
                "x": self.bbox.x,
                "y": self.bbox.y,
                "width": self.bbox.width,
                "height": self.bbox.height,
            },
            "region_type": self.region_type.value,
            "confidence": self.confidence,
            "content": self.content,
            "image_path": self.image_path,
            "page_number": self.page_number,
        }


@dataclass
class PageAnalysis:
    """頁面分析結果資料結構。"""
    page_number: int
    image_path: str
    regions: List[Region] = field(default_factory=list)
    full_text: Optional[str] = None
    detected_type: Optional[str] = None  # 主要類型（text/table/figure/mixed）
    
    def to_dict(self) -> dict:
        """轉換為字典。"""
        return {
            "page_number": self.page_number,
            "image_path": self.image_path,
            "regions": [r.to_dict() for r in self.regions],
            "full_text": self.full_text,
            "detected_type": self.detected_type,
        }


class PageAnalyzer:
    """
    頁面分析器 - 支援混合內容的智能分割與識別
    
    策略：
    1. 如果頁面被檢測為 "mixed" 或指定使用混合模式，將頁面垂直分割成多個區塊
    2. 對每個區塊進行類型識別
    3. 分別處理每個區塊
    """
    
    def __init__(
        self,
        ollama_client=None,
        min_region_height: int = 100,
        detection_model: str = "glm-ocr:q8_0",
        split_strategy: str = "fixed"  # fixed: 固定分割, adaptive: 自適應分割
    ):
        """
        初始化頁面分析器。
        
        Args:
            ollama_client: Ollama 客戶端
            min_region_height: 最小區域高度（像素）
            detection_model: 用於檢測的模型
            split_strategy: 分割策略（fixed/adaptive）
        """
        self.ollama_client = ollama_client
        self.min_region_height = min_region_height
        self.detection_model = detection_model
        self.split_strategy = split_strategy
    
    def analyze_page(
        self,
        image_path: str,
        page_number: int = 0,
        auto_detect: bool = True,
        mixed_mode: bool = True,
        num_regions: int = 3  # 混合模式下的分割數量
    ) -> PageAnalysis:
        """
        分析頁面，識別其中的文字、表格、圖表區域。
        
        Args:
            image_path: 頁面圖片路徑
            page_number: 頁碼
            auto_detect: 是否自動檢測
            mixed_mode: 是否啟用混合模式（將頁面分割成多個區域）
            num_regions: 混合模式下分割的區域數量
            
        Returns:
            頁面分析結果
        """
        # 取得圖片尺寸
        width, height = get_image_size(image_path)
        
        if not auto_detect:
            # 不進行自動檢測，將整頁視為混合內容
            region = Region(
                bbox=BoundingBox(0, 0, width, height),
                region_type=RegionType.MIXED,
                confidence=1.0,
                page_number=page_number
            )
            return PageAnalysis(
                page_number=page_number,
                image_path=image_path,
                regions=[region]
            )
        
        # 使用 AI 檢測頁面主要類型
        detected_type = self.detect_page_type(image_path)
        
        # 如果是混合類型或強制使用混合模式
        if detected_type == "mixed" or (mixed_mode and detected_type in ["text", "table", "figure"]):
            # 將頁面分割成多個區域
            regions = self.split_page_into_regions(
                image_path, page_number, width, height, 
                num_regions=num_regions
            )
            detected_type = "mixed"
        else:
            # 單一類型：整頁作為一個區域
            if detected_type == "table":
                region_type = RegionType.TABLE
            elif detected_type == "figure":
                region_type = RegionType.FIGURE
            else:
                region_type = RegionType.TEXT
            
            region = Region(
                bbox=BoundingBox(0, 0, width, height),
                region_type=region_type,
                confidence=0.8,
                page_number=page_number
            )
            regions = [region]
        
        return PageAnalysis(
            page_number=page_number,
            image_path=image_path,
            regions=regions,
            detected_type=detected_type
        )
    
    def detect_page_type(self, image_path: str) -> str:
        """
        檢測頁面的主要內容類型。
        
        Returns:
            檢測到的類型（text/table/figure/mixed）
        """
        prompt = (
            "分析這個頁面的主要內容類型。請回答：\n"
            "- 'text' 如果主要是純文字段落\n"
            "- 'table' 如果主要是表格數據\n"
            "- 'figure' 如果主要是圖表、圖像或視覺元素\n"
            "- 'mixed' 如果同時包含文字、表格和圖表\n"
            "只回答 text、table、figure 或 mixed："
        )
        
        try:
            response = self.ollama_client.generate(
                prompt=prompt,
                image_path=image_path,
                model=self.detection_model
            )
            
            if response:
                response_lower = response.lower()
                if "mixed" in response_lower:
                    return "mixed"
                elif "table" in response_lower:
                    return "table"
                elif "figure" in response_lower or "chart" in response_lower or "graph" in response_lower:
                    return "figure"
                else:
                    return "text"
        except Exception as e:
            print(f"⚠️ 頁面類型檢測失敗：{e}")
        
        # 預設返回 text
        return "text"
    
    def split_page_into_regions(
        self,
        image_path: str,
        page_number: int,
        width: int,
        height: int,
        num_regions: int = 3
    ) -> List[Region]:
        """
        將頁面分割成多個區域（按垂直方向切割）。
        
        Args:
            image_path: 頁面圖片路徑
            page_number: 頁碼
            width: 圖片寬度
            height: 圖片高度
            num_regions: 分割的區域數量
            
        Returns:
            區域列表
        """
        regions = []
        
        # 計算每個區域的高度
        region_height = height // num_regions
        
        for i in range(num_regions):
            y_start = i * region_height
            # 最後一個區域包含剩餘所有高度
            y_end = height if i == num_regions - 1 else (i + 1) * region_height
            
            bbox = BoundingBox(
                x=0,
                y=y_start,
                width=width,
                height=y_end - y_start
            )
            
            # 檢測這個區域的類型
            region_type = self.detect_region_type(image_path, bbox)
            
            region = Region(
                bbox=bbox,
                region_type=region_type,
                confidence=0.7,
                page_number=page_number
            )
            regions.append(region)
        
        return regions
    
    def detect_region_type(
        self,
        image_path: str,
        bbox: BoundingBox
    ) -> RegionType:
        """
        檢測指定區域名稱的類型。
        
        Args:
            image_path: 頁面圖片路徑
            bbox: 邊界框
            
        Returns:
            區域類型
        """
        # 裁剪出該區域
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                # 計算裁剪區域
                left = bbox.x
                upper = bbox.y
                right = min(bbox.x + bbox.width, img.width)
                lower = min(bbox.y + bbox.height, img.height)
                
                cropped = img.crop((left, upper, right, lower))
                
                # 保存到臨時檔案
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    cropped.save(tmp.name)
                    temp_path = tmp.name
            
            # 對該區域進行類型檢測
            prompt = (
                "分析這個區域的主要內容。只回答一個單詞：\n"
                "- 'text' 如果主要是純文字\n"
                "- 'table' 如果主要是表格\n"
                "- 'figure' 如果主要是圖表或圖片\n"
                "只回答 text、table 或 figure："
            )
            
            response = self.ollama_client.generate(
                prompt=prompt,
                image_path=temp_path,
                model=self.detection_model
            )
            
            # 清理臨時檔案
            os.unlink(temp_path)
            
            if response:
                response_lower = response.lower()
                if "table" in response_lower:
                    return RegionType.TABLE
                elif "figure" in response_lower or "chart" in response_lower:
                    return RegionType.FIGURE
                else:
                    return RegionType.TEXT
        
        except Exception as e:
            print(f"⚠️ 區域類型檢測失敗：{e}")
            return RegionType.TEXT
        
        return RegionType.TEXT
