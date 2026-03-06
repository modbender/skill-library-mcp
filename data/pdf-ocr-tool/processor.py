# Region Processor
"""區域處理模組 - 負責對不同類型的區域進行 OCR 處理"""

import os
import tempfile
from pathlib import Path
from typing import Optional, List

try:
    from .analyzer import Region, RegionType, PageAnalysis, BoundingBox
    from .utils.ollama_client import OllamaClient
    from .prompts import get_prompt
except ImportError:
    from analyzer import Region, RegionType, PageAnalysis, BoundingBox
    from utils.ollama_client import OllamaClient
    from prompts import get_prompt

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class RegionProcessor:
    """區域處理器 - 對不同類型的區域執行 OCR"""
    
    def __init__(
        self,
        ollama_client=None,
        output_dir: str = "./output",
        save_cropped_images: bool = False
    ):
        """
        初始化區域處理器。
        
        Args:
            ollama_client: Ollama 客戶端
            output_dir: 輸出目錄
            save_cropped_images: 是否保存裁剪的圖片
        """
        self.ollama_client = ollama_client
        self.output_dir = Path(output_dir)
        self.save_cropped_images = save_cropped_images
    
    def process_region(
        self,
        region: Region,
        page_image_path: str,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        處理單個區域。
        
        Args:
            region: 區域物件
            page_image_path: 頁面圖片路徑
            custom_prompt: 自訂提示詞
        
        Returns:
            OCR 結果文字
        """
        # 根據區域類型選擇提示詞
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self._get_prompt_for_type(region.region_type)
        
        # 檢查是否需要裁剪
        if region.bbox.x == 0 and region.bbox.y == 0:
            width, height = self._get_image_size(page_image_path)
            if region.bbox.width == width and region.bbox.height == height:
                # 整頁，直接使用原圖
                result = self.ollama_client.ocr_image(
                    image_path=page_image_path,
                    prompt=prompt
                )
                region.content = result or "❌ OCR 失敗"
                return region.content
        
        # 需要裁剪區域
        cropped_path = self._crop_region(page_image_path, region.bbox)
        try:
            result = self.ollama_client.ocr_image(
                image_path=cropped_path,
                prompt=prompt
            )
            region.content = result or "❌ OCR 失敗"
        finally:
            # 清理臨時檔案
            if not self.save_cropped_images and cropped_path != page_image_path:
                try:
                    os.remove(cropped_path)
                except:
                    pass
        
        return region.content
    
    def _get_prompt_for_type(self, region_type: RegionType) -> str:
        """根據區域類型取得對應的提示詞。"""
        prompt_map = {
            RegionType.TEXT: get_prompt("text"),
            RegionType.TABLE: get_prompt("table"),
            RegionType.FIGURE: get_prompt("figure"),
            RegionType.MIXED: get_prompt("mixed"),
        }
        return prompt_map.get(region_type, get_prompt("mixed"))
    
    def _crop_region(
        self,
        image_path: str,
        bbox: BoundingBox,
        output_path: Optional[str] = None
    ) -> str:
        """裁剪指定區域。"""
        if not PILLOW_AVAILABLE:
            raise ImportError("Pillow 未安裝，請執行：uv pip install Pillow")
        
        # 生成臨時輸出路徑
        if output_path is None:
            output_dir = Path(image_path).parent
            output_path = str(output_dir / f"cropped_{Path(image_path).stem}.png")
        
        with Image.open(image_path) as img:
            # 轉換 bbox 為 crop 格式 (left, upper, right, lower)
            left = bbox.x
            upper = bbox.y
            right = bbox.x + bbox.width
            lower = bbox.y + bbox.height
            
            # 確保不超出邊界
            right = min(right, img.width)
            lower = min(lower, img.height)
            
            cropped = img.crop((left, upper, right, lower))
            cropped.save(output_path)
        
        return output_path
    
    def _get_image_size(self, image_path: str) -> tuple:
        """取得圖片尺寸。"""
        if PILLOW_AVAILABLE:
            with Image.open(image_path) as img:
                return img.width, img.height
        else:
            # Fallback：使用 utils
            try:
                from .utils.image_utils import get_image_size
                return get_image_size(image_path)
            except:
                return (0, 0)
    
    def process_page_analysis(self, analysis: PageAnalysis) -> PageAnalysis:
        """
        處理整個頁面的分析結果。
        
        Args:
            analysis: 頁面分析結果
        
        Returns:
            處理後的頁面分析結果
        """
        for region in analysis.regions:
            self.process_region(region, analysis.image_path)
        return analysis
